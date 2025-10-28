"""
Final Test: "תבנה לי אפליקציה"
This tests the entire Smart Agent system
"""
import requests
import json

print("=" * 70)
print("FINAL TEST: Build Me an Application")
print("=" * 70)
print()

# Test 1: Simple app request
message1 = "תבנה לי אפליקציית Flask פשוטה עם 3 routes"
print(f"Test 1: {message1}")
print("-" * 70)

try:
    response = requests.post(
        "http://localhost:8080/api/chat",
        json={"message": message1},
        timeout=120
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Status: {response.status_code}")
        print(f"[OK] Response length: {len(data['response'])} chars")
        
        # Check if code was generated
        if "```python" in data['response'] or "def " in data['response']:
            print("[OK] Code detected in response")
        else:
            print("[WARN] No code detected")
        
        print()
        print("Response Preview:")
        print(data['response'][:500])
        print("..." if len(data['response']) > 500 else "")
    else:
        print(f"[FAIL] Status: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"[ERROR] {e}")

print()
print("=" * 70)
print("Test Complete!")
print("=" * 70)




