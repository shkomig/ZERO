"""
Perplexity AI Search Tool
==========================
Real-time AI-powered search with citations using Perplexity API
"""

import requests
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, using os.getenv only
    pass


class PerplexitySearchTool:
    """
    Perplexity AI search tool for real-time web search
    
    Features:
    - Real-time web search
    - AI-powered answers
    - Source citations
    - Multiple models available
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Perplexity search tool
        
        Args:
            api_key: Perplexity API key (or use PERPLEXITY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("Perplexity API key required! Set PERPLEXITY_API_KEY env var or pass api_key parameter")
        
        self.base_url = "https://api.perplexity.ai"
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        
        # Available models (Perplexity API models - check docs for latest)
        # Common models: sonar, pplx-7b-online, pplx-70b-online, llama-3.1-sonar
        self.models = {
            'fast': 'sonar',               # Fast, real-time search (simplest name)
            'balanced': 'pplx-7b-online',  # Balanced speed/quality  
            'quality': 'pplx-70b-online'   # Best quality
        }
    
    def search(self, 
               query: str, 
               model: str = 'fast',
               max_tokens: int = 1000,
               temperature: float = 0.2,
               return_citations: bool = True) -> Dict[str, Any]:
        """
        Search using Perplexity AI with real-time web access
        
        Args:
            query: Search query
            model: Model to use ('fast', 'balanced', 'quality')
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0.0-1.0)
            return_citations: Include source citations
            
        Returns:
            Search results with answer and citations
        """
        # Check cache first
        cache_key = f"{query}_{model}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_timeout:
                return cached_data
        
        try:
            url = f"{self.base_url}/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Select model
            model_name = self.models.get(model, self.models['fast'])
            
            # Perplexity API format
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract answer and citations
            answer = data['choices'][0]['message']['content']
            
            # Perplexity returns citations in the response text or as separate field
            citations = []
            if 'citations' in data:
                citations = data['citations']
            elif hasattr(data['choices'][0]['message'], 'citations'):
                citations = data['choices'][0]['message'].get('citations', [])
            
            # Try to extract citations from answer text if available
            import re
            citation_urls = re.findall(r'https?://[^\s\)]+', answer)
            if citation_urls and not citations:
                citations = citation_urls[:10]  # Limit to 10
            
            result = {
                'success': True,
                'source': 'Perplexity AI',
                'model': model_name,
                'query': query,
                'answer': answer,
                'citations': citations,
                'num_citations': len(citations),
                'timestamp': datetime.now().isoformat(),
                'type': 'ai_search'
            }
            
            # Cache result
            self.cache[cache_key] = (result, datetime.now())
            
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                return {
                    'success': False,
                    'error': 'Invalid API key. Please check your PERPLEXITY_API_KEY',
                    'query': query
                }
            elif e.response.status_code == 429:
                return {
                    'success': False,
                    'error': 'Rate limit exceeded. Please wait a moment',
                    'query': query
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP error {e.response.status_code}: {str(e)}',
                    'query': query
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Search failed: {str(e)}',
                'query': query
            }
    
    def format_results(self, result: Dict[str, Any]) -> str:
        """
        Format Perplexity search results for display
        
        Args:
            result: Result from search()
            
        Returns:
            Formatted string
        """
        if not result.get('success'):
            return f"❌ חיפוש נכשל: {result.get('error', 'שגיאה לא ידועה')}"
        
        output = f"**🔍 Perplexity AI Search Results**\n\n"
        output += f"**Query:** {result['query']}\n"
        output += f"**Model:** {result['model']}\n\n"
        
        # Add answer
        output += f"**Answer:**\n{result['answer']}\n\n"
        
        # Add citations
        if result.get('citations'):
            output += f"**📚 Sources ({result['num_citations']}):**\n"
            for i, citation in enumerate(result['citations'][:5], 1):
                output += f"{i}. {citation}\n"
        
        output += f"\n*Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return output
    
    def quick_search(self, query: str) -> str:
        """
        Quick search with formatted output (convenience method)
        
        Args:
            query: Search query
            
        Returns:
            Formatted answer
        """
        result = self.search(query, model='fast')
        
        if result.get('success'):
            return result['answer']
        else:
            return f"Search failed: {result.get('error', 'Unknown error')}"


# Test function
def test_perplexity():
    """Test Perplexity search"""
    import sys
    
    try:
        tool = PerplexitySearchTool()
        
        print("="*70)
        print("Testing Perplexity AI Search")
        print("="*70)
        
        # Test 1: Simple query
        print("\n[Test 1] Simple query: 'What is AI?'")
        result = tool.search("What is artificial intelligence?", model='fast')
        if result['success']:
            print(f"✓ Success!")
            print(f"Answer length: {len(result['answer'])} chars")
            print(f"Citations: {result['num_citations']}")
            print(f"First 200 chars: {result['answer'][:200]}...")
        else:
            print(f"✗ Failed: {result['error']}")
        
        # Test 2: Real-time query
        print("\n[Test 2] Real-time query: 'Latest AI news'")
        result = tool.search("What are the latest AI developments today?", model='fast')
        if result['success']:
            print(f"✓ Success!")
            print(f"Citations: {result['num_citations']}")
            if result['citations']:
                print(f"Sample citation: {result['citations'][0]}")
        else:
            print(f"✗ Failed: {result['error']}")
        
        # Test 3: Formatted output
        print("\n[Test 3] Formatted output")
        formatted = tool.format_results(result)
        print(formatted[:500])
        
        print("\n" + "="*70)
        print("Perplexity AI Search is working!")
        print("="*70)
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease set PERPLEXITY_API_KEY in your .env file:")
        print("PERPLEXITY_API_KEY=your_api_key_here")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_perplexity()

