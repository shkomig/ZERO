"""
Zero Agent - Ready to Run!
===========================
Configured for llama3.1:8b (your installed model)
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from simple_llm_improved import SimpleLLM
from orchestrator_fixed import SmartOrchestrator


def main():
    """
    Main entry point for Zero Agent
    """
    print("\n" + "="*60)
    print("🚀 Zero Agent - Interactive Mode")
    print("="*60)
    
    # Setup
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    
    MODEL = "llama3.1:8b"  # Your installed model
    
    print(f"\nWorkspace: {workspace.absolute()}")
    print(f"Model: {MODEL}")
    print(f"Ollama: http://localhost:11434")
    
    # Initialize LLM
    print("\n[INIT] Connecting to Ollama...")
    llm = SimpleLLM(model=MODEL)
    
    if not llm.test_connection(verbose=False):
        print("[ERROR] Could not connect!")
        print("\nDebug info:")
        llm.test_connection(verbose=True)
        return
    
    print("[OK] Connected to Ollama")
    
    # Initialize orchestrator
    print("[INIT] Setting up orchestrator...")
    tools = {}
    orchestrator = SmartOrchestrator(llm, tools, workspace)
    print("[OK] Orchestrator ready!")
    
    # Interactive loop
    print("\n" + "="*60)
    print("✨ Ready! Type your tasks below.")
    print("Commands:")
    print("  'history' - show execution history")
    print("  'clear'   - clear history")
    print("  'exit'    - quit")
    print("="*60 + "\n")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'history':
                show_history(orchestrator)
                continue
            
            if user_input.lower() == 'clear':
                orchestrator.clear_history()
                print("✓ History cleared\n")
                continue
            
            # Execute task
            print()
            result = orchestrator.execute(user_input)
            
            if result["success"]:
                print(f"\n✅ {result['result']}\n")
            else:
                print(f"\n❌ Error: {result.get('error', 'Unknown error')}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


def show_history(orchestrator):
    """Display execution history"""
    history = orchestrator.get_history()
    
    if not history:
        print("\n📝 No history yet\n")
        return
    
    print("\n" + "="*60)
    print("📚 EXECUTION HISTORY")
    print("="*60)
    
    for i, entry in enumerate(history, 1):
        print(f"\n{i}. {entry['task']}")
        print(f"   Time: {entry['timestamp']}")
        print(f"   Steps: {len(entry['plan'])}")
        result_preview = str(entry['result'])[:80]
        print(f"   Result: {result_preview}{'...' if len(str(entry['result'])) > 80 else ''}")
    
    print("\n" + "="*60 + "\n")


def test_quick():
    """Quick test to verify everything works"""
    print("\n" + "="*60)
    print("🧪 Zero Agent - Quick Test")
    print("="*60)
    
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    
    MODEL = "llama3.1:8b"
    
    print(f"\nModel: {MODEL}")
    print("Testing connection...")
    
    llm = SimpleLLM(model=MODEL)
    
    if not llm.test_connection(verbose=True):
        print("\n❌ Test failed - check connection")
        return False
    
    print("\n" + "-"*60)
    print("Setting up orchestrator...")
    
    tools = {}
    orchestrator = SmartOrchestrator(llm, tools, workspace)
    
    print("✓ Orchestrator ready")
    
    # Test simple task
    print("\n" + "-"*60)
    print("Testing with: 'What is 2+2?'")
    print("-"*60)
    
    result = orchestrator.execute("What is 2+2?")
    
    if result["success"]:
        print(f"\n✅ SUCCESS!")
        print(f"Result: {result['result'][:200]}")
        return True
    else:
        print(f"\n❌ FAILED: {result.get('error')}")
        return False


if __name__ == "__main__":
    import sys
    
    # Check if running test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print()
        success = test_quick()
        print("\n" + "="*60)
        if success:
            print("✅ All systems ready! Run without --test to start")
        else:
            print("❌ Test failed - check the errors above")
        print("="*60 + "\n")
        sys.exit(0 if success else 1)
    
    # Run interactive mode
    main()
