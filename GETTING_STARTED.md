# 🚀 Getting Started with Zero Agent

## Quick Start Guide

### Step 1: Install Dependencies

```bash
# Make sure you're in the project directory
cd ZERO

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### Step 2: Install Playwright Browsers

```bash
playwright install chromium
```

### Step 3: Setup Ollama Models

Make sure Ollama is running and pull the required models:

```bash
# Check Ollama is running
ollama list

# Pull required models
ollama pull deepseek-r1:32b
ollama pull llama3.1:8b
ollama pull qwen2.5-coder:32b
```

### Step 4: Configure Environment (Optional)

If you want to use Claude API:

1. Copy `env.example` to `.env`:
   ```bash
   copy env.example .env    # Windows
   cp env.example .env      # Linux/Mac
   ```

2. Edit `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```

### Step 5: Run Zero Agent!

```bash
python main.py
```

## First Commands to Try

Once Zero Agent starts, try these commands:

### System Information
```
zero check memory usage
zero check cpu usage
zero give me system information
```

### Screenshots
```
zero take a screenshot
zero capture the screen
```

### Web Search
```
zero search the web for Python tutorials
zero search google for latest AI news
```

### Git Operations
```
zero create a git repo called test-project
zero check git status
```

## Hebrew Support

Zero Agent fully supports Hebrew commands:

```
זירו תבדוק את השימוש בזיכרון
זירו תצלם את המסך
זירו תחפש באינטרנט מדריכי Python
```

## Understanding the Output

Zero Agent will:
1. **Understand** your task
2. **Plan** the steps needed
3. **Execute** each step with appropriate tools
4. **Verify** results
5. **Learn** from the execution

You'll see colored output showing each stage:
- 🤔 Understanding task...
- 📋 Creating execution plan...
- ⚙️ Executing steps...
- ✅ Task complete!

## Troubleshooting

### "No module named X"
```bash
pip install -r requirements.txt
```

### "Ollama connection error"
Make sure Ollama is running:
```bash
ollama serve
```

### "Screen capture failed"
The system will automatically fallback to available screen capture methods.

### "Browser initialization failed"
Install Playwright browsers:
```bash
playwright install chromium
```

## Next Steps

1. Explore all available commands with `help`
2. Check `tools` to see what Zero can do
3. Use `status` to see system information
4. Try complex multi-step tasks!

## Advanced Usage

### Custom Configuration

Edit `zero_agent/config/models.yaml` to:
- Adjust model routing rules
- Change priority preferences
- Add new models

Edit `zero_agent/config/tools.yaml` to:
- Enable/disable tools
- Configure tool settings
- Adjust permissions

### Environment Variables

Key environment variables in `.env`:
- `DEFAULT_MODEL` - Primary model to use
- `ENABLE_SCREEN_CAPTURE` - Enable/disable screenshots
- `ENABLE_BROWSER` - Enable/disable web automation
- `BROWSER_HEADLESS` - Run browser in headless mode

## Need Help?

- Type `help` in Zero Agent for command list
- Check `README.md` for full documentation
- See `PROJECT_STATE.md` for current implementation status
- Review example files in the documentation

**Have fun automating with Zero Agent! 🎉**

