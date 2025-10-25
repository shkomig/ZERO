"""
Zero Agent - with MEMORY! 🧠
============================
✓ Context-Aware Router
✓ Multi-Model Execution  
✓ Streaming Responses
✓ MEMORY SYSTEM (Short-term + RAG)
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

# Make sure we can import from current directory
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "memory"))

from streaming_llm import StreamingMultiModelLLM
from router_context_aware import ContextAwareRouter
from multi_model_executor import MultiModelExecutor

# Import memory system
MEMORY_AVAILABLE = False
memory_error = None

try:
    # Import components directly
    from memory.short_term_memory import ShortTermMemory, ConversationEntry
    from memory.rag_connector import RAGConnector, RAGContextBuilder  
    from memory.memory_manager import MemoryManager
    MEMORY_AVAILABLE = True
    print("✓ Memory system loaded successfully!")
except ImportError as e:
    memory_error = str(e)
    print(f"⚠️  Memory system not available: {e}")
    print("   Continuing without memory (all other features work!)")
except Exception as e:
    memory_error = str(e)
    print(f"⚠️  Memory system error: {e}")
    print("   Continuing without memory (all other features work!)")


def main():
    """
    Main entry point for Zero Agent with Memory
    """
    print("\n" + "="*70)
    print("🧠 Zero Agent - MEMORY EDITION")
    print("="*70)
    print("\n✨ FEATURES:")
    print("   • Context-Aware Router")
    print("   • Multi-Model Execution")
    print("   • Streaming Responses")
    if MEMORY_AVAILABLE:
        print("   • 🧠 MEMORY SYSTEM (learns from conversations!)")
    else:
        print(f"   • Memory: Unavailable ({memory_error})")
    print("="*70)
    
    # Setup
    workspace = Path("workspace")
    workspace.mkdir(exist_ok=True)
    
    print(f"\nWorkspace: {workspace.absolute()}")
    print("Ollama: http://localhost:11434")
    
    # Initialize LLM
    print("\n[INIT] Setting up Streaming LLM...")
    llm = StreamingMultiModelLLM(default_model="fast")
    
    if not llm.test_connection(verbose=False):
        print("[ERROR] Cannot connect to Ollama!")
        return
    
    print("[OK] Connected - Streaming enabled!")
    
    # Initialize Router
    print("\n[INIT] Setting up Context-Aware Router...")
    router = ContextAwareRouter(llm)
    print("[OK] Router ready!")
    
    # Initialize Executor
    print("\n[INIT] Setting up Multi-Model Executor...")
    executor = MultiModelExecutor(llm, router)
    print("[OK] Executor ready!")
    
    # Initialize Memory System
    memory = None
    if MEMORY_AVAILABLE:
        print("\n[INIT] Setting up Memory System...")
        try:
            memory = MemoryManager(
                memory_dir=workspace / "memory",
                rag_url="http://localhost:8000",
                enable_rag=True
            )
            print("[OK] Memory system initialized!")
        except Exception as e:
            print(f"[WARN] Memory system failed: {e}")
            print("[INFO] Continuing without memory...")
            memory = None
    
    # Show capabilities
    print("\n" + "="*70)
    print("✨ Zero Agent Capabilities:")
    print("="*70)
    
    if memory:
        print("\n🧠 MEMORY:")
        print("   • Remembers all conversations")
        print("   • Learns your preferences")
        print("   • Recalls relevant past discussions")
        print("   • Searches your documents (RAG)")
    
    print("\n🎮 Commands:")
    print("   'stats'   - usage statistics")
    if memory:
        print("   'memory'  - memory statistics")
        print("   'context' - show current context")
        print("   'summary' - session summary")
        print("   'forget'  - clear old memories")
    print("   'stream on/off' - toggle streaming")
    print("   'exit'    - quit")
    
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
                if memory:
                    print("\n📊 Final session summary:")
                    print(memory.summarize_session(hours=24))
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'stats':
                print_stats(llm, executor, memory)
                continue
            
            if user_input.lower() == 'memory' and memory:
                print_memory_stats(memory)
                continue
            
            if user_input.lower() == 'context' and memory:
                show_context(memory, "current situation")
                continue
            
            if user_input.lower() == 'summary' and memory:
                print("\n" + memory.summarize_session(hours=24) + "\n")
                continue
            
            if user_input.lower() == 'forget' and memory:
                memory.clear_old_memories(days=7)
                print("✓ Cleared memories older than 7 days\n")
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
            
            # Build context from memory
            context = ""
            if memory:
                context = memory.build_context(
                    current_task=user_input,
                    task_type=None,
                    max_length=2000
                )
            
            # Execute task with memory-enhanced context
            print()
            
            if force_model:
                result_text = execute_with_memory(
                    executor, user_input, force_model, 
                    streaming_enabled, memory, context
                )
            else:
                result_text = execute_auto_with_memory(
                    executor, user_input, streaming_enabled, 
                    memory, context
                )
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


def execute_with_memory(executor, task: str, model: str, 
                       streaming: bool, memory, context: str) -> str:
    """Execute with single model and memory"""
    print(f"[FORCED] Using {model.upper()}")
    
    # Add context if available
    prompt = f"{context}\n{task}" if context else task
    
    if streaming:
        result = executor.llm.generate(prompt, model=model, stream_to_console=True)
    else:
        result = executor.llm.generate(prompt, model=model)
        print(f"\n✅ {result}\n")
    
    # Remember this conversation
    if memory:
        memory.remember(
            user_message=task,
            assistant_message=result,
            model_used=model
        )
    
    return result


def execute_auto_with_memory(executor, task: str, streaming: bool,
                            memory, context: str) -> Dict:
    """Execute with auto-detection and memory"""
    
    # Add context to task
    full_task = f"{context}\n{task}" if context else task
    
    # Get routing decision (on original task, not with context)
    routing = executor.router.route_with_reasoning(task)
    
    print(f"[AUTO] Selected: {routing['model'].upper()}")
    print(f"       Reason: {routing['reasoning']}")
    
    if context:
        print(f"       📝 Using context from memory")
    
    if routing['requires_multi_model']:
        print(f"       🔥 Multi-model execution activated!")
    
    # Execute
    multi_models = executor.router.suggest_multi_model(task)
    
    if multi_models and streaming:
        # Multi-model with streaming
        print(f"\n{'='*70}")
        print(f"🔥 MULTI-MODEL: {' → '.join([m.upper() for m in multi_models])}")
        print(f"{'='*70}")
        
        full_results = []
        
        for i, model in enumerate(multi_models, 1):
            print(f"\n[STEP {i}/{len(multi_models)}] {model.upper()}")
            
            if i == 1:
                prompt = full_task
            else:
                prev_result = full_results[-1]
                if model == "coder":
                    prompt = f"{context}\n\nBased on: {prev_result}\n\nImplement: {task}"
                else:
                    prompt = f"{context}\n\nPrevious: {prev_result}\n\nContinue: {task}"
            
            result = executor.llm.generate(prompt, model=model, stream_to_console=True)
            full_results.append(result)
        
        final_result = full_results[-1]
        
        print(f"\n{'='*70}")
        print("✅ MULTI-MODEL COMPLETE")
        print(f"{'='*70}\n")
        
    else:
        # Single model
        if streaming:
            final_result = executor.llm.generate(
                full_task, 
                model=routing['model'], 
                stream_to_console=True
            )
        else:
            final_result = executor.llm.generate(full_task, model=routing['model'])
            print(f"\n✅ {final_result}\n")
    
    # Remember conversation
    if memory:
        memory.remember(
            user_message=task,
            assistant_message=final_result,
            model_used=routing['model']
        )
    
    return {"result": final_result}


def print_stats(llm, executor, memory):
    """Print usage statistics"""
    print("\n" + "="*70)
    print("📊 SYSTEM STATISTICS")
    print("="*70)
    
    # Model stats
    stats = llm.get_stats()
    total = sum(stats.values())
    
    if total > 0:
        print("\n🤖 Model Usage:")
        for model, count in stats.items():
            percentage = (count / total * 100)
            bar_length = int(percentage / 2)
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"  {model.upper():12} [{bar}] {count:3} ({percentage:5.1f}%)")
        print(f"\n  Total: {total} requests")
    
    # Memory stats
    if memory:
        print("\n🧠 Memory Statistics:")
        mem_stats = memory.get_memory_stats()
        print(f"  Conversations: {mem_stats['total_conversations']}")
        print(f"  Last 24h: {mem_stats['conversations_24h']}")
        print(f"  Preferences: {mem_stats['total_preferences']}")
        print(f"  Learned facts: {mem_stats['total_facts']}")
        print(f"  RAG system: {mem_stats['rag_system']}")
    
    print("="*70 + "\n")


def print_memory_stats(memory):
    """Print detailed memory statistics"""
    print("\n" + "="*70)
    print("🧠 MEMORY DETAILS")
    print("="*70)
    
    stats = memory.get_memory_stats()
    
    print(f"\n📝 Conversations: {stats['total_conversations']}")
    print(f"   Recent (24h): {stats['conversations_24h']}")
    
    if stats['total_conversations'] > 0:
        print(f"   Oldest: {stats['oldest_conversation']}")
        print(f"   Newest: {stats['newest_conversation']}")
    
    print(f"\n🎯 Preferences: {stats['total_preferences']}")
    prefs = memory.short_term.get_all_preferences()
    for key, value in prefs.items():
        print(f"   • {key}: {value}")
    
    print(f"\n📚 Learned Facts: {stats['total_facts']}")
    for fact in memory.short_term.facts[-3:]:
        print(f"   • {fact['fact'][:60]}...")
    
    print(f"\n🔗 RAG System: {stats['rag_system']}")
    
    print("="*70 + "\n")


def show_context(memory, query: str):
    """Show what context would be built"""
    print("\n" + "="*70)
    print("📝 CONTEXT PREVIEW")
    print("="*70)
    
    context = memory.build_context(query, max_length=1500)
    
    if context:
        print(f"\n{context}")
    else:
        print("\nNo relevant context found")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
