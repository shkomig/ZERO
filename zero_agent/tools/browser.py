"""
Browser automation using Playwright
Provides automated browser control for web scraping and interaction
"""

from playwright.async_api import async_playwright, Browser, Page, Playwright
from typing import Optional, List, Dict
import asyncio


class BrowserAutomation:
    """Automated browser control using Playwright"""
    
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context = None
        self.page: Optional[Page] = None
        self._initialized = False
    
    async def initialize(self, headless: bool = False):
        """Initialize browser"""
        if self._initialized:
            return
        
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=headless)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            self._initialized = True
            print(f"[OK] Browser initialized (headless={headless})")
        except Exception as e:
            print(f"[ERROR] Browser initialization failed: {e}")
            raise
    
    async def navigate(self, url: str, wait_until: str = "networkidle"):
        """
        Navigate to URL
        
        Args:
            url: Target URL
            wait_until: When to consider navigation complete
                       ('load', 'domcontentloaded', 'networkidle')
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            await self.page.goto(url, wait_until=wait_until)
            print(f"[NAV] Navigated to: {url}")
        except Exception as e:
            print(f"[ERROR] Navigation failed: {e}")
            raise
    
    async def click(self, selector: str, timeout: int = 30000):
        """Click element by selector"""
        try:
            await self.page.click(selector, timeout=timeout)
            print(f"[CLICK]  Clicked: {selector}")
        except Exception as e:
            print(f"[ERROR] Click failed on {selector}: {e}")
            raise
    
    async def type_text(self, selector: str, text: str, delay: int = 0):
        """
        Type text into element
        
        Args:
            selector: Element selector
            text: Text to type
            delay: Delay between keystrokes in ms
        """
        try:
            await self.page.fill(selector, text)
            if delay > 0:
                await self.page.type(selector, text, delay=delay)
            print(f"[TYPE]  Typed into {selector}")
        except Exception as e:
            print(f"[ERROR] Type failed on {selector}: {e}")
            raise
    
    async def screenshot(self, path: str, full_page: bool = False):
        """Take screenshot"""
        try:
            await self.page.screenshot(path=path, full_page=full_page)
            print(f"[SCREENSHOT] Screenshot saved to: {path}")
        except Exception as e:
            print(f"[ERROR] Screenshot failed: {e}")
            raise
    
    async def extract_text(self, selector: str) -> Optional[str]:
        """Extract text from element"""
        try:
            text = await self.page.text_content(selector)
            return text
        except Exception as e:
            print(f"[ERROR] Text extraction failed from {selector}: {e}")
            return None
    
    async def execute_script(self, script: str):
        """Execute JavaScript"""
        try:
            result = await self.page.evaluate(script)
            return result
        except Exception as e:
            print(f"[ERROR] Script execution failed: {e}")
            raise
    
    async def search_google(self, query: str) -> List[Dict]:
        """
        Search Google and return results
        
        Returns:
            List of dicts with 'title', 'url', 'snippet'
        """
        try:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            await self.navigate(search_url)
            
            # Wait for results
            await self.page.wait_for_selector(".g", timeout=10000)
            
            results = []
            result_elements = await self.page.query_selector_all(".g")
            
            for element in result_elements[:5]:
                try:
                    title_elem = await element.query_selector("h3")
                    link_elem = await element.query_selector("a")
                    snippet_elem = await element.query_selector(".VwiC3b")
                    
                    if title_elem and link_elem:
                        title = await title_elem.text_content()
                        url = await link_elem.get_attribute("href")
                        snippet = await snippet_elem.text_content() if snippet_elem else ""
                        
                        results.append({
                            "title": title,
                            "url": url,
                            "snippet": snippet
                        })
                except:
                    continue
            
            print(f"[SEARCH] Found {len(results)} search results")
            return results
            
        except Exception as e:
            print(f"[ERROR] Google search failed: {e}")
            return []
    
    async def get_page_content(self) -> str:
        """Get full page HTML content"""
        try:
            content = await self.page.content()
            return content
        except Exception as e:
            print(f"[ERROR] Failed to get page content: {e}")
            return ""
    
    async def wait_for_selector(self, selector: str, timeout: int = 30000):
        """Wait for element to appear"""
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
        except Exception as e:
            print(f"[ERROR] Wait failed for {selector}: {e}")
            raise
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self._initialized = False
            print("[CLOSE] Browser closed")
        except Exception as e:
            print(f"[WARN]  Browser close error: {e}")
    
    async def __aenter__(self):
        """Context manager support"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        await self.close()

