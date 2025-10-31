"""
RAG Memory System for Zero Agent
Stores and retrieves context using ChromaDB
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from zero_agent.core.config import config


class RAGMemorySystem:
    """RAG-based memory for context retention"""
    
    def __init__(self):
        db_path = Path(config.settings.chroma_db_path)
        db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create collections
        self.conversations = self._get_or_create_collection("conversations")
        self.successes = self._get_or_create_collection("successes")
        self.failures = self._get_or_create_collection("failures")
        self.knowledge = self._get_or_create_collection("knowledge")
        self.preferences = self._get_or_create_collection("preferences")
        self.personal_facts = self._get_or_create_collection("personal_facts")
        
        print(f"[MEMORY] RAG Memory initialized at {db_path}")
    
    def _get_or_create_collection(self, name: str):
        """Get or create a collection"""
        try:
            return self.client.get_or_create_collection(
                name=name,
                metadata={"description": f"Zero Agent {name}"}
            )
        except Exception as e:
            print(f"[WARN]  Collection creation error for {name}: {e}")
            return None
    
    def store_conversation(self, task: str, response: str, metadata: Optional[Dict] = None):
        """Store conversation turn"""
        try:
            if not self.conversations:
                return
            
            import uuid
            doc_id = str(uuid.uuid4())
            
            self.conversations.add(
                documents=[f"Task: {task}\nResponse: {response}"],
                metadatas=[metadata or {}],
                ids=[doc_id]
            )
        except Exception as e:
            print(f"[WARN]  Failed to store conversation: {e}")
    
    def store_success(self, task: str, plan: List[str], results: Dict):
        """Store successful task execution"""
        try:
            if not self.successes:
                return
            
            import uuid
            doc_id = str(uuid.uuid4())
            
            doc = f"Task: {task}\nPlan: {' -> '.join(plan)}\nResults: Success"
            
            self.successes.add(
                documents=[doc],
                metadatas=[{
                    "task": task,
                    "steps": len(plan),
                    "success": True
                }],
                ids=[doc_id]
            )
            print(f"[OK] Success pattern stored")
        except Exception as e:
            print(f"[WARN]  Failed to store success: {e}")
    
    def store_failure(self, task: str, error: str, context: Dict):
        """Store failed task execution"""
        try:
            if not self.failures:
                return
            
            import uuid
            doc_id = str(uuid.uuid4())
            
            doc = f"Task: {task}\nError: {error}\nContext: {str(context)}"
            
            self.failures.add(
                documents=[doc],
                metadatas=[{
                    "task": task,
                    "error_type": type(error).__name__,
                    "success": False
                }],
                ids=[doc_id]
            )
            print(f"[ERROR] Failure pattern stored for learning")
        except Exception as e:
            print(f"[WARN]  Failed to store failure: {e}")
    
    def retrieve(self, query: str, n_results: int = 5, collection: str = "conversations") -> List[Dict]:
        """
        Retrieve relevant context
        
        Args:
            query: Search query
            n_results: Number of results to return
            collection: Which collection to search
            
        Returns:
            List of relevant documents
        """
        try:
            coll = getattr(self, collection, self.conversations)
            if not coll:
                return []
            
            # Get collection count first
            count = coll.count()
            if count == 0:
                return []
            
            # Limit n_results to available documents
            n_results = min(n_results, count)
            
            results = coll.query(
                query_texts=[query],
                n_results=n_results
            )
            
            if not results or not results['documents']:
                return []
            
            # Format results
            formatted = []
            for i, doc in enumerate(results['documents'][0]):
                formatted.append({
                    "document": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results.get('distances') else 0
                })
            
            return formatted
            
        except Exception as e:
            print(f"[WARN]  Retrieval error: {e}")
            return []
    
    def search_similar(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search for similar past experiences"""
        all_results = []
        
        # Search successes
        successes = self.retrieve(query, n_results, "successes")
        all_results.extend([{**r, "type": "success"} for r in successes])
        
        # Search failures  
        failures = self.retrieve(query, n_results, "failures")
        all_results.extend([{**r, "type": "failure"} for r in failures])
        
        # Sort by distance (lower is better)
        all_results.sort(key=lambda x: x.get("distance", 999))
        
        return all_results[:n_results]
    
    def store_preference(self, key: str, value: Any):
        """Store user preference"""
        try:
            if not self.preferences:
                return
            
            import uuid
            doc_id = str(uuid.uuid4())
            
            self.preferences.add(
                documents=[f"{key}: {value}"],
                metadatas=[{"key": key, "value": str(value)}],
                ids=[doc_id]
            )
            print(f"[OK] Preference stored: {key}")
        except Exception as e:
            print(f"[WARN]  Failed to store preference: {e}")
    
    def store_personal_fact(self, key: str, value: Any):
        """Store personal fact about user"""
        try:
            if not self.personal_facts:
                return
            
            import uuid
            doc_id = str(uuid.uuid4())
            
            self.personal_facts.add(
                documents=[f"{key}: {value}"],
                metadatas=[{"key": key, "value": str(value)}],
                ids=[doc_id]
            )
            print(f"[OK] Personal fact stored: {key}")
        except Exception as e:
            print(f"[WARN]  Failed to store personal fact: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """Get memory statistics"""
        try:
            return {
                "conversations": self.conversations.count() if self.conversations else 0,
                "successes": self.successes.count() if self.successes else 0,
                "failures": self.failures.count() if self.failures else 0,
                "knowledge": self.knowledge.count() if self.knowledge else 0,
                "preferences": self.preferences.count() if self.preferences else 0,
                "personal_facts": self.personal_facts.count() if self.personal_facts else 0
            }
        except Exception as e:
            print(f"[WARN]  Stats error: {e}")
            return {}

