# 🤖 ZERO AGENT - פרומפט מקצועי לבניית סוכן AI אוטונומי

## 📋 סקירה כללית

אתה מפתח מערכת בשם **Zero Agent** - סוכן AI אוטונומי מתקדם שמבצע משימות מורכבות על מחשב Windows באמצעות ממשק שיחה טבעי. המערכת משלבת מספר מודלי AI מקומיים, כלי אוטומציה, ו-RAG לביצוע אוטונומי מלא.

---

## 🎯 יעדי המערכת

### דוגמאות לפעולות:
1. **"זירו תבנה לי משחק טטריס משודרג לילדים, תעלה לגיט ותעשה דיפלוי בנטפלאי"**
   - בניית קוד מלאה
   - אוטומציה של Git
   - דיפלוי אוטומטי

2. **"זירו תן לי 5 חדשות אחרונות בטכנולוגיה"**
   - חיפוש באינטרנט
   - סינון ותמצות

3. **"זירו בדוק מיילים עם פרסומות לא רלוונטיות ומחק אותם"**
   - אינטגרציה עם Gmail
   - סינון חכם
   - פעולות אוטומטיות

4. **"זירו בדוק את המערכת שלי והמלץ על שיפורים"**
   - ניתוח מערכת
   - המלצות מבוססות AI

---

## 🏗️ ארכיטקטורת המערכת

```
┌─────────────────────────────────────────────────┐
│         Zero Agent - Voice/Text Interface       │
│         (Speech-to-Text + Text Input)            │
└────────────────────┬────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│          Master Orchestrator (LangGraph)        │
│  - Task Planning & Decomposition                │
│  - Model Selection & Routing                    │
│  - Error Recovery & Retry Logic                 │
│  - Context Management (RAG)                     │
└────────────────────┬────────────────────────────┘
                     ↓
        ┌────────────┴────────────┐
        ↓                         ↓
┌──────────────┐          ┌──────────────┐
│ Local Models │          │ Cloud APIs   │
├──────────────┤          ├──────────────┤
│DeepSeek-R1   │          │Claude 4.5    │
│Llama-3.1     │          │(API)         │
│Qwen-Coder    │          │              │
│FLUX.1        │          │              │
│HunyuanVideo  │          │              │
│CogVideoX     │          │              │
│MMS-TTS-HEB   │          │              │
└──────┬───────┘          └──────┬───────┘
       │                         │
       └────────┬────────────────┘
                ↓
    ┌───────────────────────┐
    │   Tool Execution Layer │
    ├───────────────────────┤
    │ • Screen Capture       │
    │ • Browser Automation   │
    │ • Git Operations       │
    │ • Docker Control       │
    │ • Email Management     │
    │ • System Monitor       │
    │ • File Operations      │
    └───────────────────────┘
                ↓
    ┌───────────────────────┐
    │   RAG Memory System   │
    ├───────────────────────┤
    │ • Conversation History │
    │ • User Preferences     │
    │ • Past Successes       │
    │ • Error Patterns       │
    │ • Domain Knowledge     │
    └───────────────────────┘
```

---

## 🛠️ טכנולוגיות ותשתיות

### Core Framework
```yaml
Orchestration:
  - LangGraph (v0.2+)
  - LangChain (v0.3+)
  
Backend:
  - Python 3.11+
  - FastAPI (REST API)
  - WebSocket (real-time)
  
Database & Cache:
  - ChromaDB (RAG vector store)
  - Redis (caching + queue)
  - SQLite (metadata + logs)
```

### AI Models Stack
```yaml
Local Models (via Ollama):
  Reasoning:
    - DeepSeek-R1-32B (complex reasoning)
  
  General:
    - Llama-3.1-8B (fast general tasks)
  
  Code:
    - Qwen-2.5-Coder-32B (coding specialist)
  
  Image:
    - FLUX.1-schnell-FP8 (image generation)
  
  Video:
    - HunyuanVideo-I2V-FP8 (image-to-video)
    - CogVideoX-5B (video generation)
  
  Speech:
    - facebook/mms-tts-heb (Hebrew TTS)

Cloud APIs:
  - Claude Sonnet 4.5 (primary orchestrator)
  - Claude API for computer use tools
```

