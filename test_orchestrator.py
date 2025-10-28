import requests
import sys
import io

# Fix encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def ask_zero(question):
    """שאל את Zero משהו"""
    response = requests.post('http://localhost:8080/api/chat', 
        json={"message": question, "use_memory": True}
    )
    result = response.json()
    print(f"Response: {result['response'][:200]}")
    return result

# Test orchestrator with create project
print("Testing: צור פרויקט Python חדש בשם myapp")
result = ask_zero("צור פרויקט Python חדש בשם myapp")
print(f"\nModel used: {result.get('model_used', 'N/A')}")
print(f"Success: {result.get('response', 'N/A')[:500]}")










