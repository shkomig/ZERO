"""
Zero Agent API Server
=====================
FastAPI server with REST endpoints and WebSocket streaming

Web Interfaces:
    GET  /                  - Main web interface
    GET  /simple            - Simple chat interface
    GET  /docs              - API documentation

API Endpoints:
    POST /api/chat          - Chat with Zero
    POST /api/tools/email   - Email operations
    POST /api/tools/calendar - Calendar operations
    POST /api/tools/database - Database queries
    GET  /api/memory/stats  - Memory statistics
    WS   /ws/chat          - WebSocket streaming

Install:
    pip install fastapi uvicorn websockets
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
import asyncio
from pathlib import Path
import sys
from collections import defaultdict
from datetime import datetime, timedelta
import json
import os
import re
import time
import uuid

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import Zero components
from streaming_llm import StreamingMultiModelLLM
from router_context_aware import ContextAwareRouter
from multi_model_executor import MultiModelExecutor

# Import tools
try:
    from tool_gmail import gmail_search, gmail_recent, gmail_send
    GMAIL_AVAILABLE = True
except:
    GMAIL_AVAILABLE = False

try:
    from tool_calendar import calendar_today, calendar_week, calendar_create
    CALENDAR_AVAILABLE = True
except:
    CALENDAR_AVAILABLE = False

try:
    from tool_database import db_query, db_tables, db_schema
    DATABASE_AVAILABLE = True
except:
    DATABASE_AVAILABLE = False

try:
    from tool_websearch_improved import EnhancedWebSearchTool
    WEBSEARCH_AVAILABLE = True
except:
    try:
        from tool_websearch import WebSearchTool
        WEBSEARCH_AVAILABLE = True
    except:
        WEBSEARCH_AVAILABLE = False

# Import memory
try:
    from memory.memory_manager import MemoryManager
    from memory.short_term_memory import ShortTermMemory
    MEMORY_AVAILABLE = True
except:
    MEMORY_AVAILABLE = False

# Import code executor
try:
    from tool_codeexecutor import CodeExecutorTool
    CODE_EXECUTOR_AVAILABLE = True
except:
    CODE_EXECUTOR_AVAILABLE = False

# Rate Limiting (as per llm_internet_integration_guide.md)
class SimpleRateLimiter:
    """
    Simple in-memory rate limiter
    Recommended: 10 requests/minute per IP (from guide)
    """
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request from this IP is allowed"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        # Remove old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff
        ]
        
        # Check if under limit
        if len(self.requests[client_ip]) < self.max_requests:
            self.requests[client_ip].append(now)
            return True
        
        return False
    
    def get_remaining(self, client_ip: str) -> int:
        """Get remaining requests for this IP"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        # Count recent requests
        recent = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff
        ]
        
        return max(0, self.max_requests - len(recent))

# Initialize rate limiter
rate_limiter = SimpleRateLimiter(max_requests=10, window_seconds=60)

# Import Agent Orchestrator
try:
    from zero_agent.agent_orchestrator import AgentOrchestrator
    from zero_agent.safety_layer import SafetyLayer, Action
    AGENT_ORCHESTRATOR_AVAILABLE = True
except:
    AGENT_ORCHESTRATOR_AVAILABLE = False
    print("[API] WARNING: Agent Orchestrator not available")

# Import faster-whisper for voice transcription
try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except:
    WHISPER_AVAILABLE = False
    print("[API] WARNING: faster-whisper not available - voice features disabled")


# ============================================================================
# Pydantic Models
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None  # fast, smart, coder, balanced
    use_memory: bool = True
    stream: bool = False
    conversation_history: Optional[List[Dict[str, str]]] = None  # NEW: For context management


class ChatResponse(BaseModel):
    response: str
    model_used: str
    tokens: Optional[int] = None
    duration: Optional[float] = None


class EmailRequest(BaseModel):
    action: str  # search, recent, send
    query: Optional[str] = None
    to: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    count: int = 10


class CalendarRequest(BaseModel):
    action: str  # today, week, create
    summary: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    description: Optional[str] = None


class DatabaseRequest(BaseModel):
    action: str  # query, tables, schema
    query: Optional[str] = None
    table_name: Optional[str] = None
    db_path: str = "workspace/data.db"


class ProjectReviewRequest(BaseModel):
    project_path: str
    review_type: str = "full"  # full, quick, security, architecture


class WebSearchRequest(BaseModel):
    query: str
    max_results: int = 5


class ExecuteCodeRequest(BaseModel):
    action: str  # python, bash, filesystem
    command: str
    args: Optional[Dict[str, Any]] = None


class VoiceTranscribeRequest(BaseModel):
    audio_url: Optional[str] = None  # URL to audio file
    audio_base64: Optional[str] = None  # Base64 encoded audio
    language: Optional[str] = "he"  # Hebrew default


class VoiceTranscribeResponse(BaseModel):
    text: str
    language: str
    duration: float


class ToolResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None


