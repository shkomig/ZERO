"""
Zero Agent - Main Entry Point
AI-Powered Autonomous Agent System
"""

import asyncio
import sys
import os
from pathlib import Path

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        # Set environment variable for Python 3.7+
        os.environ['PYTHONUTF8'] = '1'
        # Reconfigure stdout/stderr to use UTF-8
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass  # If reconfiguration fails, continue with ASCII-only output

# Add zero_agent to path
sys.path.insert(0, str(Path(__file__).parent))

from zero_agent.core.orchestrator import ZeroOrchestrator
from zero_agent.models.model_router import router
from zero_agent.core.tool_executor import ToolExecutor
from zero_agent.rag.memory import RAGMemorySystem
from zero_agent.ui.cli import CLI
from zero_agent.core.config import config


async def main():
    """Initialize and run Zero Agent"""
    
    print("[START] Zero Agent - Starting up...")
    print()
    
    # Initialize components
    print("[LOAD] Loading models...")
    model_router = router
    print(f"   {model_router}")
    
    print("\n[INIT] Initializing tools...")
    tool_executor = ToolExecutor()
    
    print("\n[MEMORY] Loading RAG system...")
    rag_system = RAGMemorySystem()
    
    print("\n[BUILD] Building orchestrator...")
    orchestrator = ZeroOrchestrator(
        model_router=model_router,
        tool_executor=tool_executor,
        rag_system=rag_system
    )
    
    print("\n[OK] Zero Agent ready!\n")
    
    # Start CLI
    cli = CLI(orchestrator)
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[EXIT] Shutting down Zero Agent...")
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()

