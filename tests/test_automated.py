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
    print(f"[FAIL] Import error: {e}")
    print("\n[TIP] Make sure you have:")
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
        
        print(f"\n[OK] Success!")
        understanding = result['understanding'][:100].encode('ascii', 'replace').decode('ascii')
        result_text = result['result'][:100].encode('ascii', 'replace').decode('ascii')
        print(f"   Understanding: {understanding}...")
        print(f"   Result: {result_text}...")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main entry point - NON-INTERACTIVE"""
    
    print("Zero Agent - Automated Test Mode")
    print("="*60)
    print(f"Workspace: {SimpleConfig.WORKSPACE_DIR}")
    print(f"Ollama: {SimpleConfig.OLLAMA_HOST}")
    print("="*60)
    
    # Initialize orchestrator
    print("\n[INIT] Initializing orchestrator...")
    try:
        orchestrator = SimpleOrchestrator()
        print("[OK] Orchestrator ready!")
    except Exception as e:
        print(f"[FAIL] Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Run automated tests
    print("\n[TEST] Running automated tests...\n")
    
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
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for task, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {task}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        print("\nNext steps:")
        print("   1. The basic system works!")
        print("   2. Now we can add more features")
        print("   3. Ready for Phase 3: Systematic Fix")
    else:
        print("\n[WARN] Some tests failed. Check the errors above.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
        print("\n[OK] Test complete. Exiting normally.")
    except KeyboardInterrupt:
        print("\n\n[WARN] Interrupted by user")
    except Exception as e:
        print(f"\n[FAIL] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
