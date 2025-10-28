#!/usr/bin/env python3
"""
Quick test: Mistral Hebrew quality
"""
import requests
import json

def test_mistral():
    url = "http://localhost:11434/api/generate"
    
    test_questions = [
        "מה זה Python?",
        "What is AI?",
        "ספר לי על בינה מלאכותית"
    ]
    
    print("="*60)
    print("Testing Mistral - Hebrew Quality")
    print("="*60)
    print()
    
    for i, question in enumerate(test_questions, 1):
        print(f"Test {i}: {question}")
        print("-"*60)
        
        payload = {
            "model": "mistral",
            "prompt": f"{question}\n\nענה בעברית בלבד:",
            "stream": False,
            "options": {
                "num_predict": 150,
                "temperature": 0.7
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            result = response.json()
            answer = result.get("response", "")
            
            # Count Hebrew vs other
            hebrew_count = sum(1 for c in answer if '\u0590' <= c <= '\u05FF')
            total_alpha = sum(1 for c in answer if c.isalpha())
            hebrew_pct = (hebrew_count / total_alpha * 100) if total_alpha > 0 else 0
            
            print(f"Answer: {answer[:200]}")
            print(f"Hebrew: {hebrew_pct:.1f}%")
            print()
            
        except Exception as e:
            print(f"Error: {e}")
            print()
    
    print("="*60)

if __name__ == "__main__":
    test_mistral()




