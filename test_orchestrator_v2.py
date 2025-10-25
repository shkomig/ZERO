"""
Test Smart Orchestrator v2
===========================
Shows how the new orchestrator analyzes and executes tasks
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from simple_llm import SimpleLLM
from orchestrator_v2 import SmartOrchestrator


def test_smart_orchestrator():
    """
    Test the smart orchestrator with different types of tasks
    """
    print("\n" + "="*60)
    print("Zero Agent - Smart Orchestrator v2 Demo")
    print("="*60)
    
    # Setup
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    
    llm = SimpleLLM()
    tools = {}  # We'll add tools later
    
    orchestrator = SmartOrchestrator(llm, tools, workspace)
    
    # Test cases - from simple to complex
    test_tasks = [
        "What is 5 + 3?",
        "Explain what Python is",
        "Create a file called test.txt with 'Hello World'",
        "Search the web for Python tutorials and create a summary file"
    ]
    
    print("\n📋 Running tests with different complexity levels...\n")
    
    for i, task in enumerate(test_tasks, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}/{len(test_tasks)}")
        print(f"{'='*60}")
        
        result = orchestrator.execute(task)
        
        if result["success"]:
            print(f"\n✅ Task completed successfully!")
            print(f"\nComplexity: {result['analysis'].get('complexity', 'unknown')}")
            print(f"Steps executed: {len(result['plan'])}")
        else:
            print(f"\n❌ Task failed: {result.get('error', 'Unknown error')}")
        
        print(f"\n{'-'*60}\n")
    
    # Show history
    print("\n" + "="*60)
    print("📚 EXECUTION HISTORY")
    print("="*60)
    
    history = orchestrator.get_history()
    for i, entry in enumerate(history, 1):
        print(f"\n{i}. {entry['task']}")
        print(f"   Steps: {len(entry['plan'])}")
        print(f"   Time: {entry['timestamp']}")
    
    print("\n" + "="*60)
    print("✅ Demo complete!")
    print("="*60)


if __name__ == "__main__":
    test_smart_orchestrator()
