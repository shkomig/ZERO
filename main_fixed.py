"""
Zero Agent - Working Version (FIXED)
=====================================
Fixed to work with SimpleLLM that has .chat() method
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from simple_llm_fixed import SimpleLLM
from orchestrator_v2 import SmartOrchestrator


def main():
    """
    Main entry point for Zero Agent
    """
    print("\n" + "="*60)
    print("Zero Agent - Interactive Mode (FIXED)")
    print("="*60)
    
    # Setup
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    
    print(f"\nWorkspace: {workspace.absolute()}")
    print("Model: qwen2.5:3b")
    print("Ollama: http://localhost:11434")
    
    # Initialize LLM
    print("\n[INIT] Connecting to Ollama...")
    llm = SimpleLLM()
    
    if not llm.test_connection():
        print("[ERROR] Could not connect to Ollama!")
        print("Please make sure:")
        print("  1. Ollama is running (ollama serve)")
        print("  2. Model is installed (ollama pull qwen2.5:3b)")
        return
    
    print("[OK] Connected to Ollama")
    
    # Initialize orchestrator
    print("[INIT] Setting up orchestrator...")
    tools = {}  # Empty for now, we'll add tools later
    orchestrator = SmartOrchestrator(llm, tools, workspace)
    print("[OK] Orchestrator ready!")
    
    # Interactive loop
    print("\n" + "="*60)
    print("Ready! Type your tasks below.")
    print("Commands: 'history' - show history, 'exit' - quit")
    print("="*60 + "\n")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n[EXIT] Goodbye!")
                break
            
            if user_input.lower() == 'history':
                show_history(orchestrator)
                continue
            
            if user_input.lower() == 'clear':
                orchestrator.clear_history()
                print("[OK] History cleared")
                continue
            
            # Execute task
            print()  # New line for cleaner output
            result = orchestrator.execute(user_input)
            
            if result["success"]:
                print(f"\n✅ {result['result']}\n")
            else:
                print(f"\n❌ Error: {result.get('error', 'Unknown error')}\n")
            
        except KeyboardInterrupt:
            print("\n\n[EXIT] Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


def show_history(orchestrator):
    """
    Display execution history
    """
    history = orchestrator.get_history()
    
    if not history:
        print("\n[INFO] No history yet")
        return
    
    print("\n" + "="*60)
    print("📚 HISTORY")
    print("="*60)
    
    for i, entry in enumerate(history, 1):
        print(f"\n{i}. {entry['task']}")
        print(f"   Time: {entry['timestamp']}")
        print(f"   Steps: {len(entry['plan'])}")
        print(f"   Result: {str(entry['result'])[:80]}...")
    
    print("\n" + "="*60 + "\n")


def test_basic():
    """
    Quick test to verify everything works
    """
    print("\n" + "="*60)
    print("Zero Agent - Quick Test")
    print("="*60)
    
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    
    llm = SimpleLLM()
    
    if not llm.test_connection():
        print("❌ Ollama not connected")
        return False
    
    print("✓ LLM connected")
    
    tools = {}
    orchestrator = SmartOrchestrator(llm, tools, workspace)
    print("✓ Orchestrator ready")
    
    # Test simple task
    print("\nTesting: 'What is 2+2?'")
    result = orchestrator.execute("What is 2+2?")
    
    if result["success"]:
        print(f"✅ Success: {result['result'][:100]}")
        return True
    else:
        print(f"❌ Failed: {result.get('error')}")
        return False


if __name__ == "__main__":
    import sys
    
    # Check if running test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = test_basic()
        sys.exit(0 if success else 1)
    
    # Run interactive mode
    main()
