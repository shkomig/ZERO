#!/usr/bin/env python3
"""
Test Hebrew model fix
"""

import requests
import json

def test_hebrew_fix():
    """Test that Hebrew questions use mixtral:8x7b"""
    
    # Test Hebrew question
    hebrew_question = "שלום, איך אתה היום?"
    
    payload = {
        "message": hebrew_question,
        "conversation_history": []
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/api/chat", 
            json=payload, 
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        print(f"Hebrew question: {hebrew_question}")
        print(f"Model used: {result.get('model_used', 'unknown')}")
        print(f"Response: {result.get('response', 'no response')[:100]}...")
        print(f"Duration: {result.get('duration', 0):.2f}s")
        
        # Check if it's using the right model
        if result.get('model_used') == 'mixtral:8x7b':
            print("✅ SUCCESS: Hebrew is using mixtral:8x7b!")
        else:
            print(f"❌ FAILED: Hebrew is using {result.get('model_used')} instead of mixtral:8x7b")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_hebrew_fix()