### Automation Tools
```yaml
Screen Capture:
  - windows-capture (GPU-accelerated)
  - DXcam (240Hz+ capture)
  - PIL/PyAutoGUI (backup)

Browser Automation:
  - Playwright (primary)
  - Selenium (backup)

Computer Control:
  - pyautogui (mouse/keyboard)
  - pywin32 (Windows API)
  - powershell (system commands)

Git & Deployment:
  - GitPython
  - Docker SDK
  - Netlify CLI
  - Vercel CLI
```

---

## 📝 פרומפט מלא לקורסור

```markdown
# Zero Agent Development Task

## Context
You are developing Zero Agent - an autonomous AI agent that executes complex tasks on Windows through natural language commands. The system integrates multiple local AI models (via Ollama), cloud APIs, and automation tools.

## Current Setup
- **OS**: Windows 11
- **Docker**: Installed and running
- **Ollama Models**:
  - DeepSeek-R1-32B
  - Llama-3.1-8B
  - Qwen-2.5-Coder-32B
  - GPT-OSS
  - FLUX.1-schnell-FP8
  - HunyuanVideo-I2V-FP8
  - CogVideoX-5B
  - facebook/mms-tts-heb

- **Tools**: Cursor Pro subscription
- **RAG**: Small existing system (stock trading docs)

## Phase 1: Foundation Setup (Current Task)

### 1.1 Project Structure
Create the following directory structure:

```
zero_agent/
├── core/
│   ├── __init__.py
│   ├── orchestrator.py      # LangGraph master agent
│   ├── model_router.py      # Multi-model routing
│   ├── tool_executor.py     # Tool execution layer
│   └── config.py            # Configuration
├── models/
│   ├── __init__.py
│   ├── local_models.py      # Ollama integration
│   ├── cloud_models.py      # Claude API
│   └── router_logic.py      # Routing strategies
├── tools/
│   ├── __init__.py
│   ├── screen_capture.py    # Screenshot tools
│   ├── browser.py           # Playwright automation
│   ├── git_ops.py           # Git operations
│   ├── docker_ops.py        # Docker control
│   ├── email.py             # Email management
│   └── system_monitor.py    # System analysis
├── rag/
│   ├── __init__.py
│   ├── memory.py            # RAG memory system
│   ├── embeddings.py        # Vector embeddings
│   └── retrieval.py         # Information retrieval
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   └── websocket.py         # Real-time communication
├── ui/
│   ├── cli.py               # Command-line interface
│   └── gradio_app.py        # Web UI (future)
├── tests/
│   ├── test_orchestrator.py
│   ├── test_tools.py
│   └── test_models.py
├── config/
│   ├── models.yaml          # Model configurations
│   └── tools.yaml           # Tool configurations
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker services
├── README.md                # Project documentation
└── main.py                  # Entry point
```

### 1.2 Core Dependencies (requirements.txt)

```python
# Core Framework
langgraph>=0.2.0
langchain>=0.3.0
langchain-anthropic>=0.3.0
langchain-community>=0.3.0

# API & Server
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
websockets>=12.0
python-socketio>=5.11.0

# AI Models & Embeddings
anthropic>=0.39.0
sentence-transformers>=2.3.0
chromadb>=0.4.22
ollama>=0.1.0

# Browser & Automation
playwright>=1.55.0
selenium>=4.16.0
pyautogui>=0.9.54
pywin32>=306

# Screen Capture
windows-capture>=1.5.0
dxcam>=0.0.5
mss>=9.0.1
pillow>=10.2.0

# Git & Deployment
gitpython>=3.1.40
docker>=7.0.0

# Data Processing
pandas>=2.2.0
numpy>=1.26.0
opencv-python>=4.9.0

# Database & Cache
redis>=5.0.1
sqlalchemy>=2.0.25

# Utilities
python-dotenv>=1.0.0
pydantic>=2.5.0
aiohttp>=3.9.1
requests>=2.31.0
pyyaml>=6.0.1
```

### 1.3 Core Implementation

#### core/orchestrator.py
```python
"""
Master orchestrator using LangGraph for task planning and execution.
Based on research: LangGraph provides stateful multi-agent workflows
with built-in persistence and human-in-the-loop capabilities.
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator

class AgentState(TypedDict):
    """State shared across all nodes in the graph"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    task: str
    plan: list[str]
    current_step: int
    tool_results: dict
    context: dict
    error_count: int
    needs_clarification: bool

