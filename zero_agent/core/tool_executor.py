"""
Tool execution layer for Zero Agent
Manages and executes all available tools
"""

from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
import asyncio
import platform

from zero_agent.tools.git_ops import GitOperations
from zero_agent.tools.system_monitor import SystemMonitor
from zero_agent.tools.screen_capture import ScreenCapture
from zero_agent.tools.browser import BrowserAutomation
from zero_agent.core.config import config


class ToolExecutor:
    """Executes tools based on task requirements"""
    
    def __init__(self):
        # Initialize tools
        self.git_ops = GitOperations() if config.is_tool_enabled("git") else None
        self.system_monitor = SystemMonitor()
        self.screen_capture = ScreenCapture() if config.is_tool_enabled("screen_capture") else None
        self.browser = None  # Initialized on demand
        
        # Tool registry
        self.tools: Dict[str, Callable] = {
            # Git operations
            "git_init": self._git_init,
            "git_clone": self._git_clone,
            "git_commit": self._git_commit,
            "git_push": self._git_push,
            "git_status": self._git_status,
            
            # System monitoring
            "system_info": self._system_info,
            "cpu_usage": self._cpu_usage,
            "memory_usage": self._memory_usage,
            "disk_usage": self._disk_usage,
            "process_list": self._process_list,
            
            # Screen capture
            "screenshot": self._screenshot,
            "capture_region": self._capture_region,
            
            # Browser automation
            "web_search": self._web_search,
            "navigate_url": self._navigate_url,
            "extract_webpage": self._extract_webpage,
        }
        
        print(f"[INIT] ToolExecutor initialized with {len(self.tools)} tools")
    
    async def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name
        
        Args:
            tool_name: Name of tool to execute
            **kwargs: Tool-specific parameters
            
        Returns:
            Dict with 'success', 'result', and optionally 'error'
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(self.tools.keys())
            }
        
        try:
            print(f"[EXEC] Executing tool: {tool_name}")
            tool_func = self.tools[tool_name]
            
            # Check if async
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**kwargs)
            else:
                result = tool_func(**kwargs)
            
            return {
                "success": True,
                "tool": tool_name,
                "result": result
            }
            
        except Exception as e:
            print(f"[ERROR] Tool execution failed: {e}")
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e)
            }
    
    def list_tools(self) -> List[str]:
        """List all available tools"""
        return list(self.tools.keys())
    
    # Git Operations
    def _git_init(self, name: str) -> Dict:
        """Initialize git repository"""
        if not self.git_ops:
            return {"success": False, "error": "Git operations disabled"}
        return self.git_ops.init_repo(name)
    
    def _git_clone(self, url: str, name: Optional[str] = None) -> Dict:
        """Clone git repository"""
        if not self.git_ops:
            return {"success": False, "error": "Git operations disabled"}
        return self.git_ops.clone_repo(url, name)
    
    def _git_commit(self, message: str, author: Optional[Dict] = None) -> Dict:
        """Commit changes"""
        if not self.git_ops:
            return {"success": False, "error": "Git operations disabled"}
        # First add all files
        self.git_ops.add_files()
        return self.git_ops.commit(message, author)
    
    def _git_push(self, remote: str = "origin", branch: Optional[str] = None) -> Dict:
        """Push commits"""
        if not self.git_ops:
            return {"success": False, "error": "Git operations disabled"}
        return self.git_ops.push(remote, branch)
    
    def _git_status(self) -> Dict:
        """Get git status"""
        if not self.git_ops:
            return {"success": False, "error": "Git operations disabled"}
        return self.git_ops.status()
    
    # System Monitoring
    def _system_info(self) -> Dict:
        """Get system information"""
        return self.system_monitor.get_system_info()
    
    def _cpu_usage(self, interval: float = 1.0) -> Dict:
        """Get CPU usage"""
        return self.system_monitor.get_cpu_usage(interval)
    
    def _memory_usage(self) -> Dict:
        """Get memory usage"""
        return self.system_monitor.get_memory_usage()
    
    def _disk_usage(self, path: Optional[str] = None) -> Dict:
        """Get disk usage"""
        if path is None:
            path = "C:\\" if platform.system() == "Windows" else "/"
        return self.system_monitor.get_disk_usage(path)
    
    def _process_list(self, sort_by: str = "memory") -> Dict:
        """Get process list"""
        return self.system_monitor.get_process_list(sort_by)
    
    # Screen Capture
    def _screenshot(self, save_path: Optional[str] = None) -> Dict:
        """Take screenshot"""
        if not self.screen_capture:
            return {"success": False, "error": "Screen capture disabled"}
        
        if save_path is None:
            save_path = f"zero_agent/data/screenshots/screenshot_{int(asyncio.get_event_loop().time())}.png"
        
        img = self.screen_capture.capture_screen(Path(save_path))
        
        if img is not None:
            return {
                "success": True,
                "path": save_path,
                "size": img.shape
            }
        else:
            return {"success": False, "error": "Screenshot failed"}
    
    def _capture_region(self, x: int, y: int, width: int, height: int, save_path: Optional[str] = None) -> Dict:
        """Capture screen region"""
        if not self.screen_capture:
            return {"success": False, "error": "Screen capture disabled"}
        
        if save_path is None:
            save_path = f"zero_agent/data/screenshots/region_{int(asyncio.get_event_loop().time())}.png"
        
        img = self.screen_capture.capture_region(x, y, width, height, Path(save_path))
        
        if img is not None:
            return {
                "success": True,
                "path": save_path,
                "size": img.shape
            }
        else:
            return {"success": False, "error": "Region capture failed"}
    
    # Browser Automation
    async def _web_search(self, query: str) -> Dict:
        """Search the web"""
        if not config.is_tool_enabled("browser"):
            return {"success": False, "error": "Browser operations disabled"}
        
        try:
            if self.browser is None:
                self.browser = BrowserAutomation()
                await self.browser.initialize(headless=config.settings.browser_headless)
            
            results = await self.browser.search_google(query)
            
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
    
    async def _navigate_url(self, url: str) -> Dict:
        """Navigate to URL"""
        if not config.is_tool_enabled("browser"):
            return {"success": False, "error": "Browser operations disabled"}
        
        try:
            if self.browser is None:
                self.browser = BrowserAutomation()
                await self.browser.initialize(headless=config.settings.browser_headless)
            
            await self.browser.navigate(url)
            
            return {
                "success": True,
                "url": url
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _extract_webpage(self, url: str) -> Dict:
        """Extract content from webpage"""
        if not config.is_tool_enabled("browser"):
            return {"success": False, "error": "Browser operations disabled"}
        
        try:
            if self.browser is None:
                self.browser = BrowserAutomation()
                await self.browser.initialize(headless=config.settings.browser_headless)
            
            await self.browser.navigate(url)
            content = await self.browser.get_page_content()
            
            return {
                "success": True,
                "url": url,
                "content": content[:1000],  # First 1000 chars
                "full_length": len(content)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.browser:
            await self.browser.close()
        if self.screen_capture:
            self.screen_capture.close()

