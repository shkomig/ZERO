"""
Zero Agent Configuration
=========================
Easy way to change models without editing code
"""

# Which model to use
# Options: any model you have installed (see: ollama list)
MODEL = "llama3.1:8b"  # ✓ Installed and ready!

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434"

# Workspace settings
WORKSPACE_DIR = "workspace"

# LLM settings
MAX_TOKENS = 2000
TEMPERATURE = 0.7

# Display settings
VERBOSE = True
SHOW_THINKING = True

# Available models on your system:
# - llama3.1:8b          (recommended - good balance)
# - gpt-oss:20b-cloud    (larger, more capable)
# - deepseek-r1:32b      (very large, best quality)
# - qwen2.5-coder:32b    (specialized for coding)

print("Zero Agent Config Loaded")
print(f"Model: {MODEL}")
