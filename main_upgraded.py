"""
Zero Agent - UPGRADED! 🚀
==========================
✓ Context-Aware Router (understands depth vs breadth)
✓ Multi-Model Execution (Strategy → Code)
✓ Streaming Responses (3x faster feel)
"""

import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from streaming_llm import StreamingMultiModelLLM
from router_context_aware import ContextAwareRouter
from multi_model_executor import MultiModelExecutor
from orchestrator_multi_model import MultiModelOrchestrator
from tool_filesystem import FileSystemTool
from tool_websearch import WebSearchTool
from tool_codeexecutor import CodeExecutorTool


def main():
    """
    Main entry point for Zero Agent UPGRADED
    """
    print("\n" + "="*70)
    print("🚀 Zero Agent - UPGRADED EDITION")
    print("="*70)
    print("\n✨ NEW FEATURES:")
    print("   • Context-Aware Router (understands strategy vs code)")
    print("   • Multi-Model Execution (deep thinking + implementation)")
    print("   • Streaming Responses (real-time feedback)")
    print("="*70)
    
    # Setup
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    
    print(f"\nWorkspace: {workspace.absolute()}")
    print("Ollama: http://localhost:11434")
    
    # Initialize Streaming Multi-Model LLM
    print("\n[INIT] Setting up Streaming LLM...")
    llm = StreamingMultiModelLLM(default_model="fast")
    
    if not llm.test_connection(verbose=False):
        print("[ERROR] Cannot connect to Ollama!")
        return
    
    print("[OK] Connected - Streaming enabled!")
    
    # Initialize Context-Aware Router
    print("\n[INIT] Setting up Context-Aware Router...")
    router = ContextAwareRouter(llm)
    print("[OK] Router ready - understands context depth!")
    
    # Initialize Multi-Model Executor
    print("\n[INIT] Setting up Multi-Model Executor...")
    executor = MultiModelExecutor(llm, router)
    print("[OK] Executor ready - can use multiple models!")
    
    # Initialize Tools
    print("\n[INIT] Loading tools...")
    tools = {
        "filesystem": FileSystemTool(workspace),
        "websearch": WebSearchTool(),
        "codeexecutor": CodeExecutorTool(workspace)
    }
    print(f"[OK] Loaded {len(tools)} tools")
    
    # Show capabilities
    print("\n" + "="*70)
    print("✨ Zero Agent Capabilities:")
    print("="*70)
    
    print("\n🧠 SMART ROUTING:")
    print("   • 'Design trading strategy' → deepseek-r1 (smart)")
    print("   • 'Fix bug in code' → qwen2.5-coder (coder)")
    print("   • 'What is 2+2?' → llama3.1 (fast)")
    
    print("\n🔥 MULTI-MODEL EXECUTION:")
    print("   • 'Create strategy AND implement' → smart → coder")
    print("   • Automatic detection of complex tasks")
    print("   • Seamless context passing")
    
    print("\n⚡ STREAMING:")
    print("   • Real-time response display")
    print("   • Feels 3x faster!")
    print("   • No more waiting")
    
    print("\n📁 TOOLS:")
    print("   • FileSystem - create, read, delete")
    print("   • WebSearch - search internet")
    print("   • CodeExecutor - run Python/Bash")
    
    # Interactive loop
    print("\n" + "="*70)
    print("Ready! Try these examples:")
    print("\n💡 Simple:")
    print("   'What is the capital of France?'")
    print("\n💡 Code:")
    print("   'Write a Python function to calculate fibonacci'")
    print("\n💡 Strategy (will use SMART model!):")
    print("   'Design a risk management strategy for trading'")
    print("\n💡 Multi-Model (will use both!):")
    print("   'Create trading signals strategy and implement in Python'")
    
    print("\n🎮 Commands:")
    print("   'stats'   - show usage statistics")
    print("   'models'  - show available models")
    print("   'history' - execution history")
    print("   'stream on/off' - toggle streaming")
    print("   'exit'    - quit")
    
    print("\n🔧 Force model:")
    print("   Add @fast, @coder, @smart, or @balanced")
    print("   Example: 'Explain AI @smart'")
    
    print("="*70 + "\n")
    
    # State
    streaming_enabled = True
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'stats':
                print_stats(llm, executor)
                continue
            
            if user_input.lower() == 'models':
                llm.print_models_info()
                continue
            
            if user_input.lower().startswith('stream '):
                cmd = user_input.lower().split()[1]
                if cmd == 'on':
                    streaming_enabled = True
                    print("✓ Streaming enabled")
                elif cmd == 'off':
                    streaming_enabled = False
                    print("✓ Streaming disabled")
                continue
            
            # Check for forced model
            force_model = None
            for model_type in ['@fast', '@coder', '@smart', '@balanced']:
                if model_type in user_input.lower():
                    force_model = model_type[1:]
                    user_input = user_input.lower().replace(model_type, '').strip()
                    break
            
            # Execute task
            print()
            
            if force_model:
                # Single model forced
                result = execute_single_with_streaming(
                    llm, user_input, force_model, streaming_enabled
                )
            else:
                # Auto-detect (may use multi-model)
                result = execute_auto_with_streaming(
                    executor, user_input, streaming_enabled
                )
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