class ZeroOrchestrator:
    """Main orchestrator for Zero Agent"""
    
    def __init__(self, model_router, tool_executor, rag_system):
        self.model_router = model_router
        self.tool_executor = tool_executor
        self.rag_system = rag_system
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("understand", self._understand_task)
        workflow.add_node("plan", self._create_plan)
        workflow.add_node("execute", self._execute_step)
        workflow.add_node("verify", self._verify_result)
        workflow.add_node("reflect", self._reflect_and_learn)
        
        # Add edges
        workflow.set_entry_point("understand")
        workflow.add_edge("understand", "plan")
        workflow.add_edge("plan", "execute")
        workflow.add_edge("execute", "verify")
        
        # Conditional edges
        workflow.add_conditional_edges(
            "verify",
            self._should_continue,
            {
                "continue": "execute",
                "clarify": "understand",
                "complete": "reflect"
            }
        )
        workflow.add_edge("reflect", END)
        
        return workflow.compile()
    
    def _understand_task(self, state: AgentState) -> AgentState:
        """Understand user's task using RAG and reasoning"""
        # Retrieve relevant context from RAG
        context = self.rag_system.retrieve(state["task"])
        
        # Use best model for understanding
        model = self.model_router.select_model(
            task="understand",
            complexity="medium"
        )
        
        # Generate understanding
        response = model.invoke([
            HumanMessage(content=f"""
            Task: {state['task']}
            Context: {context}
            
            Analyze this task:
            1. What is the user asking for?
            2. What tools will be needed?
            3. What are potential challenges?
            4. Is clarification needed?
            """)
        ])
        
        return {
            **state,
            "messages": [response],
            "context": context,
            "needs_clarification": self._check_needs_clarification(response)
        }
    
    def _create_plan(self, state: AgentState) -> AgentState:
        """Create detailed execution plan"""
        model = self.model_router.select_model(
            task="planning",
            complexity="high"
        )
        
        response = model.invoke([
            HumanMessage(content=f"""
            Task: {state['task']}
            Context: {state['context']}
            
            Create a detailed step-by-step plan:
            1. Break down into atomic steps
            2. Identify required tools for each step
            3. Consider dependencies
            4. Add verification checkpoints
            
            Return as JSON list of steps.
            """)
        ])
        
        plan = self._parse_plan(response.content)
        
        return {
            **state,
            "plan": plan,
            "current_step": 0
        }
    
    def _execute_step(self, state: AgentState) -> AgentState:
        """Execute current plan step"""
        step = state["plan"][state["current_step"]]
        
        try:
            # Route to appropriate model
            model = self.model_router.select_for_step(step)
            
            # Execute using tool executor
            result = self.tool_executor.execute(
                step=step,
                model=model,
                context=state["context"]
            )
            
            return {
                **state,
                "tool_results": {
                    **state["tool_results"],
                    state["current_step"]: result
                },
                "error_count": 0
            }
            
        except Exception as e:
            return {
                **state,
                "error_count": state.get("error_count", 0) + 1,
                "tool_results": {
                    **state["tool_results"],
                    state["current_step"]: {"error": str(e)}
                }
            }
    
    def _verify_result(self, state: AgentState) -> AgentState:
        """Verify step execution"""
        result = state["tool_results"][state["current_step"]]
        
        # Use reasoning model for verification
        model = self.model_router.select_model(
            task="verification",
            complexity="medium"
        )
        
        verification = model.invoke([
            HumanMessage(content=f"""
            Verify this step result:
            Step: {state['plan'][state['current_step']]}
            Result: {result}
            
            Is this successful? Should we continue?
            """)
        ])
        
        return {
            **state,
            "messages": state["messages"] + [verification]
        }
    
    def _should_continue(self, state: AgentState) -> str:
        """Decide next action"""
        if state.get("error_count", 0) >= 3:
            return "clarify"
        
        if state["current_step"] < len(state["plan"]) - 1:
            state["current_step"] += 1
            return "continue"
        
        return "complete"
    
    def _reflect_and_learn(self, state: AgentState) -> AgentState:
        """Learn from execution and store in RAG"""
        # Store successful pattern
        self.rag_system.store_success(
            task=state["task"],
            plan=state["plan"],
            results=state["tool_results"]
        )
        
        return state
    
    async def run(self, task: str) -> dict:
        """Execute task"""
        initial_state = {
            "messages": [],
            "task": task,
            "plan": [],
            "current_step": 0,
            "tool_results": {},
            "context": {},
            "error_count": 0,
            "needs_clarification": False
        }
        
        result = await self.graph.ainvoke(initial_state)
        return result
