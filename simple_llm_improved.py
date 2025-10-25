"""
Simple LLM Wrapper - IMPROVED CONNECTION TEST
==============================================
Better error handling and connection testing
"""

import requests
import json
from typing import List, Dict, Optional


class SimpleLLM:
    """
    Simple wrapper for Ollama LLM with improved connection testing
    """
    
    def __init__(self, 
                 model: str = "qwen2.5:3b",
                 base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.conversation_history = []
        
    def generate(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate a response for a single prompt
        """
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             max_tokens: int = 1000) -> str:
        """
        Chat with conversation history
        """
        try:
            url = f"{self.base_url}/api/chat"
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            message = result.get("message", {})
            return message.get("content", "").strip()
            
        except requests.exceptions.RequestException as e:
            return f"Error connecting to Ollama: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def chat_with_history(self, user_message: str, max_tokens: int = 1000) -> str:
        """Chat with automatic history management"""
        self.add_to_history("user", user_message)
        response = self.chat(self.conversation_history, max_tokens)
        self.add_to_history("assistant", response)
        return response
    
    def test_connection(self, verbose: bool = False) -> bool:
        """
        IMPROVED: Test if Ollama is running and model is available
        """
        try:
            # Test 1: Check if Ollama server is running
            if verbose:
                print("   Testing Ollama server...")
            
            response = requests.get(self.base_url, timeout=5)
            if response.status_code != 200:
                if verbose:
                    print(f"   ✗ Server not responding (status {response.status_code})")
                return False
            
            if verbose:
                print("   ✓ Ollama server is running")
            
            # Test 2: Check if model is available
            if verbose:
                print(f"   Testing model {self.model}...")
            
            # Try to list models
            try:
                tags_url = f"{self.base_url}/api/tags"
                tags_response = requests.get(tags_url, timeout=5)
                
                if tags_response.status_code == 200:
                    models_data = tags_response.json()
                    models = models_data.get("models", [])
                    model_names = [m.get("name", "") for m in models]
                    
                    if verbose:
                        print(f"   Available models: {model_names}")
                    
                    # Check if our model exists
                    if not any(self.model in name for name in model_names):
                        if verbose:
                            print(f"   ✗ Model {self.model} not found")
                            print(f"   Install it with: ollama pull {self.model}")
                        return False
                    
                    if verbose:
                        print(f"   ✓ Model {self.model} is available")
            except:
                if verbose:
                    print("   ! Could not verify model, but will try anyway")
            
            # Test 3: Try a simple generation
            if verbose:
                print("   Testing generation...")
            
            test_response = self.generate("Hi", max_tokens=10)
            
            if "Error" in test_response:
                if verbose:
                    print(f"   ✗ Generation failed: {test_response}")
                return False
            
            if verbose:
                print("   ✓ Generation works")
            
            return True
            
        except requests.exceptions.ConnectionError:
            if verbose:
                print("   ✗ Cannot connect to Ollama server")
                print("   Is Ollama running? Try: ollama serve")
            return False
        except requests.exceptions.Timeout:
            if verbose:
                print("   ✗ Connection timeout")
            return False
        except Exception as e:
            if verbose:
                print(f"   ✗ Unexpected error: {str(e)}")
            return False


# Test the improved LLM
if __name__ == "__main__":
    print("Testing SimpleLLM (Improved Connection Test)")
    print("=" * 60)
    
    llm = SimpleLLM()
    
    print("\n🔍 Running detailed connection test...\n")
    
    if llm.test_connection(verbose=True):
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
        # Quick demo
        print("\n📝 Quick demo:")
        response = llm.generate("Say hello in one short sentence")
        print(f"Response: {response}")
        
    else:
        print("\n" + "="*60)
        print("❌ CONNECTION FAILED")
        print("="*60)
        print("\nTroubleshooting:")
        print("1. Check if Ollama is running:")
        print("   ollama serve")
        print("2. Check if model is installed:")
        print("   ollama list")
        print("3. Install model if needed:")
        print("   ollama pull qwen2.5:3b")
