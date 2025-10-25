"""
Zero Agent Memory System
========================
Unified memory system combining short-term and long-term storage

Usage:
    from memory import MemoryManager
    
    memory = MemoryManager()
    memory.remember(user_msg, assistant_msg, model)
    context = memory.build_context(current_task)
"""

from .memory_manager import MemoryManager
from .short_term_memory import ShortTermMemory, ConversationEntry, UserPreference, LearnedFact
from .rag_connector import RAGConnector, RAGContextBuilder, RAGResult

__all__ = [
    'MemoryManager',
    'ShortTermMemory',
    'RAGConnector',
    'RAGContextBuilder',
    'ConversationEntry',
    'UserPreference',
    'LearnedFact',
    'RAGResult'
]

__version__ = '1.0.0'
