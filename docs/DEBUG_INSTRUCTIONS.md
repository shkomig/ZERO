"""
Working main.py - NON-INTERACTIVE VERSION for Cursor
This version runs predefined tests instead of waiting for input
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from orchestrator_simple import SimpleOrchestrator
    from config_simple import SimpleConfig
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\n💡 Make sure you have:")
    print("   - orchestrator_simple.py")
    print("   - config_simple.py")
    print("   in the same directory")
    sys.exit(1)

async def test_task(orchestrator, task: str):
    """Test a single task"""
    print(f"\n{'='*60}")
    print(f"Testing: {task}")
    print('='*60)
    
    try:
        result = await orchestrator.execute(task)
        
        print(f"\n✅ Success!")
        print(f"   Understanding: {result['understanding'][:100]}...")
        print(f"   Result: {result['result'][:100]}...")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main entry point - NON-INTERACTIVE"""
    
    print("🤖 Zero Agent - Automated Test Mode")
    print("="*60)
    print(f"Workspace: {SimpleConfig.WORKSPACE_DIR}")
    print(f"Ollama: {SimpleConfig.OLLAMA_HOST}")
    print("="*60)
    
    # Initialize orchestrator
    print("\n📦 Initializing orchestrator...")
    try:
        orchestrator = SimpleOrchestrator()
        print("✅ Orchestrator ready!")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Run automated tests
    print("\n🧪 Running automated tests...\n")
    
    test_tasks = [
        "Say hello in Hebrew",
        "What is 2+2?",
        "Tell me a short joke",
    ]
    
    results = []
    for task in test_tasks:
        success = await test_task(orchestrator, task)
        results.append((task, success))
        await asyncio.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for task, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {task}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print("\n📝 Next steps:")
        print("   1. The basic system works!")
        print("   2. Now we can add more features")
        print("   3. Run: python test_interactive.py for manual testing")
    else:
        print("\n⚠️ Some tests failed. Check the errors above.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
        print("\n✅ Test complete. Exiting normally.")
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)