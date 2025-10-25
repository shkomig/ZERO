"""
Zero Agent - Smart Orchestrator with Tools
===========================================
Orchestrator that can use FileSystem, WebSearch, and CodeExecutor tools
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class SmartOrchestratorWithTools:
    """
    Smart orchestrator with tool support
    """
    
    def __init__(self, llm, tools: Dict[str, Any], workspace: Path):
        self.llm = llm
        self.tools = tools
        self.workspace = workspace
        self.history = []
        self.current_task = ""
        
    def execute(self, task: str) -> Dict[str, Any]:
        """Main execution method"""
        print(f"\n{'='*60}")
        print(f"[TASK] {task}")
        print(f"{'='*60}")
        
        self.current_task = task
        
        try:
            # Step 1: Analyze task
            analysis = self._analyze_task(task)
            
            # Step 2: Create execution plan
            plan = self._create_plan(task, analysis)
            
            # Step 3: Execute plan with tools
            result = self._execute_plan(plan, task)
            
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
        """Analyze task and identify required tools"""
        print("[STEP 1/4] Analyzing task...")
        
        # Get available tools info
        tools_info = self._get_tools_info()
        
        prompt = f"""
Analyze this task and respond in JSON format:

Task: {task}

Available tools:
{tools_info}

Determine:
1. complexity: "simple" | "medium" | "complex"
2. category: "question" | "file_operation" | "web_search" | "code" | "mixed"
3. requires_tools: list of tool names needed (from: filesystem, websearch, codeexecutor)
4. estimated_steps: number (1-10)

Example response:
{{
    "complexity": "medium",
    "category": "file_operation",
    "requires_tools": ["filesystem"],
    "estimated_steps": 2,
    "reasoning": "Need to create a file"
}}

Your analysis:
"""
        
        response = self.llm.generate(prompt, max_tokens=500)
        
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
        """Create execution plan based on analysis"""
        print("[STEP 2/4] Creating execution plan...")
        
        requires_tools = analysis.get("requires_tools", [])
        
        if not requires_tools:
            # Simple task - no tools needed
            plan = [{
                "step": 1,
                "action": "answer",
                "description": "Answer directly",
                "tool": None,
                "params": {}
            }]
        else:
            # Complex task - create detailed plan
            plan = self._generate_plan_with_llm(task, analysis)
        
        print(f"   ✓ Created plan with {len(plan)} steps")
        for step in plan:
            tool_info = f" (using {step['tool']})" if step['tool'] else ""
            print(f"      {step['step']}. {step['description']}{tool_info}")
        
        return plan
    
    def _generate_plan_with_llm(self, task: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed plan using LLM"""
        tools_info = self._get_tools_info()
        
        prompt = f"""
Create a step-by-step execution plan for this task.

Task: {task}
Analysis: {json.dumps(analysis, indent=2)}

Available tools and their methods:
{tools_info}

Create a plan as JSON array. Each step should specify:
- step: number
- action: "answer" | "filesystem" | "websearch" | "codeexecutor"
- description: what to do
- tool: tool name or null
- params: dict of parameters for the tool method

Example for file creation:
[
    {{
        "step": 1,
        "action": "filesystem",
        "description": "Create the file",
        "tool": "filesystem",
        "params": {{"method": "create_file", "path": "test.txt", "content": "Hello"}}
    }},
    {{
        "step": 2,
        "action": "answer",
        "description": "Confirm completion",
        "tool": null,
        "params": {{}}
    }}
]

Your plan:
"""
        
        response = self.llm.generate(prompt, max_tokens=1000)
        
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
            "tool": None,
            "params": {}
        }]
    
    def _execute_plan(self, plan: List[Dict[str, Any]], task: str) -> Any:
        """Execute plan step by step"""
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
                # Generate answer
                result = self._generate_final_answer(task, context)
                results.append(result)
                print(f"   ✓ {result[:100]}...")
                
            elif tool_name in self.tools:
                # Execute tool
                tool_result = self._execute_tool(tool_name, params, context)
                results.append(tool_result)
                context += f"\nTool result: {tool_result}\n"
                print(f"   ✓ Tool executed: {str(tool_result)[:100]}...")
                
            else:
                result = f"Tool {tool_name} not found"
                results.append(result)
                print(f"   ✗ {result}")
        
        return results[-1] if results else "No result"
    
    def _execute_tool(self, tool_name: str, params: Dict[str, Any], context: str) -> Any:
        """Execute a specific tool with parameters"""
        tool = self.tools.get(tool_name)
        if not tool:
            return f"Error: Tool {tool_name} not found"
        
        try:
            method_name = params.get("method")
            if not method_name:
                return f"Error: No method specified for {tool_name}"
            
            method = getattr(tool, method_name, None)
            if not method:
                return f"Error: Method {method_name} not found in {tool_name}"
            
            # Remove 'method' from params before calling
            call_params = {k: v for k, v in params.items() if k != "method"}
            
            # Call the tool method
            result = method(**call_params)
            
            return result
            
        except Exception as e:
            return f"Tool error: {str(e)}"
    
    def _generate_final_answer(self, task: str, context: str) -> str:
        """Generate final answer"""
        prompt = f"""
Task: {task}

Context from previous steps:
{context}

Please provide a clear and direct answer to this task.

Your answer:
"""
        
        return self.llm.generate(prompt, max_tokens=500)
    
    def _get_tools_info(self) -> str:
        """Get information about available tools"""
        info = []
        for name, tool in self.tools.items():
            if hasattr(tool, 'get_info'):
                info.append(f"\n{name.upper()}:\n{tool.get_info()}")
        return "\n".join(info) if info else "No tools available"
    
    def _save_to_history(self, task: str, plan: List[Dict], result: Any):
        """Save to history"""
        print("[STEP 4/4] Saving to history...")
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "plan": plan,
            "result": str(result)[:500]  # Limit result size
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
    print("Smart Orchestrator with Tools")
    print("=" * 60)
    print("\nFeatures:")
    print("✓ Tool integration (FileSystem, WebSearch, CodeExecutor)")
    print("✓ Smart tool selection")
    print("✓ Multi-step execution")
    print("✓ Context preservation")
