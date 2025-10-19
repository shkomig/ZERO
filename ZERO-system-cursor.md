# ZERO - AI-Powered Desktop Context & Automation System
## Comprehensive Development Guide for Cursor AI

---

## Project Overview

**Project Name:** ZERO  
**Type:** Desktop AI Context Engine with Automation Capabilities  
**Core Purpose:** Local-first screen recording, OCR processing, and intelligent automation using local AI models  
**Target Platform:** Windows/Linux/macOS  
**Primary Language:** Python 3.10+  
**AI Models:** DeepSeek-R1-32B, Llama 3.1-8B, Qwen 2.5-Coder-32B (via Ollama)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ZERO Application                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Capture    │  │  Processing  │  │  AI Engine   │  │
│  │    Layer     │  │    Layer     │  │    Layer     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                  │                  │          │
│         ▼                  ▼                  ▼          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Storage    │  │     API      │  │  Automation  │  │
│  │    Layer     │  │    Layer     │  │    Layer     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

**Core Framework:**
- Python 3.10+ (main language)
- FastAPI (REST API + WebSocket support)
- SQLite + SQLAlchemy (data persistence)
- Ollama (local AI model management)

**Screen Capture & Processing:**
- `mss` (ultra-fast screen capture, cross-platform)
- `pytesseract` (OCR with Hebrew + English support)
- `pillow` (image processing)
- `opencv-python` (advanced image preprocessing)

**Automation:**
- `pyautogui` (keyboard/mouse control)
- `playwright` (optional: DOM-based web automation)

**AI Integration:**
- `langchain` (AI orchestration)
- `ollama-python` (local model interface)
- `chromadb` (vector database for semantic search)

---

## Project Structure

```
zero/
├── .cursor/
│   └── rules/
│       ├── python-best-practices.mdc
│       ├── fastapi-patterns.mdc
│       └── ai-integration.mdc
├── src/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── config.py                  # Configuration management
│   ├── capture/
│   │   ├── __init__.py
│   │   ├── screen_recorder.py    # Screen capture engine
│   │   ├── audio_recorder.py     # Audio capture (future)
│   │   └── frame_buffer.py       # Buffer management
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── ocr_engine.py         # OCR processing (Tesseract)
│   │   ├── image_processor.py    # Image preprocessing
│   │   └── text_extractor.py     # Text extraction logic
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── model_manager.py      # Ollama model management
│   │   ├── context_builder.py    # Context window management
│   │   ├── query_engine.py       # AI query processing
│   │   └── embeddings.py         # Vector embeddings
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py           # SQLite ORM models
│   │   ├── vector_store.py       # ChromaDB integration
│   │   └── file_manager.py       # File system operations
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py             # FastAPI routes
│   │   ├── websocket.py          # WebSocket handlers
│   │   └── schemas.py            # Pydantic models
│   ├── automation/
│   │   ├── __init__.py
│   │   ├── desktop_controller.py # PyAutoGUI wrapper
│   │   └── playwright_preset.py  # Playwright integration (optional)
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # Logging configuration
│       └── helpers.py            # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_capture.py
│   ├── test_ocr.py
│   └── test_api.py
├── data/
│   ├── screenshots/              # Captured frames
│   ├── database/                 # SQLite DB
│   └── vectors/                  # ChromaDB storage
├── requirements.txt
├── pyproject.toml
├── README.md
└── .env.example
```

---

## Core Components Implementation

### 1. Screen Capture Engine (`src/capture/screen_recorder.py`)

**Purpose:** Continuously capture screen at configurable intervals using `mss` for maximum performance.

**Key Features:**
- Multi-monitor support
- Configurable FPS (default: 0.5-1 frame/sec)
- Asynchronous processing pipeline
- Frame deduplication (skip identical frames)

**Implementation Requirements:**
```python
# Requirements:
# - Use mss for screen capture (10x faster than PIL)
# - Implement frame buffer with max size (e.g., 100 frames)
# - Add frame comparison to skip duplicates (using perceptual hash)
# - Support pausing/resuming capture
# - Thread-safe operations
```

**Reference Architecture:**
```python
class ScreenRecorder:
    def __init__(self, fps: float = 0.5, monitors: List[int] = None):
        self.fps = fps
        self.monitors = monitors or [1]  # Default to primary monitor
        self.running = False
        self.frame_buffer = FrameBuffer(max_size=100)
        
    async def start_recording(self):
        # Capture loop with mss
        # Send frames to processing queue
        pass
        
    async def stop_recording(self):
        # Cleanup and flush buffer
        pass
```

