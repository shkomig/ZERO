"""
Test Improvements - Structure + Code Detection
"""
import requests
import json

print("=" * 70)
print("Testing Improvements - Step by Step")
print("=" * 70)
print()

tests = [
    {
        "name": "Test 1: Code Request - 'תן לי קוד'",
        "message": "תן לי קוד Python למשחק פשוט",
        "expect_code": True
    },
    {
        "name": "Test 2: Structured Explanation",
        "message": "מה זה Docker?",
        "expect_structure": True
    },
    {
        "name": "Test 3: Simple Math",
        "message": "כמה זה 7+3?",
        "expect_short": True
    }
]

for i, test in enumerate(tests, 1):
    print(f"\n{test['name']}")
    print("-" * 70)
    print(f"Message: {test['message']}")
    print()
    
    try:
        response = requests.post(
            "http://localhost:8080/api/chat",
            json={"message": test["message"]},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            text = data['response']
            
            print(f"[OK] Status: 200")
            print(f"Length: {len(text)} chars")
            
            # Check expectations
            if test.get('expect_code'):
                has_code = "```" in text or "def " in text
                print(f"Has code: {'YES' if has_code else 'NO'}")
                if has_code:
                    print("[PASS] Code detected!")
                else:
                    print("[FAIL] No code found")
            
            if test.get('expect_structure'):
                has_headers = "**" in text
                has_lists = any(x in text for x in ["1.", "2.", "•", "-"])
                print(f"Has headers: {'YES' if has_headers else 'NO'}")
                print(f"Has lists: {'YES' if has_lists else 'NO'}")
                if has_headers or has_lists:
                    print("[PASS] Structure detected!")
                else:
                    print("[INFO] No structure markers")
            
            if test.get('expect_short'):
                if len(text) < 50:
                    print("[PASS] Short answer (as expected)")
                else:
                    print(f"[INFO] Answer is {len(text)} chars")
            
            print()
            print("Response preview (first 400 chars):")
            print(text[:400])
            if len(text) > 400:
                print("...")
        
        else:
            print(f"[FAIL] Status: {response.status_code}")
            print(response.text[:200])
    
    except Exception as e:
        print(f"[ERROR] {e}")
    
    print()

print("=" * 70)
print("Test Complete!")
print("=" * 70)




