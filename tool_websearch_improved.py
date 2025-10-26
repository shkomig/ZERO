"""
Enhanced WebSearch Tool
=======================
Improved web search with multiple sources and stock market support
"""

import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import re


class EnhancedWebSearchTool:
    """
    Enhanced web search tool with:
    - Multiple search engines
    - Stock market data
    - Better error handling
    - Results caching
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
        
    def search_stock(self, symbol: str) -> Dict[str, Any]:
        """
        Search for stock/ETF price using Yahoo Finance
        
        Args:
            symbol: Stock symbol (e.g., "SPY", "AAPL", "QQQ")
            
        Returns:
            Stock information
        """
        try:
            # Yahoo Finance API endpoint
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol.upper()}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            params = {
                'interval': '1d',
                'range': '1d'
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'chart' not in data or 'result' not in data['chart']:
                return {
                    "success": False,
                    "error": f"לא נמצא מידע עבור {symbol}"
                }
            
            result = data['chart']['result'][0]
            meta = result.get('meta', {})
            
            # Extract current price
            current_price = meta.get('regularMarketPrice', 0)
            previous_close = meta.get('previousClose', 0)
            change = current_price - previous_close if previous_close else 0
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            # Get additional info
            currency = meta.get('currency', 'USD')
            market_state = meta.get('marketState', 'UNKNOWN')
            
            return {
                "success": True,
                "symbol": symbol.upper(),
                "name": meta.get('longName', symbol.upper()),
                "price": round(current_price, 2),
                "currency": currency,
                "change": round(change, 2),
                "change_percent": round(change_percent, 2),
                "previous_close": round(previous_close, 2),
                "market_state": market_state,
                "timestamp": datetime.now().isoformat(),
                "type": "stock"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"שגיאה בחיפוש מניה: {str(e)}",
                "symbol": symbol
            }
    
    def search_web(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Enhanced web search using multiple methods
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            Search results
        """
        # Check cache first
        cache_key = f"{query}_{max_results}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if (datetime.now() - timestamp).seconds < self.cache_timeout:
                return cached_data
        
        try:
            # Method 1: DuckDuckGo HTML
            results = self._search_duckduckgo_html(query, max_results)
            
            if results:
                response = {
                    "success": True,
                    "query": query,
                    "results": results,
                    "count": len(results),
                    "source": "DuckDuckGo",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Cache results
                self.cache[cache_key] = (response, datetime.now())
                return response
            
            # Method 2: Fallback to API
            results = self._search_duckduckgo_api(query, max_results)
            
            response = {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results),
                "source": "DuckDuckGo API",
                "timestamp": datetime.now().isoformat()
            }
            
            self.cache[cache_key] = (response, datetime.now())
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def _search_duckduckgo_html(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """DuckDuckGo HTML search"""
        try:
            url = "https://html.duckduckgo.com/html/"
            params = {"q": query}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            result_links = soup.find_all('a', class_='result__a')
            
            for link in result_links[:max_results]:
                title = link.text.strip()
                url = link.get('href', '')
                
                parent = link.find_parent('div', class_='result')
                snippet = ""
                if parent:
                    snippet_elem = parent.find('a', class_='result__snippet')
                    if snippet_elem:
                        snippet = snippet_elem.text.strip()
                
                if title and url:
                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "url": url,
                        "type": "web_result"
                    })
            
            return results
            
        except Exception:
            return []
    
    def _search_duckduckgo_api(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """DuckDuckGo API search (fallback)"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            
            # Abstract
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
            
            return results
            
        except Exception:
            return []
    
    def smart_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Smart search - automatically detects query type
        - Stock symbols (SPY, AAPL, etc.)
        - Regular web search
        
        Args:
            query: Search query
            max_results: Max results
            
        Returns:
            Appropriate search results
        """
        # Check if it's a stock query
        stock_patterns = [
            r'\b([A-Z]{1,5})\s+(stock|price|מחיר|מניה)',
            r'(stock|price|מחיר|מניה)\s+\b([A-Z]{1,5})\b',
            r'\b([A-Z]{2,5})\b.*?(qqq|spy|aapl|msft|googl|amzn|tsla)'
        ]
        
        for pattern in stock_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                # Extract symbol
                groups = match.groups()
                symbol = next((g for g in groups if g and g.isupper() and 1 <= len(g) <= 5), None)
                
                if symbol:
                    stock_data = self.search_stock(symbol)
                    if stock_data.get("success"):
                        return stock_data
        
        # Regular web search
        return self.search_web(query, max_results)
    
    def format_results(self, search_result: Dict[str, Any]) -> str:
        """
        Format search results as readable text
        
        Args:
            search_result: Result from smart_search
            
        Returns:
            Formatted string
        """
        if not search_result.get("success"):
            return f"❌ חיפוש נכשל: {search_result.get('error', 'שגיאה לא ידועה')}"
        
        # Stock result
        if search_result.get("type") == "stock":
            symbol = search_result["symbol"]
            name = search_result.get("name", symbol)
            price = search_result["price"]
            currency = search_result["currency"]
            change = search_result["change"]
            change_percent = search_result["change_percent"]
            market_state = search_result["market_state"]
            
            direction = "📈" if change >= 0 else "📉"
            sign = "+" if change >= 0 else ""
            
            output = f"💰 **{name} ({symbol})**\n\n"
            output += f"**מחיר נוכחי:** {price} {currency}\n"
            output += f"**שינוי:** {direction} {sign}{change} ({sign}{change_percent}%)\n"
            output += f"**סגירה קודמת:** {search_result['previous_close']} {currency}\n"
            output += f"**מצב שוק:** {market_state}\n"
            output += f"**עודכן:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            return output
        
        # Web search results
        results = search_result.get("results", [])
        if not results:
            return f"❌ לא נמצאו תוצאות עבור: {search_result.get('query', '')}"
        
        query = search_result.get("query", "")
        source = search_result.get("source", "Web")
        
        output = f"🔍 **תוצאות חיפוש עבור:** '{query}'\n"
        output += f"**מקור:** {source}\n\n"
        
        for i, result in enumerate(results, 1):
            output += f"**{i}. {result['title']}**\n"
            if result.get('snippet'):
                snippet = result['snippet'][:300]
                output += f"   {snippet}...\n"
            if result.get('url'):
                output += f"   🔗 {result['url']}\n"
            output += "\n"
        
        return output


# Test
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("Testing Enhanced WebSearch Tool\n")
    print("="*60)
    
    tool = EnhancedWebSearchTool()
    
    # Test 1: Stock search
    print("\n[1] Testing stock search: SPY")
    print("-"*60)
    result = tool.smart_search("what is the current price of SPY stock?")
    print(tool.format_results(result))
    
    # Test 2: Web search
    print("\n[2] Testing web search: Python programming")
    print("-"*60)
    result = tool.smart_search("Python programming tutorial", max_results=3)
    print(tool.format_results(result))
    
    print("\n" + "="*60)
    print("[OK] Enhanced WebSearch Tool test complete!")