### 2. OCR Engine (`src/processing/ocr_engine.py`)

**Purpose:** Extract text from captured frames with Hebrew + English support.

**Key Features:**
- Multi-language OCR (Hebrew + English)
- Image preprocessing for better accuracy
- Caching results to avoid re-processing
- Error handling for low-quality images

**Implementation Requirements:**
```python
# Requirements:
# - Use Tesseract with 'heb+eng' language pack
# - Preprocess images: grayscale, contrast enhancement, noise reduction
# - Implement confidence scoring (reject low-quality results)
# - Cache OCR results by frame hash
# - Handle right-to-left (RTL) text properly
```

**Tesseract Configuration:**
```python
# Install Hebrew language pack:
# sudo apt-get install tesseract-ocr-heb (Linux)
# brew install tesseract-lang (macOS)

# Configuration for better accuracy:
custom_config = r'--oem 3 --psm 6 -l heb+eng'
```

### 3. AI Model Manager (`src/ai/model_manager.py`)

**Purpose:** Interface with local Ollama models for intelligent context understanding.

**Key Features:**
- Model switching (DeepSeek-R1-32B, Llama 3.1-8B, Qwen 2.5-Coder-32B)
- Context window management (128K tokens for DeepSeek-R1)
- Streaming responses
- Error handling and fallbacks

**Implementation Requirements:**
```python
# Requirements:
# - Use ollama-python library
# - Implement model health checks
# - Support streaming for long responses
# - Handle context window overflow (truncate oldest data)
# - Log model performance metrics (latency, tokens/sec)
```

**Model Selection Strategy:**
- **DeepSeek-R1-32B:** Complex reasoning, trading analysis
- **Llama 3.1-8B:** Fast general queries, UI interactions
- **Qwen 2.5-Coder-32B:** Code analysis, development tasks

### 4. Playwright Preset (Optional) (`src/automation/playwright_preset.py`)

**Purpose:** DOM-based automation for stable interactions with web apps (Gmail, news sites).

**Key Features:**
- Browser context management
- Element waiting strategies
- Error recovery
- Fallback to OCR when DOM unavailable

**Why Playwright over OCR?**
- **Reliability:** DOM selectors are deterministic vs OCR accuracy issues
- **Speed:** Direct DOM access is faster than image processing
- **Maintainability:** Selectors update with site changes, OCR requires retraining
- **Data Quality:** Extract structured data (JSON) vs unstructured text

**Use Cases:**
- Gmail: Read emails, send messages, filter inbox
- News sites: Extract articles, headlines, metadata
- Web forms: Fill forms, submit data
- SPAs: Handle dynamic content loading

**Implementation Requirements:**
```python
# Requirements:
# - Use Playwright with persistent browser context
# - Implement retry logic with exponential backoff
# - Add screenshot capture on failure (for debugging)
# - Graceful degradation to OCR if DOM not accessible
# - Support headless and headful modes
```

**Playwright vs OCR Decision Tree:**
```
Is target a web application?
├─ Yes: Can we access DOM reliably?
│  ├─ Yes: Use Playwright (preferred)
│  └─ No: Use OCR fallback
└─ No (Desktop app): Use OCR
```

### 5. Database Schema (`src/storage/database.py`)

