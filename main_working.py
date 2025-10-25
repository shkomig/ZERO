"""
Working main.py with simple orchestrator
"""

import asyncio
from orchestrator_simple import SimpleOrchestrator
from config_simple import SimpleConfig

async def main():
    """Main entry point"""
    
    print("Zero Agent - Simple Version")
    print("="*50)
    print(f"Workspace: {SimpleConfig.WORKSPACE_DIR}")
    print(f"Ollama: {SimpleConfig.OLLAMA_HOST}")
    print("="*50)
    
    # Initialize orchestrator
    orchestrator = SimpleOrchestrator()
    
    print("\n[OK] Zero Agent ready!\n")
    
    # Interactive loop
    while True:
        try:
            task = input("Zero> ").strip()
            
            if not task:
                continue
            
            if task.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            # Execute task
            result = await orchestrator.execute(task)
            
            print(f"\n[RESPONSE] {result['result']}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] Error: {e}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")