```

#### models/model_router.py
```python
"""
Multi-model routing based on research:
- RouteLLM for cost-effective routing
- IBM's router research for task-based selection
- Semantic routing for context understanding
"""

import anthropic
import ollama
from typing import Literal, Optional
from pydantic import BaseModel

class ModelCapability(BaseModel):
    """Model capability profile"""
    name: str
    speed: int  # 1-10
    quality: int  # 1-10
    cost: float  # per 1M tokens
    specialties: list[str]
    context_window: int

class ModelRouter:
    """Intelligent model routing system"""
    
    def __init__(self):
        self.ollama_client = ollama.Client()
        self.claude_client = anthropic.Anthropic()
        
        # Model capabilities database
        self.models = {
            # Cloud
            "claude-sonnet-4.5": ModelCapability(
                name="claude-sonnet-4.5",
                speed=7,
                quality=10,
                cost=3.0,
                specialties=["planning", "complex_reasoning", "orchestration"],
                context_window=200000
            ),
            
            # Local - Reasoning
            "deepseek-r1-32b": ModelCapability(
                name="deepseek-r1-32b",
                speed=5,
                quality=9,
                cost=0.0,
                specialties=["reasoning", "math", "logic"],
                context_window=32000
            ),
            
            # Local - Fast
            "llama-3.1-8b": ModelCapability(
                name="llama-3.1-8b",
                speed=9,
                quality=7,
                cost=0.0,
                specialties=["quick_tasks", "chat", "classification"],
                context_window=8000
            ),
            
            # Local - Code
            "qwen-2.5-coder-32b": ModelCapability(
                name="qwen-2.5-coder-32b",
                speed=6,
                quality=9,
                cost=0.0,
                specialties=["coding", "debugging", "code_review"],
                context_window=32000
            ),
        }
        
        # Routing rules based on research
        self.routing_rules = {
            "planning": ["claude-sonnet-4.5"],
            "coding": ["qwen-2.5-coder-32b", "claude-sonnet-4.5"],
            "reasoning": ["deepseek-r1-32b", "claude-sonnet-4.5"],
            "quick_response": ["llama-3.1-8b"],
            "complex_analysis": ["claude-sonnet-4.5", "deepseek-r1-32b"],
        }
    
    def select_model(
        self,
        task: str,
        complexity: Literal["low", "medium", "high"],
        priority: Literal["speed", "quality", "cost"] = "quality"
    ) -> str:
        """
        Select optimal model based on task and requirements.
        
        Routing strategy inspired by:
        - AWS multi-LLM routing (semantic + cost-based)
        - RouteLLM (complexity-based routing)
        - IBM router (task specialization)
        """
        
        # Get candidate models for task
        candidates = self._get_candidates(task)
        
        # Filter by complexity
        if complexity == "low":
            candidates = [m for m in candidates if self.models[m].speed >= 7]
        elif complexity == "high":
            candidates = [m for m in candidates if self.models[m].quality >= 9]
        
        # Prioritize based on preference
        if priority == "speed":
            return max(candidates, key=lambda m: self.models[m].speed)
        elif priority == "cost":
            return min(candidates, key=lambda m: self.models[m].cost)
        else:  # quality
            return max(candidates, key=lambda m: self.models[m].quality)
    
    def _get_candidates(self, task: str) -> list[str]:
        """Get candidate models for task"""
        for task_type, models in self.routing_rules.items():
            if task_type in task.lower():
                return models
        
        # Default to balanced model
        return ["claude-sonnet-4.5"]
    
    def invoke_model(self, model_name: str, messages: list) -> str:
        """Invoke selected model"""
        if "claude" in model_name:
            return self._invoke_claude(model_name, messages)
        else:
            return self._invoke_ollama(model_name, messages)
    
    def _invoke_claude(self, model_name: str, messages: list) -> str:
        """Invoke Claude API"""
        response = self.claude_client.messages.create(
            model=model_name,
            max_tokens=8000,
            messages=messages
        )
        return response.content[0].text
    
    def _invoke_ollama(self, model_name: str, messages: list) -> str:
        """Invoke Ollama local model"""
        response = self.ollama_client.chat(
            model=model_name,
            messages=messages
        )
        return response['message']['content']
