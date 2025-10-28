"""Quick test to check if memory is working in API"""
import requests
import json
from pathlib import Path

print("="*70)
print("Quick Memory API Test")
print("="*70)

# Test 1: Send a message
print("\n[1] Sending test message...")
response = requests.post("http://localhost:8080/api/chat", 
                        json={"message": "Test memory - my name is Shay"})

if response.status_code == 200:
    result = response.json()
    print(f"   [OK] Response received (length: {len(result['response'])} chars)")
else:
    print(f"   [FAIL] Status: {response.status_code}")
    exit(1)

# Test 2: Check if it was saved
print("\n[2] Checking if saved to memory...")
from memory.short_term_memory import ShortTermMemory
memory = ShortTermMemory(Path("workspace/memory"))
stats = memory.get_statistics()
print(f"   [DATA] Total conversations: {stats['total_conversations']}")

# Get last conversation
if memory.conversations:
    last = memory.conversations[-1]
    user_msg = last['user_message']
    print(f"   [DATA] Last user message length: {len(user_msg)} chars")
    if "Shay" in user_msg or "Test memory" in user_msg:
        print("   [OK] Memory saved correctly!")
    else:
        print(f"   [WARN] Last message: '{user_msg[:30]}...'")
else:
    print("   [FAIL] No conversations found")

print("\n" + "="*70)
print("Test complete!")
print("="*70)

