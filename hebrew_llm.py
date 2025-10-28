"""
Hebrew LLM Integration for Zero Agent
======================================
DictaLM 2.0 - State-of-the-art Hebrew Language Model
96%+ Hebrew accuracy, optimized for RTX5090
"""

import torch
from typing import Generator, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread
import time


class HebrewLLM:
    """
    Wrapper for DictaLM 2.0 Hebrew model
    Provides streaming generation compatible with Zero Agent
    """
    
    def __init__(self, model_path: str = "models/dictalm2.0", device: str = "auto"):
        """
        Initialize Hebrew LLM
        
        Args:
            model_path: Path to downloaded model
            device: "auto" for automatic, "cuda" for GPU, "cpu" for CPU
        """
        print(f"[HebrewLLM] Loading DictaLM 2.0 from {model_path}...")
        start_time = time.time()
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True
        )
        
        # Load model with optimizations for RTX5090
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map=device,
            torch_dtype=torch.float16,  # Use FP16 for faster inference
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        
        self.device = self.model.device
        load_time = time.time() - start_time
        
        print(f"[HebrewLLM] ✅ Model loaded in {load_time:.1f}s")
        print(f"[HebrewLLM] Device: {self.device}")
        print(f"[HebrewLLM] Model size: ~7B parameters")
        print(f"[HebrewLLM] Hebrew accuracy: 96%+")
    
    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """
        Generate response (non-streaming)
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generated text
        """
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                top_k=50,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the generated part (after the prompt)
        response = response[len(prompt):].strip()
        
        return response
    
    def generate_stream(self, prompt: str, max_tokens: int = 2048, 
                       temperature: float = 0.7) -> Generator[str, None, None]:
        """
        Generate response with streaming
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Yields:
            Generated text chunks
        """
        # Create streamer
        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )
        
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        # Generation kwargs
        generation_kwargs = {
            **inputs,
            "max_new_tokens": max_tokens,
            "temperature": temperature,
            "do_sample": True,
            "top_p": 0.9,
            "top_k": 50,
            "pad_token_id": self.tokenizer.eos_token_id,
            "streamer": streamer
        }
        
        # Start generation in separate thread
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        
        # Yield tokens as they're generated
        for text in streamer:
            yield text
        
        thread.join()
    
    def test_connection(self) -> bool:
        """Test if model is working"""
        try:
            test_prompt = "שאלה: מה זה Python?\nתשובה:"
            response = self.generate(test_prompt, max_tokens=50)
            return len(response) > 0
        except Exception as e:
            print(f"[HebrewLLM] ❌ Test failed: {e}")
            return False


class HebrewLLMFallback:
    """
    Fallback when Hebrew model is not available
    Uses Ollama with existing models
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        print("[HebrewLLM] Using Ollama fallback (deepseek-r1:32b)")
    
    def generate(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """Generate using Ollama"""
        import requests
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": "deepseek-r1:32b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        response = requests.post(url, json=payload, timeout=120)
        return response.json().get("response", "")
    
    def generate_stream(self, prompt: str, max_tokens: int = 2048, 
                       temperature: float = 0.7) -> Generator[str, None, None]:
        """Generate with streaming using Ollama"""
        import requests
        
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": "deepseek-r1:32b",
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        response = requests.post(url, json=payload, stream=True, timeout=120)
        
        for line in response.iter_lines():
            if line:
                import json
                chunk = json.loads(line)
                if "response" in chunk:
                    yield chunk["response"]
    
    def test_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


def get_hebrew_llm(model_path: str = "models/dictalm2.0", 
                   use_fallback: bool = False):
    """
    Factory function to get Hebrew LLM
    
    Args:
        model_path: Path to DictaLM model
        use_fallback: Force use of Ollama fallback
    
    Returns:
        HebrewLLM or HebrewLLMFallback instance
    """
    if use_fallback:
        print("[HebrewLLM] Using fallback mode (Ollama)")
        return HebrewLLMFallback()
    
    try:
        # Try to load DictaLM
        return HebrewLLM(model_path=model_path)
    except Exception as e:
        print(f"[HebrewLLM] ⚠️ Failed to load DictaLM: {e}")
        print("[HebrewLLM] Falling back to Ollama")
        return HebrewLLMFallback()


if __name__ == "__main__":
    # Test script
    print("="*60)
    print("Testing Hebrew LLM")
    print("="*60)
    
    llm = get_hebrew_llm()
    
    if llm.test_connection():
        print("\n✅ Connection successful!")
        
        # Test generation
        test_prompt = "שאלה: מה זה Python?\nתשובה:"
        print(f"\nPrompt: {test_prompt}")
        print("\nResponse:")
        
        for chunk in llm.generate_stream(test_prompt, max_tokens=100):
            print(chunk, end="", flush=True)
        
        print("\n\n" + "="*60)
        print("Test completed!")
    else:
        print("\n❌ Connection failed!")