```

#### tools/screen_capture.py
```python
"""
Screen capture tool using windows-capture (fastest, GPU-accelerated)
Based on research: windows-capture uses Graphics Capture API for
high-performance capturing at 240Hz+
"""

import windows_capture
import numpy as np
from PIL import Image
import cv2
from pathlib import Path

class ScreenCapture:
    """High-performance screen capture for Windows"""
    
    def __init__(self):
        self.capture = None
        self.setup_capture()
    
    def setup_capture(self):
        """Initialize capture system"""
        try:
            # Use windows-capture for best performance
            import windows_capture
            self.backend = "windows_capture"
        except ImportError:
            # Fallback to DXcam
            try:
                import dxcam
                self.capture = dxcam.create()
                self.backend = "dxcam"
            except ImportError:
                # Final fallback to mss
                import mss
                self.capture = mss.mss()
                self.backend = "mss"
    
    def capture_screen(self, save_path: Optional[Path] = None) -> np.ndarray:
        """Capture entire screen"""
        if self.backend == "windows_capture":
            # Fastest method
            img = windows_capture.capture()
        elif self.backend == "dxcam":
            # Fast fallback
            img = self.capture.grab()
        else:
            # Slowest fallback
            monitor = self.capture.monitors[0]
            sct_img = self.capture.grab(monitor)
            img = np.array(sct_img)
        
        if save_path:
            Image.fromarray(img).save(save_path)
        
        return img
    
    def capture_window(self, window_title: str, save_path: Optional[Path] = None) -> np.ndarray:
        """Capture specific window"""
        import pygetwindow as gw
        
        try:
            window = gw.getWindowsWithTitle(window_title)[0]
            x, y, w, h = window.left, window.top, window.width, window.height
            
            # Capture region
            if self.backend == "windows_capture":
                img = windows_capture.capture_region(x, y, w, h)
            elif self.backend == "dxcam":
                img = self.capture.grab(region=(x, y, x+w, y+h))
            else:
                monitor = {"left": x, "top": y, "width": w, "height": h}
                sct_img = self.capture.grab(monitor)
                img = np.array(sct_img)
            
            if save_path:
                Image.fromarray(img).save(save_path)
            
            return img
            
        except IndexError:
            raise ValueError(f"Window '{window_title}' not found")
    
    def analyze_screen(self, description: str) -> str:
        """Use vision model to analyze screenshot"""
        img = self.capture_screen()
        
        # Save temporarily
        temp_path = Path("temp_screenshot.png")
        Image.fromarray(img).save(temp_path)
        
        # Use Claude Vision or local vision model
        # TODO: Implement vision analysis
        
        return "Analysis result"
```

#### tools/browser.py
```python
"""
Browser automation using Playwright
Based on research: Playwright outperforms Selenium with:
- Auto-waiting mechanism
- Better DevTools protocol integration
- Cross-browser support
"""

from playwright.async_api import async_playwright, Browser, Page
from typing import Optional, List, Dict
import asyncio

