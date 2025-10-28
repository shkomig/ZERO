"""
Test Hebrew Quality for Different Models
=========================================
Tests multiple Ollama models to find the best one for Hebrew responses
"""

import requests
import json
import time
from datetime import datetime

# Test questions in Hebrew
TEST_QUESTIONS = [
    "מה זה Python?",
    "5+5 זה כמה?",
    "תסביר לי על בינה מלאכותית",
    "מה ההבדל בין C++ ל-Python?",
]

# Models to test
MODELS = [
    "qwen2.5:3b",
    "llama3.1:8b",
    "deepseek-r1:32b",
    "qwen2.5-coder:32b",
]

def test_model(model_name, question):
    """Test a single model with a question"""
    try:
        print(f"\n[Testing {model_name}]")
        print(f"Question: {question}")
        
        start_time = time.time()
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": f"You are an AI assistant. Answer ONLY in Hebrew. No other languages allowed.\n\nQuestion: {question}\n\nAnswer in Hebrew:",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                }
            },
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "").strip()
            
            # Check if answer contains Hebrew
            hebrew_chars = sum(1 for c in answer if '\u0590' <= c <= '\u05FF')
            total_chars = len([c for c in answer if c.isalpha()])
            hebrew_ratio = (hebrew_chars / total_chars * 100) if total_chars > 0 else 0
            
            print(f"Answer: {answer[:150]}...")
            print(f"Response time: {elapsed:.2f}s")
            print(f"Hebrew ratio: {hebrew_ratio:.1f}%")
            
            return {
                "model": model_name,
                "question": question,
                "answer": answer,
                "time": elapsed,
                "hebrew_ratio": hebrew_ratio,
                "success": True
            }
        else:
            print(f"ERROR: {response.status_code}")
            return {
                "model": model_name,
                "question": question,
                "error": response.status_code,
                "success": False
            }
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            "model": model_name,
            "question": question,
            "error": str(e),
            "success": False
        }

def main():
    print("="*70)
    print("בדיקת איכות עברית - מודלים שונים")
    print("="*70)
    
    results = []
    
    # Test each model with each question
    for model in MODELS:
        print(f"\n{'='*70}")
        print(f"Testing Model: {model}")
        print(f"{'='*70}")
        
        model_results = []
        for question in TEST_QUESTIONS:
            result = test_model(model, question)
            model_results.append(result)
            time.sleep(1)  # Small delay between requests
        
        # Calculate average for this model
        successful = [r for r in model_results if r.get("success")]
        if successful:
            avg_time = sum(r["time"] for r in successful) / len(successful)
            avg_hebrew = sum(r["hebrew_ratio"] for r in successful) / len(successful)
            
            print(f"\n[{model} Summary]")
            print(f"  Average time: {avg_time:.2f}s")
            print(f"  Average Hebrew: {avg_hebrew:.1f}%")
            print(f"  Success rate: {len(successful)}/{len(TEST_QUESTIONS)}")
            
            results.append({
                "model": model,
                "avg_time": avg_time,
                "avg_hebrew": avg_hebrew,
                "success_rate": len(successful) / len(TEST_QUESTIONS),
                "tests": model_results
            })
    
    # Final summary
    print("\n" + "="*70)
    print("סיכום סופי - המלצות")
    print("="*70)
    
    # Sort by Hebrew quality
    results.sort(key=lambda x: x["avg_hebrew"], reverse=True)
    
    print("\nדירוג לפי איכות עברית:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['model']:25} - עברית: {result['avg_hebrew']:.1f}%, זמן: {result['avg_time']:.2f}s")
    
    # Best recommendation
    if results:
        best = results[0]
        print(f"\n[המלצה] המודל הטוב ביותר: {best['model']}")
        print(f"  - {best['avg_hebrew']:.1f}% תשובות בעברית")
        print(f"  - {best['avg_time']:.2f} שניות זמן תגובה ממוצע")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hebrew_quality_test_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nתוצאות נשמרו ב: {filename}")

if __name__ == "__main__":
    main()

