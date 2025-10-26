"""
Simple configuration - no external dependencies
"""
from pathlib import Path
from typing import Dict, Any
import os

class SimpleConfig:
    """Simple configuration without yaml/external files"""
    
    # Paths
    BASE_DIR = Path(__file__).parent
    WORKSPACE_DIR = BASE_DIR / "workspace"
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Ollama
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    # Models (only those that exist)
    AVAILABLE_MODELS = {
        "fast": "gpt-oss:20b-cloud",
        "reasoning": "gpt-oss:20b-cloud",
        "coding": "gpt-oss:20b-cloud"
    }
    
    # API Keys (optional)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    @classmethod
    def setup(cls):
        """Create necessary directories"""
        cls.WORKSPACE_DIR.mkdir(exist_ok=True)
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_model(cls, task_type: str = "fast") -> str:
        """Get model for task type"""
        return cls.AVAILABLE_MODELS.get(task_type, cls.AVAILABLE_MODELS["fast"])

# Setup on import
SimpleConfig.setup()







