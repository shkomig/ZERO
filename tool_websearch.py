"""
WebSearch Tool
==============
Tool for searching the web and getting results
"""

import requests
from typing import Dict, Any, List, Optional
import json


class WebSearchTool:
    """
    Tool for web search using DuckDuckGo API
    Simple and doesn't require API keys
    """
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.last_results = []
        
    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search the web
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            Search results
        """
        try:
            # DuckDuckGo Instant Answer API
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract results
            results = []
            
            # Abstract (main answer)
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", "Summary"),
                    "snippet": data.get("Abstract", ""),
                    "url": data.get("AbstractURL", ""),
                    "type": "abstract"
                })
            
            # Related topics
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "")[:100],
                        "snippet": topic.get("Text", ""),
                        "url": topic.get("FirstURL", ""),
                        "type": "related"
                    })
            
            self.last_results = results
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def search_simple(self, query: str) -> str:
        """
        Simple search that returns formatted text
        
        Args:
            query: Search query
            
        Returns:
            Formatted search results as string
        """
        result = self.search(query)
        
        if not result["success"]:
            return f"Search failed: {result.get('error', 'Unknown error')}"
        
        if not result["results"]:
            return f"No results found for: {query}"
        
        # Format results
        output = f"Search results for '{query}':\n\n"
        
        for i, item in enumerate(result["results"], 1):
            output += f"{i}. {item['title']}\n"
            if item['snippet']:
                output += f"   {item['snippet'][:200]}...\n"
            if item['url']:
                output += f"   URL: {item['url']}\n"
            output += "\n"
        
        return output
    
    def get_last_results(self) -> List[Dict[str, Any]]:
        """
        Get results from last search
        """
        return self.last_results
    
    def get_info(self) -> str:
        """
        Get tool information for LLM
        """
        return """WebSearch Tool - Search the internet:

1. search(query, max_results=5) - Search and get structured results
   Example: search("Python programming")
   Returns: {"success": True, "results": [...], "count": 5}
   
2. search_simple(query) - Search and get formatted text
   Example: search_simple("What is AI?")
   Returns: Formatted string with results

Note: Uses DuckDuckGo API (no API key required)"""


# Alternative: Google Custom Search (requires API key)
class GoogleSearchTool:
    """
    Alternative tool using Google Custom Search API
    Requires API key and Search Engine ID
    """
    
    def __init__(self, api_key: Optional[str] = None, search_engine_id: Optional[str] = None):
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Search using Google Custom Search API
        """
        if not self.api_key or not self.search_engine_id:
            return {
                "success": False,
                "error": "API key and Search Engine ID required"
            }
        
        try:
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": max_results
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "type": "web"
                })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Test the tool
if __name__ == "__main__":
    print("WebSearch Tool Test")
    print("="*60)
    
    # Create tool
    search = WebSearchTool()
    
    print("\n1. Searching for 'Python programming'...")
    result = search.search("Python programming", max_results=3)
    
    if result["success"]:
        print(f"   Found {result['count']} results:")
        for i, item in enumerate(result['results'], 1):
            print(f"\n   {i}. {item['title']}")
            print(f"      {item['snippet'][:100]}...")
    else:
        print(f"   Error: {result.get('error')}")
    
    print("\n2. Simple search for 'What is AI?'...")
    result = search.search_simple("What is AI?")
    print(result[:300] + "...")
    
    print("\n" + "="*60)
    print("✅ WebSearch Tool is ready!")
    print("\nNote: DuckDuckGo API has limited results.")
    print("For better results, use GoogleSearchTool with API key.")
