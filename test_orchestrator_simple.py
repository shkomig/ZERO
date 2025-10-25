"""
Simple orchestrator test
"""

import asyncio
from zero_agent.core.orchestrator import ZeroOrchestrator
from zero_agent.models.model_router import router
from zero_agent.core.tool_executor import ToolExecutor
from zero_agent.rag.memory import RAGMemorySystem

async def test_simple():
    """Test simple orchestrator functionality"""
    
    print("Testing Simple Orchestrator...")
    print("="*50)
    
    try:
        # Initialize components
        tool_executor = ToolExecutor()
        rag_system = RAGMemorySystem()
        orchestrator = ZeroOrchestrator(
            model_router=router,
            tool_executor=tool_executor,
            rag_system=rag_system
        )
        print("[OK] Components initialized")
        
        # Test simple task
        print("\nTesting simple task...")
        result = await orchestrator.run("Check CPU usage")
        print(f"[OK] Task completed: {result.get('final_response', 'No response')[:100]}...")
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple())






