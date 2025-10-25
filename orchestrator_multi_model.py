"""
Smart Orchestrator with Multi-Model Routing
============================================
Automatically selects best model for each task
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class MultiModelOrchestrator:
    """
    Orchestrator with automatic model selection
    """
    
    def __init__(self, llm, router, tools: Dict[str, Any], workspace: Path):
        self.llm = llm
        self.router = router
        self.tools = tools
        self.workspace = workspace
        self.history = []
        self.current_task = ""
        
    def execute(self, task: str, force_model: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute task with automatic model selection
        
        Args:
            task: The task
            force_model: Force specific model (optional)
        """
        print(f"\n{'='*60}")
        print(f"[TASK] {task}")
        print(f"{'='*60}")
        
        self.current_task = task
        
        try:
            # Step 1: Route to best model
            if force_model:
                selected_model = force_model
                print(f"[MODEL] Using forced model: {selected_model}")
            else:
                routing_result = self.router.route_with_reasoning(task)
                selected_model = routing_result["model"]
                print(f"[MODEL] Auto-selected: {selected_model.upper()}")
                print(f"        Reason: {routing_result['reasoning']}")
                print(f"        Confidence: {routing_result['confidence']*100:.0f}%")
            
            # Step 2: Analyze task
            analysis = self._analyze_task(task, selected_model)
            
            # Step 3: Create plan
            plan = self._create_plan(task, analysis, selected_model)
            
            # Step 4: Execute plan
            result = self._execute_plan(plan, task, selected_model)
            
            # Step 5: Save history
            self._save_to_history(task, plan, result, selected_model)
            
            return {
                "success": True,
                "task": task,
                "model": selected_model,
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
    
    def _analyze_task(self, task: str, model: str) -> Dict[str, Any]:
        """Analyze task complexity"""
        print("[STEP 1/4] Analyzing task...")
        
        tools_info = self._get_tools_info()
        
        prompt = f"""
Analyze this task and respond in JSON format:

Task: {task}

Available tools:
{tools_info}

Determine:
1. complexity: "simple" | "medium" | "complex"
2. category: "question" | "file_operation" | "web_search" | "code" | "mixed"
3. requires_tools: list of tool names needed
4. estimated_steps: number (1-10)

Example:
{{
    "complexity": "simple",
    "category": "question",
    "requires_tools": [],
    "estimated_steps": 1,
    "reasoning": "Simple question"
}}

Your analysis:
"""
        
        response = self.llm.generate(prompt, model=model, max_tokens=500)
        
        try:
            analysis = self._extract_json(response)
            print(f"   ✓ Complexity: {analysis.get('complexity', 'unknown')}")
            print(f"   ✓ Category: {analysis.get('category', 'unknown')}")
            print(f"   ✓ Tools: {analysis.get('requires_tools', [])}")
            return analysis
        except:
            return {
                "complexity": "simple",
                "category": "question",
                "requires_tools": [],
                "estimated_steps": 1
            }
    
    def _create_plan(self, task: str, analysis: Dict[str, Any], model: str) -> List[Dict[str, Any]]:
        """Create execution plan"""
        print("[STEP 2/4] Creating plan...")
        
        requires_tools = analysis.get("requires_tools", [])
        
        if not requires_tools:
            plan = [{
                "step": 1,
                "action": "answer",
                "description": "Answer directly",
                "tool": None,
                "params": {}
            }]
        else:
            plan = self._generate_plan_with_llm(task, analysis, model)
        
        print(f"   ✓ Created plan with {len(plan)} steps")
        for step in plan:
            tool_info = f" (using {step['tool']})" if step['tool'] else ""
            print(f"      {step['step']}. {step['description']}{tool_info}")
        
        return plan
    
    def _generate_plan_with_llm(self, task: str, analysis: Dict[str, Any], model: str) -> List[Dict[str, Any]]:
        """Generate plan using LLM"""
        tools_info = self._get_tools_info()
        
        prompt = f"""
Create execution plan for this task.

Task: {task}
Analysis: {json.dumps(analysis, indent=2)}
Tools: {tools_info}

Create plan as JSON array with steps.

Your plan:
"""
        
        response = self.llm.generate(prompt, model=model, max_tokens=1000)
        
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
            "tool": None,
            "params": {}
        }]
    
    def _execute_plan(self, plan: List[Dict[str, Any]], task: str, model: str) -> Any:
        """Execute plan"""
        print("[STEP 3/4] Executing plan...")
        
        results = []
        context = f"Task: {task}\n\n"
        
        for step_info in plan:
            step_num = step_info["step"]
            action = step_info["action"]
            tool_name = step_info.get("tool")
            params = step_info.get("params", {})
            
            print(f"\n   Step {step_num}: {step_info['description']}")
            
            if action == "answer" or tool_name is None:
                result = self._generate_final_answer(task, context, model)
                results.append(result)
                print(f"   ✓ {result[:100]}...")
                
            elif tool_name in self.tools:
                tool_result = self._execute_tool(tool_name, params, context)
                results.append(tool_result)
                context += f"\nTool result: {tool_result}\n"
                print(f"   ✓ Tool executed")
                
            else:
                result = f"Tool {tool_name} not found"
                results.append(result)
        
        return results[-1] if results else "No result"
    
    def _execute_tool(self, tool_name: str, params: Dict[str, Any], context: str) -> Any:
        """Execute tool"""
        tool = self.tools.get(tool_name)
        if not tool:
            return f"Error: Tool {tool_name} not found"
        
        try:
            method_name = params.get("method")
            if not method_name:
                return f"Error: No method specified"
            
            method = getattr(tool, method_name, None)
            if not method:
                return f"Error: Method {method_name} not found"
            
            call_params = {k: v for k, v in params.items() if k != "method"}
            result = method(**call_params)
            return result
            
        except Exception as e:
            return f"Tool error: {str(e)}"
    
    def _generate_final_answer(self, task: str, context: str, model: str) -> str:
        """Generate answer with selected model"""
        prompt = f"""
Task: {task}

Context:
{context}

Provide a clear answer.

Your answer:
"""
        
        return self.llm.generate(prompt, model=model, max_tokens=1000)
    
    def _get_tools_info(self) -> str:
        """Get tools info"""
        info = []
        for name, tool in self.tools.items():
            if hasattr(tool, 'get_info'):
                info.append(f"\n{name}: {tool.get_info()[:200]}")
        return "\n".join(info) if info else "No tools"
    
    def _save_to_history(self, task: str, plan: List[Dict], result: Any, model: str):
        """Save to history"""
        print("[STEP 4/4] Saving...")
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "model": model,
            "plan": plan,
            "result": str(result)[:500]
        }
        
        self.history.append(entry)
        
        try:
            history_file = self.workspace / "history.json"
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            print("   ✓ Saved")
        except:
            pass
    
    def _extract_json(self, text: str) -> Any:
        """Extract JSON"""
        text = text.replace("```json", "").replace("```", "")
        start = text.find("{") if "{" in text else text.find("[")
        if start == -1:
            raise ValueError("No JSON")
        end = text.rfind("}") + 1 if text[start] == "{" else text.rfind("]") + 1
        return json.loads(text[start:end])
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get history"""
        return self.history[-limit:]
    
    def clear_history(self):
        """Clear history"""
        self.history = []
        history_file = self.workspace / "history.json"
        if history_file.exists():
            history_file.unlink()
    
    def print_stats(self):
        """Print usage statistics"""
        print("\n" + "="*60)
        print("📊 USAGE STATISTICS")
        print("="*60)
        
        stats = self.llm.get_stats()
        total = sum(stats.values())
        
        for model, count in stats.items():
            percentage = (count / total * 100) if total > 0 else 0
            print(f"{model.upper():12} : {count:3} times ({percentage:5.1f}%)")
        
        print(f"\n{'TOTAL':12} : {total:3} requests")
        print("="*60 + "\n")


if __name__ == "__main__":
    print("Multi-Model Orchestrator")
    print("="*60)
    print("\nFeatures:")
    print("✓ Automatic model selection")
    print("✓ Smart routing based on task")
    print("✓ Performance tracking")
    print("✓ Tool integration")