**SQLite Schema:**
```sql
-- Captured frames metadata
CREATE TABLE frames (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    monitor_id INTEGER,
    frame_hash TEXT UNIQUE,
    image_path TEXT,
    processed BOOLEAN DEFAULT FALSE
);

-- Extracted text content
CREATE TABLE content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    frame_id INTEGER,
    text TEXT,
    language TEXT,
    confidence REAL,
    ocr_engine TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (frame_id) REFERENCES frames(id)
);

-- AI interactions
CREATE TABLE queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT,
    model TEXT,
    response TEXT,
    context_frames TEXT,  -- JSON array of frame IDs
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Automation tasks
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT,  -- 'playwright' or 'pyautogui'
    target TEXT,
    action TEXT,
    status TEXT,
    result TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 6. FastAPI Application (`src/api/routes.py`)

**API Endpoints:**
```python
# Core API routes:
POST   /api/start            # Start recording
POST   /api/stop             # Stop recording
GET    /api/status           # System status
POST   /api/search           # Search content
POST   /api/query            # AI query with context
GET    /api/frames           # List captured frames
GET    /api/frames/{id}      # Get specific frame
POST   /api/automate         # Execute automation task
WS     /ws/live              # Live frame stream
```

---

## Development Phases

### Phase 1: Core MVP (2-3 weeks)
**Goal:** Basic screen capture + OCR + search

**Tasks:**
1. Set up project structure
2. Implement screen capture with `mss`
3. Integrate Tesseract OCR (Hebrew + English)
4. Create SQLite database
5. Build FastAPI endpoints
6. Add basic search functionality

**Acceptance Criteria:**
- Capture 1 frame per second
- Extract text with >85% accuracy
- Search indexed text
- API returns results in <500ms

### Phase 2: AI Integration (2-3 weeks)
**Goal:** Connect local Ollama models

**Tasks:**
1. Integrate Ollama SDK
2. Build context window manager
3. Implement query engine
4. Add vector embeddings (ChromaDB)
5. Create semantic search

**Acceptance Criteria:**
- Query context from past 24 hours
- Response time <3 seconds
- Support all 3 models
- Handle 128K token context

### Phase 3: Automation Layer (2-3 weeks)
**Goal:** Add Playwright + PyAutoGUI

**Tasks:**
1. Implement PyAutoGUI controller
2. Add Playwright preset
3. Build task scheduler
4. Create automation API
5. Add error handling

**Acceptance Criteria:**
- Execute Gmail automation
- Fallback to OCR when needed
- Task success rate >90%
- Detailed error reporting

### Phase 4: Polish & Optimization (1-2 weeks)
**Goal:** Performance, UI, documentation

**Tasks:**
1. Optimize frame processing
2. Add web UI (optional)
3. Write documentation
4. Create demo videos
5. Package for distribution

---

## Performance Targets

**Capture:**
- Frame rate: 0.5-1 FPS (configurable)
- CPU usage: <10%
- RAM usage: <2GB
- Storage: ~500MB/hour (compressed)

**OCR:**
- Processing time: <200ms per frame
- Accuracy: >90% (clean text), >80% (complex layouts)
- Language detection: 99%

**AI Queries:**
- Response time: <3 seconds
- Context retrieval: <500ms
- Model switching: <1 second

**Automation:**
- Task execution: <5 seconds
- Error recovery: <2 seconds
- Playwright vs OCR: 5x faster with Playwright

---

## Configuration (`src/config.py`)

**Environment Variables (.env):**
```bash
# Recording settings
RECORDING_FPS=0.5
RECORDING_MONITORS=1,2
FRAME_BUFFER_SIZE=100

# OCR settings
OCR_LANGUAGES=heb+eng
OCR_CONFIDENCE_THRESHOLD=0.8
OCR_ENGINE=tesseract

# AI settings
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=deepseek-r1:32b
CONTEXT_WINDOW_SIZE=128000

# Playwright settings (optional)
PLAYWRIGHT_ENABLED=true
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000

# Storage
DATABASE_PATH=data/database/zero.db
SCREENSHOTS_PATH=data/screenshots
VECTORS_PATH=data/vectors

# API
API_HOST=0.0.0.0
API_PORT=8000
ENABLE_CORS=true
```

---

## Cursor AI Rules

### Python Best Practices (`.cursor/rules/python-best-practices.mdc`)

```markdown
---
description: Python coding standards for ZERO project
globs: src/**/*.py
---

# Python Best Practices

## Code Style
- Follow PEP 8 conventions
- Use type hints for all function signatures
- Maximum line length: 100 characters
- Use docstrings (Google style) for all public functions

## Async/Await
- Prefer async/await for I/O operations
- Use asyncio.gather() for parallel tasks
- Never block event loop with sync code

## Error Handling
- Use specific exception types
- Always log errors with context
- Implement retry logic for network calls
- Graceful degradation on failures

## Testing
- Write unit tests for all core functions
- Use pytest fixtures for setup
- Mock external dependencies
- Aim for >80% code coverage

## Examples

Good:
```python
async def process_frame(frame_id: int) -> dict[str, Any]:
    """Process captured frame with OCR.
    
    Args:
        frame_id: Database ID of frame to process
        
    Returns:
        Dictionary with extracted text and metadata
        
    Raises:
        ProcessingError: If OCR fails
    """
    try:
        frame = await db.get_frame(frame_id)
        text = await ocr_engine.extract(frame.image)
        return {"text": text, "confidence": 0.95}
    except OCRError as e:
        logger.error(f"OCR failed for frame {frame_id}: {e}")
        raise ProcessingError(f"Cannot process frame: {e}")
```

