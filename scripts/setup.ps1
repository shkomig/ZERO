# ============================================================================
# Zero Agent - Setup Script (PowerShell)
# ============================================================================
#
# This script sets up the Zero Agent development environment on Windows
#
# Usage:
#   .\scripts\setup.ps1

Write-Host "🚀 Zero Agent - Setup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "📋 Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1 | Out-String
    Write-Host "✅ Found $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed. Please install Python 3.10+ first." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "⏭️  Virtual environment already exists" -ForegroundColor Gray
}

Write-Host ""

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✅ Virtual environment activated" -ForegroundColor Green

Write-Host ""

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✅ pip upgraded" -ForegroundColor Green

Write-Host ""

# Install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt --quiet
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠️  requirements.txt not found" -ForegroundColor Yellow
}

Write-Host ""

# Check Ollama
Write-Host "🤖 Checking Ollama..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1 | Out-String
    Write-Host "✅ Ollama is installed" -ForegroundColor Green
    
    # Check available models
    Write-Host "📋 Checking available models..." -ForegroundColor Yellow
    ollama list
} catch {
    Write-Host "⚠️  Ollama is not installed" -ForegroundColor Yellow
    Write-Host "   Install from: https://ollama.ai/" -ForegroundColor Gray
    Write-Host "   Then run: ollama pull llama3.1:8b" -ForegroundColor Gray
    Write-Host "             ollama pull qwen2.5-coder:32b" -ForegroundColor Gray
    Write-Host "             ollama pull deepseek-r1:32b" -ForegroundColor Gray
}

Write-Host ""

# Create .env file
Write-Host "⚙️  Setting up environment variables..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Host "✅ Created .env from env.example" -ForegroundColor Green
        Write-Host "   Please edit .env and add your API keys" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  env.example not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "⏭️  .env already exists" -ForegroundColor Gray
}

Write-Host ""

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
$directories = @("workspace", "logs", "data\vectors", "data\database")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✅ Directories created" -ForegroundColor Green

Write-Host ""

# Summary
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Activate the virtual environment:" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Edit .env and add your API keys (if needed)" -ForegroundColor White
Write-Host ""
Write-Host "3. Start Zero Agent:" -ForegroundColor White
Write-Host "   python api_server.py" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Open in browser:" -ForegroundColor White
Write-Host "   http://localhost:8080/zero_web_interface.html" -ForegroundColor Gray
Write-Host ""
Write-Host "Happy coding! 🚀" -ForegroundColor Cyan

