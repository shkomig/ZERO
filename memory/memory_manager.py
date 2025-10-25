"""
Unified Memory Manager
======================
The brain of Zero's memory system
Combines short-term (JSON) + long-term (RAG)
Domain-agnostic - works with everything!
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import sys

# Import memory components
try:
    from .short_term_memory import ShortTermMemory, ConversationEntry
    from .rag_connector import RAGConnector, RAGContextBuilder
except ImportError:
    from short_term_memory import ShortTermMemory, ConversationEntry
    from rag_connector import RAGConnector, RAGContextBuilder


class MemoryManager:
    """
    Unified memory manager for Zero Agent
    Intelligently combines multiple memory sources
    """
    
    def __init__(self, 
                 memory_dir: Path = Path("memory"),
                 rag_url: str = "http://localhost:8000",
                 enable_rag: bool = True):
        
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(exist_ok=True)
        
        # Initialize short-term memory
        print("   [Memory] Initializing short-term memory...")
        self.short_term = ShortTermMemory(memory_dir)
        print("   [Memory] ✓ Short-term memory ready")
        
        # Initialize RAG connector
        self.rag_enabled = enable_rag
        if enable_rag:
            print("   [Memory] Connecting to RAG system...")
            try:
                self.rag = RAGConnector(rag_url)
                self.rag_builder = RAGContextBuilder(self.rag)
                
                if self.rag.is_available():
                    print("   [Memory] ✓ RAG system connected")
                else:
                    print("   [Memory] ⚠️  RAG system not available (will continue without it)")
                    self.rag_enabled = False
            except Exception as e:
                print(f"   [Memory] ⚠️  RAG connection failed: {str(e)}")
                self.rag_enabled = False
        else:
            print("   [Memory] RAG disabled")
        
        print("   [Memory] Memory system initialized!\n")
    
    def remember(self,
                user_message: str,
                assistant_message: str,
                model_used: str,
                context_score: float = 0.0,
                topic: Optional[str] = None) -> ConversationEntry:
        """
        Remember a conversation
        Stores in both short-term and optionally RAG
        
        Args:
            user_message: What user said
            assistant_message: What Zero replied
            model_used: Which model was used
            context_score: Relevance score
            topic: Topic category (optional)
            
        Returns:
            ConversationEntry
        """
        # Store in short-term memory
        entry = self.short_term.add_conversation(
            user_message=user_message,
            assistant_message=assistant_message,
            model_used=model_used,
            context_score=context_score,
            topic=topic
        )
        
        # Optionally index in RAG for long-term
        if self.rag_enabled and self.rag.is_available():
            try:
                self.rag.index_conversation(
                    user_message=user_message,
                    assistant_message=assistant_message,
                    metadata={
                        "timestamp": entry.timestamp,
                        "model": model_used,
                        "topic": topic
                    }
                )
            except:
                pass  # Not critical if indexing fails
        
        return entry
    
    def recall(self, 
               query: str,
               hours: int = 24,
               use_rag: bool = True) -> Dict[str, Any]:
        """
        Recall relevant information
        Searches both short-term and RAG
        
        Args:
            query: What to search for
            hours: Time window for short-term search
            use_rag: Whether to search RAG
            
        Returns:
            Dict with recent conversations and RAG results
        """
        results = {
            "recent_conversations": [],
            "rag_context": None,
            "preferences": {},
            "facts": []
        }
        
        # Search short-term memory
        results["recent_conversations"] = self.short_term.search_conversations(
            query, 
            limit=3
        )
        
        # Get preferences
        results["preferences"] = self.short_term.get_all_preferences()
        
        # Get relevant facts
        results["facts"] = self.short_term.get_relevant_facts(query, limit=3)
        
        # Search RAG if enabled
        if use_rag and self.rag_enabled and self.rag.is_available():
            # Check if we should use RAG for this query
            if self.rag_builder.should_use_rag(query):
                results["rag_context"] = self.rag.get_context(query, max_chars=2000)
        
        return results
    
    def build_context(self,
                     current_task: str,
                     task_type: Optional[str] = None,
                     include_recent: bool = True,
                     include_preferences: bool = True,
                     include_rag: bool = True,
                     max_length: int = 3000) -> str:
        """
        Build complete context for the model
        Intelligently combines all memory sources
        
        Args:
            current_task: Current user query/task
            task_type: Type of task (coding, analysis, etc.)
            include_recent: Include recent conversations
            include_preferences: Include user preferences
            include_rag: Search RAG system
            max_length: Maximum context length
            
        Returns:
            Formatted context string
        """
        context_parts = []
        current_length = 0
        
        # 1. User preferences (highest priority)
        if include_preferences:
            prefs = self.short_term.get_all_preferences()
            if prefs:
                pref_text = "\n🎯 User Preferences:\n"
                for key, value in prefs.items():
                    pref_text += f"  • {key}: {value}\n"
                
                if current_length + len(pref_text) < max_length:
                    context_parts.append(pref_text)
                    current_length += len(pref_text)
        
        # 2. Recent relevant conversations
        if include_recent:
            recent = self.short_term.search_conversations(current_task, limit=2)
            if recent:
                recent_text = "\n💭 Recent relevant discussions:\n"
                for conv in recent:
                    snippet = f"  • {conv['user_message'][:80]}...\n"
                    if current_length + len(snippet) < max_length:
                        recent_text += snippet
                        current_length += len(snippet)
                
                if len(recent_text) > 50:  # Has content
                    context_parts.append(recent_text)
        
        # 3. RAG context (if available and relevant)
        if include_rag and self.rag_enabled:
            try:
                if self.rag_builder.should_use_rag(current_task):
                    rag_context = self.rag_builder.build_context(
                        current_task, 
                        task_type
                    )
                    if rag_context and current_length + len(rag_context) < max_length:
                        context_parts.append(f"\n{rag_context}")
                        current_length += len(rag_context)
            except:
                pass  # Continue without RAG context
        
        # 4. Learned facts
        facts = self.short_term.get_relevant_facts(current_task, limit=2)
        if facts:
            facts_text = "\n📝 Relevant facts:\n"
            for fact in facts:
                snippet = f"  • {fact['fact'][:80]}...\n"
                if current_length + len(snippet) < max_length:
                    facts_text += snippet
                    current_length += len(snippet)
            
            if len(facts_text) > 30:
                context_parts.append(facts_text)
        
        # Combine all parts
        if context_parts:
            full_context = "\n".join(context_parts)
            return f"═══ CONTEXT ═══\n{full_context}\n═══════════════\n"
        
        return ""
    
    def learn_preference(self, key: str, value: Any, confidence: float = 1.0):
        """
        Explicitly teach Zero a preference
        """
        self.short_term.add_preference(key, value, confidence)
    
    def learn_fact(self, fact: str, relevance: float = 1.0):
        """
        Explicitly teach Zero a fact
        """
        self.short_term.add_fact(
            fact=fact,
            source="explicit_learning",
            relevance=relevance
        )
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive memory statistics
        """
        stats = self.short_term.get_statistics()
        
        # Add RAG stats if available
        if self.rag_enabled and self.rag.is_available():
            rag_stats = self.rag.get_statistics()
            if rag_stats:
                stats["rag_system"] = rag_stats
            else:
                stats["rag_system"] = "available"
        else:
            stats["rag_system"] = "unavailable"
        
        return stats
    
    def clear_old_memories(self, days: int = 30):
        """
        Clear old short-term memories
        (RAG keeps everything)
        """
        self.short_term.clear_old_data(days)
    
    def export_memories(self, filepath: Path):
        """
        Export all memories to a file
        """
        import json
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "statistics": self.get_memory_stats(),
            "conversations": self.short_term.conversations,
            "preferences": self.short_term.preferences,
            "facts": self.short_term.facts
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def summarize_session(self, hours: int = 24) -> str:
        """
        Generate a summary of recent session
        """
        recent = self.short_term.get_recent_conversations(hours=hours)
        stats = self.short_term.get_statistics()
        
        if not recent:
            return "No recent activity"
        
        summary = f"""
📊 Session Summary (last {hours} hours)

Conversations: {len(recent)}
Topics covered:
"""
        
        topics = set()
        for conv in recent:
            topic = conv.get('topic', 'general')
            topics.add(topic)
        
        for topic in topics:
            count = sum(1 for c in recent if c.get('topic') == topic)
            summary += f"  • {topic}: {count} conversation(s)\n"
        
        models_used = set(c['model_used'] for c in recent)
        summary += f"\nModels used: {', '.join(models_used)}"
        
        return summary


