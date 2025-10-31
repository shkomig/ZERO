"""
Configuration management for Zero Agent
Loads settings from environment variables and YAML files
"""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    perplexity_api_key: Optional[str] = Field(default=None, env="PERPLEXITY_API_KEY")
    
    # Ollama
    ollama_host: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    ollama_timeout: int = Field(default=120, env="OLLAMA_TIMEOUT")
    
    # Models
    default_model: str = Field(default="llama-3.1-8b", env="DEFAULT_MODEL")
    fallback_model: str = Field(default="llama3.1:8b", env="FALLBACK_MODEL")
    cloud_model: str = Field(default="claude-sonnet-4.5", env="CLOUD_MODEL")
    
    # Database
    chroma_db_path: str = Field(default="./zero_agent/data/vectors", env="CHROMA_DB_PATH")
    sqlite_db_path: str = Field(default="./zero_agent/data/database/zero_agent.db", env="SQLITE_DB_PATH")
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="./zero_agent/logs/zero_agent.log", env="LOG_FILE")
    
    # Features
    enable_voice: bool = Field(default=False, env="ENABLE_VOICE")
    enable_screen_capture: bool = Field(default=True, env="ENABLE_SCREEN_CAPTURE")
    enable_browser: bool = Field(default=True, env="ENABLE_BROWSER")
    enable_git: bool = Field(default=True, env="ENABLE_GIT")
    enable_docker: bool = Field(default=True, env="ENABLE_DOCKER")
    enable_email: bool = Field(default=False, env="ENABLE_EMAIL")
    
    # Browser
    browser_headless: bool = Field(default=False, env="BROWSER_HEADLESS")
    browser_timeout: int = Field(default=30, env="BROWSER_TIMEOUT")
    
    # Screen Capture
    capture_fps: float = Field(default=1.0, env="CAPTURE_FPS")
    capture_quality: int = Field(default=85, env="CAPTURE_QUALITY")
    
    # Security
    require_confirmation_for_destructive: bool = Field(default=True, env="REQUIRE_CONFIRMATION_FOR_DESTRUCTIVE")
    audit_log_enabled: bool = Field(default=True, env="AUDIT_LOG_ENABLED")
    
    # Performance
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    max_context_tokens: int = Field(default=128000, env="MAX_CONTEXT_TOKENS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Allow extra fields in .env file


class ConfigManager:
    """Manages all configuration for Zero Agent"""
    
    def __init__(self):
        self.settings = Settings()
        self.base_dir = Path(__file__).parent.parent
        self.config_dir = self.base_dir / "config"
        
        # Load YAML configs
        self.models_config = self._load_yaml("models.yaml")
        self.tools_config = self._load_yaml("tools.yaml")
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            print(f"[WARN]  Warning: {filename} not found at {config_path}")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[ERROR] Error loading {filename}: {e}")
            return {}
    
    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific model"""
        models = self.models_config.get("models", {})
        
        # Check cloud models
        if model_name in models.get("cloud", {}):
            return models["cloud"][model_name]
        
        # Check local models
        if model_name in models.get("local", {}):
            return models["local"][model_name]
        
        return None
    
    def get_routing_rules(self) -> Dict[str, Any]:
        """Get model routing rules"""
        return self.models_config.get("routing", {})
    
    def get_tool_config(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for specific tool"""
        tools = self.tools_config.get("tools", {})
        return tools.get(tool_name)
    
    def get_permissions(self) -> Dict[str, bool]:
        """Get permission settings"""
        return self.tools_config.get("permissions", {})
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if tool is enabled"""
        tool_config = self.get_tool_config(tool_name)
        if tool_config is None:
            return False
        return tool_config.get("enabled", False)
    
    def ensure_directories(self):
        """Ensure all required directories exist"""
        dirs = [
            Path(self.settings.chroma_db_path),
            Path(self.settings.sqlite_db_path).parent,
            Path(self.settings.log_file).parent,
            self.base_dir / "data" / "screenshots",
        ]
        
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)
            
    def __repr__(self) -> str:
        return f"ConfigManager(ollama={self.settings.ollama_host}, default_model={self.settings.default_model})"


# Global config instance
config = ConfigManager()

# Ensure directories exist on import
config.ensure_directories()