Bad:
```python
def process_frame(frame_id):  # No type hints, no async
    frame = db.get_frame(frame_id)  # Blocking call
    return ocr_engine.extract(frame.image)  # No error handling
```
```

### FastAPI Patterns (`.cursor/rules/fastapi-patterns.mdc`)

```markdown
---
description: FastAPI development patterns for ZERO API
globs: src/api/**/*.py
---

# FastAPI Patterns

## Route Structure
- Use APIRouter for modular routes
- Group related endpoints
- Use dependency injection for auth
- Return Pydantic models, not dicts

## Request/Response
- Use Pydantic schemas for validation
- Return 422 for validation errors
- Include error details in responses
- Use HTTPException for errors

## Background Tasks
- Use BackgroundTasks for async work
- Don't block request handlers
- Log background task status
- Handle task failures gracefully

## Examples

Good:
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/frames", tags=["frames"])

class FrameResponse(BaseModel):
    id: int
    timestamp: datetime
    text: str
    confidence: float

@router.get("/{frame_id}", response_model=FrameResponse)
async def get_frame(
    frame_id: int,
    db: AsyncSession = Depends(get_db)
) -> FrameResponse:
    frame = await db.get(Frame, frame_id)
    if not frame:
        raise HTTPException(status_code=404, detail="Frame not found")
    return FrameResponse.from_orm(frame)
```
```

### AI Integration (`.cursor/rules/ai-integration.mdc`)

```markdown
---
description: Guidelines for integrating Ollama models
globs: src/ai/**/*.py
---

# AI Integration Rules

## Model Selection
- Use DeepSeek-R1-32B for complex reasoning
- Use Llama 3.1-8B for fast queries
- Use Qwen 2.5-Coder-32B for code tasks
- Always check model availability before queries

## Context Management
- Limit context to 128K tokens (DeepSeek-R1)
- Prioritize recent frames over old ones
- Include system prompt in all queries
- Use streaming for long responses

## Error Handling
- Retry failed queries (max 3 attempts)
- Fall back to smaller model on timeout
- Log all model interactions
- Handle JSON parsing errors

## Examples

Good:
```python
async def query_with_context(
    query: str,
    model: str = "deepseek-r1:32b",
    max_tokens: int = 4096
) -> str:
    """Query AI model with screen context."""
    # Build context from recent frames
    frames = await get_recent_frames(limit=50)
    context = build_context_window(frames, max_tokens=120000)
    
    # Query with retry
    for attempt in range(3):
        try:
            response = await ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Context: {context}\n\nQuery: {query}"}
                ],
                stream=False
            )
            return response["message"]["content"]
        except Exception as e:
            if attempt == 2:
                logger.error(f"Query failed after 3 attempts: {e}")
                raise
            await asyncio.sleep(2 ** attempt)
```
```

---

## Testing Strategy

**Unit Tests:**
```python
# tests/test_capture.py
import pytest
from src.capture.screen_recorder import ScreenRecorder

@pytest.mark.asyncio
async def test_screen_capture():
    recorder = ScreenRecorder(fps=1.0)
    await recorder.start_recording()
    await asyncio.sleep(2)
    frames = recorder.frame_buffer.get_all()
    assert len(frames) >= 2
    await recorder.stop_recording()
```

**Integration Tests:**
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_start_recording():
    response = client.post("/api/start")
    assert response.status_code == 200
    assert response.json()["status"] == "recording"
```

---

## Deployment

**Local Installation:**
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Tesseract with Hebrew support
# Linux: sudo apt-get install tesseract-ocr tesseract-ocr-heb
# macOS: brew install tesseract tesseract-lang

# 3. Install Ollama and pull models
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull deepseek-r1:32b
ollama pull llama3.1:8b
ollama pull qwen2.5-coder:32b

# 4. Set up environment
cp .env.example .env
# Edit .env with your settings

# 5. Initialize database
python -m src.storage.database init

# 6. Run application
python -m src.main
```

**Docker Deployment (Future):**
```dockerfile
FROM python:3.10-slim
RUN apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-heb
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ /app/src/
CMD ["python", "-m", "src.main"]
```

---

## Security Considerations

**Data Privacy:**
- All data stored locally (no cloud)
- Encrypt sensitive screenshots
- Secure database with password
- No telemetry or tracking

**API Security:**
- Add authentication middleware
- Rate limiting on endpoints
- Input validation on all routes
- CORS configuration

**Automation Safety:**
- Confirm destructive actions
- Log all automation tasks
- Sandbox Playwright execution
- User approval for sensitive operations

---

## Monitoring & Logging

