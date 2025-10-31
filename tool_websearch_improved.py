"""
Enhanced WebSearch Tool
=======================
Improved web search with multiple sources and stock market support
NOW WITH PERPLEXITY AI FOR REAL-TIME SEARCH!
"""

import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import os

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, using os.getenv only
    pass


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
        
        # Perplexity API (if available)
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        self.use_perplexity = bool(self.perplexity_key)
        
        if self.use_perplexity:
            print("[WebSearch] [OK] Perplexity AI enabled - real-time search active!")
        else:
            print("[WebSearch] Using DuckDuckGo (set PERPLEXITY_API_KEY for real-time AI search)")
        
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
    
    def fetch_content_with_jina(self, url: str) -> Optional[str]:
        """
        Fetch and extract clean content using Jina Reader API
        FREE tier: 1M requests/month! Token-optimized markdown output.
        
        Args:
            url: URL to fetch
            
        Returns:
            Clean markdown content (LLM-optimized) or None if failed
        """
        try:
            jina_url = f"https://r.jina.ai/{url}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(jina_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Jina returns clean markdown - perfect for LLMs!
            # Limit to ~5000 chars (~1250 tokens) to fit in context
            content = response.text[:5000]
            return content if content.strip() else None
            
        except Exception:
            return None
    
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
    
    def search_perplexity(self, query: str) -> Dict[str, Any]:
        """
        Search using Perplexity AI - REAL-TIME with citations!
        
        Args:
            query: Search query
            
        Returns:
            AI-powered answer with citations
        """
        if not self.use_perplexity:
            return {'success': False, 'error': 'Perplexity API key not configured'}
        
        try:
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.perplexity_key}",
                "Content-Type": "application/json"
            }
            # Perplexity API - simplified format
            # Optimize for concise, factual answers with real-time data
            payload = {
                "model": "sonar",  # Real-time model (simplest name)
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a factual assistant. Provide concise, accurate answers with specific details (dates, numbers, facts). Focus on current, real-time information. Be direct and brief."
                    },
                    {"role": "user", "content": query}
                ],
                "temperature": 0.2,  # Lower temperature for more factual responses
                "max_tokens": 800  # Limit to prevent overly long answers
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            answer = data['choices'][0]['message']['content']
            citations = data.get('citations', [])
            
            return {
                'success': True,
                'source': 'Perplexity AI',
                'query': query,
                'answer': answer,
                'citations': citations,
                'num_citations': len(citations),
                'timestamp': datetime.now().isoformat(),
                'type': 'ai_answer'
            }
            
        except Exception as e:
            print(f"[Perplexity] Error: {e}")
            return {'success': False, 'error': str(e)}
    
    def smart_search(self, query: str, max_results: int = 5, prefer_ai: bool = True) -> Dict[str, Any]:
        """
        Smart search - automatically detects query type
        - Stock symbols (SPY, AAPL, etc.) - Perplexity FIRST for real-time analysis
        - Stock price only - Yahoo Finance
        - Perplexity AI for real-time answers (if available)
        - Regular web search (fallback)
        
        Args:
            query: Search query
            max_results: Max results
            prefer_ai: Use Perplexity AI if available (default: True)
            
        Returns:
            Appropriate search results
        """
        # List of known stock symbols (most popular)
        known_stocks = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
                       'NVDA', 'META', 'NFLX', 'AMD', 'INTC', 'DIA', 'IWM',
                       'QBTS', 'RGTI']  # Added quantum computing stocks
        
        # Check if query contains stock keywords in Hebrew or English
        stock_keywords = ['מחיר', 'מניה', 'מניית', 'price', 'stock', 'סימול', 'symbol']
        has_stock_keyword = any(keyword in query.lower() for keyword in stock_keywords)
        
        # Extract uppercase words (potential stock symbols)
        uppercase_words = re.findall(r'\b[A-Z]{2,5}\b', query)
        
        # PRIORITY 1: For stock symbols with analysis/context keywords - use Perplexity FIRST
        # This gives real-time data instead of halluciating
        analysis_keywords = ['analysis', 'analyze', 'news', 'latest', 'trend', 'outlook',
                            'performance', 'target', 'rating', 'forecast', 'prediction',
                            'review', 'research', 'report', 'update', 'developments']
        
        if any(word.upper() in known_stocks for word in uppercase_words):
            has_analysis = any(kw in query.lower() for kw in analysis_keywords)
            
            # For analysis/context queries - Perplexity FIRST (real-time data)
            if has_analysis and prefer_ai and self.use_perplexity:
                print(f"[WebSearch] Stock analysis query detected - using Perplexity for real-time data")
                perp_result = self.search_perplexity(query)
                if perp_result.get('success'):
                    return perp_result
            
            # For simple price-only queries - Yahoo Finance is fine
            if not has_analysis:
                stock_symbol = next((w for w in uppercase_words if w.upper() in known_stocks), None)
                if stock_symbol:
                    stock_data = self.search_stock(stock_symbol.upper())
                    if stock_data.get("success") and stock_data.get("price", 0) > 0:
                        return stock_data
                
                # If Yahoo Finance failed, fallback to Perplexity
                if prefer_ai and self.use_perplexity:
                    print(f"[WebSearch] Yahoo Finance failed, using Perplexity")
                    perp_result = self.search_perplexity(query)
                    if perp_result.get('success'):
                        return perp_result
        
        # PRIORITY 2: Check if we should use Perplexity AI for better real-time results
        if prefer_ai and self.use_perplexity:
            # Keywords that benefit from AI search (including stock analysis)
            ai_keywords = ['latest', 'recent', 'news', 'current', 'today', 'who is', 
                          'what is', 'explain', 'how does', 'why', 'compare',
                          'stock', 'price', 'analysis', 'market', 'trading', 'chart',
                          'trend', 'forecast', 'prediction', 'outlook', 'review']
            
            if any(kw in query.lower() for kw in ai_keywords):
                perp_result = self.search_perplexity(query)
                if perp_result.get('success'):
                    return perp_result
        
        # FALLBACK: Regular web search
        return self.search_web(query, max_results)
    
    def format_results(self, search_result: Dict[str, Any], max_length: int = 800) -> str:
        """
        Format search results as readable text
        
        Args:
            search_result: Result from smart_search
            max_length: Maximum length for answer (to prevent too long responses)
            
        Returns:
            Formatted string
        """
        if not search_result.get("success"):
            return f"חיפוש נכשל: {search_result.get('error', 'שגיאה לא ידועה')}"
        
        # Perplexity AI result (NEW!)
        if search_result.get("type") == "ai_answer":
            answer = search_result['answer']
            
            # Limit answer length to prevent overly long responses
            if len(answer) > max_length:
                # Truncate at sentence boundary (more aggressive)
                truncated = answer[:max_length]
                
                # Try to find a good breaking point
                break_points = [
                    truncated.rfind('. '),  # End of sentence
                    truncated.rfind('.\n'),  # End of sentence with newline
                    truncated.rfind('? '),   # Question mark
                    truncated.rfind('! '),   # Exclamation
                    truncated.rfind('\n'),  # Newline
                    truncated.rfind('.')     # Any period
                ]
                
                # Find the best break point
                best_break = -1
                for bp in break_points:
                    if bp > max_length * 0.7:  # At least 70% of max_length
                        best_break = max(best_break, bp)
                
                if best_break > 0:
                    answer = truncated[:best_break + 1] + "..."
                else:
                    # Fallback: just truncate
                    answer = truncated[:max_length - 3] + "..."
            
            # Add citations inline to save space
            if search_result.get('citations'):
                citations = search_result['citations'][:2]  # Only top 2
                if citations:
                    answer += " " + " | ".join([f"[{i+1}]({cite})" if 'http' in str(cite) else str(cite)
                                                for i, cite in enumerate(citations)])
            
            # Ensure total length doesn't exceed max_length (including citations)
            if len(answer) > max_length:
                answer = answer[:max_length-3] + "..."
            
            return answer.strip()  # Clean output
        
        # Stock result
        if search_result.get("type") == "stock":
            symbol = search_result["symbol"]
            name = search_result.get("name", symbol)
            price = search_result["price"]
            currency = search_result["currency"]
            change = search_result["change"]
            change_percent = search_result["change_percent"]
            market_state = search_result["market_state"]
            
            direction = "+" if change >= 0 else "-"
            sign = "+" if change >= 0 else ""
            
            output = f"**{name} ({symbol})**\n\n"
            output += f"**מחיר נוכחי:** {price} {currency}\n"
            output += f"**שינוי:** {direction} {sign}{change} ({sign}{change_percent}%)\n"
            output += f"**סגירה קודמת:** {search_result['previous_close']} {currency}\n"
            output += f"**מצב שוק:** {market_state}\n"
            output += f"**עודכן:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            return output
        
        # Web search results
        results = search_result.get("results", [])
        if not results:
            return f"לא נמצאו תוצאות עבור: {search_result.get('query', '')}"
        
        query = search_result.get("query", "")
        source = search_result.get("source", "Web")
        
        output = f"**תוצאות חיפוש עבור:** '{query}'\n"
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

