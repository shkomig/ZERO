"""
Multi-Model LLM
===============
Supports multiple Ollama models with smart switching
"""

import requests
from typing import Dict, Any, List, Optional
import time


class MultiModelLLM:
    """
    LLM wrapper that supports multiple models
    Can switch between models based on task requirements
    """
    
    # Model configurations
    MODELS = {
        "fast": {
            "name": "llama3.1:8b",
            "description": "Fast, good for simple tasks",
            "size": "4.9GB",
            "speed": "⚡⚡⚡",
            "quality": "⭐⭐⭐"
        },
        "coder": {
            "name": "qwen2.5-coder:32b",
            "description": "Expert in coding tasks",
            "size": "19GB",
            "speed": "⚡⚡",
            "quality": "⭐⭐⭐⭐⭐"
        },
        "smart": {
            "name": "deepseek-r1:32b",
            "description": "Deep reasoning, complex tasks",
            "size": "19GB",
            "speed": "⚡⚡",
            "quality": "⭐⭐⭐⭐⭐"
        },
        "balanced": {
            "name": "gpt-oss:20b-cloud",
            "description": "Balanced speed and quality",
            "size": "Unknown",
            "speed": "⚡⚡",
            "quality": "⭐⭐⭐⭐"
        }
    }
    
    def __init__(self, 
                 default_model: str = "fast",
                 base_url: str = "http://localhost:11434"):
        self.default_model = default_model
        self.base_url = base_url
        self.current_model = self.MODELS[default_model]["name"]
        self.conversation_history = []
        self.stats = {
            "fast": 0,
            "coder": 0,
            "smart": 0,
            "balanced": 0
        }
        
    def generate(self, 
                 prompt: str, 
                 model: Optional[str] = None,
                 max_tokens: int = 2000) -> str:
        """
        Generate response with specified or default model
        
        Args:
            prompt: The prompt
            model: Model type ("fast", "coder", "smart", "balanced") or None for default
            max_tokens: Maximum tokens
            
        Returns:
            Generated text
        """
        # Select model
        if model and model in self.MODELS:
            model_name = self.MODELS[model]["name"]
            self.stats[model] += 1
        else:
            model_name = self.current_model
            self.stats[self.default_model] += 1
        
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            }
            
            start_time = time.time()
            response = requests.post(url, json=payload, timeout=180)
            response.raise_for_status()
            elapsed = time.time() - start_time
            
            result = response.json()
            generated = result.get("response", "").strip()
            
            # Log performance
            tokens = len(generated.split())
            speed = tokens / elapsed if elapsed > 0 else 0
            
            if model:
                print(f"   [Model: {model_name} | {elapsed:.1f}s | {speed:.0f} tokens/s]")
            
            return generated
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             model: Optional[str] = None,
             max_tokens: int = 2000) -> str:
        """
        Chat with conversation history
        """
        # Select model
        if model and model in self.MODELS:
            model_name = self.MODELS[model]["name"]
            self.stats[model] += 1
        else:
            model_name = self.current_model
            self.stats[self.default_model] += 1
        
        try:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            }
            
            start_time = time.time()
            response = requests.post(url, json=payload, timeout=180)
            response.raise_for_status()
            elapsed = time.time() - start_time
            
            result = response.json()
            message = result.get("message", {})
            generated = message.get("content", "").strip()
            
            # Log performance
            tokens = len(generated.split())
            speed = tokens / elapsed if elapsed > 0 else 0
            
            if model:
                print(f"   [Model: {model_name} | {elapsed:.1f}s | {speed:.0f} tokens/s]")
            
            return generated
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def set_default_model(self, model_type: str):
        """
        Change default model
        """
        if model_type in self.MODELS:
            self.default_model = model_type
            self.current_model = self.MODELS[model_type]["name"]
            print(f"✓ Default model set to: {self.current_model}")
        else:
            print(f"✗ Unknown model type: {model_type}")
    
    def get_available_models(self) -> Dict[str, Dict[str, str]]:
        """
        Get list of available models
        """
        return self.MODELS
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get usage statistics
        """
        return self.stats
    
    def print_models_info(self):
        """
        Print information about available models
        """
        print("\n" + "="*70)
        print("📊 AVAILABLE MODELS")
        print("="*70)
        
        for model_type, info in self.MODELS.items():
            print(f"\n🔹 {model_type.upper()}: {info['name']}")
            print(f"   Description: {info['description']}")
            print(f"   Size: {info['size']}")
            print(f"   Speed: {info['speed']} | Quality: {info['quality']}")
            print(f"   Usage: {self.stats[model_type]} times")
        
        print("\n" + "="*70)
    
    def test_connection(self, verbose: bool = False) -> bool:
        """
        Test connection to Ollama
        """
        try:
            response = requests.get(self.base_url, timeout=5)
            if response.status_code == 200:
                if verbose:
                    print("✓ Connected to Ollama")
                return True
            return False
        except:
            if verbose:
                print("✗ Cannot connect to Ollama")
            return False


# Test
if __name__ == "__main__":
    print("Multi-Model LLM Test")
    print("="*70)
    
    llm = MultiModelLLM(default_model="fast")
    
    if not llm.test_connection(verbose=True):
        print("Please start Ollama first!")
        exit(1)
    
    llm.print_models_info()
    
    print("\n" + "="*70)
    print("Testing different models:")
    print("="*70)
    
    # Test fast model
    print("\n1. Testing FAST model (llama3.1:8b)...")
    response = llm.generate("What is 2+2?", model="fast")
    print(f"   Response: {response[:100]}")
    
    # Test smart model (if you want to test - it's slower)
    # print("\n2. Testing SMART model (deepseek-r1:32b)...")
    # response = llm.generate("Explain quantum computing", model="smart")
    # print(f"   Response: {response[:100]}")
    
    print("\n" + "="*70)
    print("✅ Multi-Model LLM Ready!")
