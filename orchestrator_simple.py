"""
Simple orchestrator - no LangGraph, just basic flow
"""

import asyncio
import ollama
from typing import Dict, Any
from config_simple import SimpleConfig

class SimpleOrchestrator:
    """Simple task orchestrator without complex dependencies"""
    
    def __init__(self):
        self.ollama_client = ollama.Client(host=SimpleConfig.OLLAMA_HOST)
        print("[OK] SimpleOrchestrator initialized")
    
    async def execute(self, task: str) -> Dict[str, Any]:
        """Execute a simple task"""
        
        print(f"\n[TASK] {task}")
        
        # Step 1: Understand task
        print("[STEP] Understanding task...")
        understanding = await self._understand_task(task)
        
        # Step 2: Execute
        print("[STEP] Executing...")
        result = await self._execute_task(understanding)
        
        print("[OK] Done!")
        
        return {
            "task": task,
            "understanding": understanding,
            "result": result,
            "success": True
        }
    
    async def _understand_task(self, task: str) -> str:
        """Understand what user wants"""
        
        model = SimpleConfig.get_model("fast")
        
        try:
            response = self.ollama_client.chat(
                model=model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a helpful assistant. Analyze the task briefly.'
                    },
                    {
                        'role': 'user',
                        'content': f'Task: {task}\n\nWhat does the user want? Answer in 1 sentence.'
                    }
                ]
            )
            
            return response['message']['content']
            
        except Exception as e:
            print(f"[WARN] Understanding failed: {e}")
            return "Could not understand task"
    
    async def _execute_task(self, understanding: str) -> str:
        """Execute the task"""
        
        # For now, just return the understanding
        # Later we'll add actual execution
        return f"Understood: {understanding}"

# Test
async def test_orchestrator():
    """Test the simple orchestrator"""
    
    orch = SimpleOrchestrator()
    
    # Test simple task
    result = await orch.execute("Say hello")
    
    print("\n" + "="*50)
    print("Result:")
    print(f"  Task: {result['task']}")
    print(f"  Understanding: {result['understanding']}")
    print(f"  Result: {result['result']}")
    print(f"  Success: {result['success']}")

if __name__ == "__main__":
    print("Testing SimpleOrchestrator...\n")
    asyncio.run(test_orchestrator())

