# Test
if __name__ == "__main__":
    print("="*70)
    print("Unified Memory Manager Test")
    print("="*70)
    
    # Initialize
    memory = MemoryManager(
        memory_dir=Path("memory"),
        rag_url="http://localhost:8000",
        enable_rag=True
    )
    
    # Test 1: Remember a conversation
    print("\n1. Testing remember...")
    memory.remember(
        user_message="Explain machine learning",
        assistant_message="Machine learning is...",
        model_used="smart",
        context_score=0.8,
        topic="AI"
    )
    print("   ✓ Conversation remembered")
    
    # Test 2: Recall
    print("\n2. Testing recall...")
    results = memory.recall("machine learning")
    print(f"   ✓ Found {len(results['recent_conversations'])} relevant conversations")
    print(f"   ✓ Preferences: {len(results['preferences'])}")
    print(f"   ✓ Facts: {len(results['facts'])}")
    print(f"   ✓ RAG context: {'Yes' if results['rag_context'] else 'No'}")
    
    # Test 3: Build context
    print("\n3. Testing context building...")
    context = memory.build_context(
        current_task="Tell me about neural networks",
        task_type="explanation"
    )
    print(f"   ✓ Built context ({len(context)} chars)")
    if context:
        print(f"\n{context}")
    
    # Test 4: Statistics
    print("\n4. Memory statistics:")
    stats = memory.get_memory_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test 5: Session summary
    print("\n5. Session summary:")
    summary = memory.summarize_session(hours=24)
    print(summary)
    
    print("\n" + "="*70)
    print("✅ Memory Manager ready!")
    print("\nFeatures:")
    print("  ✓ Short-term memory (JSON)")
    print("  ✓ Long-term memory (RAG)")
    print("  ✓ Intelligent context building")
    print("  ✓ Domain-agnostic")
    print("  ✓ Graceful degradation")
