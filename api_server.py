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
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
        self.code_executor = None
        self.initialized = False
    
    def initialize(self):
        """Initialize Zero Agent components"""
        if self.initialized:
            return
        
        print("\n[API] Initializing Zero Agent...")
        
        # Initialize LLM - use smart model for better instruction following
        self.llm = StreamingMultiModelLLM(default_model="smart")
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
                    enable_rag=True
                )
                print("[API] OK Memory ready")
            except Exception as e:
                print(f"[API] WARNING Memory unavailable: {e}")
                self.memory = None
        
        # Initialize Code Executor
        if CODE_EXECUTOR_AVAILABLE:
            try:
                self.code_executor = CodeExecutorTool(workspace=Path("workspace"))
                print("[API] OK Code executor ready")
            except Exception as e:
                print(f"[API] WARNING Code executor unavailable: {e}")
                self.code_executor = None
        
        self.initialized = True
        print("[API] SUCCESS Zero Agent ready!\n")


# Global agent instance
zero = ZeroAgent()

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

# Serve logo
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
# Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize Zero Agent on startup"""
    try:
        zero.initialize()
    except Exception as e:
        print(f"[API] ERROR Initialization failed: {e}")
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
            "project_review": "/api/tools/project-review",
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
        
        # Check if user wants to search the web
        search_triggered = False
        search_results = ""
        action_result = None
        
        if any(keyword in request.message.lower() for keyword in ['חפש ברשת', 'חפש', 'חיפוש', 'search', 'google', 'search for']):
            if WEBSEARCH_AVAILABLE:
                search_triggered = True
                # Extract search query (everything after "search for" or similar)
                search_query = request.message
                for trigger in ['חפש ברשת', 'חפש', 'חיפוש על', 'search for', 'google']:
                    if trigger in request.message.lower():
                        search_query = request.message.lower().split(trigger, 1)[1].strip()
                        break
                
                from tool_websearch import WebSearchTool
                search_tool = WebSearchTool()
                search_result = search_tool.search_simple(search_query)
                search_results = f"\n\nחיפוש עדכני ברשת:\n{search_result}\n"
        
        # Check for action requests
        if any(keyword in request.message.lower() for keyword in ['צור תיקייה', 'create folder', 'עשה תיקייה', 'צר תיקיה', 'תיצור תיקייה']):
            if zero.code_executor:
                try:
                    from pathlib import Path
                    # Extract folder name
                    words = request.message.split()
                    for i, word in enumerate(words):
                        if 'תיקייה' in word or 'folder' in word.lower():
                            folder_name = ' '.join(words[i+1:]) if i+1 < len(words) else 'new_folder'
                            break
                    else:
                        folder_name = 'new_folder'
                    
                    workspace = Path("workspace")
                    new_dir = workspace / folder_name
                    new_dir.mkdir(parents=True, exist_ok=True)
                    action_result = f"✅ Created directory: {new_dir}"
                except Exception as e:
                    action_result = f"❌ Error: {str(e)}"
        
        # Build context from memory
        context = ""
        preferences = ""
        if request.use_memory and zero.memory:
            context = zero.memory.build_context(
                current_task=request.message,
                max_length=2000
            )
            
            # Load user preferences and add to system message
            try:
                prefs = zero.memory.short_term.get_all_preferences()
                if prefs:
                    # Based on llm-concise-guide.md - Best Practices for Concise Responses
                    # Using: Few-Shot + Temperature Control + Max Tokens + Clear Structure
                    
                    preferences = """# אתה Zero - עוזר AI תמציתי בעברית

## כללים קריטיים - תמציתיות
- ענה במשפט אחד בלבד (מקסימום 2 משפטים)
- מקסימום 40 מילים - חסום את עצמך
- ללא הקדמות, ללא סיכומים
- ישיר לעניין - no fluff

## דוגמאות נכונות (תמציתיות)

ש: מה זה Python?
ת: שפת תכנות רב-תכליתית לפיתוח אפליקציות.

ש: מה זה Docker?
ת: כלי לניהול קונטיינרים של אפליקציות.

ש: צור תיקייה test
ת: ✅ נוצר test/

ש: מה זה machine learning?
ת: AI שמאפשר למחשבים ללמוד מנתונים ללא תכנות מפורש.

## דוגמה שגויה - אל תעשה כך
ש: מה זה Docker?
ת: Docker הוא פלטפורמה מתקדמת שפותחה בשנת 2013 על ידי חברת Docker Inc., והיא מאפשרת... [ארוך מדי! 150+ מילים]

---

כל תשובה: משפט אחד בלבד, ישיר, תמציתי."""
            except:
                pass
        
        # Build prompt with modular architecture (from llm-concise-guide.md)
        # Structure: Role + Constraints + Format + Task (for better instruction following)
        prompt = ""
        
        # 1. Role and constraints (from preferences) - at the start for clarity
        if preferences:
            prompt += f"{preferences}\n\n"
        
        # 2. Context (conversation history) - if exists
        if context and request.use_memory:
            prompt += f"## הקשר מהשיחה הקודמת:\n{context}\n\n"
        
        # 3. Additional info (search results, actions)
        extra_info = ""
        if search_triggered and search_results:
            extra_info += f"\nמידע נוסף מהרשת:\n{search_results}\n"
        if action_result:
            extra_info += f"\nפעולה שבוצעה: {action_result}\n"
        
        if extra_info:
            prompt += extra_info + "\n"
        
        # 4. User message - clear and direct
        prompt += f"ש: {request.message}\nת: "
        
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
