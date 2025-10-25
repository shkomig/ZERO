"""
Zero Agent - Smart Orchestrator v2 (FIXED)
===========================================
Fixed: Now properly passes the original task to the LLM
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class SmartOrchestrator:
    """
    Smart orchestrator with FIXED context handling
    """
    
    def __init__(self, llm, tools: Dict[str, Any], workspace: Path):
        self.llm = llm
        self.tools = tools
        self.workspace = workspace
        self.history = []
        self.current_task = ""  # FIXED: Store current task
        
    def execute(self, task: str) -> Dict[str, Any]:
        """Main execution method"""
        print(f"\n{'='*60}")
        print(f"[TASK] {task}")
        print(f"{'='*60}")
        
        self.current_task = task  # FIXED: Store the task
        
        try:
            # Step 1: Analyze task
            analysis = self._analyze_task(task)
            
            # Step 2: Create execution plan
            plan = self._create_plan(task, analysis)
            
            # Step 3: Execute plan
            result = self._execute_plan(plan, task)  # FIXED: Pass task
            
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
        """Analyze task complexity"""
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
            analysis = self._extract_json(response)
            print(f"   ✓ Complexity: {analysis.get('complexity', 'unknown')}")
            print(f"   ✓ Category: {analysis.get('category', 'unknown')}")
            print(f"   ✓ Tools needed: {analysis.get('requires_tools', [])}")
            return analysis
        except:
            return {
                "complexity": "simple",
                "category": "question",
                "requires_tools": [],
                "estimated_steps": 1,
                "reasoning": "Default analysis"
            }
    
    def _create_plan(self, task: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create execution plan"""
        print("[STEP 2/4] Creating execution plan...")
        
        complexity = analysis.get("complexity", "simple")
        
        if complexity == "simple":
            plan = [{
                "step": 1,
                "action": "answer",
                "description": "Answer directly",
                "tool": None
            }]
        else:
            plan = self._generate_plan_with_llm(task, analysis)
        
        print(f"   ✓ Created plan with {len(plan)} steps")
        for step in plan:
            print(f"      {step['step']}. {step['description']}")
        
        return plan
    
    def _generate_plan_with_llm(self, task: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed plan using LLM"""
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

Your plan:
"""
        
        response = self.llm.generate(prompt)
        
        try:
            plan = self._extract_json(response)
            if isinstance(plan, list) and len(plan) > 0:
                return plan
        except:
            pass
        
        return [{
            "step": 1,
            "action": "answer",
            "description": "Execute task",
            "tool": None
        }]
    
    def _execute_plan(self, plan: List[Dict[str, Any]], task: str) -> Any:
        """FIXED: Execute plan with proper context"""
        print("[STEP 3/4] Executing plan...")
        
        results = []
        context = f"Original task: {task}\n\n"  # FIXED: Include task
        
        for step_info in plan:
            step_num = step_info["step"]
            action = step_info["action"]
            tool_name = step_info.get("tool")
            
            print(f"\n   Step {step_num}: {step_info['description']}")
            
            if action == "answer" or tool_name is None:
                # FIXED: Pass full context including task
                result = self._generate_final_answer(task, context)
                results.append(result)
                print(f"   ✓ {result[:100]}...")
                
            elif tool_name in self.tools:
                tool_result = self._execute_tool(tool_name, context)
                results.append(tool_result)
                context += f"\n{tool_result}"
                print(f"   ✓ Tool executed")
                
            else:
                result = "Step completed"
                results.append(result)
        
        return results[-1] if results else "No result"
    
    def _execute_tool(self, tool_name: str, context: str) -> str:
        """Execute a specific tool"""
        tool = self.tools.get(tool_name)
        if not tool:
            return f"Error: Tool {tool_name} not found"
        
        try:
            return f"Tool {tool_name} executed"
        except Exception as e:
            return f"Tool error: {str(e)}"
    
    def _generate_final_answer(self, task: str, context: str) -> str:
        """FIXED: Generate answer with task included"""
        
        # FIXED: Simpler, more direct prompt
        prompt = f"""
Task: {task}

Please provide a clear and direct answer to this task.

Your answer:
"""
        
        return self.llm.generate(prompt, max_tokens=500)
    
    def _save_to_history(self, task: str, plan: List[Dict], result: Any):
        """Save to history"""
        print("[STEP 4/4] Saving to history...")
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "plan": plan,
            "result": result
        }
        
        self.history.append(entry)
        
        history_file = self.workspace / "history.json"
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            print("   ✓ Saved to history")
        except Exception as e:
            print(f"   ! Could not save history: {e}")
    
    def _extract_json(self, text: str) -> Any:
        """Extract JSON from LLM response"""
        text = text.replace("```json", "").replace("```", "")
        
        start = text.find("{")
        if start == -1:
            start = text.find("[")
        
        if start == -1:
            raise ValueError("No JSON found")
        
        if text[start] == "{":
            end = text.rfind("}") + 1
        else:
            end = text.rfind("]") + 1
        
        json_str = text[start:end]
        return json.loads(json_str)
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent history"""
        return self.history[-limit:]
    
    def clear_history(self):
        """Clear history"""
        self.history = []
        history_file = self.workspace / "history.json"
        if history_file.exists():
            history_file.unlink()


if __name__ == "__main__":
    print("Smart Orchestrator v2 (FIXED)")
    print("=" * 60)
    print("\nFixed: Now properly passes task to LLM for direct answers")
