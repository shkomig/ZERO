"""
Multi-model routing system for Zero Agent
Intelligently routes tasks to the best available model
"""

from typing import Literal, Optional, Dict, List
from pydantic import BaseModel
import anthropic
import ollama
from zero_agent.core.config import config


class ModelCapability(BaseModel):
    """Model capability profile"""
    name: str
    provider: str
    speed: int  # 1-10
    quality: int  # 1-10
    cost: float  # per 1M tokens
    specialties: List[str]
    context_window: int
    temperature: float = 0.7


class ModelRouter:
    """Intelligent model routing system"""
    
    def __init__(self):
        # Initialize clients
        self.ollama_client = ollama.Client(host=config.settings.ollama_host)
        
        # Initialize Claude if API key available
        if config.settings.anthropic_api_key:
            self.claude_client = anthropic.Anthropic(
                api_key=config.settings.anthropic_api_key
            )
        else:
            self.claude_client = None
            print("[WARN]  Warning: Anthropic API key not found. Cloud models disabled.")
        
        # Load model capabilities from config
        self.models: Dict[str, ModelCapability] = {}
        self._load_models()
        
        # Load routing rules
        self.routing_rules = config.get_routing_rules()
    
    def _load_models(self):
        """Load model configurations"""
        models_config = config.models_config.get("models", {})
        
        # Load cloud models
        for model_name, model_config in models_config.get("cloud", {}).items():
            if self.claude_client:  # Only if API key available
                self.models[model_name] = ModelCapability(
                    name=model_name,
                    provider=model_config.get("provider", "anthropic"),
                    speed=model_config.get("speed", 7),
                    quality=model_config.get("quality", 10),
                    cost=model_config.get("cost", 3.0),
                    specialties=model_config.get("specialties", []),
                    context_window=model_config.get("context_window", 200000),
                    temperature=model_config.get("temperature", 0.7)
                )
        
        # Load local models
        for model_name, model_config in models_config.get("local", {}).items():
            self.models[model_name] = ModelCapability(
                name=model_name,
                provider=model_config.get("provider", "ollama"),
                speed=model_config.get("speed", 7),
                quality=model_config.get("quality", 7),
                cost=model_config.get("cost", 0.0),
                specialties=model_config.get("specialties", []),
                context_window=model_config.get("context_window", 8000),
                temperature=model_config.get("temperature", 0.7)
            )
    
    def select_model(
        self,
        task: str,
        complexity: Literal["low", "medium", "high"] = "medium",
        priority: Literal["speed", "quality", "cost"] = "quality"
    ) -> str:
        """
        Select optimal model based on task and requirements
        
        Args:
            task: Task type or description
            complexity: Task complexity level
            priority: What to optimize for
            
        Returns:
            Model name
        """
        # Get candidate models for task
        candidates = self._get_candidates(task)
        
        if not candidates:
            # Fallback to default
            return config.settings.default_model
        
        # Filter by complexity
        if complexity == "low":
            # Prefer fast models
            candidates = [m for m in candidates if m in self.models and self.models[m].speed >= 7]
        elif complexity == "high":
            # Prefer high quality models
            candidates = [m for m in candidates if m in self.models and self.models[m].quality >= 9]
        
        # If no candidates after filtering, use all original candidates
        if not candidates:
            candidates = self._get_candidates(task)
        
        # Select based on priority
        if priority == "speed":
            selected = max(
                candidates,
                key=lambda m: self.models[m].speed if m in self.models else 0
            )
        elif priority == "cost":
            selected = min(
                candidates,
                key=lambda m: self.models[m].cost if m in self.models else 999
            )
        else:  # quality
            selected = max(
                candidates,
                key=lambda m: self.models[m].quality if m in self.models else 0
            )
        
        return selected
    
    def _get_candidates(self, task: str) -> List[str]:
        """Get candidate models for task type"""
        task_lower = task.lower()
        task_routing = self.routing_rules.get("task_routing", {})
        
        # Check each task type
        for task_type, models in task_routing.items():
            if task_type in task_lower:
                return models
        
        # Check specialties
        for model_name, model in self.models.items():
            for specialty in model.specialties:
                if specialty.replace("_", " ") in task_lower:
                    return [model_name]
        
        # Default: general task routing
        return task_routing.get("general", [config.settings.default_model])
    
    def invoke_model(self, model_name: str, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Invoke selected model
        
        Args:
            model_name: Name of model to use
            messages: List of messages [{"role": "user", "content": "..."}]
            **kwargs: Additional model parameters
            
        Returns:
            Model response as string
        """
        if model_name not in self.models:
            print(f"[WARN]  Model {model_name} not found, using fallback")
            model_name = config.settings.fallback_model
        
        model = self.models[model_name]
        
        if model.provider == "anthropic":
            return self._invoke_claude(model_name, messages, **kwargs)
        elif model.provider == "ollama":
            return self._invoke_ollama(model_name, messages, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {model.provider}")
    
    def _invoke_claude(self, model_name: str, messages: List[Dict[str, str]], **kwargs) -> str:
        """Invoke Claude API"""
        if not self.claude_client:
            raise ValueError("Claude API not available (missing API key)")
        
        model = self.models[model_name]
        
        # Get actual Claude model name from config
        model_config = config.get_model_config(model_name)
        claude_model = model_config.get("model_name", model_name) if model_config else model_name
        
        try:
            response = self.claude_client.messages.create(
                model=claude_model,
                max_tokens=kwargs.get("max_tokens", 8000),
                temperature=kwargs.get("temperature", model.temperature),
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            print(f"[ERROR] Claude API error: {e}")
            # Fallback to local model
            return self._invoke_ollama(config.settings.fallback_model, messages, **kwargs)
    
    def _invoke_ollama(self, model_name: str, messages: List[Dict[str, str]], **kwargs) -> str:
        """Invoke Ollama local model"""
        model = self.models[model_name]
        
        # Get actual Ollama model name from config
        model_config = config.get_model_config(model_name)
        ollama_model = model_config.get("model_name", model_name) if model_config else model_name
        
        try:
            response = self.ollama_client.chat(
                model=ollama_model,
                messages=messages,
                options={
                    "temperature": kwargs.get("temperature", model.temperature),
                    "num_ctx": model.context_window,
                }
            )
            return response['message']['content']
        except Exception as e:
            print(f"[ERROR] Ollama error: {e}")
            raise
    
    def get_model_info(self, model_name: str) -> Optional[ModelCapability]:
        """Get information about a model"""
        return self.models.get(model_name)
    
    def list_available_models(self) -> List[str]:
        """List all available models"""
        return list(self.models.keys())
    
    def __repr__(self) -> str:
        return f"ModelRouter(models={len(self.models)}, cloud_enabled={self.claude_client is not None})"


# Global router instance
router = ModelRouter()

