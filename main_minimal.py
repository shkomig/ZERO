"""
Minimal working version of Zero Agent
Test basic functionality only
"""

import asyncio
from pathlib import Path

print("Zero Agent - Minimal Test")
print("="*50)

# Test 1: Basic imports
print("\n1. Testing imports...")
try:
    from langchain_anthropic import ChatAnthropic
    print("   [OK] LangChain imports OK")
except Exception as e:
    print(f"   [FAIL] LangChain import failed: {e}")
    exit(1)

try:
    import ollama
    print("   [OK] Ollama import OK")
except Exception as e:
    print(f"   [FAIL] Ollama import failed: {e}")
    exit(1)

# Test 2: Ollama connection
print("\n2. Testing Ollama connection...")
try:
    client = ollama.Client()
    models = client.list()
    print(f"   [OK] Ollama connected. Models: {len(models.get('models', []))}")
except Exception as e:
    print(f"   [FAIL] Ollama connection failed: {e}")
    print("   [TIP] Start Ollama: 'ollama serve'")
    exit(1)

# Test 3: Simple model call
print("\n3. Testing model call...")
try:
    response = client.chat(
        model='gpt-oss:20b-cloud',
        messages=[{'role': 'user', 'content': 'Say "OK" only'}]
    )
    result = response['message']['content']
    print(f"   [OK] Model responded: {result[:50]}")
except Exception as e:
    print(f"   [FAIL] Model call failed: {e}")
    print("   [TIP] Pull model: 'ollama pull llama3.1:8b'")

# Test 4: File system
print("\n4. Testing file system...")
try:
    workspace = Path("./workspace")
    workspace.mkdir(exist_ok=True)
    test_file = workspace / "test.txt"
    test_file.write_text("test")
    assert test_file.read_text() == "test"
    test_file.unlink()
    print("   [OK] File system OK")
except Exception as e:
    print(f"   [FAIL] File system failed: {e}")

print("\n" + "="*50)
print("[OK] Minimal test complete!")
print("\nIf all tests passed, we can proceed to full system.")






