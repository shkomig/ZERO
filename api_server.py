"""
Zero Agent API Server
=====================
FastAPI server with REST endpoints and WebSocket streaming

Endpoints:
    POST /api/chat          - Chat with Zero
    POST /api/tools/email   - Email operations
    POST /api/tools/calendar - Calendar operations
    POST /api/tools/database - Database queries
    GET  /api/memory/stats  - Memory statistics
    WS   /ws/chat          - WebSocket streaming

Install:
    pip install fastapi uvicorn websockets
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
from pathlib import Path
import sys

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

# Import memory
try:
    from memory.memory_manager import MemoryManager
    MEMORY_AVAILABLE = True
except:
    MEMORY_AVAILABLE = False


# ============================================================================
# Pydantic Models
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None  # fast, smart, coder, balanced
    use_memory: bool = True
    stream: bool = False


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


class ToolResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Zero Agent API",
    description="AI Agent with Memory, Tools, and Multi-Model Support",
    version="1.0.0"
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
        self.initialized = False
    
    def initialize(self):
        """Initialize Zero Agent components"""
        if self.initialized:
            return
        
        print("\n[API] Initializing Zero Agent...")
        
        # Initialize LLM
        self.llm = StreamingMultiModelLLM(default_model="fast")
        if not self.llm.test_connection(verbose=False):
            raise ConnectionError("Cannot connect to Ollama!")
        print("[API] ✓ LLM connected")
        
        # Initialize Router
        self.router = ContextAwareRouter(self.llm)
        print("[API] ✓ Router ready")
        
        # Initialize Executor
        self.executor = MultiModelExecutor(self.llm, self.router)
        print("[API] ✓ Executor ready")
        
        # Initialize Memory
        if MEMORY_AVAILABLE:
            try:
                self.memory = MemoryManager(
                    memory_dir=Path("workspace/memory"),
                    rag_url="http://localhost:8000",
                    enable_rag=True
                )
                print("[API] ✓ Memory ready")
            except Exception as e:
                print(f"[API] ⚠️  Memory unavailable: {e}")
                self.memory = None
        
        self.initialized = True
        print("[API] ✅ Zero Agent ready!\n")


# Global agent instance
zero = ZeroAgent()


# ============================================================================
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize Zero Agent on startup"""
    try:
        zero.initialize()
    except Exception as e:
        print(f"[API] ❌ Initialization failed: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n[API] Shutting down...")


# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
async def root():
    """Health check and API info"""
    return {
        "status": "online",
        "agent": "Zero Agent",
        "version": "1.0.0",
        "features": {
            "llm": zero.initialized,
            "memory": MEMORY_AVAILABLE and zero.memory is not None,
            "gmail": GMAIL_AVAILABLE,
            "calendar": CALENDAR_AVAILABLE,
            "database": DATABASE_AVAILABLE
        },
        "endpoints": {
            "chat": "/api/chat",
            "email": "/api/tools/email",
            "calendar": "/api/tools/calendar",
            "database": "/api/tools/database",
            "memory": "/api/memory/stats",
            "websocket": "/ws/chat"
        }
    }


@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "initialized": zero.initialized}


# ============================================================================
# Chat Endpoints
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with Zero Agent
    
    Example:
        POST /api/chat
        {
            "message": "What's the weather?",
            "model": "fast",
            "use_memory": true
        }
    """
    if not zero.initialized:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        import time
        start_time = time.time()
        
        # Build context from memory
        context = ""
        if request.use_memory and zero.memory:
            context = zero.memory.build_context(
                current_task=request.message,
                max_length=2000
            )
        
        # Prepare prompt
        prompt = f"{context}\n{request.message}" if context else request.message
        
        # Get routing decision
        if request.model:
            # Forced model
            model = request.model
            response = zero.llm.generate(prompt, model=model)
        else:
            # Auto-route
            routing = zero.router.route_with_reasoning(request.message)
            model = routing['model']
            response = zero.llm.generate(prompt, model=model)
        
        # Remember conversation
        if zero.memory:
            zero.memory.remember(
                user_message=request.message,
                assistant_message=response,
                model_used=model
            )
        
        duration = time.time() - start_time
        
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
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("="*70)
    print("🚀 Zero Agent API Server")
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