class BrowserAutomation:
    """Automated browser control"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context = None
        self.page: Optional[Page] = None
    
    async def initialize(self, headless: bool = False):
        """Initialize browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
    
    async def navigate(self, url: str):
        """Navigate to URL"""
        await self.page.goto(url)
        await self.page.wait_for_load_state("networkidle")
    
    async def click(self, selector: str):
        """Click element"""
        await self.page.click(selector)
    
    async def type_text(self, selector: str, text: str):
        """Type text into element"""
        await self.page.fill(selector, text)
    
    async def screenshot(self, path: str, full_page: bool = False):
        """Take screenshot"""
        await self.page.screenshot(path=path, full_page=full_page)
    
    async def extract_text(self, selector: str) -> str:
        """Extract text from element"""
        return await self.page.text_content(selector)
    
    async def execute_script(self, script: str) -> any:
        """Execute JavaScript"""
        return await self.page.evaluate(script)
    
    async def search_google(self, query: str) -> List[Dict]:
        """Search Google and return results"""
        await self.navigate(f"https://www.google.com/search?q={query}")
        
        results = []
        result_elements = await self.page.query_selector_all(".g")
        
        for element in result_elements[:5]:
            title_elem = await element.query_selector("h3")
            link_elem = await element.query_selector("a")
            snippet_elem = await element.query_selector(".VwiC3b")
            
            if title_elem and link_elem:
                results.append({
                    "title": await title_elem.text_content(),
                    "url": await link_elem.get_attribute("href"),
                    "snippet": await snippet_elem.text_content() if snippet_elem else ""
                })
        
        return results
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
```

### 1.4 Configuration Files

#### config/models.yaml
```yaml
models:
  cloud:
    claude-sonnet-4.5:
      provider: anthropic
      api_key: ${ANTHROPIC_API_KEY}
      max_tokens: 8000
      temperature: 0.7
      
  local:
    deepseek-r1-32b:
      provider: ollama
      context_window: 32000
      temperature: 0.3
      
    llama-3.1-8b:
      provider: ollama
      context_window: 8000
      temperature: 0.7
      
    qwen-2.5-coder-32b:
      provider: ollama
      context_window: 32000
      temperature: 0.2

routing:
  default_strategy: quality
  fallback_model: llama-3.1-8b
  max_retries: 3
  timeout_seconds: 120
```

#### .env.example
```bash
# API Keys
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here  # Optional

# Ollama
OLLAMA_HOST=http://localhost:11434

# Database
CHROMA_DB_PATH=./data/chroma
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/zero_agent.log

# Features
ENABLE_VOICE=false
ENABLE_SCREEN_CAPTURE=true
ENABLE_BROWSER=true
```

### 1.5 Main Entry Point

#### main.py
```python
"""
Zero Agent - Main Entry Point
"""

import asyncio
from core.orchestrator import ZeroOrchestrator
from models.model_router import ModelRouter
from tools.tool_executor import ToolExecutor
from rag.memory import RAGMemorySystem
from ui.cli import CLI

async def main():
    """Initialize and run Zero Agent"""
    
    print("🤖 Zero Agent - Starting up...")
    
    # Initialize components
    print("📦 Loading models...")
    model_router = ModelRouter()
    
    print("🔧 Initializing tools...")
    tool_executor = ToolExecutor()
    
    print("🧠 Loading RAG system...")
    rag_system = RAGMemorySystem()
    
    print("🎯 Building orchestrator...")
    orchestrator = ZeroOrchestrator(
        model_router=model_router,
        tool_executor=tool_executor,
        rag_system=rag_system
    )
    
    print("✅ Zero Agent ready!\n")
    
    # Start CLI
    cli = CLI(orchestrator)
    await cli.run()

if __name__ == "__main__":
    asyncio.run(main())
```

## Implementation Instructions

### Step 1: Environment Setup
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Copy and configure environment
copy .env.example .env
# Edit .env with your API keys
```

### Step 2: Verify Ollama Models
```bash
# Check models are available
ollama list

# If any missing, pull them:
ollama pull deepseek-r1:32b
ollama pull llama3.1:8b
ollama pull qwen2.5-coder:32b
```

### Step 3: Initialize Databases
```bash
# Start Redis (if using Docker)
docker run -d -p 6379:6379 redis:latest

# Initialize ChromaDB
python scripts/init_chroma.py
```

### Step 4: Run Tests
```bash
# Run unit tests
pytest tests/ -v

# Test individual components
python -m tests.test_orchestrator
python -m tests.test_tools
```

### Step 5: Start Zero Agent
```bash
python main.py
```

## Key Features to Implement Next (Phase 2)