def execute_single_with_streaming(llm, task: str, model: str, streaming: bool) -> str:
    """Execute with single model and streaming"""
    print(f"[FORCED] Using {model.upper()}")
    
    if streaming:
        result = llm.generate(task, model=model, stream_to_console=True)
    else:
        result = llm.generate(task, model=model)
        print(f"\n✅ {result}\n")
    
    return result


def execute_auto_with_streaming(executor, task: str, streaming: bool) -> Dict:
    """Execute with auto-detection and streaming"""
    
    # Get routing decision
    routing = executor.router.route_with_reasoning(task)
    
    print(f"[AUTO] Selected: {routing['model'].upper()}")
    print(f"       Reason: {routing['reasoning']}")
    print(f"       Context Score: {routing['context_score']:.2f}")
    
    if routing['requires_multi_model']:
        print(f"       🔥 Multi-model execution activated!")
    
    # Check if multi-model
    multi_models = executor.router.suggest_multi_model(task)
    
    if multi_models and streaming:
        # Multi-model with streaming
        print(f"\n{'='*70}")
        print(f"🔥 MULTI-MODEL PIPELINE: {' → '.join([m.upper() for m in multi_models])}")
        print(f"{'='*70}")
        
        full_results = []
        
        for i, model in enumerate(multi_models, 1):
            print(f"\n[STEP {i}/{len(multi_models)}] {model.upper()}")
            
            if i == 1:
                # First model gets original task
                prompt = task
            else:
                # Subsequent models get context
                prev_result = full_results[-1]
                if model == "coder":
                    prompt = f"""Based on this strategy/analysis:

{prev_result}

Now implement in Python. Original task: {task}

Your code:"""
                else:
                    prompt = f"""Previous output:

{prev_result}

Continue: {task}

Your response:"""
            
            # Stream this step
            result = executor.llm.generate(prompt, model=model, stream_to_console=True)
            full_results.append(result)
        
        print(f"\n{'='*70}")
        print("✅ MULTI-MODEL EXECUTION COMPLETE")
        print(f"{'='*70}\n")
        
        return {"results": full_results}
        
    elif multi_models:
        # Multi-model without streaming
        result = executor.execute_sequential(task, multi_models, verbose=True)
        print(f"\n✅ {result['final_result']}\n")
        return result
        
    else:
        # Single model
        if streaming:
            result = executor.llm.generate(
                task, 
                model=routing['model'], 
                stream_to_console=True
            )
        else:
            result = executor.llm.generate(task, model=routing['model'])
            print(f"\n✅ {result}\n")
        
        return {"result": result}


def print_stats(llm, executor):
    """Print usage statistics"""
    print("\n" + "="*70)
    print("📊 USAGE STATISTICS")
    print("="*70)
    
    stats = llm.get_stats()
    total = sum(stats.values())
    
    if total == 0:
        print("\nNo requests yet")
        return
    
    print("\nModel Usage:")
    for model, count in stats.items():
        percentage = (count / total * 100) if total > 0 else 0
        bar_length = int(percentage / 2)
        bar = "█" * bar_length + "░" * (50 - bar_length)
        print(f"  {model.upper():12} [{bar}] {count:3} ({percentage:5.1f}%)")
    
    print(f"\nTotal requests: {total}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