# ============================================================================
# FastAPI App with Lifespan
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown events.
    Replaces deprecated @app.on_event("startup") and @app.on_event("shutdown")
    """
    # Startup
    try:
        zero.initialize()
        # Initialize Computer Control Agent
        if COMPUTER_CONTROL_AVAILABLE:
            initialize_computer_control()
            print("[API] Computer Control Agent initialized")
        
        # Preload LLM Model (eliminate cold start!)
        print("[API] Preloading LLM model...")
        try:
            import requests
            # Warm up the model with a simple request
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:3b",
                    "prompt": "test",
                    "stream": False
                },
                timeout=30
            )
            if response.status_code == 200:
                print("[API] OK LLM model preloaded successfully! (No more cold start)")
            else:
                print(f"[API] WARNING LLM preload responded with code {response.status_code}")
        except Exception as preload_error:
            print(f"[API] WARNING LLM preload failed (will load on first request): {preload_error}")
        
    except Exception as e:
        print(f"[API] ERROR Initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    print("\n[API] Shutting down...")

app = FastAPI(
    title="Zero Agent API",
    description="AI Agent with Memory, Tools, and Multi-Model Support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Global State
# ============================================================================

class ZeroAgent:
    """Global Zero Agent instance"""
    
    def __init__(self):
        self.llm = None
        self.router = None
        self.executor = None
        self.memory = None
        self.code_executor = None
        self.agent_orchestrator = None
        self.safety_layer = None
        self.initialized = False
    
    def initialize(self):
        """Initialize Zero Agent components"""
        if self.initialized:
            return
        
        print("\n[API] Initializing Zero Agent...")
        
        # Initialize LLM - use Mixtral 8x7B for best performance and Hebrew quality
        # Alternative: "fast" (mistral:latest) for speed, "smart" (deepseek-r1:32b) for complex reasoning
        self.llm = StreamingMultiModelLLM(default_model="expert")
        if not self.llm.test_connection(verbose=False):
            raise ConnectionError("Cannot connect to Ollama!")
        print("[API] OK LLM connected")
        
        # Initialize Router
        self.router = ContextAwareRouter(self.llm)
        print("[API] OK Router ready")
        
        # Initialize Executor
        self.executor = MultiModelExecutor(self.llm, self.router)
        print("[API] OK Executor ready")
        
        # Initialize Memory
        if MEMORY_AVAILABLE:
            try:
                self.memory = MemoryManager(
                    memory_dir=Path("workspace/memory"),
                    rag_url="http://localhost:8000",
                    enable_rag=False  # We'll use embedded RAG instead
                )
                print("[API] OK Memory ready")
            except Exception as e:
                print(f"[API] WARNING Memory unavailable: {e}")
                self.memory = None
        
        # Initialize RAG System (Embedded ChromaDB - Phase 3)
        try:
            from zero_agent.rag.memory import RAGMemorySystem
            self.rag = RAGMemorySystem()
            print("[API] OK RAG System ready (Embedded ChromaDB)")
        except Exception as e:
            print(f"[API] WARNING RAG unavailable: {e}")
            self.rag = None
        
        # Initialize Learning System (Phase 3: Behavior Learning)
        try:
            from zero_agent.tools.behavior_learner import BehaviorLearner, UserAction
            from datetime import datetime
            self.learner = BehaviorLearner(memory_system=self.memory)
            self.UserAction = UserAction  # Store class for easy access
            print("[API] OK Behavior Learner ready")
        except Exception as e:
            print(f"[API] WARNING Learner unavailable: {e}")
            self.learner = None
        
        # Initialize Code Executor
        if CODE_EXECUTOR_AVAILABLE:
            try:
                self.code_executor = CodeExecutorTool(workspace=Path("workspace"))
                print("[API] OK Code executor ready")
            except Exception as e:
                print(f"[API] WARNING Code executor unavailable: {e}")
                self.code_executor = None
        
        # Initialize Agent Orchestrator
        print(f"[API] AGENT_ORCHESTRATOR_AVAILABLE = {AGENT_ORCHESTRATOR_AVAILABLE}")
        if AGENT_ORCHESTRATOR_AVAILABLE:
            try:
                # Create tools dict for orchestrator
                tools_dict = {}
                if self.code_executor:
                    tools_dict['execute_python'] = self.code_executor
                    tools_dict['execute_bash'] = self.code_executor
                    tools_dict['create_folder'] = self.code_executor
                    tools_dict['create_file'] = self.code_executor
                    print(f"[API] Tools dict created: {list(tools_dict.keys())}")
                
                self.safety_layer = SafetyLayer()
                self.agent_orchestrator = AgentOrchestrator(
                    llm=self.llm,
                    tools=tools_dict
                )
                print("[API] OK Agent Orchestrator ready")
            except Exception as e:
                import traceback
                print(f"[API] WARNING Agent Orchestrator unavailable: {e}")
                print(f"[API] Traceback: {traceback.format_exc()}")
                self.agent_orchestrator = None
                self.safety_layer = None
        else:
            print("[API] Agent Orchestrator not available (AGENT_ORCHESTRATOR_AVAILABLE = False)")
        
        self.initialized = True
        print("[API] SUCCESS Zero Agent ready!\n")


# Global agent instance
zero = ZeroAgent()

# Regular expressions for Hebrew enforcement
LATIN_PATTERN = re.compile(r"[A-Za-z]")
CODE_BLOCK_PATTERN = re.compile(r"```")


def enforce_hebrew_output(text: str, model: str) -> str:
    """
    DISABLED: This function was causing severe text corruption by removing characters.
    The proper solution is to use correct prompt templates and parameters.
    """
    # Simply return the original text without any modifications
    return text

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="."), name="static")
except Exception as e:
    print(f"[API] WARNING: Could not mount static files: {e}")

# Mount zero logo directory
try:
    app.mount("/zero%20logo", StaticFiles(directory="zero logo"), name="zero-logo")
except Exception as e:
    print(f"[API] WARNING: Could not mount zero logo: {e}")

# Serve HTML file
@app.get("/zero_web_interface.html")
async def serve_html():
    """Serve the web interface HTML file"""
    html_path = Path("zero_web_interface.html")
    if html_path.exists():
        return FileResponse(html_path)
    else:
        raise HTTPException(status_code=404, detail="HTML file not found")

@app.get("/zero_chat_simple.html")
async def serve_simple_chat():
    """Serve the simple chat interface HTML file"""
    html_path = Path("zero_chat_simple.html")
    if html_path.exists():
        return FileResponse(html_path)
    else:
        raise HTTPException(status_code=404, detail="HTML file not found")

# Serve logo
@app.get("/logo.png")
async def serve_main_logo():
    """Serve main logo"""
    logo_path = Path("logo.png")
    if logo_path.exists():
        return FileResponse(logo_path)
    else:
        raise HTTPException(status_code=404, detail="Logo not found")

@app.get("/zero_logo/{filename}")
async def serve_logo(filename: str):
    """Serve files from zero logo directory"""
    logo_dir = Path("zero logo")
    file_path = logo_dir / filename
    if file_path.exists():
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Logo file not found")


# ============================================================================
# Startup/Shutdown - Moved to lifespan context manager above
# ============================================================================
# Note: @app.on_event("startup") and @app.on_event("shutdown") are deprecated
# in FastAPI and have been replaced with the lifespan context manager.
# See the lifespan function definition above for the current implementation.


# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
async def root():
    """Serve the main web interface"""
    html_path = Path("zero_web_interface.html")
    if html_path.exists():
        return FileResponse(html_path)
    # Fallback to API info if HTML not found
    return {
        "status": "online",
        "agent": "Zero Agent",
        "version": "1.0.0",
        "features": {
            "llm": zero.initialized,
            "memory": MEMORY_AVAILABLE and zero.memory is not None,
            "gmail": GMAIL_AVAILABLE,
            "calendar": CALENDAR_AVAILABLE,
            "database": DATABASE_AVAILABLE,
            "agent_system": AGENT_ORCHESTRATOR_AVAILABLE and zero.agent_orchestrator is not None,
            "computer_control": COMPUTER_CONTROL_AVAILABLE
        },
        "endpoints": {
            "ui": {
                "main": "/",
                "simple": "/simple",
                "docs": "/docs"
            },
            "chat": "/api/chat",
            "email": "/api/tools/email",
            "calendar": "/api/tools/calendar",
            "database": "/api/tools/database",
            "memory": "/api/memory/stats",
            "project_review": "/api/tools/project-review",
            "computer_control": {
                "command": "/api/computer-control/command",
                "suggestions": "/api/computer-control/suggestions",
                "analyze_screen": "/api/computer-control/analyze-screen",
                "find_element": "/api/computer-control/find-element",
                "learning_stats": "/api/computer-control/learning-stats"
            },
            "websocket": "/ws/chat"
        }
    }


@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "initialized": zero.initialized}


@app.get("/simple")
async def serve_simple():
    """Serve the simple chat interface"""
    html_path = Path("zero_chat_simple.html")
    if html_path.exists():
        return FileResponse(html_path)
    raise HTTPException(status_code=404, detail="Simple interface not found")


@app.get("/advanced")
async def serve_advanced():
    """Serve the advanced voice interface"""
    html_path = Path("zero_chat_advanced.html")
    if html_path.exists():
        return FileResponse(html_path)
    raise HTTPException(status_code=404, detail="Advanced interface not found")


@app.get("/memory-dashboard", response_class=HTMLResponse)
async def memory_dashboard():
    """
    Memory Dashboard - Phase 3: Step 5.2
    Shows memory statistics, recent conversations, and preferences
    """
    if not zero.memory:
        return "<h1>Memory not initialized</h1>"
    
    try:
        stats = zero.memory.short_term.get_statistics()
        prefs = zero.memory.short_term.get_all_preferences()
        recent = zero.memory.short_term.get_recent_conversations(hours=24, limit=10)
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>Zero Memory Dashboard</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; margin: 0; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
                h1 {{ color: #667eea; margin-top: 0; }}
                h2 {{ color: #764ba2; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .stat-number {{ font-size: 36px; font-weight: bold; }}
                .stat-label {{ font-size: 14px; opacity: 0.9; }}
                .pref-item, .conv-item {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #667eea; }}
                .nav-link {{ display: inline-block; margin-top: 20px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Zero Memory Dashboard</h1>
                <h2>Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-card"><div class="stat-number">{stats['total_conversations']}</div><div class="stat-label">Total Conversations</div></div>
                    <div class="stat-card"><div class="stat-number">{stats['conversations_24h']}</div><div class="stat-label">Today</div></div>
                    <div class="stat-card"><div class="stat-number">{stats['total_preferences']}</div><div class="stat-label">Preferences</div></div>
                    <div class="stat-card"><div class="stat-number">{stats['total_facts']}</div><div class="stat-label">Facts</div></div>
                </div>
                <h2>Preferences</h2>
        """
        
        if prefs:
            for key, val in prefs.items():
                html += f'<div class="pref-item"><strong>{key}:</strong> {val}</div>'
        else:
            html += '<div class="pref-item">No preferences saved</div>'
        
        html += '<h2>Recent Conversations</h2>'
        
        if recent:
            for conv in recent[:5]:
                user_msg = str(conv['user_message'])[:80]
                asst_msg = str(conv['assistant_message'])[:80]
                html += f'<div class="conv-item"><strong>User:</strong> {user_msg}...<br><strong>Zero:</strong> {asst_msg}...</div>'
        else:
            html += '<div class="conv-item">No recent conversations</div>'
        
        html += '<a href="/simple" class="nav-link">Back to Chat</a></div></body></html>'
        
        return html
        
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"


