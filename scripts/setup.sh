#!/bin/bash

# ============================================================================
# Zero Agent - Setup Script
# ============================================================================
#
# This script sets up the Zero Agent development environment
#
# Usage:
#   bash scripts/setup.sh
#   OR
#   chmod +x scripts/setup.sh && ./scripts/setup.sh

set -e  # Exit on error

echo "🚀 Zero Agent - Setup Script"
echo "================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
echo "✅ Found Python $PYTHON_VERSION"

# Check if Python version is >= 3.10
MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
    echo "⚠️  Warning: Python 3.10+ is recommended. You have $PYTHON_VERSION"
fi

echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⏭️  Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet
echo "✅ pip upgraded"

echo ""

# Install dependencies
echo "📥 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found"
fi

echo ""

# Check Ollama
echo "🤖 Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    
    # Check if models are available
    echo "📋 Checking available models..."
    ollama list
else
    echo "⚠️  Ollama is not installed"
    echo "   Install from: https://ollama.ai/"
    echo "   Then run: ollama pull llama3.1:8b"
    echo "             ollama pull qwen2.5-coder:32b"
    echo "             ollama pull deepseek-r1:32b"
fi

echo ""

# Create .env file if it doesn't exist
echo "⚙️  Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Created .env from env.example"
        echo "   Please edit .env and add your API keys"
    else
        echo "⚠️  env.example not found"
    fi
else
    echo "⏭️  .env already exists"
fi

echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p workspace logs data/vectors data/database
echo "✅ Directories created"

echo ""

# Summary
echo "================================"
echo "✅ Setup completed successfully!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Edit .env and add your API keys (if needed)"
echo ""
echo "3. Start Zero Agent:"
echo "   python api_server.py"
echo ""
echo "4. Open in browser:"
echo "   http://localhost:8080/zero_web_interface.html"
echo ""
echo "Happy coding! 🚀"

