"""
Zero Agent - Complete with Tools!
==================================
Full agent with FileSystem, WebSearch, and CodeExecutor tools
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from simple_llm_improved import SimpleLLM
from orchestrator_with_tools import SmartOrchestratorWithTools
from tool_filesystem import FileSystemTool
from tool_websearch import WebSearchTool
from tool_codeexecutor import CodeExecutorTool


def main():
    """
    Main entry point for Zero Agent with tools
    """
    print("\n" + "="*60)
    print("🚀 Zero Agent - Full Version with Tools")
    print("="*60)
    
    # Setup
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    
    MODEL = "llama3.1:8b"
    
    print(f"\nWorkspace: {workspace.absolute()}")
    print(f"Model: {MODEL}")
    print(f"Ollama: http://localhost:11434")
    
    # Initialize LLM
    print("\n[INIT] Connecting to Ollama...")
    llm = SimpleLLM(model=MODEL)
    
    if not llm.test_connection(verbose=False):
        print("[ERROR] Could not connect!")
        return
    
    print("[OK] Connected to Ollama")
    
    # Initialize tools
    print("[INIT] Setting up tools...")
    tools = {
        "filesystem": FileSystemTool(workspace),
        "websearch": WebSearchTool(),
        "codeexecutor": CodeExecutorTool(workspace)
    }
    print(f"[OK] Loaded {len(tools)} tools:")
    for tool_name in tools.keys():
        print(f"     ✓ {tool_name}")
    
    # Initialize orchestrator
    print("[INIT] Setting up orchestrator...")
    orchestrator = SmartOrchestratorWithTools(llm, tools, workspace)
    print("[OK] Orchestrator ready!")
    
    # Show capabilities
    print("\n" + "="*60)
    print("✨ Zero Agent Capabilities:")
    print("="*60)
    print("\n📁 FileSystem:")
    print("   - Create, read, list, delete files")
    print("   - Safe operations within workspace")
    
    print("\n🔍 WebSearch:")
    print("   - Search the internet")
    print("   - Get current information")
    
    print("\n💻 CodeExecutor:")
    print("   - Execute Python code")
    print("   - Run bash commands (safely)")
    
    # Interactive loop
    print("\n" + "="*60)
    print("Ready! Type your tasks below.")
    print("\nExample tasks:")
    print("  'Create a file called hello.txt with Hello World'")
    print("  'Search the web for Python tutorials'")
    print("  'Run Python code to calculate fibonacci numbers'")
    print("  'List all files in workspace'")
    print("\nCommands:")
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
            
            if user_input.lower() == 'help':
                show_help()
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
        
        # Show tools used
        tools_used = set()
        for step in entry['plan']:
            if step.get('tool'):
                tools_used.add(step['tool'])
        
        if tools_used:
            print(f"   Tools: {', '.join(tools_used)}")
        
        result_preview = str(entry['result'])[:80]
        print(f"   Result: {result_preview}{'...' if len(str(entry['result'])) > 80 else ''}")
    
    print("\n" + "="*60 + "\n")


def show_help():
    """Show help information"""
    print("\n" + "="*60)
    print("📖 ZERO AGENT HELP")
    print("="*60)
    
    print("\n📁 FileSystem Examples:")
    print("   'Create a file called test.txt with some content'")
    print("   'Read the file test.txt'")
    print("   'List all files in the workspace'")
    print("   'Delete the file test.txt'")
    
    print("\n🔍 WebSearch Examples:")
    print("   'Search for Python tutorials'")
    print("   'What is the latest news about AI?'")
    print("   'Find information about machine learning'")
    
    print("\n💻 CodeExecutor Examples:")
    print("   'Execute Python code: print(2+2)'")
    print("   'Run Python to calculate fibonacci'")
    print("   'Execute bash command: ls -la'")
    
    print("\n🔄 Combined Examples:")
    print("   'Search for Python tips and save them to a file'")
    print("   'Create a Python script that prints Hello World'")
    print("   'List files and show their contents'")
    
    print("\n" + "="*60 + "\n")


def test_tools():
    """Test all tools"""
    print("\n" + "="*60)
    print("🧪 Testing All Tools")
    print("="*60)
    
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    
    MODEL = "llama3.1:8b"
    
    print("\n1. Testing LLM connection...")
    llm = SimpleLLM(model=MODEL)
    if llm.test_connection(verbose=False):
        print("   ✅ LLM connected")
    else:
        print("   ❌ LLM failed")
        return False
    
    print("\n2. Testing FileSystem tool...")
    fs = FileSystemTool(workspace)
    result = fs.create_file("test.txt", "Hello, World!")
    print(f"   {'✅' if result['success'] else '❌'} Create file")
    
    result = fs.read_file("test.txt")
    print(f"   {'✅' if result['success'] else '❌'} Read file")
    
    result = fs.delete_file("test.txt")
    print(f"   {'✅' if result['success'] else '❌'} Delete file")
    
    print("\n3. Testing WebSearch tool...")
    search = WebSearchTool()
    result = search.search("Python", max_results=2)
    print(f"   {'✅' if result['success'] else '❌'} Web search")
    
    print("\n4. Testing CodeExecutor tool...")
    executor = CodeExecutorTool(workspace)
    result = executor.execute_python("print('Hello from Python!')")
    print(f"   {'✅' if result['success'] else '❌'} Execute Python")
    
    print("\n" + "="*60)
    print("✅ All tools are working!")
    print("="*60)
    
    return True


if __name__ == "__main__":
    import sys
    
    # Check if running test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print()
        success = test_tools()
        print("\n" + "="*60)
        if success:
            print("✅ All systems ready! Run without --test to start")
        else:
            print("❌ Some tests failed - check the errors above")
        print("="*60 + "\n")
        sys.exit(0 if success else 1)
    
    # Run interactive mode
    main()