@app.get("/api/tts")
async def text_to_speech(text: str):
    """
    Text-to-Speech endpoint - converts text to audio
    
    Phase 2: Voice Output support
    """
    try:
        import requests
        from fastapi.responses import Response
        
        # Call TTS service (Hebrew TTS on port 9033)
        tts_url = f"http://localhost:9033/tts?text={text}"
        response = requests.get(tts_url, timeout=10)
        
        if response.status_code == 200:
            return Response(
                content=response.content,
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "inline",
                    "Cache-Control": "no-cache"
                }
            )
        else:
            raise HTTPException(status_code=503, detail="TTS service unavailable")
            
    except requests.exceptions.RequestException as e:
        print(f"[TTS] Service unavailable: {e}")
        raise HTTPException(status_code=503, detail="TTS service not running")
    except Exception as e:
        print(f"[TTS] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agent/direct")
async def direct_agent_execution(request: ChatRequest):
    """
    Direct execution via Agent Orchestrator - bypasses normal chat flow
    """
    if not zero.initialized:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if not zero.agent_orchestrator:
        raise HTTPException(status_code=503, detail="Agent Orchestrator not available")
    
    try:
        print(f"[API/DIRECT] Executing goal: {request.message}")
        result = zero.agent_orchestrator.execute_goal(request.message, max_iterations=10)
        
        return ChatResponse(
            response=f"Agent Orchestrator Result:\n\nSuccess: {result.success}\n\nOutput: {result.output}\n\nDuration: {result.duration if hasattr(result, 'duration') else 'N/A'}s",
            model_used="agent_orchestrator",
            duration=result.duration if hasattr(result, 'duration') else None
        )
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"[API/DIRECT] ERROR: {error_msg}")
        return ChatResponse(
            response=error_msg,
            model_used="agent_orchestrator_error"
        )


