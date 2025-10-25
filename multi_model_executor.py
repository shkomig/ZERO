"""
Multi-Model Execution Engine
=============================
Execute tasks using multiple models in sequence or parallel
Perfect for: Strategy → Code, Analysis → Implementation
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time


@dataclass
class ModelExecution:
    """Single model execution result"""
    model: str
    input: str
    output: str
    elapsed_time: float
    tokens_per_sec: float


class MultiModelExecutor:
    """
    Execute complex tasks using multiple models
    """
    
    def __init__(self, llm, router):
        self.llm = llm
        self.router = router
        
    def execute_sequential(self, 
                          task: str, 
                          models: List[str],
                          verbose: bool = True) -> Dict[str, Any]:
        """
        Execute task using multiple models in sequence
        
        Args:
            task: Original task
            models: List of models in execution order ["smart", "coder"]
            verbose: Print progress
            
        Returns:
            {
                "success": bool,
                "task": str,
                "executions": List[ModelExecution],
                "final_result": str,
                "total_time": float
            }
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"🔥 MULTI-MODEL EXECUTION")
            print(f"{'='*70}")
            print(f"Task: {task}")
            print(f"Pipeline: {' → '.join([m.upper() for m in models])}")
            print(f"{'='*70}\n")
        
        executions = []
        current_input = task
        start_time = time.time()
        
        for i, model in enumerate(models, 1):
            if verbose:
                print(f"[Step {i}/{len(models)}] Executing with {model.upper()}...")
            
            # Execute model
            exec_result = self._execute_single(
                model=model,
                input_text=current_input,
                step_num=i,
                total_steps=len(models),
                verbose=verbose
            )
            
            executions.append(exec_result)
            
            # Prepare input for next model
            if i < len(models):
                current_input = self._prepare_next_input(
                    original_task=task,
                    previous_output=exec_result.output,
                    next_model=models[i],
                    verbose=verbose
                )
        
        total_time = time.time() - start_time
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"✅ MULTI-MODEL EXECUTION COMPLETE")
            print(f"{'='*70}")
            print(f"Total time: {total_time:.1f}s")
            print(f"Models used: {len(executions)}")
            print(f"{'='*70}\n")
        
        return {
            "success": True,
            "task": task,
            "executions": executions,
            "final_result": executions[-1].output,
            "total_time": total_time
        }
    
    def _execute_single(self, 
                       model: str, 
                       input_text: str,
                       step_num: int,
                       total_steps: int,
                       verbose: bool) -> ModelExecution:
        """Execute single model"""
        
        # Build context-aware prompt
        if step_num == 1:
            # First model - gets original task
            prompt = input_text
        else:
            # Subsequent models - get context + task
            prompt = input_text
        
        # Execute
        start = time.time()
        output = self.llm.generate(prompt, model=model, max_tokens=4096)
        elapsed = time.time() - start
        
        # Calculate speed
        tokens = len(output.split())
        tokens_per_sec = tokens / elapsed if elapsed > 0 else 0
        
        if verbose:
            print(f"   ✓ Completed in {elapsed:.1f}s ({tokens_per_sec:.0f} tokens/s)")
            print(f"   Output preview: {output[:100]}...")
        
        return ModelExecution(
            model=model,
            input=input_text,
            output=output,
            elapsed_time=elapsed,
            tokens_per_sec=tokens_per_sec
        )
    
    def _prepare_next_input(self,
                           original_task: str,
                           previous_output: str,
                           next_model: str,
                           verbose: bool) -> str:
        """
        Prepare input for next model in pipeline
        """
        if verbose:
            print(f"\n   Preparing input for {next_model.upper()}...")
        
        # Strategy: SMART → CODER
        if next_model == "coder":
            prompt = f"""Based on this strategy/analysis:

{previous_output}

Now implement this in Python code. Create clean, well-documented code that follows the strategy above.

Original task: {original_task}

Your implementation:"""
            
        # Code: CODER → SMART
        elif next_model == "smart":
            prompt = f"""Here is the code implementation:

{previous_output}

Now provide:
1. Detailed explanation of how this code works
2. Strategic insights and recommendations
3. Potential improvements or considerations

Original task: {original_task}

Your analysis:"""
            
        # Default: pass context forward
        else:
            prompt = f"""Previous output:

{previous_output}

Continue working on: {original_task}

Your response:"""
        
        return prompt
    
    def auto_execute(self, task: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Automatically determine if multi-model is needed and execute
        
        Returns:
            Same format as execute_sequential, with added "mode" field
        """
        # Get routing decision
        routing = self.router.route_with_reasoning(task)
        
        # Check if multi-model is suggested
        multi_models = self.router.suggest_multi_model(task)
        
        if multi_models:
            if verbose:
                print(f"\n🎯 Auto-mode: Multi-model execution detected")
                print(f"   Reason: {routing['reasoning']}")
            
            result = self.execute_sequential(task, multi_models, verbose)
            result["mode"] = "multi-model"
            result["models_used"] = multi_models
            
        else:
            if verbose:
                print(f"\n⚡ Auto-mode: Single model execution")
                print(f"   Model: {routing['model'].upper()}")
                print(f"   Reason: {routing['reasoning']}")
            
            # Single model execution
            exec_result = self._execute_single(
                model=routing['model'],
                input_text=task,
                step_num=1,
                total_steps=1,
                verbose=verbose
            )
            
            result = {
                "success": True,
                "task": task,
                "executions": [exec_result],
                "final_result": exec_result.output,
                "total_time": exec_result.elapsed_time,
                "mode": "single-model",
                "models_used": [routing['model']]
            }
        
        return result
    
    def get_execution_summary(self, result: Dict[str, Any]) -> str:
        """
        Generate human-readable summary of execution
        """
        summary = []
        summary.append(f"\n{'='*70}")
        summary.append(f"📊 EXECUTION SUMMARY")
        summary.append(f"{'='*70}")
        
        summary.append(f"\nTask: {result['task'][:100]}...")
        summary.append(f"Mode: {result['mode'].upper()}")
        summary.append(f"Models: {' → '.join([m.upper() for m in result['models_used']])}")
        summary.append(f"Total time: {result['total_time']:.1f}s")
        
        summary.append(f"\n{'─'*70}")
        summary.append("Model Breakdown:")
        summary.append(f"{'─'*70}")
        
        for i, exec in enumerate(result['executions'], 1):
            summary.append(f"\n{i}. {exec.model.upper()}")
            summary.append(f"   Time: {exec.elapsed_time:.1f}s")
            summary.append(f"   Speed: {exec.tokens_per_sec:.0f} tokens/s")
            summary.append(f"   Output: {len(exec.output)} chars")
        
        summary.append(f"\n{'='*70}")
        
        return "\n".join(summary)


# Test
if __name__ == "__main__":
    from multi_model_llm import MultiModelLLM
    from router_context_aware import ContextAwareRouter
    
    print("Multi-Model Execution Engine Test")
    print("="*70)
    
    # Initialize
    llm = MultiModelLLM()
    router = ContextAwareRouter(llm)
    executor = MultiModelExecutor(llm, router)
    
    # Test case: Strategy + Implementation
    task = "Design a simple moving average crossover trading strategy and implement it in Python"
    
    print("\n🧪 Testing auto-execution (should detect multi-model need):\n")
    
    result = executor.auto_execute(task, verbose=True)
    
    # Print summary
    print(executor.get_execution_summary(result))
    
    print("\n" + "="*70)
    print("✅ Multi-Model Executor ready!")
    print("\nCapabilities:")
    print("  ✓ Sequential execution (Strategy → Code)")
    print("  ✓ Auto-detection of multi-model needs")
    print("  ✓ Context passing between models")
    print("  ✓ Performance tracking")
