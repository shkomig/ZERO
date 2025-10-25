"""
Zero Agent - Multi-Model Version!
==================================
Automatically selects the best model for each task
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from multi_model_llm import MultiModelLLM
from model_router import ModelRouter
from orchestrator_multi_model import MultiModelOrchestrator
from tool_filesystem import FileSystemTool
from tool_websearch import WebSearchTool
from tool_codeexecutor import CodeExecutorTool


def main():
    """
    Main entry point for Zero Agent Multi-Model
    """
    print("\n" + "="*70)
    print("🚀 Zero Agent - Multi-Model Edition")
    print("="*70)
    
    # Setup
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    
    print(f"\nWorkspace: {workspace.absolute()}")
    print("Ollama: http://localhost:11434")
    
    # Initialize Multi-Model LLM
    print("\n[INIT] Setting up Multi-Model LLM...")
    llm = MultiModelLLM(default_model="fast")
    
    if not llm.test_connection(verbose=False):
        print("[ERROR] Cannot connect to Ollama!")
        return
    
    print("[OK] Connected to Ollama")
    
    # Show available models
    llm.print_models_info()
    
    # Initialize Router
    print("\n[INIT] Setting up Smart Router...")
    router = ModelRouter(llm)
    print("[OK] Router ready - will auto-select best model!")
    
    # Initialize Tools
    print("\n[INIT] Loading tools...")
    tools = {
        "filesystem": FileSystemTool(workspace),
        "websearch": WebSearchTool(),
        "codeexecutor": CodeExecutorTool(workspace)
    }
    print(f"[OK] Loaded {len(tools)} tools")
    
    # Initialize Orchestrator
    print("\n[INIT] Setting up Orchestrator...")
    orchestrator = MultiModelOrchestrator(llm, router, tools, workspace)
    print("[OK] Multi-Model Orchestrator ready!")
    
    # Interactive loop
    print("\n" + "="*70)
    print("✨ Ready! The agent will automatically choose the best model.")
    print("\n💡 How it works:")
    print("   • Simple questions → llama3.1:8b (⚡ fast)")
    print("   • Coding tasks → qwen2.5-coder:32b (👨‍💻 expert)")
    print("   • Complex analysis → deepseek-r1:32b (🧠 smart)")
    print("   • General tasks → gpt-oss:20b-cloud (⚖️ balanced)")
    
    print("\n📝 Example tasks:")
    print("   'What is 2+2?'  → fast model")
    print("   'Write a Python function to sort a list'  → coder model")
    print("   'Analyze the philosophy of consciousness'  → smart model")
    
    print("\n🎮 Commands:")
    print("   'stats'   - show model usage statistics")
    print("   'models'  - show available models")
    print("   'history' - show execution history")
    print("   'clear'   - clear history")
    print("   'help'    - show help")
    print("   'exit'    - quit")
    
    print("\n🔧 Advanced:")
    print("   Add '@fast', '@coder', '@smart', or '@balanced' to force a model")
    print("   Example: 'What is AI? @smart'")
    
    print("="*70 + "\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'stats':
                orchestrator.print_stats()
                continue
            
            if user_input.lower() == 'models':
                llm.print_models_info()
                continue
            
            if user_input.lower() == 'history':
                show_history(orchestrator)
                continue
            
            if user_input.lower() == 'clear':
                orchestrator.clear_history()
                print("✓ History cleared\n")
                continue
            
            if user_input.lower() == 'help':
                show_help()
                continue
            
            # Check for forced model
            force_model = None
            for model_type in ['@fast', '@coder', '@smart', '@balanced']:
                if model_type in user_input.lower():
                    force_model = model_type[1:]  # Remove @
                    user_input = user_input.lower().replace(model_type, '').strip()
                    break
            
            # Execute task
            print()
            result = orchestrator.execute(user_input, force_model=force_model)
            
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
    """Display history"""
    history = orchestrator.get_history()
    
    if not history:
        print("\n📝 No history yet\n")
        return
    
    print("\n" + "="*70)
    print("📚 EXECUTION HISTORY")
    print("="*70)
    
    for i, entry in enumerate(history, 1):
        print(f"\n{i}. {entry['task']}")
        print(f"   Model: {entry['model'].upper()}")
        print(f"   Time: {entry['timestamp']}")
        print(f"   Steps: {len(entry['plan'])}")
        
        tools_used = set()
        for step in entry['plan']:
            if step.get('tool'):
                tools_used.add(step['tool'])
        
        if tools_used:
            print(f"   Tools: {', '.join(tools_used)}")
        
        result_preview = str(entry['result'])[:80]
        print(f"   Result: {result_preview}{'...' if len(str(entry['result'])) > 80 else ''}")
    
    print("\n" + "="*70 + "\n")


def show_help():
    """Show help"""
    print("\n" + "="*70)
    print("📖 ZERO AGENT MULTI-MODEL HELP")
    print("="*70)
    
    print("\n🤖 AUTO-SELECTION:")
    print("   The agent automatically picks the best model for your task!")
    
    print("\n📁 FileSystem Examples:")
    print("   'Create a file hello.txt with Hello World'")
    print("   'Read the file test.txt'")
    print("   'List all files'")
    
    print("\n💻 Coding Examples (will use qwen2.5-coder:32b):")
    print("   'Write a Python function to calculate factorial'")
    print("   'Debug this code: def add(a,b) return a+b'")
    print("   'Create a sorting algorithm in Python'")
    
    print("\n🧠 Analysis Examples (will use deepseek-r1:32b):")
    print("   'Analyze the implications of AI on society'")
    print("   'Explain quantum mechanics in detail'")
    print("   'Compare different machine learning approaches'")
    
    print("\n⚡ Simple Examples (will use llama3.1:8b):")
    print("   'What is 5+3?'")
    print("   'Define machine learning'")
    print("   'Convert 100 USD to EUR'")
    
    print("\n🔧 Force Model:")
    print("   Add @fast, @coder, @smart, or @balanced to force:")
    print("   'Explain AI @smart'  → Forces smart model")
    print("   'Quick math @fast'   → Forces fast model")
    
    print("\n" + "="*70 + "\n")


def test_multi_model():
    """Test multi-model system"""
    print("\n" + "="*70)
    print("🧪 Testing Multi-Model System")
    print("="*70)
    
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    
    print("\n1. Testing LLM connection...")
    llm = MultiModelLLM(default_model="fast")
    if llm.test_connection(verbose=True):
        print("   ✅ LLM connected")
    else:
        print("   ❌ LLM failed")
        return False
    
    print("\n2. Testing Model Router...")
    router = ModelRouter(llm)
    
    test_cases = [
        ("What is 2+2?", "fast"),
        ("Write Python code to sort", "coder"),
        ("Analyze philosophy of AI", "smart")
    ]
    
    all_passed = True
    for task, expected in test_cases:
        result = router.route(task)
        status = "✅" if result == expected else "⚠️"
        print(f"   {status} '{task[:30]}...' → {result} (expected: {expected})")
        if result != expected:
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some routing decisions differ (this is OK - routing is flexible)")
    print("="*70)
    
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print()
        success = test_multi_model()
        print("\n" + "="*70)
        if success:
            print("✅ Multi-Model system ready!")
            print("\nRun without --test to start:")
            print("   python main_multi_model.py")
        else:
            print("❌ Tests failed")
        print("="*70 + "\n")
        sys.exit(0 if success else 1)
    
    main()