# ============================================================================
# Chat Endpoints
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    """
    Chat with Zero Agent (with Rate Limiting)
    
    Example:
        POST /api/chat
        {
            "message": "What's the weather?",
            "model": "fast",
            "use_memory": true
        }
    """
    # Fix encoding for Hebrew/Unicode
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    
    if not zero.initialized:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # Rate limiting check (10 requests/minute as per guide)
    client_ip = http_request.client.host
    if not rate_limiter.is_allowed(client_ip):
        remaining = rate_limiter.get_remaining(client_ip)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again later. ({remaining} requests remaining)"
        )
    
    import time
    start_time = time.time()
    
    try:
        
        # Check if user wants to search the web
        search_triggered = False
        search_results = ""
        action_result = None
        
        # Detect search requests - expanded keywords
        search_keywords = [
            'חפש ברשת', 'חפש', 'חיפוש', 'חיפוש על', 
            'search', 'google', 'search for',
            'מה המחיר', 'מחיר של', 'מחיר מניית', 'price of', 'price', 'stock price',
            'spy', 'qqq', 'aapl', 'tsla', 'msft', 'amzn', 'googl',  # Popular stocks
            'מה חדש', 'מה השעה', 'מה התאריך', 'what time', 'what date',
            'איך לבנות', 'how to build', 'tutorial'
        ]
        
        if any(keyword in request.message.lower() for keyword in search_keywords):
            try:
                print(f"[API] Search keyword detected in: {request.message}")
            except:
                print(f"[API] Search keyword detected in message")
            if WEBSEARCH_AVAILABLE:
                search_triggered = True
                print(f"[API] Triggering Enhanced WebSearch...")
                # Extract search query (everything after "search for" or similar)
                search_query = request.message
                for trigger in ['חפש ברשת', 'חפש', 'חיפוש על', 'search for', 'google']:
                    if trigger in request.message.lower():
                        search_query = request.message.lower().split(trigger, 1)[1].strip()
                        break
                
                # Use Enhanced WebSearch if available (with timeout protection)
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("Search timeout exceeded")
                
                try:
                    from tool_websearch_improved import EnhancedWebSearchTool
                    search_tool = EnhancedWebSearchTool()
                    
                    # Set 10-second timeout for search (as per guide recommendation)
                    try:
                        search_result = search_tool.smart_search(search_query)
                        formatted_result = search_tool.format_results(search_result)
                        search_results = f"\n\nחיפוש עדכני ברשת:\n{formatted_result}\n"
                        
                        # Log success (avoid Unicode errors by not printing content)
                        result_type = search_result.get("type", "unknown")
                        if result_type == "stock":
                            symbol = search_result.get("symbol", "?")
                            price = search_result.get("price", "?")
                            print(f"[WebSearch] SUCCESS - Stock data for {symbol}: ${price}")
                        else:
                            num_results = len(search_result.get("results", []))
                            print(f"[WebSearch] SUCCESS - Got {num_results} web results ({len(formatted_result)} chars)")
                    except TimeoutError:
                        print(f"[WebSearch] TIMEOUT - Search took too long (>10s)")
                        search_triggered = False
                        search_results = ""
                        
                except Exception as e:
                    print(f"[WebSearch] ERROR in Enhanced: {e}")
                    # Graceful degradation - continue without search results
                    search_triggered = False
                    search_results = ""
                    print(f"[WebSearch] Graceful degradation - continuing without search")
        
        # Check for Computer Control commands FIRST
        computer_control_keywords = [
            # Open commands
            'פתח ', 'תפתח ', 'הפעל ', 'תפעיל ', 'הרץ ', 'תריץ ',
            'open ', 'launch ', 'start ', 'run ',
            # Click commands
            'לחץ ', 'תלחץ ', 'לחיצה ',
            'click ', 'press ',
            # Type commands
            'הקלד ', 'תקליד ',
            'type ', 'enter ',
            # Scroll commands
            'גלול ', 'תגלול ',
            'scroll ',
            # Screenshot commands
            'צלם מסך', 'תצלם מסך', 'צילום מסך',
            'screenshot', 'take screenshot', 'capture screen',
            # Image generation commands
            'צור תמונה', 'תצור תמונה', 'צייר', 'תצייר', 'הפק תמונה',
            'generate image', 'create image', 'draw', 'make image',
            # Video generation commands
            'צור סרטון', 'תצור סרטון', 'הפק סרטון', 'צור וידאו',
            'generate video', 'create video', 'make video', 'render video',
            # TTS commands
            'הקרא בקול', 'תקרא בקול', 'דבר', 'תדבר', 'הגה', 'תהגה',
            'speak', 'say', 'read out', 'read aloud', 'voice',
            # Hotkey commands (check for + in message for keyboard shortcuts)
        ]
        
        # Check for keyboard shortcuts (contains + for combinations)
        is_hotkey = '+' in request.message and any(k in request.message.lower() for k in ['ctrl', 'alt', 'shift', 'win', 'קונטרול', 'אלט', 'שיפט'])
        
        is_computer_control = any(request.message.lower().startswith(keyword) for keyword in computer_control_keywords) or is_hotkey
        
        if is_computer_control and COMPUTER_CONTROL_AVAILABLE and computer_control_agent:
            try:
                print(f"[API] Computer Control command detected: {request.message}")
                result = computer_control_agent.process_command(request.message)
                
                if result.get("success"):
                    # Return the action result as the response
                    return ChatResponse(
                        response=f"✅ {result.get('result', 'פעולה בוצעה בהצלחה')}",
                        model_used=request.model or "computer-control",
                        tokens=0,
                        duration=time.time() - start_time
                    )
                else:
                    error_msg = result.get('error', 'פעולה נכשלה')
                    return ChatResponse(
                        response=f"❌ {error_msg}",
                        model_used=request.model or "computer-control",
                        tokens=0,
                        duration=time.time() - start_time
                    )
            except Exception as e:
                print(f"[API] Computer Control error: {e}")
                # Continue to normal chat if Computer Control fails
        
        # Check if this is a complex task that requires Agent Orchestrator
        complex_task_keywords = [
            'צור פרויקט', 'create project', 'צור אפליקציה', 'create app',
            'צור תיקייה', 'create folder', 'עשה תיקייה', 'צר תיקיה', 'תיצור תיקייה',
            'צור קובץ', 'create file', 'עשה קובץ',
            'רשום הודעה', 'write message',
            'הרץ פקודה', 'run command'
        ]
        
        # Safely print message (avoid encoding errors)
        try:
            print(f"[API] Checking message: {request.message}")
        except:
            print(f"[API] Checking message: [Hebrew text - {len(request.message)} chars]")
        print(f"[API] Agent Orchestrator available: {zero.agent_orchestrator is not None}")
        
        # Check if we should use Agent Orchestrator for complex tasks
        use_orchestrator = False
        orchestrator_result = None
        
        if zero.agent_orchestrator and any(keyword in request.message.lower() for keyword in complex_task_keywords):
            try:
                # Use Agent Orchestrator for complex tasks
                print(f"[API] Using Agent Orchestrator for: {request.message}")
                use_orchestrator = True
                orchestrator_result = zero.agent_orchestrator.execute_goal(request.message, max_iterations=5)
                
                if orchestrator_result.success:
                    # Create a simplified response based on orchestrator result
                    action_result = f"✅ Task completed: {orchestrator_result.output}"
                else:
                    action_result = f"⚠️ Task completed with issues: {orchestrator_result.error}"
            except Exception as e:
                action_result = f"❌ Error in orchestrator: {str(e)}"
        
        # Check for simple action requests - expanded support (if not using orchestrator)
        action_keywords = [
            'צור תיקייה', 'create folder', 'עשה תיקייה', 'צר תיקיה', 'תיצור תיקייה',
            'פתח דפדפן', 'open browser', 'open chrome', 'פתח כרום',
            'צור קובץ', 'create file', 'עשה קובץ',
            'רשום הודעה', 'write message',
            'הרץ פקודה', 'run command'
        ]
        
        if not use_orchestrator and any(keyword in request.message.lower() for keyword in action_keywords):
            if zero.code_executor:
                try:
                    from pathlib import Path
                    import subprocess
                    import os
                    
                    # Create folder action
                    if any(kw in request.message.lower() for kw in ['צור תיקייה', 'create folder', 'עשה תיקייה']):
                        # Extract folder name
                        words = request.message.split()
                        folder_name = None
                        for i, word in enumerate(words):
                            if 'תיקייה' in word or 'folder' in word.lower():
                                folder_name = ' '.join(words[i+1:]) if i+1 < len(words) else 'new_folder'
                                break
                        
                        # Support for C: drive
                        if 'c:' in request.message.lower() or 'כונן c' in request.message.lower():
                            folder_name = 'new_folder' if not folder_name else folder_name
                            new_dir = Path("C:/") / folder_name
                        else:
                            folder_name = folder_name if folder_name else 'new_folder'
                            workspace = Path("workspace")
                            new_dir = workspace / folder_name
                        
                        new_dir.mkdir(parents=True, exist_ok=True)
                        action_result = f"✅ Created directory: {new_dir}"
                    
                    # Open browser action
                    elif any(kw in request.message.lower() for kw in ['פתח דפדפן', 'open browser', 'open chrome', 'פתח כרום']):
                        # Extract URL if provided
                        url = None
                        if 'http' in request.message.lower():
                            import re
                            urls = re.findall(r'https?://[^\s]+', request.message)
                            url = urls[0] if urls else None
                        
                        if url:
                            subprocess.Popen(['start', url], shell=True)
                            action_result = f"✅ Opened browser with URL: {url}"
                        else:
                            subprocess.Popen(['start', 'chrome'], shell=True)
                            action_result = "✅ Opened browser"
                    
                    # Create file action
                    elif any(kw in request.message.lower() for kw in ['צור קובץ', 'create file', 'עשה קובץ']):
                        # Extract filename
                        words = request.message.split()
                        filename = 'new_file.txt'
                        for i, word in enumerate(words):
                            if 'קובץ' in word or 'file' in word.lower():
                                filename = ' '.join(words[i+1:]) if i+1 < len(words) else 'new_file.txt'
                                break
                        
                        # Support for C: drive
                        if 'c:' in request.message.lower():
                            file_path = Path("C:/") / filename
                        else:
                            file_path = Path("workspace") / filename
                        
                        file_path.touch()
                        action_result = f"✅ Created file: {file_path}"
                    
                except Exception as e:
                    action_result = f"❌ Error: {str(e)}"
        
        # Build context from conversation history (Phase 2)
        context = ""
        if request.conversation_history:
            # Format last 10 messages for context
            context_msgs = []
            for msg in request.conversation_history[-10:]:  # Last 10 only
                role = "משתמש" if msg.get('role') == 'user' else "Zero"
                content = msg.get('content', '')
                context_msgs.append(f"{role}: {content}")
            context = "\n".join(context_msgs)
            print(f"[Context] Got {len(request.conversation_history)} messages in history")
            print(f"[Context] Context built: {len(context)} chars")
        else:
            print(f"[Context] No conversation_history provided")
        
        # Fallback to old memory system if no conversation history provided
        if not context and request.use_memory and zero.memory:
            context = zero.memory.build_context(
                current_task=request.message,
                max_length=2000
            )
            print(f"[Context] Using old memory system: {len(context)} chars")
        
        # Check for Memory Commands (Phase 3: Step 4.2)
        memory_command_keywords = [
            'מה אתה זוכר', 'מה אתה יודע עליי', 'מה למדת', 'מה יודע',
            'what do you remember', 'what do you know about me',
            'שכח', 'תשכח', 'forget',
            'רשום', 'זכור', 'תזכור', 'remember this', 'save this'
        ]
        
        is_memory_command = any(kw in request.message.lower() for kw in memory_command_keywords)
        
        if is_memory_command and zero.memory:
            # Handle memory commands directly
            if any(kw in request.message.lower() for kw in ['מה אתה זוכר', 'מה אתה יודע', 'מה למדת', 'what do you remember', 'what do you know']):
                # Show what Zero knows
                prefs = zero.memory.short_term.get_all_preferences()
                stats = zero.memory.short_term.get_statistics()
                
                response = "אני זוכר:\n\n"
                if prefs:
                    response += "העדפות שלך:\n"
                    for key, val in prefs.items():
                        response += f"  • {key}: {val}\n"
                    response += "\n"
                
                response += f"דיברנו ביחד {stats['conversations_24h']} פעמים היום\n"
                response += f"סה\"כ {stats['total_conversations']} שיחות בזיכרון\n"
                
                return ChatResponse(
                    response=response,
                    model_used="memory_command",
                    duration=time.time() - start_time
                )
        
        # Add RAG context for complex questions (Phase 3)
        rag_context = ""
        if zero.rag and request.use_memory:
            # Determine if question needs long-term memory
            complex_keywords = ['זוכר', 'אמרתי', 'דיברנו', 'לפני', 'אתמול', 'שבוע',
                              'remember', 'said', 'talked', 'before', 'yesterday', 'ago',
                              'מה אתה יודע', 'מה למדנו', 'what do you know']
            
            needs_rag = any(kw in request.message.lower() for kw in complex_keywords)
            
            if needs_rag:
                try:
                    rag_results = zero.rag.retrieve(request.message, n_results=3)
                    if rag_results:
                        rag_context = "\n\n## זיכרון ארוך טווח:\n"
                        for i, result in enumerate(rag_results[:2], 1):  # Top 2 only
                            doc = result.get('document', '')[:150]  # First 150 chars
                            rag_context += f"{i}. {doc}...\n"
                        print(f"[RAG] Added {len(rag_results)} results to context")
                except Exception as rag_err:
                    print(f"[RAG] Failed to retrieve: {rag_err}")
        
        # Always use enhanced system prompts for HIGH-QUALITY responses
        preferences = ""
        try:
            from enhanced_system_prompt import get_system_prompt
            
            # Check if user has specific preference
            if request.use_memory and zero.memory:
                try:
                    prefs = zero.memory.short_term.get_all_preferences()
                    response_mode = prefs.get('response_mode', 'detailed')
                    preferences = get_system_prompt(detailed=(response_mode == 'detailed'))
                except:
                    # Default to DETAILED mode for high-quality responses
                    preferences = get_system_prompt(detailed=True)
            else:
                # Default to DETAILED mode for high-quality responses
                preferences = get_system_prompt(detailed=True)
        except Exception as e:
            print(f"[API] Warning: Could not load enhanced_system_prompt: {e}")
            # Fallback to simple, clean prompt
            preferences = """You are Zero Agent - a helpful AI assistant powered by Mixtral 8x7B.

Be direct, accurate, and clear. Match the user's language. No unnecessary preambles."""
        
        # Build prompt with modular architecture (from llm-concise-guide.md)
        # Structure: Role + Constraints + Format + Task (for better instruction following)
        prompt = ""
        
        # 1. Role and constraints (from preferences) - at the start for clarity
        if preferences:
            prompt += f"{preferences}\n\n"
        
        # 2. Context (conversation history) - if exists
        if context and request.use_memory:
            prompt += f"## הקשר מהשיחה הקודמת:\n{context}\n\n"
        
        # 2.5 RAG long-term memory context (Phase 3)
        if rag_context:
            prompt += rag_context + "\n"
        
        # 3. Additional info (search results, actions)
        extra_info = ""
        if search_triggered and search_results:
            extra_info += f"\nמידע נוסף מהרשת:\n{search_results}\n"
            print(f"[Prompt] Adding search_results to prompt ({len(search_results)} chars)")
        if action_result:
            extra_info += f"\nפעולה שבוצעה: {action_result}\n"
        
        if extra_info:
            prompt += extra_info + "\n"
            print(f"[Prompt] Total extra_info added: {len(extra_info)} chars")
        
        # 4. User message - Mixtral requires [INST] tags!
        # Wrap everything in Mixtral's prompt template: <s>[INST] ... [/INST]
        user_message = request.message
        
        # Prepare the final prompt with Mixtral template
        instruction_content = prompt + f"\nשאלה: {user_message}\nתשובה:"
        prompt = f"<s>[INST] {instruction_content} [/INST]"
        
        # DEBUG: Print first and last 500 chars of prompt
        print(f"[Prompt Debug] First 500 chars:\n{prompt[:500]}\n")
        print(f"[Prompt Debug] Last 500 chars:\n{prompt[-500:]}\n")
        
        # Get routing decision
        if request.model:
            # Forced model
            model = request.model
            response = zero.llm.generate(prompt, model=model)
        else:
            # Auto-route
            routing = zero.router.route_with_reasoning(request.message)
            model = routing['model']
            
            # For DeepSeek-R1 (smart model), enhance with Chain-of-Thought
            if model == "smart":
                # Check if it's a complex reasoning task
                complex_keywords = ['למה', 'איך', 'בצע', 'פתור', 'תכנן', 'מיישם', 
                                    'why', 'how', 'solve', 'implement', 'plan',
                                    'analyz', 'explain', 'compare', 'evalu']
                
                is_complex = any(keyword in request.message.lower() for keyword in complex_keywords)
                
                if is_complex:
                    # Add CoT instruction to prompt for R1
                    cot_instruction = """

שים לב: אתה DeepSeek-R1 עם יכולות Chain-of-Thought משופרות.
לשאלות מורכבות - חשוב שלב אחר שלב אך ענה תמציתי:
1. זהה את הבעיה
2. הצג פתרון
3. תמצת למשפט אחד

חזור לתשובה תמציתית:"""
                    
                    # Insert CoT after preferences but before context
                    prompt = prompt.replace("---\n\nכל תשובה:", cot_instruction + "\n\n---\n\nכל תשובה:")
                
                # For R1, add stop sequences to remove thinking tokens
                response = zero.llm.generate(prompt, model=model)
                
                # Post-process to remove thinking tags if present
                if "<think>" in response or "</think>" in response:
                    import re
                    response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
                    
            else:
                response = zero.llm.generate(prompt, model=model)
        
        # Enforce Hebrew-only output when אפשרי
        response = enforce_hebrew_output(response, model)

        # Remember conversation (Phase 3)
        if zero.memory:
            zero.memory.remember(
                user_message=request.message,
                assistant_message=response,
                model_used=model
            )
        
        # Store in RAG for long-term memory (Phase 3)
        if zero.rag:
            try:
                zero.rag.store_conversation(
                    task=request.message,
                    response=response,
                    metadata={"model": model, "timestamp": time.time()}
                )
            except Exception as rag_err:
                print(f"[RAG] Failed to store: {rag_err}")
        
        duration = time.time() - start_time
        
        # Learn from this interaction (Phase 3: Learning System)
        if zero.learner:
            try:
                from datetime import datetime
                action = zero.UserAction(
                    timestamp=datetime.now(),
                    action_type="chat",
                    target="llm_response",
                    parameters={"model": model, "message_length": len(request.message)},
                    success=True,  # Assume success if we got here
                    context={"response_length": len(response)},
                    duration=duration
                )
                zero.learner.learn_from_action(action)
            except Exception as learn_err:
                print(f"[LEARN] Failed to learn: {learn_err}")
        
        return ChatResponse(
            response=response,
            model_used=model,
            duration=duration
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Tool Endpoints
# ============================================================================

@app.post("/api/tools/email", response_model=ToolResponse)
async def email_tool(request: EmailRequest):
    """
    Email operations via Gmail
    
    Actions:
        - search: Search emails
        - recent: Get recent emails
        - send: Send email
    """
    if not GMAIL_AVAILABLE:
        raise HTTPException(status_code=501, detail="Gmail not available")
    
    try:
        if request.action == "search":
            result = gmail_search(request.query, max_results=request.count)
        elif request.action == "recent":
            result = gmail_recent(count=request.count)
        elif request.action == "send":
            result = gmail_send(request.to, request.subject, request.body)
        else:
            raise ValueError(f"Unknown action: {request.action}")
        
        return ToolResponse(success=True, result=result)
        
    except Exception as e:
        return ToolResponse(success=False, result=None, error=str(e))


@app.post("/api/tools/calendar", response_model=ToolResponse)
async def calendar_tool(request: CalendarRequest):
    """
    Calendar operations via Google Calendar
    
    Actions:
        - today: Get today's events
        - week: Get this week's events
        - create: Create new event
    """
    if not CALENDAR_AVAILABLE:
        raise HTTPException(status_code=501, detail="Calendar not available")
    
    try:
        if request.action == "today":
            result = calendar_today()
        elif request.action == "week":
            result = calendar_week()
        elif request.action == "create":
            result = calendar_create(
                request.summary,
                request.start,
                request.end,
                request.description or ""
            )
        else:
            raise ValueError(f"Unknown action: {request.action}")
        
        return ToolResponse(success=True, result=result)
        
    except Exception as e:
        return ToolResponse(success=False, result=None, error=str(e))


@app.post("/api/tools/database", response_model=ToolResponse)
async def database_tool(request: DatabaseRequest):
    """
    Database operations
    
    Actions:
        - query: Execute SQL query
        - tables: List tables
        - schema: Show table schema
    """
    if not DATABASE_AVAILABLE:
        raise HTTPException(status_code=501, detail="Database not available")
    
    try:
        if request.action == "query":
            result = db_query(request.query, request.db_path)
        elif request.action == "tables":
            result = db_tables(request.db_path)
        elif request.action == "schema":
            result = db_schema(request.table_name, request.db_path)
        else:
            raise ValueError(f"Unknown action: {request.action}")
        
        return ToolResponse(success=True, result=result)
        
    except Exception as e:
        return ToolResponse(success=False, result=None, error=str(e))


# ============================================================================
# Memory Endpoints
# ============================================================================

@app.get("/api/memory/stats")
async def memory_stats():
    """Get memory statistics"""
    if not zero.memory:
        raise HTTPException(status_code=501, detail="Memory not available")
    
    try:
        stats = zero.memory.get_memory_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory/context")
async def memory_context(query: str):
    """Get context for a query"""
    if not zero.memory:
        raise HTTPException(status_code=501, detail="Memory not available")
    
    try:
        context = zero.memory.build_context(query, max_length=2000)
        return {"success": True, "context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/clear")
async def memory_clear(days: int = 30):
    """Clear old memories"""
    if not zero.memory:
        raise HTTPException(status_code=501, detail="Memory not available")
    
    try:
        zero.memory.clear_old_memories(days=days)
        return {"success": True, "message": f"Cleared memories older than {days} days"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Project Review Endpoint
# ============================================================================

@app.post("/api/tools/project-review")
async def project_review(request: ProjectReviewRequest):
    """
    Professional project review and analysis
    
    Performs:
    - Code quality analysis
    - Architecture review
    - Security assessment
    - Best practices check
    - Performance recommendations
    """
    from pathlib import Path
    import os
    
    try:
        project_path = Path(request.project_path)
        
        if not project_path.exists():
            return {
                "success": False,
                "error": f"Project path does not exist: {project_path}"
            }
        
        # Gather project information
        project_files = []
        file_sizes = {}
        
        for root, dirs, files in os.walk(project_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv']]
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                file_path = Path(root) / file
                rel_path = file_path.relative_to(project_path)
                
                try:
                    size = file_path.stat().st_size
                    file_sizes[str(rel_path)] = size
                    project_files.append(str(rel_path))
                except:
                    pass
        
        # Get project stats
        total_files = len(project_files)
        total_size = sum(file_sizes.values())
        
        # Analyze by file type
        file_types = {}
        for file in project_files:
            ext = Path(file).suffix.lower()
            if ext in file_types:
                file_types[ext] += 1
            else:
                file_types[ext] = 1
        
        # Prepare analysis prompt for Zero
        analysis_prompt = f"""
נתח את הפרויקט הבא וספק חוות דעת מקצועית:

**מידע על הפרויקט:**
- נתיב: {project_path}
- מספר קבצים: {total_files}
- גודל כולל: {total_size / 1024 / 1024:.2f} MB
- סוגי קבצים: {file_types}

**קבצים עיקריים:**
{chr(10).join(project_files[:50])}

{'...ועוד קבצים' if len(project_files) > 50 else ''}

אנא ספק:
1. **ארכיטקטורה**: הערכת המבנה והארגון
2. **איכות קוד**: Best practices ו-coding standards
3. **אבטחה**: נקודות תורפה פוטנציאליות
4. **ביצועים**: אופטימיזציות אפשריות
5. **חזקות**: מה הפרויקט עושה טוב
6. **שיפורים**: המלצות לקידום

התייחס ספציפית לטכנולוגיות שזיהית בפרויקט.
"""
        
        # Use Zero to analyze
        if zero.initialized:
            analysis = zero.llm.generate(analysis_prompt, model="smart")
        else:
            analysis = "Zero Agent not initialized. Cannot perform analysis."
        
        return {
            "success": True,
            "project_path": str(project_path),
            "result": {
                "project_path": str(project_path),
                "stats": {
                    "total_files": total_files,
                    "total_size_mb": round(total_size / 1024 / 1024, 2),
                    "file_types": file_types,
                    "sample_files": project_files[:20]
                },
                "review": analysis,
                "review_type": request.review_type
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Execute Actions Endpoint
# ============================================================================

@app.post("/api/tools/execute", response_model=ToolResponse)
async def execute_action(request: ExecuteCodeRequest):
    """
    Execute actions like creating directories, running commands, etc.
    
    Actions:
    - filesystem: Create dir, list files, etc.
    - python: Execute Python code
    - bash: Run shell commands
    """
    if not CODE_EXECUTOR_AVAILABLE or zero.code_executor is None:
        raise HTTPException(status_code=501, detail="Code executor not available")
    
    try:
        action = request.action.lower()
        command = request.command
        args = request.args or {}
        
        if action == "filesystem":
            # Handle filesystem operations
            if command.startswith("mkdir "):
                from pathlib import Path
                dir_name = command.replace("mkdir ", "").strip()
                workspace = Path("workspace")
                new_dir = workspace / dir_name
                new_dir.mkdir(parents=True, exist_ok=True)
                return ToolResponse(
                    success=True,
                    result=f"Created directory: {new_dir}"
                )
            
            elif command.startswith("ls") or command.startswith("list"):
                from pathlib import Path
                workspace = Path("workspace")
                files = list(workspace.iterdir())
                return ToolResponse(
                    success=True,
                    result={"files": [str(f.name) for f in files]}
                )
            
            else:
                return ToolResponse(
                    success=False,
                    error=f"Unknown filesystem command: {command}"
                )
        
        elif action == "python":
            result = zero.code_executor.execute_python_simple(command)
            return ToolResponse(success=True, result=result)
        
        elif action == "bash":
            result = zero.code_executor.execute_bash(command, safe_mode=True)
            return ToolResponse(success=result["success"], result=result)
        
        else:
            return ToolResponse(
                success=False,
                error=f"Unknown action: {action}"
            )
        
    except Exception as e:
        return ToolResponse(
            success=False,
            error=str(e)
        )


# ============================================================================
# Voice Transcription Endpoint
# ============================================================================

@app.post("/api/voice/transcribe", response_model=VoiceTranscribeResponse)
async def transcribe_voice(request: VoiceTranscribeRequest):
    """
    Transcribe audio to text using faster-whisper
    
    Supports:
    - Hebrew (default)
    - English and many other languages
    """
    if not WHISPER_AVAILABLE:
        raise HTTPException(status_code=501, detail="Whisper not available - install faster-whisper")
    
    try:
        import time
        import base64
        from pathlib import Path
        from faster_whisper import WhisperModel
        
        # Load Whisper model (small, fast, good quality)
        model = WhisperModel("small", device="cpu", compute_type="int8")
        
        # Handle audio input
        if request.audio_base64:
            # Decode base64 audio
            audio_data = base64.b64decode(request.audio_base64)
            # Save to temp file
            temp_file = Path("workspace/temp_audio.wav")
            temp_file.write_bytes(audio_data)
            audio_path = str(temp_file)
        elif request.audio_url:
            # Download from URL
            import requests
            response = requests.get(request.audio_url)
            temp_file = Path("workspace/temp_audio_from_url.wav")
            temp_file.write_bytes(response.content)
            audio_path = str(temp_file)
        else:
            raise HTTPException(status_code=400, detail="No audio provided")
        
        # Transcribe
        start_time = time.time()
        segments, info = model.transcribe(
            audio_path,
            language=request.language,
            beam_size=5,
            vad_filter=True,  # Voice Activity Detection
        )
        
        # Combine all segments
        text = " ".join([segment.text for segment in segments])
        duration = time.time() - start_time
        
        # Cleanup
        if temp_file.exists():
            temp_file.unlink()
        
        return VoiceTranscribeResponse(
            text=text,
            language=info.language,
            duration=duration
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


# ============================================================================
# Computer Control Agent Endpoints
# ============================================================================

# Import Computer Control Agent
try:
    from zero_agent.tools.computer_control_agent import ComputerControlAgent
    COMPUTER_CONTROL_AVAILABLE = True
except:
    COMPUTER_CONTROL_AVAILABLE = False
    print("[API] WARNING: Computer Control Agent not available")

# Initialize Computer Control Agent
computer_control_agent = None

def initialize_computer_control():
    """Initialize Computer Control Agent"""
    global computer_control_agent
    if COMPUTER_CONTROL_AVAILABLE and not computer_control_agent:
        try:
            computer_control_agent = ComputerControlAgent(
                llm=zero.llm,
                orchestrator=zero.agent_orchestrator
            )
            
            # Add computer control to orchestrator tools
            if zero.agent_orchestrator:
                zero.agent_orchestrator.tools['computer_control'] = computer_control_wrapper
                zero.agent_orchestrator.tools['open_browser'] = computer_control_wrapper
                zero.agent_orchestrator.tools['open_app'] = computer_control_wrapper
                zero.agent_orchestrator.tools['click'] = computer_control_wrapper
                print(f"[API] Computer Control tools added: {list(zero.agent_orchestrator.tools.keys())}")
            
            print("[API] OK Computer Control Agent ready")
        except Exception as e:
            print(f"[API] WARNING Computer Control Agent failed: {e}")
            computer_control_agent = None

def computer_control_wrapper(command: str, **kwargs) -> Dict[str, Any]:
    """Wrapper for Computer Control Agent to be used as a tool"""
    if not computer_control_agent:
        return {"success": False, "error": "Computer Control not initialized"}
    
    try:
        result = computer_control_agent.process_command(command, kwargs)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

# Pydantic models for Computer Control
class ComputerControlRequest(BaseModel):
    command: str
    context: Optional[Dict[str, Any]] = None

class ComputerControlResponse(BaseModel):
    success: bool
    action: str
    target: Optional[str] = None
    result: str
    error: Optional[str] = None
    confidence: Optional[float] = 0.0
    reasoning: Optional[str] = ""

class ProactiveSuggestionRequest(BaseModel):
    context: Optional[Dict[str, Any]] = None

class ProactiveSuggestionResponse(BaseModel):
    suggestions: List[Dict[str, Any]]
    count: int

class ScreenAnalysisRequest(BaseModel):
    screenshot_path: Optional[str] = None

class ScreenAnalysisResponse(BaseModel):
    success: bool
    analysis: Dict[str, Any]
    error: Optional[str] = None

class ElementFindRequest(BaseModel):
    description: str
    screenshot_path: Optional[str] = None

class ElementFindResponse(BaseModel):
    success: bool
    element: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class LearningStatsResponse(BaseModel):
    success: bool
    stats: Dict[str, Any]
    error: Optional[str] = None

@app.post("/api/computer-control/command", response_model=ComputerControlResponse)
async def computer_control_command(request: ComputerControlRequest):
    """
    Execute computer control command
    
    Examples:
        - "לחץ על הכפתור הכחול"
        - "click on the red button"
        - "הקלד 'שלום עולם'"
        - "type 'hello world'"
        - "צלם מסך"
        - "take screenshot"
    """
    if not COMPUTER_CONTROL_AVAILABLE:
        raise HTTPException(status_code=501, detail="Computer Control Agent not available")
    
    if not computer_control_agent:
        initialize_computer_control()
        if not computer_control_agent:
            raise HTTPException(status_code=503, detail="Computer Control Agent not initialized")
    
    try:
        result = computer_control_agent.process_command(
            request.command, 
            request.context
        )
        
        return ComputerControlResponse(
            success=result.get("success", False),
            action=result.get("action", "unknown"),
            target=result.get("target", ""),
            result=result.get("result", ""),
            error=result.get("error"),
            confidence=result.get("confidence", 0.0),
            reasoning=result.get("reasoning", "")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/computer-control/suggestions", response_model=ProactiveSuggestionResponse)
async def get_proactive_suggestions(request: ProactiveSuggestionRequest):
    """
    Get proactive action suggestions based on current context
    """
    if not COMPUTER_CONTROL_AVAILABLE:
        raise HTTPException(status_code=501, detail="Computer Control Agent not available")
    
    if not computer_control_agent:
        initialize_computer_control()
        if not computer_control_agent:
            raise HTTPException(status_code=503, detail="Computer Control Agent not initialized")
    
    try:
        suggestions = computer_control_agent.get_proactive_suggestions(
            request.context
        )
        
        return ProactiveSuggestionResponse(
            suggestions=suggestions,
            count=len(suggestions)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/computer-control/analyze-screen", response_model=ScreenAnalysisResponse)
async def analyze_screen(request: ScreenAnalysisRequest):
    """
    Analyze current screen using computer vision
    """
    if not COMPUTER_CONTROL_AVAILABLE:
        raise HTTPException(status_code=501, detail="Computer Control Agent not available")
    
    if not computer_control_agent:
        initialize_computer_control()
        if not computer_control_agent:
            raise HTTPException(status_code=503, detail="Computer Control Agent not initialized")
    
    try:
        analysis = computer_control_agent.analyze_screen(
            request.screenshot_path
        )
        
        return ScreenAnalysisResponse(
            success=analysis.get("success", False),
            analysis=analysis,
            error=analysis.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/computer-control/find-element", response_model=ElementFindResponse)
async def find_element(request: ElementFindRequest):
    """
    Find UI element by description using computer vision
    """
    if not COMPUTER_CONTROL_AVAILABLE:
        raise HTTPException(status_code=501, detail="Computer Control Agent not available")
    
    if not computer_control_agent:
        initialize_computer_control()
        if not computer_control_agent:
            raise HTTPException(status_code=503, detail="Computer Control Agent not initialized")
    
    try:
        result = computer_control_agent.find_element(
            request.description,
            request.screenshot_path
        )
        
        return ElementFindResponse(
            success=result.get("success", False),
            element=result.get("element"),
            error=result.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/computer-control/learning-stats", response_model=LearningStatsResponse)
async def get_learning_stats():
    """
    Get learning statistics from behavior learning system
    """
    if not COMPUTER_CONTROL_AVAILABLE:
        raise HTTPException(status_code=501, detail="Computer Control Agent not available")
    
    if not computer_control_agent:
        initialize_computer_control()
        if not computer_control_agent:
            raise HTTPException(status_code=503, detail="Computer Control Agent not initialized")
    
    try:
        stats = computer_control_agent.get_learning_stats()
        
        return LearningStatsResponse(
            success=True,
            stats=stats
        )
        
    except Exception as e:
        return LearningStatsResponse(
            success=False,
            stats={},
            error=str(e)
        )


# ============================================================================
# Streaming Chat Endpoint (Phase 1 - Latency Improvement)
# ============================================================================

@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    """
    Streaming chat endpoint - returns response word by word in real-time
    
    Real-time streaming response
    """
    import json
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Parse request
        data = await request.json()
        message = data.get("message", "").strip()
        conversation_history = data.get("conversation_history", [])
        
        # DEBUG: Log the incoming request
        logger.info(f"[DEBUG] Received request data: {data}")
        logger.info(f"[DEBUG] Message: '{message}'")
        logger.info(f"[DEBUG] Conversation history type: {type(conversation_history)}")
        logger.info(f"[DEBUG] Conversation history value: {conversation_history}")
        
        if not message:
            async def error_gen():
                yield f"data: {json.dumps({'error': 'No message provided'})}\n\n"
            return StreamingResponse(error_gen(), media_type="text/event-stream")
        
        # Log context
        logger.info(f"[CONTEXT] History length: {len(conversation_history)} messages")
        
        # Define computer control keywords
        computer_control_keywords = [
            # Open commands
            'פתח ', 'תפתח ', 'הפעל ', 'תפעיל ', 'הרץ ', 'תריץ ',
            'open ', 'launch ', 'start ', 'run ',
            # Click commands
            'לחץ ', 'תלחץ ', 'קליק ', 'click ',
            # Type commands
            'הקלד ', 'תקליד ', 'type ',
            # Other
            'צלם מסך', 'screenshot', 'סגור', 'close'
        ]
        
        # Check if it's a computer control command (these don't stream)
        if any(kw in message.lower() for kw in computer_control_keywords):
            logger.info(f"[STREAM] Computer Control command detected: {message}")
            
            async def computer_control_gen():
                result = computer_control_agent.execute_from_text(message)
                response_text = result.get('result', 'פעולה בוצעה')
                yield f"data: {json.dumps({'chunk': response_text, 'full': response_text, 'done': True})}\n\n"
            
            return StreamingResponse(computer_control_gen(), media_type="text/event-stream")
        
        # Regular LLM streaming
        logger.info(f"[STREAM] Starting streaming response for: {message[:50]}...")
        
        async def generate():
            try:
                full_response = ""
                chunk_count = 0
                
                # Get streaming LLM
                llm = zero.llm if hasattr(zero, 'llm') else StreamingMultiModelLLM()
                
                # Build prompt with context (Phase 2: Context-Aware!)
                # Use enhanced system prompt for better responses
                try:
                    from enhanced_system_prompt import get_system_prompt
                    prompt_parts = [get_system_prompt(detailed=True)]
                except Exception as e:
                    print(f"[API] Warning: Could not load enhanced_system_prompt: {e}")
                    prompt_parts = ["You are Zero Agent - a helpful AI assistant powered by Mixtral 8x7B. Be direct, accurate, and clear. Match the user's language."]
                
                # Add conversation history if available
                if conversation_history:
                    prompt_parts.append("\nהקשר השיחה:")
                    for msg in conversation_history[-6:]:  # Last 3 turns
                        role = "ש" if msg.get("role") == "user" else "ת"
                        content = msg.get("content", "")
                        prompt_parts.append(f"{role}: {content}")
                
                # Language matching is handled by the system prompt
                
                # Add current question
                prompt_parts.append(f"ש: {message}")
                prompt_parts.append("ת: ")
                
                prompt = "\n".join(prompt_parts)
                
                # Stream chunks
                for chunk in llm.stream_generate(prompt):
                    full_response += chunk
                    chunk_count += 1
                    
                    yield f"data: {json.dumps({'chunk': chunk, 'full': full_response, 'done': False})}\n\n"
                    
                    # Small delay to avoid overwhelming the client
                    await asyncio.sleep(0.01)
                
                # Send final done signal
                yield f"data: {json.dumps({'chunk': '', 'full': full_response, 'done': True})}\n\n"
                
                logger.info(f"[STREAM] Completed: {chunk_count} chunks sent")
                
                # Save to memory (Phase 3: Memory System)
                if zero.memory and full_response:
                    try:
                        zero.memory.remember(
                            user_message=message,
                            assistant_message=full_response,
                            model_used="fast"  # Streaming typically uses fast model
                        )
                        logger.info(f"[STREAM] Saved to memory")
                    except Exception as mem_err:
                        logger.warning(f"[STREAM] Failed to save to memory: {mem_err}")
                
                # Save to RAG for long-term memory (Phase 3)
                if zero.rag and full_response:
                    try:
                        import time as time_module
                        zero.rag.store_conversation(
                            task=message,
                            response=full_response,
                            metadata={"model": "fast", "timestamp": time_module.time()}
                        )
                        logger.info(f"[STREAM] Saved to RAG")
                    except Exception as rag_err:
                        logger.warning(f"[STREAM] Failed to save to RAG: {rag_err}")
                
            except Exception as e:
                logger.error(f"[STREAM] Error during generation: {e}")
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
        
    except Exception as e:
        logger.error(f"[STREAM] Request error: {e}")
        error_msg = str(e)  # Capture error message in outer scope
        async def error_gen():
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream")


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Fix encoding for Windows
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    print("="*70)
    print("Zero Agent API Server")
    print("="*70)
    print("\nStarting server...")
    print("API Docs: http://localhost:8080/docs")
    print("Health: http://localhost:8080/health")
    print("="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
