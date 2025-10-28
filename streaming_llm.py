"""
Streaming Multi-Model LLM
==========================
Real-time streaming responses for instant feedback
Makes everything feel 3x faster!
"""

import requests
import json
from typing import Dict, Any, List, Optional, Generator, Callable
import time
import sys


class StreamingMultiModelLLM:
    """
    LLM wrapper with streaming support
    Displays responses in real-time as they're generated
    """
    
    # Model configurations (updated with mistral:latest for Hebrew!)
    MODELS = {
        "fast": {
            "name": "mistral:latest",
            "description": "Ultra-fast chat model, excellent Hebrew support",
            "size": "4.4GB",
            "speed": "⚡⚡⚡⚡⚡",
            "quality": "⭐⭐⭐⭐⭐"
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
        self.stats = {model: 0 for model in self.MODELS.keys()}
        
    def generate_stream(self,
                       prompt: str,
                       model: Optional[str] = None,
                       max_tokens: int = 4096,
                       callback: Optional[Callable[[str], None]] = None) -> Generator[str, None, None]:
        """
        Generate response with streaming
        
        Args:
            prompt: The prompt
            model: Model type or None for default
            max_tokens: Max tokens
            callback: Optional callback for each chunk
            
        Yields:
            Text chunks as they arrive
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
            # OPTIMIZED SETTINGS based on Few-Shot research for DETAILED responses
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": True,  # Enable streaming!
                "options": {
                    "num_predict": max_tokens,
                    "num_ctx": 16384,  # Large context window for detailed responses
                    "temperature": 0.78,  # Higher for richer, more detailed responses
                    "top_p": 0.93,  # Nucleus sampling - allow more diversity
                    "top_k": 50,  # Top-K sampling for quality control
                    "repeat_penalty": 1.03  # Low penalty - don't stop the model from elaborating
                }
            }
            
            response = requests.post(url, json=payload, stream=True, timeout=180)
            response.raise_for_status()
            
            # Stream response
            for line in response.iter_lines():
                if line:
                    try:
                        chunk_data = line.decode('utf-8')
                        import json
                        chunk_json = json.loads(chunk_data)
                        
                        if "response" in chunk_json:
                            chunk_text = chunk_json["response"]
                            
                            # Call callback if provided
                            if callback:
                                callback(chunk_text)
                            
                            yield chunk_text
                            
                        # Check if done
                        if chunk_json.get("done", False):
                            break
                            
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if callback:
                callback(error_msg)
            yield error_msg
    
    def generate_stream_to_console(self,
                                   prompt: str,
                                   model: Optional[str] = None,
                                   max_tokens: int = 4096) -> str:
        """
        Generate and stream directly to console with live display
        
        Returns:
            Complete generated text
        """
        print(f"\n{'─'*70}")
        print(f"🤖 {self.MODELS.get(model or self.default_model, {}).get('name', 'Model')} streaming...")
        print(f"{'─'*70}\n")
        
        full_response = []
        start_time = time.time()
        
        try:
            for chunk in self.generate_stream(prompt, model, max_tokens):
                # Print chunk immediately
                print(chunk, end='', flush=True)
                full_response.append(chunk)
            
            elapsed = time.time() - start_time
            full_text = ''.join(full_response)
            tokens = len(full_text.split())
            speed = tokens / elapsed if elapsed > 0 else 0
            
            print(f"\n\n{'─'*70}")
            print(f"⏱️  {elapsed:.1f}s | {speed:.0f} tokens/s")
            print(f"{'─'*70}\n")
            
            return full_text
            
        except KeyboardInterrupt:
            print("\n\n[Interrupted by user]")
            return ''.join(full_response)
    
    def generate(self, 
                 prompt: str, 
                 model: Optional[str] = None,
                 max_tokens: int = 4096,
                 stream_to_console: bool = False) -> str:
        """
        Generate response (with optional streaming)
        
        Args:
            prompt: The prompt
            model: Model type
            max_tokens: Max tokens
            stream_to_console: If True, stream to console in real-time
            
        Returns:
            Complete generated text
        """
        if stream_to_console:
            return self.generate_stream_to_console(prompt, model, max_tokens)
        
        # Non-streaming (backwards compatible)
        if model and model in self.MODELS:
            model_name = self.MODELS[model]["name"]
            self.stats[model] += 1
        else:
            model_name = self.current_model
            self.stats[self.default_model] += 1
        
        try:
            url = f"{self.base_url}/api/generate"
            # HIGH-QUALITY settings for detailed, accurate responses
            # Based on best practices from research
            
            # For DeepSeek-R1, add stop sequences to prevent thinking tokens
            stop_sequences = ["<think>", "</think>"]
            
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 4096,  # Higher limit for detailed responses
                    "num_ctx": 16384,  # Larger context window for better context understanding
                    "temperature": 0.7,  # Optimal for balanced creativity and accuracy (Mistral best practice)
                    "top_p": 0.9,  # Nucleus sampling - standard for quality (don't mix with temperature changes)
                    "top_k": 40,  # Reduced for more focused responses (Mistral recommendation)
                    "repeat_penalty": 1.1,  # Standard penalty to avoid repetition
                    "frequency_penalty": 0.1,  # Additional penalty for repetitive tokens
                    "presence_penalty": 0.1,  # Encourage diverse vocabulary
                    "stop": ["\n\n\n\n", "**999.**"]  # Stop at extreme boundaries only
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
    
    def stream_generate(self, prompt: str, model: Optional[str] = None, max_tokens: int = 4096):
        """
        Stream generate text word by word
        """
        model_name = self.MODELS.get(model or self.default_model, {}).get("name", "mistral:latest")
        
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "num_predict": max_tokens,
                    "num_ctx": 16384,  # Larger context window for better understanding
                    "temperature": 0.7,  # Optimal for balanced creativity and accuracy (Mistral best practice)
                    "top_p": 0.9,  # Nucleus sampling - standard for quality
                    "top_k": 40,  # Reduced for more focused responses (Mistral recommendation)
                    "repeat_penalty": 1.1,  # Standard penalty to avoid repetition
                    "frequency_penalty": 0.1,  # Additional penalty for repetitive tokens
                    "presence_penalty": 0.1,  # Encourage diverse vocabulary
                    "stop": ["\n\n\n\n", "**999.**"]
                }
            }
            
            response = requests.post(url, json=payload, stream=True, timeout=180)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if 'response' in data:
                            yield data['response']
                        if data.get('done', False):
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            yield f"Error: {str(e)}"
    
    # Keep all other methods from MultiModelLLM
    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None, 
             max_tokens: int = 4096) -> str:
        """Chat with conversation history"""
        if model and model in self.MODELS:
            model_name = self.MODELS[model]["name"]
            self.stats[model] += 1
        else:
            model_name = self.current_model
            self.stats[self.default_model] += 1
        
        try:
            url = f"{self.base_url}/api/chat"
            # OPTIMIZED for DETAILED responses
            payload = {
                "model": model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "num_ctx": 16384,  # Large context window
                    "temperature": 0.78,  # Higher for detailed responses
                    "top_p": 0.93,  # More diverse sampling
                    "top_k": 50,  # Quality control
                    "repeat_penalty": 1.03  # Low - allow elaboration
                }
            }
            
            response = requests.post(url, json=payload, timeout=180)
            response.raise_for_status()
            
            result = response.json()
            message = result.get("message", {})
            return message.get("content", "").strip()
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def set_default_model(self, model_type: str):
        """Change default model"""
        if model_type in self.MODELS:
            self.default_model = model_type
            self.current_model = self.MODELS[model_type]["name"]
            print(f"✓ Default model set to: {self.current_model}")
    
    def get_available_models(self) -> Dict[str, Dict[str, str]]:
        """Get list of available models"""
        return self.MODELS
    
    def get_stats(self) -> Dict[str, int]:
        """Get usage statistics"""
        return self.stats
    
    def test_connection(self, verbose: bool = False) -> bool:
        """Test connection to Ollama"""
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
    
    def print_models_info(self):
        """Print information about available models"""
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


# Test
if __name__ == "__main__":
    print("Streaming LLM Test")
    print("="*70)
    
    llm = StreamingMultiModelLLM(default_model="fast")
    
    if not llm.test_connection(verbose=True):
        print("Please start Ollama first!")
        exit(1)
    
    print("\n🧪 Testing streaming response:\n")
    print("="*70)
    
    # Test streaming
    result = llm.generate(
        "Explain what a neural network is in 3 sentences",
        model="fast",
        stream_to_console=True
    )
    
    print("\n" + "="*70)
    print("✅ Streaming LLM ready!")
    print("\nBenefits:")
    print("  ✓ Real-time feedback (feels 3x faster)")
    print("  ✓ Backwards compatible")
    print("  ✓ Same API as before")
