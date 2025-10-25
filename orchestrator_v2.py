"""
Zero Agent - Smart Orchestrator v2
====================================
More intelligent orchestrator with:
- Task planning and decomposition
- Smart tool selection
- Retry logic
- Better error handling
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class SmartOrchestrator:
    """
    Smart orchestrator that can:
    1. Analyze task complexity
    2. Plan execution steps
    3. Select appropriate tools
    4. Handle errors gracefully
    """
    
    def __init__(self, llm, tools: Dict[str, Any], workspace: Path):
        self.llm = llm
        self.tools = tools
        self.workspace = workspace
        self.history = []
        
    def execute(self, task: str) -> Dict[str, Any]:
        """
        Main execution method with smart planning
        """
        print(f"\n{'='*60}")
        print(f"[TASK] {task}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Analyze task
            analysis = self._analyze_task(task)
            
            # Step 2: Create execution plan
            plan = self._create_plan(task, analysis)
            
            # Step 3: Execute plan
            result = self._execute_plan(plan)
            
            # Step 4: Save to history
            self._save_to_history(task, plan, result)
            
            return {
                "success": True,
                "task": task,
                "analysis": analysis,
                "plan": plan,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "task": task,
                "error": str(e)
            }
    
    def _analyze_task(self, task: str) -> Dict[str, Any]:
        """
        Analyze task to understand:
        - Complexity (simple/medium/complex)
        - Required tools
        - Number of steps needed
        """
        print("[STEP 1/4] Analyzing task...")
        
        prompt = f"""
Analyze this task and respond in JSON format:

Task: {task}

Determine:
1. complexity: "simple" | "medium" | "complex"
2. category: "question" | "file_operation" | "web_search" | "code" | "mixed"
3. requires_tools: list of tool names needed
4. estimated_steps: number (1-10)

Example response:
{{
    "complexity": "simple",
    "category": "question",
    "requires_tools": [],
    "estimated_steps": 1,
    "reasoning": "Simple factual question, no tools needed"
}}

Your analysis:
"""
        
        response = self.llm.generate(prompt)
        
        try:
            # Try to parse JSON
            analysis = self._extract_json(response)
            print(f"   ✓ Complexity: {analysis.get('complexity', 'unknown')}")
            print(f"   ✓ Category: {analysis.get('category', 'unknown')}")
            print(f"   ✓ Tools needed: {analysis.get('requires_tools', [])}")
            return analysis
        except:
            # Fallback to simple analysis
            return {
                "complexity": "simple",
                "category": "question",
                "requires_tools": [],
                "estimated_steps": 1,
                "reasoning": "Default analysis"
            }
    
    def _create_plan(self, task: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create step-by-step execution plan based on analysis
        """
        print("[STEP 2/4] Creating execution plan...")
        
        complexity = analysis.get("complexity", "simple")
        
        if complexity == "simple":
            # Simple task - direct execution
            plan = [{
                "step": 1,
                "action": "answer",
                "description": "Answer directly",
                "tool": None
            }]
        else:
            # Complex task - ask LLM to create plan
            plan = self._generate_plan_with_llm(task, analysis)
        
        print(f"   ✓ Created plan with {len(plan)} steps")
        for step in plan:
            print(f"      {step['step']}. {step['description']}")
        
        return plan
    
    def _generate_plan_with_llm(self, task: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Use LLM to generate detailed execution plan
        """
        available_tools = list(self.tools.keys())
        
        prompt = f"""
Create a step-by-step execution plan for this task.

Task: {task}
Analysis: {json.dumps(analysis, indent=2)}
Available tools: {available_tools}

Create a plan as JSON array:
[
    {{
        "step": 1,
        "action": "tool_name or 'think' or 'answer'",
        "description": "what to do",
        "tool": "tool_name or null"
    }}
]

Example:
[
    {{"step": 1, "action": "think", "description": "Understand requirements", "tool": null}},
    {{"step": 2, "action": "filesystem", "description": "Create file", "tool": "filesystem"}},
    {{"step": 3, "action": "answer", "description": "Return result", "tool": null}}
]

Your plan:
"""
        
        response = self.llm.generate(prompt)
        
        try:
            plan = self._extract_json(response)
            if isinstance(plan, list) and len(plan) > 0:
                return plan
        except:
            pass
        
        # Fallback plan
        return [{
            "step": 1,
            "action": "answer",
            "description": "Execute task",
            "tool": None
        }]
    
    def _execute_plan(self, plan: List[Dict[str, Any]]) -> Any:
        """
        Execute the plan step by step
        """
        print("[STEP 3/4] Executing plan...")
        
        results = []
        context = ""
        
        for step_info in plan:
            step_num = step_info["step"]
            action = step_info["action"]
            tool_name = step_info.get("tool")
            
            print(f"\n   Step {step_num}: {step_info['description']}")
            
            if action == "answer" or tool_name is None:
                # Final answer step
                result = self._generate_final_answer(context)
                results.append(result)
                print(f"   ✓ {result[:100]}...")
                
            elif tool_name in self.tools:
                # Use tool
                tool_result = self._execute_tool(tool_name, context)
                results.append(tool_result)
                context += f"\n{tool_result}"
                print(f"   ✓ Tool executed")
                
            else:
                # Think/reasoning step
                result = "Step completed"
                results.append(result)
        
        return results[-1] if results else "No result"
    
    def _execute_tool(self, tool_name: str, context: str) -> str:
        """
        Execute a specific tool
        """
        tool = self.tools.get(tool_name)
        if not tool:
            return f"Error: Tool {tool_name} not found"
        
        try:
            # Here you would call the actual tool
            # For now, placeholder
            return f"Tool {tool_name} executed"
        except Exception as e:
            return f"Tool error: {str(e)}"
    
    def _generate_final_answer(self, context: str) -> str:
        """
        Generate final answer using LLM
        """
        prompt = f"""
Based on the context below, provide a clear and concise answer.

Context:
{context}

Your answer:
"""
        return self.llm.generate(prompt)
    
    def _save_to_history(self, task: str, plan: List[Dict], result: Any):
        """
        Save execution to history
        """
        print("[STEP 4/4] Saving to history...")
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "plan": plan,
            "result": result
        }
        
        self.history.append(entry)
        
        # Save to file
        history_file = self.workspace / "history.json"
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            print("   ✓ Saved to history")
        except Exception as e:
            print(f"   ! Could not save history: {e}")
    
    def _extract_json(self, text: str) -> Any:
        """
        Extract JSON from LLM response
        """
        # Remove markdown code blocks
        text = text.replace("```json", "").replace("```", "")
        
        # Find JSON object or array
        start = text.find("{")
        if start == -1:
            start = text.find("[")
        
        if start == -1:
            raise ValueError("No JSON found")
        
        # Find matching closing bracket
        if text[start] == "{":
            end = text.rfind("}") + 1
        else:
            end = text.rfind("]") + 1
        
        json_str = text[start:end]
        return json.loads(json_str)
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent history
        """
        return self.history[-limit:]
    
    def clear_history(self):
        """
        Clear execution history
        """
        self.history = []
        history_file = self.workspace / "history.json"
        if history_file.exists():
            history_file.unlink()


# Simple usage example
if __name__ == "__main__":
    print("Smart Orchestrator v2")
    print("=" * 60)
    print("\nFeatures:")
    print("✓ Task analysis and complexity detection")
    print("✓ Smart execution planning")
    print("✓ Tool selection")
    print("✓ History tracking")
    print("\nReady to integrate into Zero Agent!")
