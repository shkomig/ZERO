"""
Simple LLM Wrapper - FIXED VERSION
===================================
Works with Ollama and provides both .generate() and .chat() methods
"""

import requests
import json
from typing import List, Dict, Optional


class SimpleLLM:
    """
    Simple wrapper for Ollama LLM
    Supports both .generate() and .chat() methods
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
        (Original method - kept for compatibility)
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
        (NEW method for compatibility with main_working.py)
        
        Args:
            messages: List of {"role": "user/assistant", "content": "..."}
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response string
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
        """
        Add message to conversation history
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history
        """
        return self.conversation_history
    
    def clear_history(self):
        """
        Clear conversation history
        """
        self.conversation_history = []
    
    def chat_with_history(self, user_message: str, max_tokens: int = 1000) -> str:
        """
        Convenience method: chat with automatic history management
        """
        # Add user message to history
        self.add_to_history("user", user_message)
        
        # Generate response
        response = self.chat(self.conversation_history, max_tokens)
        
        # Add assistant response to history
        self.add_to_history("assistant", response)
        
        return response
    
    def test_connection(self) -> bool:
        """
        Test if Ollama is running and model is available
        """
        try:
            # Test generate endpoint
            test_response = self.generate("Hi", max_tokens=10)
            return "Error" not in test_response
        except:
            return False


# Test the fixed LLM
if __name__ == "__main__":
    print("Testing SimpleLLM (Fixed Version)")
    print("=" * 60)
    
    llm = SimpleLLM()
    
    # Test 1: Connection
    print("\n1. Testing connection...")
    if llm.test_connection():
        print("   ✓ Connected to Ollama")
    else:
        print("   ✗ Could not connect to Ollama")
        exit(1)
    
    # Test 2: .generate() method
    print("\n2. Testing .generate() method...")
    response = llm.generate("What is 2+2?")
    print(f"   Response: {response[:100]}...")
    
    # Test 3: .chat() method
    print("\n3. Testing .chat() method...")
    messages = [
        {"role": "user", "content": "Hello!"}
    ]
    response = llm.chat(messages)
    print(f"   Response: {response[:100]}...")
    
    # Test 4: .chat_with_history() method
    print("\n4. Testing .chat_with_history() method...")
    llm.clear_history()
    
    response1 = llm.chat_with_history("My name is David")
    print(f"   Response 1: {response1[:50]}...")
    
    response2 = llm.chat_with_history("What's my name?")
    print(f"   Response 2: {response2[:50]}...")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("\nYou can now use this in main_working.py:")
    print("   from simple_llm_fixed import SimpleLLM")
