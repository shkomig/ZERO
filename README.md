# 🤖 Zero Agent

**AI-Powered Autonomous Agent System**

Zero Agent is an advanced autonomous AI agent that executes complex tasks on your computer through natural language commands. It combines multiple AI models, intelligent routing, and powerful automation tools.

## ✨ Features

- **🧠 Multi-Model Intelligence**: Automatically routes tasks to the best AI model (Claude, DeepSeek, Llama, Qwen)
- **🔧 Powerful Tools**: Git operations, system monitoring, web automation, screen capture
- **💾 RAG Memory**: Learns from past successes and failures
- **🎯 Smart Orchestration**: LangGraph-powered task planning and execution
- **⚡ Local-First**: Most operations use local models (Ollama)

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) installed with models:
  - `ollama pull deepseek-r1:32b`
  - `ollama pull llama3.1:8b`
  - `ollama pull qwen2.5-coder:32b`
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

### Hebrew Support

```
זירו תחפש באינטרנט מדריכי Python
זירו תצלם את המסך
זירו תבדוק את השימוש בזיכרון
```

### Complex Tasks

```
zero search for React best practices and save the top results
zero create a new git repository called awesome-project
zero take a screenshot and analyze what's on screen
```

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `git_*` | Git operations (init, clone, commit, push, status) |
| `system_*` | System monitoring (CPU, memory, disk, processes) |
| `screenshot` | Screen capture with multiple backends |
| `web_search` | Google search with result extraction |
| `navigate_url` | Browser automation |

## 📊 Architecture

```
Zero Agent
├── Core
│   ├── Orchestrator (LangGraph)
│   ├── Model Router (Multi-model selection)
│   ├── Tool Executor
│   └── Config Manager
├── Models
│   ├── Local Models (Ollama)
│   └── Cloud Models (Claude)
├── Tools
│   ├── Git Operations
│   ├── Browser Automation
│   ├── Screen Capture
│   └── System Monitor
├── RAG
│   ├── Memory System (ChromaDB)
│   └── Context Retrieval
└── UI
    └── CLI Interface
```

## ⚙️ Configuration

Edit `env.example` (then rename to `.env`):

```bash
# API Keys
ANTHROPIC_API_KEY=your_key_here

# Models
DEFAULT_MODEL=deepseek-r1:32b
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

### Phase 2: Advanced Features (In Progress)
- [ ] Docker integration
- [ ] Email automation
- [ ] Voice input/output
- [ ] Web UI (Gradio)

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

