# 🤖 Zero Agent

**AI-Powered Autonomous Agent System with Hebrew Support**

Zero Agent is an advanced autonomous AI agent that executes complex tasks on your computer through natural language commands. It combines multiple AI models, intelligent routing, and powerful automation tools with **excellent Hebrew language support**.

## ✨ Features

- **🧠 Multi-Model Intelligence**: Automatically routes tasks to the best AI model (Mistral, Mixtral 8x7B, DeepSeek, Llama, Qwen)
- **🇮🇱 Hebrew Support**: Native Hebrew language support with excellent quality
- **🔧 Powerful Tools**: Git operations, system monitoring, web automation, screen capture
- **💾 RAG Memory**: Learns from past successes and failures (224+ conversations stored)
- **🎯 Smart Orchestration**: LangGraph-powered task planning and execution
- **⚡ Local-First**: Most operations use local models (Ollama)
- **🖥️ Computer Control**: Full computer control including app launching and clicking
- **📊 Web Search**: Real-time web search with stock prices and current data

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) installed with models:
  - `ollama pull mistral:latest` (Default - 4.4GB)
  - `ollama pull deepseek-r1:32b` (19GB - for complex reasoning)
  - `ollama pull llama3.1:8b` (4.9GB - fast responses)
  - `ollama pull qwen2.5-coder:32b` (19GB - for coding tasks)
- (Optional) Anthropic API key for Claude

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/zero-agent.git
cd zero-agent
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers** (for web automation)
```bash
playwright install chromium
```

5. **Configure environment**
```bash
# Copy example env file
copy env.example .env    # Windows
cp env.example .env      # Linux/Mac

# Edit .env and add your API keys (optional)
```

### Run Zero Agent

**Option 1: API Server (Recommended)**
```bash
python api_server.py
```
Then open `http://localhost:8080/zero_chat_simple.html` in your browser.

**Available Interfaces:**
- `zero_chat_simple.html` - Simple chat interface (Recommended)
- `zero_web_interface.html` - Advanced web interface
- `zero_ui.html` - Basic UI

**Option 2: CLI Mode**
```bash
python main.py
```

## 📖 Usage Examples

### Basic Commands

```
# Search the web
zero search the web for Python tutorials

# Take screenshot
zero take a screenshot

# Check system resources
zero check memory usage
zero check cpu usage

# Git operations
zero create a git repo called my-project
zero check git status
```

### Hebrew Support (Native)

```
מה זה פיתון?
צור לי קוד פיתון למשחק טטריס
תן לי ניתוח על מניית QQQ כולל המלצת קניה
בדוק את המערכת
```

### Complex Tasks

```
zero search for React best practices and save the top results
zero create a new git repository called awesome-project
zero take a screenshot and analyze what's on screen
```

## 🛠️ Available Tools

| Tool | Description | Status |
|------|-------------|--------|
| **WebSearch** | Enhanced search with stock prices (Yahoo Finance + DuckDuckGo) | ✅ Active |
| **Code Executor** | Execute Python/bash code, create files and folders | ✅ Active |
| **Computer Control** | Launch apps, click, keyboard input | ✅ Active |
| **Screen Capture** | Take screenshots and analyze | ✅ Active |
| **Memory System** | RAG-based memory with 224+ conversations | ✅ Active |
| **Gmail** | Send and read emails | ⚠️ Config Required |
| **Calendar** | Manage Google Calendar events | ⚠️ Config Required |
| **Database** | SQLite database operations | ✅ Active |
| **Git Operations** | Git init, clone, commit, push, status | ✅ Active |
| **System Monitor** | CPU, memory, disk, processes | ✅ Active |
| **Browser** | Automated web navigation | ✅ Active |

## 📊 Architecture

```
Zero Agent
├── Core
│   ├── Orchestrator (LangGraph)
│   ├── Model Router (Multi-model selection)
│   ├── Tool Executor
│   └── Config Manager
├── Models
│   ├── Mistral:latest (Default - Hebrew optimized)
│   ├── Mixtral:8x7b (Expert - Advanced reasoning)
│   ├── DeepSeek-r1:32b (Complex reasoning)
│   ├── Llama3.1:8b (Fast responses)
│   └── Qwen2.5-coder:32b (Coding tasks)
├── Tools
│   ├── Computer Control
│   ├── Screen Capture
│   ├── Web Search
│   ├── Git Operations
│   └── System Monitor
├── Memory
│   ├── Short-term Memory (224+ conversations)
│   ├── RAG System (ChromaDB)
│   └── Context Retrieval
└── UI
    ├── Web Interface (zero_chat_simple.html)
    ├── Advanced UI (zero_web_interface.html)
    └── CLI Interface
```

## ⚙️ Configuration

Edit `env.example` (then rename to `.env`):

```bash
# API Keys
ANTHROPIC_API_KEY=your_key_here

# Models
DEFAULT_MODEL=mistral:latest
FALLBACK_MODEL=llama3.1:8b

# Features
ENABLE_SCREEN_CAPTURE=true
ENABLE_BROWSER=true
ENABLE_GIT=true
```

Edit `zero_agent/config/models.yaml` for model routing rules.

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_orchestrator.py -v

# Run with coverage
pytest tests/ --cov=zero_agent --cov-report=html
```

## 🔒 Security

- All data stored locally
- Requires confirmation for destructive operations
- Audit logging enabled by default
- Permission system for sensitive actions

## 📝 Development

### Project Structure

```
zero_agent/
├── core/          # Core orchestration
├── models/        # AI model integration
├── tools/         # Automation tools
├── rag/           # Memory system
├── api/           # API layer (future)
├── ui/            # User interfaces
├── tests/         # Tests
└── config/        # Configuration files
```

### Adding New Tools

1. Create tool in `zero_agent/tools/`
2. Add to `ToolExecutor` in `core/tool_executor.py`
3. Update tool mapping in orchestrator
4. Add tests

## 🗺️ Roadmap

### Phase 1: Foundation ✅
- [x] Core orchestration
- [x] Model routing
- [x] Basic tools
- [x] CLI interface

### Phase 2: Advanced Features ✅
- [x] Web UI with Projects system
- [x] Enhanced WebSearch with stock prices
- [x] Agent Orchestrator with task planning
- [x] Memory system with RAG
- [x] Email and Calendar integration
- [ ] Voice input/output
- [ ] Docker integration

### Phase 3: Intelligence
- [ ] Multi-agent collaboration
- [ ] Self-improvement loop
- [ ] Predictive execution
- [ ] Advanced RAG

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [Ollama](https://ollama.ai/)
- Uses [Anthropic Claude](https://anthropic.com/)

## 💬 Support

- Issues: GitHub Issues
- Discussions: GitHub Discussions
- Documentation: [Full Docs](docs/)

---

**Made with ❤️ for the AI community**

🚀 Happy automating with Zero Agent!

