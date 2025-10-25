"""
RAG Connector
=============
Connects to your existing RAG system (Docker:8000)
Domain-agnostic - works with any documents you add
"""

import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time


@dataclass
class RAGResult:
    """Result from RAG search"""
    content: str
    source: str
    relevance: float
    metadata: Dict[str, Any]


class RAGConnector:
    """
    Connector to existing RAG system
    Flexible - works with any type of documents
    """
    
    def __init__(self, 
                 rag_url: str = "http://localhost:8000",
                 timeout: int = 30):
        self.rag_url = rag_url
        self.timeout = timeout
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """
        Test connection to RAG system
        """
        try:
            response = requests.get(
                self.rag_url, 
                timeout=5
            )
            return response.status_code in [200, 404]  # 404 is OK (root endpoint)
        except:
            return False
    
    def is_available(self) -> bool:
        """
        Check if RAG system is available
        """
        return self._test_connection()
    
    def search(self, 
               query: str,
               top_k: int = 3,
               min_relevance: float = 0.5) -> List[RAGResult]:
        """
        Search in RAG system
        
        Args:
            query: Search query
            top_k: Number of results
            min_relevance: Minimum relevance score
            
        Returns:
            List of relevant documents
        """
        if not self.is_available():
            return []
        
        try:
            # Call your RAG API
            response = requests.post(
                f"{self.rag_url}/query",
                json={
                    "question": query,
                    "top_k": top_k
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_results(data, min_relevance)
            
            return []
            
        except requests.exceptions.Timeout:
            print("⚠️  RAG search timed out")
            return []
        except Exception as e:
            print(f"⚠️  RAG search error: {str(e)}")
            return []
    
    def _parse_results(self, 
                      data: Dict,
                      min_relevance: float) -> List[RAGResult]:
        """
        Parse RAG API response
        Adapts to your RAG system's format
        """
        results = []
        
        # Try different response formats
        # Format 1: {answer, sources, relevance}
        if 'answer' in data:
            results.append(RAGResult(
                content=data['answer'],
                source=data.get('source', 'RAG'),
                relevance=data.get('relevance', 1.0),
                metadata=data.get('metadata', {})
            ))
        
        # Format 2: {results: [{text, score, metadata}]}
        elif 'results' in data:
            for item in data['results']:
                score = item.get('score', 1.0)
                if score >= min_relevance:
                    results.append(RAGResult(
                        content=item.get('text', ''),
                        source=item.get('source', 'document'),
                        relevance=score,
                        metadata=item.get('metadata', {})
                    ))
        
        # Format 3: {documents: [...]}
        elif 'documents' in data:
            for doc in data['documents']:
                results.append(RAGResult(
                    content=doc.get('content', ''),
                    source=doc.get('source', 'document'),
                    relevance=1.0,
                    metadata=doc.get('metadata', {})
                ))
        
        return results
    
    def get_context(self, 
                   query: str,
                   max_chars: int = 2000) -> Optional[str]:
        """
        Get context string for the model
        
        Args:
            query: Search query
            max_chars: Maximum characters to return
            
        Returns:
            Formatted context string or None
        """
        results = self.search(query, top_k=3)
        
        if not results:
            return None
        
        context_parts = ["Relevant information from your documents:"]
        current_length = len(context_parts[0])
        
        for i, result in enumerate(results, 1):
            source_text = f"\n\n[Source {i}: {result.source}]"
            content_preview = result.content[:500] + "..." if len(result.content) > 500 else result.content
            
            entry = f"{source_text}\n{content_preview}"
            
            if current_length + len(entry) > max_chars:
                break
            
            context_parts.append(entry)
            current_length += len(entry)
        
        return "\n".join(context_parts)
    
    def index_conversation(self, 
                          user_message: str,
                          assistant_message: str,
                          metadata: Optional[Dict] = None) -> bool:
        """
        Index a conversation in RAG for future retrieval
        
        Args:
            user_message: User's message
            assistant_message: Assistant's response
            metadata: Additional metadata
            
        Returns:
            Success status
        """
        if not self.is_available():
            return False
        
        try:
            # Try to add to RAG
            response = requests.post(
                f"{self.rag_url}/index",
                json={
                    "content": f"Q: {user_message}\nA: {assistant_message}",
                    "metadata": metadata or {}
                },
                timeout=self.timeout
            )
            
            return response.status_code in [200, 201]
            
        except:
            # If indexing fails, that's OK - not critical
            return False
    
    def get_statistics(self) -> Optional[Dict[str, Any]]:
        """
        Get RAG system statistics
        """
        if not self.is_available():
            return None
        
        try:
            response = requests.get(
                f"{self.rag_url}/stats",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except:
            return None


class RAGContextBuilder:
    """
    Builds context from RAG results
    Smart about what to include and how
    """
    
    def __init__(self, rag_connector: RAGConnector):
        self.rag = rag_connector
    
    def build_context(self, 
                     query: str,
                     task_type: Optional[str] = None) -> str:
        """
        Build intelligent context from RAG
        
        Args:
            query: The current query
            task_type: Type of task (optional)
            
        Returns:
            Formatted context string
        """
        # Check if RAG is available
        if not self.rag.is_available():
            return ""
        
        # Search RAG
        context = self.rag.get_context(query, max_chars=2000)
        
        if not context:
            return ""
        
        # Format based on task type
        if task_type == "coding":
            prefix = "📚 Relevant code/documentation from your knowledge base:\n"
        elif task_type == "analysis":
            prefix = "📊 Relevant analysis from your knowledge base:\n"
        else:
            prefix = "💡 Relevant information from your knowledge base:\n"
        
        return f"{prefix}{context}"
    
    def should_use_rag(self, query: str) -> bool:
        """
        Determine if RAG should be consulted for this query
        
        Returns:
            True if RAG might be helpful
        """
        # Don't use RAG for very simple queries
        simple_keywords = [
            "what is", "define", "calculate", 
            "convert", "how much", "what's"
        ]
        
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in simple_keywords):
            if len(query.split()) < 8:
                return False
        
        # Use RAG if asking about documents or past conversations
        rag_keywords = [
            "document", "file", "you told me",
            "we discussed", "last time", "previously",
            "in my", "from the", "according to"
        ]
        
        if any(kw in query_lower for kw in rag_keywords):
            return True
        
        # Default: try RAG
        return True


# Test
if __name__ == "__main__":
    print("RAG Connector Test")
    print("="*70)
    
    # Initialize
    print("\n1. Connecting to RAG system...")
    rag = RAGConnector(rag_url="http://localhost:8000")
    
    if rag.is_available():
        print("   ✅ Connected to RAG system")
    else:
        print("   ⚠️  RAG system not available (this is OK!)")
        print("   Memory will work without it")
    
    # Test search
    if rag.is_available():
        print("\n2. Testing search...")
        results = rag.search("test query", top_k=2)
        print(f"   Found {len(results)} results")
        
        if results:
            print("\n   Sample result:")
            print(f"   Content: {results[0].content[:100]}...")
            print(f"   Relevance: {results[0].relevance}")
    
    # Test context builder
    print("\n3. Testing context builder...")
    builder = RAGContextBuilder(rag)
    
    should_use = builder.should_use_rag("What did we discuss about AI?")
    print(f"   Should use RAG for 'past discussion': {should_use}")
    
    should_not = builder.should_use_rag("What is 2+2?")
    print(f"   Should use RAG for 'simple math': {should_not}")
    
    print("\n" + "="*70)
    print("✅ RAG Connector ready!")
    print("\nFeatures:")
    print("  ✓ Connects to your RAG (Docker:8000)")
    print("  ✓ Domain-agnostic (works with any documents)")
    print("  ✓ Graceful fallback if RAG unavailable")
    print("  ✓ Smart about when to use RAG")
