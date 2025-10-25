"""
Test LangGraph Orchestrator functionality
"""

import asyncio
from zero_agent.core.orchestrator import ZeroOrchestrator
from zero_agent.models.model_router import router
from zero_agent.core.tool_executor import ToolExecutor
from zero_agent.rag.memory import RAGMemorySystem

async def test_orchestrator():
    """Test orchestrator functionality"""
    
    print("Testing LangGraph Orchestrator...")
    print("="*50)
    
    # Initialize components
    try:
        print("Initializing components...")
        tool_executor = ToolExecutor()
        rag_system = RAGMemorySystem()
        orchestrator = ZeroOrchestrator(
            model_router=router,
            tool_executor=tool_executor,
            rag_system=rag_system
        )
        print("[OK] All components initialized")
    except Exception as e:
        print(f"[FAIL] Initialization failed: {e}")
        return
    
    # Test 1: Simple task
    print("\n1. Testing simple task:")
    try:
        result = await orchestrator.run("Check system CPU usage")
        print(f"   [OK] Task completed: {result.get('final_response', 'No response')[:100]}...")
    except Exception as e:
        print(f"   [FAIL] Task failed: {e}")
    
    # Test 2: Complex task
    print("\n2. Testing complex task:")
    try:
        result = await orchestrator.run("Take a screenshot and check system memory")
        print(f"   [OK] Task completed: {result.get('final_response', 'No response')[:100]}...")
    except Exception as e:
        print(f"   [FAIL] Task failed: {e}")
    
    print("\n" + "="*50)
    print("Orchestrator test complete!")

if __name__ == "__main__":
    asyncio.run(test_orchestrator())