**Logging Configuration:**
```python
# src/utils/logger.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler (10MB, 5 backups)
    file_handler = RotatingFileHandler(
        "logs/zero.log",
        maxBytes=10485760,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
```

**Metrics to Track:**
- Frames captured per hour
- OCR success rate
- AI query latency
- Storage usage
- System resource usage

---

## Future Enhancements

**Phase 5+ Ideas:**
1. **Audio Recording:** Integrate Whisper for speech-to-text
2. **Web UI:** React dashboard for visualization
3. **Mobile Sync:** Cross-device context sharing
4. **Plugin System:** Extensible automation modules
5. **Cloud Backup:** Optional encrypted cloud storage
6. **Multi-user:** Support multiple user profiles
7. **Smart Alerts:** Proactive notifications based on screen content
8. **Meeting Assistant:** Automatic meeting transcription + summaries

---

## Troubleshooting

**Common Issues:**

1. **OCR accuracy low:**
   - Increase DPI of captures
   - Improve image preprocessing
   - Update Tesseract training data

2. **High CPU usage:**
   - Reduce FPS
   - Increase frame deduplication threshold
   - Disable real-time OCR

3. **Model timeouts:**
   - Reduce context window size
   - Switch to smaller model
   - Check Ollama service status

4. **Playwright failures:**
   - Update browser drivers
   - Increase timeout values
   - Check website DOM structure
   - Fall back to OCR

---

## Development Workflow with Cursor

### Getting Started

1. **Initialize project:**
   ```bash
   cursor .
   ```

2. **Load this file:**
   - Open this file in Cursor
   - Reference with @ZERO-system-cursor.md in prompts

3. **Start development:**
   ```
   @ZERO-system-cursor.md Implement the ScreenRecorder class in src/capture/screen_recorder.py
   ```

4. **Iterate:**
   - Use Composer for large changes
   - Use Chat for specific questions
   - Reference relevant files with @filename

### Example Prompts

**For screen capture:**
```
@ZERO-system-cursor.md @src/capture/screen_recorder.py

Implement the ScreenRecorder class with:
- Asynchronous screen capture using mss
- Frame buffer with max size 100
- Frame deduplication using perceptual hashing
- Proper error handling and logging
- Unit tests in tests/test_capture.py
```

**For OCR integration:**
```
@ZERO-system-cursor.md @src/processing/ocr_engine.py

Build the OCR engine with:
- Tesseract integration for Hebrew + English
- Image preprocessing pipeline
- Confidence scoring
- Caching mechanism
- Handle RTL text properly
```

**For AI integration:**
```
@ZERO-system-cursor.md @src/ai/model_manager.py

Create model manager for Ollama with:
- Support for 3 models (DeepSeek-R1, Llama, Qwen)
- Dynamic model switching
- Context window management (128K tokens)
- Streaming responses
- Comprehensive error handling
```

---

## Success Criteria

**MVP Success:**
- ✅ Captures screen at 1 FPS
- ✅ OCR extracts Hebrew + English text
- ✅ SQLite stores all data
- ✅ FastAPI serves queries
- ✅ Search works accurately

**Full System Success:**
- ✅ All 3 AI models working
- ✅ Playwright automation functional
- ✅ <2GB RAM usage
- ✅ <10% CPU usage
- ✅ Query response <3 seconds
- ✅ 90% automation success rate

---

## Resources

**Documentation:**
- mss: https://python-mss.readthedocs.io/
- Tesseract: https://tesseract-ocr.github.io/
- Playwright: https://playwright.dev/python/
- Ollama: https://github.com/ollama/ollama-python
- FastAPI: https://fastapi.tiangolo.com/

**Similar Projects:**
- ScreenPipe: https://github.com/mediar-ai/screenpipe
- Bytebot: https://github.com/bytebot-ai/bytebot

---

## Notes for Cursor AI

**When building this system:**
1. Always use type hints
2. Prefer async/await for I/O
3. Add comprehensive error handling
4. Write docstrings for all functions
5. Include unit tests
6. Log important events
7. Optimize for performance
8. Keep code modular

**Focus on:**
- Clean architecture
- Testability
- Performance
- User privacy
- Extensibility

**Avoid:**
- Blocking operations
- Hardcoded values
- Tight coupling
- Missing error handling
- Undocumented code

---

## Conclusion

This document provides everything needed to build ZERO from scratch. Follow the phases sequentially, use Cursor's AI assistance effectively, and refer to this document throughout development.

**Start with Phase 1 (MVP) and iterate from there.**

Good luck building ZERO! 🚀