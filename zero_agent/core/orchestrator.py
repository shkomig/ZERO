"""
Master orchestrator using LangGraph for task planning and execution
"""

from typing import TypedDict, Annotated, Sequence, Literal
import operator
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, AIMessage


class AgentState(TypedDict):
    """State shared across all nodes in the graph"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    task: str
    plan: list[str]
    current_step: int
    tool_results: dict
    context: dict
    error_count: int
    needs_clarification: bool
    final_response: str


class ZeroOrchestrator:
    """Main orchestrator for Zero Agent"""
    
    def __init__(self, model_router, tool_executor, rag_system):
        self.model_router = model_router
        self.tool_executor = tool_executor
        self.rag_system = rag_system
        self.graph = self._build_graph()
        
        print("[TARGET] Zero Orchestrator initialized")
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("understand", self._understand_task)
        workflow.add_node("plan", self._create_plan)
        workflow.add_node("execute", self._execute_step)
        workflow.add_node("verify", self._verify_result)
        workflow.add_node("reflect", self._reflect_and_learn)
        
        # Add edges
        workflow.set_entry_point("understand")
        workflow.add_edge("understand", "plan")
        workflow.add_edge("plan", "execute")
        workflow.add_edge("execute", "verify")
        
        # Conditional edges
        workflow.add_conditional_edges(
            "verify",
            self._should_continue,
            {
                "continue": "execute",
                "clarify": "understand",
                "complete": "reflect"
            }
        )
        workflow.add_edge("reflect", END)
        
        return workflow.compile()
    
    def _understand_task(self, state: AgentState) -> AgentState:
        """Understand user's task using RAG and reasoning"""
        print("[THINK] Understanding task...")
        
        task = state["task"]
        
        # Retrieve relevant context from RAG
        context_docs = self.rag_system.retrieve(task, n_results=3)
        context = "\n".join([doc["document"] for doc in context_docs])
        
        # Select model for understanding
        model_name = self.model_router.select_model(
            task="understanding task requirements",
            complexity="medium"
        )
        
        # Generate understanding
        messages = [
            {
                "role": "user",
                "content": f"""Analyze this task:
                
Task: {task}

Previous context:
{context}

Provide:
1. What is the user asking for?
2. What tools might be needed?
3. Any potential challenges?
4. Is the task clear enough to proceed?

Be concise."""
            }
        ]
        
        try:
            response = self.model_router.invoke_model(model_name, messages)
            
            needs_clarification = "unclear" in response.lower() or "clarification" in response.lower()
            
            return {
                **state,
                "messages": [AIMessage(content=response)],
                "context": {"understanding": response, "previous_context": context},
                "needs_clarification": needs_clarification
            }
        except Exception as e:
            print(f"[ERROR] Understanding failed: {e}")
            return {
                **state,
                "messages": [AIMessage(content=f"Error: {e}")],
                "error_count": state.get("error_count", 0) + 1
            }
    
    def _create_plan(self, state: AgentState) -> AgentState:
        """Create detailed execution plan"""
        print("[PLAN] Creating execution plan...")
        
        if state.get("needs_clarification"):
            return {
                **state,
                "plan": [],
                "final_response": "I need more information to proceed. Could you please clarify your request?"
            }
        
        task = state["task"]
        context = state.get("context", {})
        
        # Select planning model
        model_name = self.model_router.select_model(
            task="planning",
            complexity="high"
        )
        
        # Available tools
        available_tools = self.tool_executor.list_tools()
        
        messages = [
            {
                "role": "user",
                "content": f"""Create a step-by-step execution plan for this task:

Task: {task}

Understanding: {context.get('understanding', '')}

Available tools: {', '.join(available_tools)}

Create a numbered list of specific steps to execute this task.
Each step should be one clear action.
Format as: 1. action, 2. action, etc.

Example:
1. Take screenshot
2. Search web for information
3. Analyze results

Your plan:"""
            }
        ]
        
        try:
            response = self.model_router.invoke_model(model_name, messages)
            
            # Parse plan into list
            plan = self._parse_plan(response)
            
            print(f"[OK] Plan created with {len(plan)} steps")
            
            return {
                **state,
                "plan": plan,
                "current_step": 0,
                "tool_results": {}
            }
        except Exception as e:
            print(f"[ERROR] Planning failed: {e}")
            return {
                **state,
                "plan": [],
                "error_count": state.get("error_count", 0) + 1
            }
    
    def _parse_plan(self, plan_text: str) -> list[str]:
        """Parse plan text into list of steps"""
        lines = plan_text.strip().split('\n')
        steps = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Remove numbering
            if line[0].isdigit() and ('. ' in line or ') ' in line):
                line = line.split('. ', 1)[-1] if '. ' in line else line.split(') ', 1)[-1]
            if line:
                steps.append(line)
        
        return steps
    
    async def _execute_step(self, state: AgentState) -> AgentState:
        """Execute current plan step"""
        current_step = state.get("current_step", 0)
        plan = state.get("plan", [])
        
        if not plan or current_step >= len(plan):
            return state
        
        step = plan[current_step]
        print(f"[EXEC]  Executing step {current_step + 1}/{len(plan)}: {step}")
        
        # Determine which tool to use
        tool_name, params = await self._map_step_to_tool(step)
        
        if tool_name:
            try:
                result = await self.tool_executor.execute(tool_name, **params)
                
                return {
                    **state,
                    "tool_results": {
                        **state.get("tool_results", {}),
                        current_step: {
                            "step": step,
                            "tool": tool_name,
                            "result": result
                        }
                    },
                    "error_count": 0
                }
            except Exception as e:
                print(f"[ERROR] Step execution failed: {e}")
                return {
                    **state,
                    "tool_results": {
                        **state.get("tool_results", {}),
                        current_step: {
                            "step": step,
                            "error": str(e)
                        }
                    },
                    "error_count": state.get("error_count", 0) + 1
                }
        else:
            # No tool needed, just acknowledge
            return {
                **state,
                "tool_results": {
                    **state.get("tool_results", {}),
                    current_step: {
                        "step": step,
                        "result": {"success": True, "note": "No tool execution needed"}
                    }
                }
            }
    
    async def _map_step_to_tool(self, step: str) -> tuple[str, dict]:
        """Map plan step to tool and parameters"""
        step_lower = step.lower()
        
        # Pattern matching for tools
        if "screenshot" in step_lower or "capture screen" in step_lower:
            return "screenshot", {}
        elif "search" in step_lower and ("web" in step_lower or "google" in step_lower or "internet" in step_lower):
            # Extract search query
            query = step.split("search")[-1].strip()
            query = query.replace("web for", "").replace("google for", "").replace("internet for", "").strip()
            return "web_search", {"query": query}
        elif "memory" in step_lower or "ram" in step_lower:
            return "memory_usage", {}
        elif "cpu" in step_lower:
            return "cpu_usage", {}
        elif "disk" in step_lower:
            return "disk_usage", {}
        elif "system" in step_lower and "info" in step_lower:
            return "system_info", {}
        elif "git" in step_lower:
            if "init" in step_lower:
                # Extract repo name
                words = step.split()
                name = words[-1] if words else "new-repo"
                return "git_init", {"name": name}
            elif "status" in step_lower:
                return "git_status", {}
        
        # No specific tool matched
        return None, {}
    
    def _verify_result(self, state: AgentState) -> AgentState:
        """Verify step execution"""
        current_step = state.get("current_step", 0)
        tool_results = state.get("tool_results", {})
        
        if current_step in tool_results:
            result = tool_results[current_step]
            
            if "error" in result:
                print(f"[WARN]  Step {current_step + 1} failed")
            else:
                print(f"[OK] Step {current_step + 1} completed")
        
        return state
    
    def _should_continue(self, state: AgentState) -> Literal["continue", "clarify", "complete"]:
        """Decide next action"""
        error_count = state.get("error_count", 0)
        current_step = state.get("current_step", 0)
        plan = state.get("plan", [])
        
        # Too many errors
        if error_count >= 3:
            return "clarify"
        
        # More steps to execute
        if current_step < len(plan) - 1:
            state["current_step"] = current_step + 1
            return "continue"
        
        # All steps completed
        return "complete"
    
    def _reflect_and_learn(self, state: AgentState) -> AgentState:
        """Learn from execution and store in RAG"""
        print("[MEMORY] Reflecting and learning...")
        
        task = state["task"]
        plan = state.get("plan", [])
        tool_results = state.get("tool_results", {})
        
        # Check if successful
        success = all("error" not in result for result in tool_results.values())
        
        if success:
            self.rag_system.store_success(task, plan, tool_results)
            
            # Create summary
            summary = f"Task completed successfully:\n{task}\n\n"
            for step_idx, result in tool_results.items():
                summary += f"Step {step_idx + 1}: {result.get('step', '')}\n"
                if result.get('result', {}).get('success'):
                    summary += f"  [OK] Success\n"
            
            return {
                **state,
                "final_response": summary
            }
        else:
            # Store failure for learning
            errors = [r for r in tool_results.values() if "error" in r]
            if errors:
                self.rag_system.store_failure(task, str(errors[0].get("error")), state.get("context", {}))
            
            return {
                **state,
                "final_response": f"Task completed with errors. Please check the results."
            }
    
    async def run(self, task: str) -> dict:
        """Execute task"""
        print(f"\n[START] Starting task: {task}\n")
        
        initial_state = AgentState(
            messages=[],
            task=task,
            plan=[],
            current_step=0,
            tool_results={},
            context={},
            error_count=0,
            needs_clarification=False,
            final_response=""
        )
        
        try:
            # Execute graph - need to handle sync vs async
            result = await self._run_graph_async(initial_state)
            
            # Store conversation
            self.rag_system.store_conversation(
                task=task,
                response=result.get("final_response", ""),
                metadata={"success": result.get("error_count", 0) == 0}
            )
            
            return result
        except Exception as e:
            print(f"[ERROR] Orchestration error: {e}")
            return {
                "success": False,
                "error": str(e),
                "final_response": f"Error executing task: {e}"
            }
    
    async def _run_graph_async(self, initial_state):
        """Run the graph asynchronously"""
        # LangGraph invoke returns the final state
        # We need to handle the async execution of steps
        current_state = initial_state
        
        # Manually execute the graph steps
        current_state = self._understand_task(current_state)
        current_state = self._create_plan(current_state)
        
        # Execute all steps
        while current_state["current_step"] < len(current_state.get("plan", [])):
            current_state = await self._execute_step(current_state)
            current_state = self._verify_result(current_state)
            
            decision = self._should_continue(current_state)
            if decision == "complete":
                break
            elif decision == "clarify":
                break
        
        # Final reflection
        current_state = self._reflect_and_learn(current_state)
        
        return current_state

