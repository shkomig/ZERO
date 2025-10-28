"""
Comprehensive Zero Agent Test Suite
====================================
Tests all components: Hebrew quality, Memory, Context, and Integration
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8080"

class TestResults:
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
    
    def add(self, name, passed, details=""):
        self.tests.append({
            "name": name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"Total tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success rate: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        
        if self.failed > 0:
            print("\nFailed tests:")
            for test in self.tests:
                if not test["passed"]:
                    print(f"  - {test['name']}: {test['details']}")

results = TestResults()

def check_hebrew_ratio(text):
    """Check percentage of Hebrew characters in text"""
    hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05FF')
    total_chars = len([c for c in text if c.isalpha()])
    return (hebrew_chars / total_chars * 100) if total_chars > 0 else 0

def test_health():
    """Test 1: Server Health"""
    print("\n[Test 1] Server Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("OK - Server is running")
            results.add("Server Health", True)
            return True
        else:
            print(f"FAIL - Status: {response.status_code}")
            results.add("Server Health", False, f"Status {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL - {str(e)}")
        results.add("Server Health", False, str(e))
        return False

def test_simple_chat():
    """Test 2: Simple Chat - Hebrew Quality"""
    print("\n[Test 2] Simple Chat - Hebrew Quality")
    
    test_questions = [
        ("5+5", "10"),
        ("What is Python?", None),  # Should answer in Hebrew!
        ("Tell me about AI", None),  # Should answer in Hebrew!
    ]
    
    for question, expected in test_questions:
        try:
            print(f"\n  Question: {question}")
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": question},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "")
                hebrew_ratio = check_hebrew_ratio(answer)
                
                print(f"  Answer: {answer[:100]}...")
                print(f"  Hebrew: {hebrew_ratio:.1f}%")
                
                if hebrew_ratio > 70:  # At least 70% Hebrew
                    print("  OK - Good Hebrew quality")
                    results.add(f"Hebrew Quality: {question}", True)
                else:
                    print(f"  FAIL - Low Hebrew ratio: {hebrew_ratio:.1f}%")
                    results.add(f"Hebrew Quality: {question}", False, f"Only {hebrew_ratio:.1f}% Hebrew")
            else:
                print(f"  FAIL - Status: {response.status_code}")
                results.add(f"Chat: {question}", False, f"Status {response.status_code}")
                
        except Exception as e:
            print(f"  FAIL - {str(e)}")
            results.add(f"Chat: {question}", False, str(e))
        
        time.sleep(2)

def test_memory():
    """Test 3: Memory System"""
    print("\n[Test 3] Memory System")
    
    # Step 1: Tell Zero something
    print("\n  Step 1: Sharing info...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": "My name is Shay and I love Python programming"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("response", "")
            print(f"  Answer: {answer[:100]}...")
            
            # Step 2: Ask Zero to recall
            print("\n  Step 2: Testing recall...")
            time.sleep(2)
            
            response2 = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": "What is my name?"},
                timeout=30
            )
            
            if response2.status_code == 200:
                data2 = response2.json()
                answer2 = data2.get("response", "")
                print(f"  Answer: {answer2[:100]}...")
                
                if "Shay" in answer2 or "shay" in answer2.lower():
                    print("  OK - Zero remembered!")
                    results.add("Memory - Name Recall", True)
                else:
                    print("  FAIL - Zero didn't remember the name")
                    results.add("Memory - Name Recall", False, "Name not recalled")
            else:
                print(f"  FAIL - Status: {response2.status_code}")
                results.add("Memory - Recall", False, f"Status {response2.status_code}")
        else:
            print(f"  FAIL - Status: {response.status_code}")
            results.add("Memory - Save", False, f"Status {response.status_code}")
            
    except Exception as e:
        print(f"  FAIL - {str(e)}")
        results.add("Memory Test", False, str(e))

def test_conversation_history():
    """Test 4: Conversation History / Context"""
    print("\n[Test 4] Conversation History")
    
    conversation = []
    
    try:
        # Message 1
        print("\n  Message 1: Asking about Python...")
        response1 = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "message": "What is Python?",
                "conversation_history": conversation
            },
            timeout=30
        )
        
        if response1.status_code == 200:
            data1 = response1.json()
            answer1 = data1.get("response", "")
            
            conversation.append({"role": "user", "content": "What is Python?"})
            conversation.append({"role": "assistant", "content": answer1})
            
            # Message 2 - follow-up
            print("\n  Message 2: Follow-up question...")
            time.sleep(2)
            
            response2 = requests.post(
                f"{BASE_URL}/api/chat",
                json={
                    "message": "Can you teach me?",  # Should understand context
                    "conversation_history": conversation
                },
                timeout=30
            )
            
            if response2.status_code == 200:
                data2 = response2.json()
                answer2 = data2.get("response", "")
                print(f"  Answer: {answer2[:150]}...")
                
                # Check if answer is about Python/programming
                if any(word in answer2.lower() for word in ["python", "code", "program"]):
                    print("  OK - Context understood")
                    results.add("Context - Follow-up", True)
                else:
                    print("  FAIL - Context not understood")
                    results.add("Context - Follow-up", False, "Context lost")
            else:
                print(f"  FAIL - Status: {response2.status_code}")
                results.add("Context Test", False, f"Status {response2.status_code}")
        else:
            print(f"  FAIL - Status: {response1.status_code}")
            results.add("Context - Initial", False, f"Status {response1.status_code}")
            
    except Exception as e:
        print(f"  FAIL - {str(e)}")
        results.add("Context Test", False, str(e))

def test_memory_dashboard():
    """Test 5: Memory Dashboard"""
    print("\n[Test 5] Memory Dashboard")
    try:
        response = requests.get(f"{BASE_URL}/memory-dashboard", timeout=10)
        if response.status_code == 200 and "html" in response.headers.get("content-type", "").lower():
            print("  OK - Dashboard accessible")
            results.add("Memory Dashboard", True)
        else:
            print(f"  FAIL - Status: {response.status_code}")
            results.add("Memory Dashboard", False, f"Status {response.status_code}")
    except Exception as e:
        print(f"  FAIL - {str(e)}")
        results.add("Memory Dashboard", False, str(e))

def main():
    print("="*70)
    print("ZERO AGENT - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    if test_health():
        test_simple_chat()
        test_memory()
        test_conversation_history()
        test_memory_dashboard()
    else:
        print("\nSERVER NOT RUNNING - Skipping remaining tests")
        print("Please start the server with: python api_server.py")
    
    # Print summary
    results.print_summary()
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "total": results.passed + results.failed,
            "passed": results.passed,
            "failed": results.failed,
            "tests": results.tests
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {filename}")
    print("\nEND OF TESTS")

if __name__ == "__main__":
    main()

