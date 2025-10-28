"""
Test: Why is Zero not returning code?
"""
import requests
import json

print("=" * 70)
print("Testing Code Generation")
print("=" * 70)
print()

# Test with clear code request
messages = [
    "תן לי קוד Python למשחק פשוט",
    "כתוב לי קוד Python להדפסת Hello World",
    "תבנה לי פונקציה Python לחישוב סכום"
]

for i, message in enumerate(messages, 1):
    print(f"Test {i}: {message}")
    print("-" * 70)
    
    try:
        response = requests.post(
            "http://localhost:8080/api/chat",
            json={"message": message},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data['response']
            
            # Check if code was returned
            has_code_block = "```python" in response_text or "```" in response_text
            has_def = "def " in response_text
            has_imports = "import " in response_text
            
            print(f"[OK] Status: {response.status_code}")
            print(f"Response length: {len(response_text)} chars")
            print(f"Has code block (```): {has_code_block}")
            print(f"Has function (def): {has_def}")
            print(f"Has imports: {has_imports}")
            print()
            print("Response preview:")
            print(response_text[:300])
            print("..." if len(response_text) > 300 else "")
            
        else:
            print(f"[FAIL] Status: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"[ERROR] {e}")
    
    print()
    print()

print("=" * 70)
print("Test Complete")
print("=" * 70)