1. **Advanced Tool Integration**
   - Git operations (GitPython)
   - Docker management
   - Email automation
   - System monitoring

2. **RAG Enhancement**
   - Expand knowledge base
   - Implement semantic caching
   - Add conversation memory

3. **Error Handling**
   - Automatic retry with backoff
   - Intelligent error recovery
   - User notification system

4. **Security**
   - Tool action confirmation
   - Sensitive operation protection
   - Audit logging

5. **UI Improvements**
   - Gradio web interface
   - Voice input (Whisper)
   - Streaming responses

## Success Criteria

✅ **Must Work:**
- Task understanding from natural language
- Model routing based on task complexity
- Screen capture and analysis
- Browser automation (search, navigate)
- Basic error recovery

✅ **Should Work:**
- Multi-step task execution
- Context retention across steps
- Tool chaining (Git → Deploy)
- RAG-based learning

✅ **Nice to Have:**
- Voice input/output
- Real-time streaming
- Advanced error prediction

## Development Philosophy

1. **Start Simple**: Build MVP first, then enhance
2. **Test Often**: Every component has tests
3. **Fail Gracefully**: Always have fallbacks
4. **Learn Continuously**: Store successes in RAG
5. **User First**: Confirm risky operations

## Notes

- Use type hints everywhere
- Document complex logic
- Keep functions small and focused
- Prefer async for I/O operations
- Cache frequently used data

---

זה הפרומפט המלא. התחל עם Phase 1 ואנחנו נבנה את המערכת שלב אחר שלב.
```

---

## 🎓 מקורות המחקר

### LangGraph & Orchestration
- LangGraph מספק ארכיטקטורה מבוססת גרפים עם state management מתקדם, תומך בworkflows מורכבים עם human-in-the-loop
- LangGraph משתמש ב-persistence layer מרכזי המאפשר memory וcontext לאורך אינטראקציות

### Multi-Model Routing
- אסטרטגיות routing דינמיות כוללות semantic routing ו-LLM-assisted routing
- ניתוח מחקר IBM: routing יכול לחסוך עד 85% בעלויות תוך שמירה על איכות
- RouteLLM מספק routers מאומנים מראש שמכלילים היטב לזוגות מודלים שונים

### Screen Capture
- DXcam משתמש ב-Desktop Duplication API ומסוגל ל-240Hz+ capturing, מהיר יותר מכל הפתרונות האחרים
- windows-capture הוא ספריית Python המהירה ביותר, משתמשת ב-Graphics Capture API

### Browser Automation
- Playwright מספק auto-waiting mechanism שמפחית flaky tests, תומך ב-multiple browsers
- Playwright מאפשר network interception, mobile device simulation, והרצה headless

### Claude Computer Use
- Claude Computer Use API מספק כלים מובנים: computer, bash, ו-text_editor
- Claude 3.5 Sonnet הוא המודל הציבורי הראשון עם computer use capabilities

### RAG Systems
- RAG 2025 כולל טכניקות מתקדמות כמו Adaptive RAG, GraphRAG, ו-Self-RAG
- מערכות RAG production-ready דורשות streaming updates, hybrid search, ו-rerankers

---

## 📊 סיכום טכני

### ✅ טכנולוגיות נבחרות (מבוסס מחקר):

1. **LangGraph** - orchestration (60% מפתחי AI agents משתמשים בזה)
2. **windows-capture** - הכי מהיר לscreenshots (GPU-accelerated)
3. **Playwright** - browser automation (עדיף על Selenium)
4. **RouteLLM approach** - multi-model routing
5. **ChromaDB** - RAG vector store
6. **Claude Sonnet 4.5** - master orchestrator

### 🎯 יתרונות הגישה:
- **מהירות**: Local models למשימות פשוטות
- **איכות**: Claude למשימות מורכבות
- **עלות**: חיסכון של עד 85% דרך routing חכם
- **גמישות**: תמיכה במספר מודלים ב-parallel
- **אמינות**: Error recovery + fallbacks

---

## 🚀 Next Steps

1. העתק את הפרומפט לCursor
2. התחל עם Phase 1
3. בדוק כל component לפני המשך
4. בנה incrementally

בהצלחה! 🎉
