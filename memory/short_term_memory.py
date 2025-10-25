"""
Short-Term Memory System
=========================
Fast JSON-based memory for current session
Stores: conversations, preferences, facts
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict


@dataclass
class ConversationEntry:
    """Single conversation exchange"""
    timestamp: str
    user_message: str
    assistant_message: str
    model_used: str
    context_score: float = 0.0
    topic: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class UserPreference:
    """User preference item"""
    key: str
    value: Any
    learned_at: str
    confidence: float = 1.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class LearnedFact:
    """Fact learned from conversations"""
    fact: str
    source: str  # Which conversation
    learned_at: str
    relevance: float = 1.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ShortTermMemory:
    """
    Short-term memory manager
    Fast access to recent conversations and learned patterns
    """
    
    def __init__(self, memory_dir: Path = Path("memory")):
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(exist_ok=True)
        
        self.conversations_file = self.memory_dir / "conversations.json"
        self.preferences_file = self.memory_dir / "preferences.json"
        self.facts_file = self.memory_dir / "facts.json"
        
        # Load existing data
        self.conversations = self._load_conversations()
        self.preferences = self._load_preferences()
        self.facts = self._load_facts()
    
    def add_conversation(self, 
                        user_message: str,
                        assistant_message: str,
                        model_used: str,
                        context_score: float = 0.0,
                        topic: Optional[str] = None) -> ConversationEntry:
        """
        Add new conversation to memory
        """
        entry = ConversationEntry(
            timestamp=datetime.now().isoformat(),
            user_message=user_message,
            assistant_message=assistant_message,
            model_used=model_used,
            context_score=context_score,
            topic=topic
        )
        
        self.conversations.append(entry.to_dict())
        self._save_conversations()
        
        # Auto-learn from this conversation
        self._auto_learn(entry)
        
        return entry
    
    def get_recent_conversations(self, 
                                 hours: int = 24,
                                 limit: int = 10) -> List[Dict]:
        """
        Get recent conversations within time window
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent = [
            conv for conv in self.conversations
            if datetime.fromisoformat(conv['timestamp']) > cutoff
        ]
        
        # Return most recent first
        return recent[-limit:][::-1]
    
    def search_conversations(self, 
                            query: str,
                            limit: int = 5) -> List[Dict]:
        """
        Simple keyword search in conversations
        """
        query_lower = query.lower()
        results = []
        
        for conv in reversed(self.conversations):
            # Search in both user and assistant messages
            if (query_lower in conv['user_message'].lower() or 
                query_lower in conv['assistant_message'].lower()):
                results.append(conv)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def add_preference(self, 
                      key: str, 
                      value: Any,
                      confidence: float = 1.0) -> UserPreference:
        """
        Add or update user preference
        """
        pref = UserPreference(
            key=key,
            value=value,
            learned_at=datetime.now().isoformat(),
            confidence=confidence
        )
        
        # Update if exists, add if new
        existing_idx = next(
            (i for i, p in enumerate(self.preferences) 
             if p['key'] == key),
            None
        )
        
        if existing_idx is not None:
            self.preferences[existing_idx] = pref.to_dict()
        else:
            self.preferences.append(pref.to_dict())
        
        self._save_preferences()
        return pref
    
    def get_preference(self, key: str) -> Optional[Any]:
        """
        Get user preference value
        """
        pref = next(
            (p for p in self.preferences if p['key'] == key),
            None
        )
        return pref['value'] if pref else None
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """
        Get all preferences as dict
        """
        return {p['key']: p['value'] for p in self.preferences}
    
    def add_fact(self, 
                 fact: str,
                 source: str,
                 relevance: float = 1.0) -> LearnedFact:
        """
        Add learned fact
        """
        fact_entry = LearnedFact(
            fact=fact,
            source=source,
            learned_at=datetime.now().isoformat(),
            relevance=relevance
        )
        
        # Avoid duplicates
        if not any(f['fact'].lower() == fact.lower() for f in self.facts):
            self.facts.append(fact_entry.to_dict())
            self._save_facts()
        
        return fact_entry
    
    def get_relevant_facts(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Get facts relevant to query
        """
        query_lower = query.lower()
        relevant = [
            f for f in self.facts
            if any(word in f['fact'].lower() 
                   for word in query_lower.split())
        ]
        
        # Sort by relevance
        relevant.sort(key=lambda x: x['relevance'], reverse=True)
        return relevant[:limit]
    
    def _auto_learn(self, conversation: ConversationEntry):
        """
        Automatically learn preferences and facts from conversation
        """
        user_msg = conversation.user_message.lower()
        
        # Learn preferences
        if 'prefer' in user_msg or 'like' in user_msg:
            # Extract preference
            if 'prefer' in user_msg:
                parts = user_msg.split('prefer')
                if len(parts) > 1:
                    pref = parts[1].strip()
                    self.add_preference(
                        'style_preference',
                        pref,
                        confidence=0.8
                    )
        
        # Learn about response style
        if any(word in user_msg for word in ['shorter', 'brief', 'concise']):
            self.add_preference('response_length', 'short', confidence=0.9)
        
        if any(word in user_msg for word in ['detailed', 'explain', 'elaborate']):
            self.add_preference('response_length', 'detailed', confidence=0.9)
        
        # Learn facts about user
        if 'i am' in user_msg or "i'm" in user_msg:
            self.add_fact(
                user_msg,
                f"conversation_{conversation.timestamp}",
                relevance=0.8
            )
    
    def get_context_summary(self, 
                           hours: int = 24,
                           include_preferences: bool = True,
                           include_facts: bool = True) -> str:
        """
        Generate context summary for the model
        """
        summary_parts = []
        
        # Recent conversations
        recent = self.get_recent_conversations(hours=hours, limit=5)
        if recent:
            summary_parts.append("Recent conversation topics:")
            for conv in recent:
                topic = conv.get('topic', 'general')
                summary_parts.append(f"  - {topic}: {conv['user_message'][:50]}...")
        
        # Preferences
        if include_preferences and self.preferences:
            summary_parts.append("\nUser preferences:")
            for pref in self.preferences:
                summary_parts.append(f"  - {pref['key']}: {pref['value']}")
        
        # Facts
        if include_facts and self.facts:
            summary_parts.append("\nKnown facts:")
            for fact in self.facts[-5:]:  # Last 5 facts
                summary_parts.append(f"  - {fact['fact'][:80]}...")
        
        return "\n".join(summary_parts) if summary_parts else "No recent context"
    
    def clear_old_data(self, days: int = 30):
        """
        Clear data older than specified days
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        # Filter conversations
        self.conversations = [
            conv for conv in self.conversations
            if datetime.fromisoformat(conv['timestamp']) > cutoff
        ]
        
        # Filter facts
        self.facts = [
            fact for fact in self.facts
            if datetime.fromisoformat(fact['learned_at']) > cutoff
        ]
        
        self._save_conversations()
        self._save_facts()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory statistics
        """
        return {
            "total_conversations": len(self.conversations),
            "conversations_24h": len(self.get_recent_conversations(hours=24)),
            "total_preferences": len(self.preferences),
            "total_facts": len(self.facts),
            "models_used": list(set(c['model_used'] for c in self.conversations)),
            "oldest_conversation": self.conversations[0]['timestamp'] if self.conversations else None,
            "newest_conversation": self.conversations[-1]['timestamp'] if self.conversations else None
        }
    
    # Private methods for file operations
    
    def _load_conversations(self) -> List[Dict]:
        """Load conversations from file"""
        if self.conversations_file.exists():
            try:
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_conversations(self):
        """Save conversations to file"""
        with open(self.conversations_file, 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, indent=2, ensure_ascii=False)
    
    def _load_preferences(self) -> List[Dict]:
        """Load preferences from file"""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_preferences(self):
        """Save preferences to file"""
        with open(self.preferences_file, 'w', encoding='utf-8') as f:
            json.dump(self.preferences, f, indent=2, ensure_ascii=False)
    
    def _load_facts(self) -> List[Dict]:
        """Load facts from file"""
        if self.facts_file.exists():
            try:
                with open(self.facts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_facts(self):
        """Save facts to file"""
        with open(self.facts_file, 'w', encoding='utf-8') as f:
            json.dump(self.facts, f, indent=2, ensure_ascii=False)


# Test
if __name__ == "__main__":
    print("Short-Term Memory Test")
    print("="*70)
    
    memory = ShortTermMemory()
    
    # Test conversation
    print("\n1. Adding conversation...")
    memory.add_conversation(
        user_message="Explain quantum computing",
        assistant_message="Quantum computing uses qubits...",
        model_used="smart",
        context_score=0.8,
        topic="technology"
    )
    print("   ✓ Added")
    
    # Test preference
    print("\n2. Adding preference...")
    memory.add_preference("response_style", "detailed")
    print("   ✓ Added")
    
    # Test fact
    print("\n3. Adding fact...")
    memory.add_fact(
        "User is interested in AI",
        "conversation_test",
        relevance=0.9
    )
    print("   ✓ Added")
    
    # Test retrieval
    print("\n4. Getting recent conversations...")
    recent = memory.get_recent_conversations(hours=24, limit=5)
    print(f"   ✓ Found {len(recent)} conversations")
    
    # Test context summary
    print("\n5. Generating context summary...")
    summary = memory.get_context_summary()
    print(f"\n{summary}\n")
    
    # Statistics
    print("\n6. Statistics:")
    stats = memory.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n" + "="*70)
    print("✅ Short-Term Memory ready!")
