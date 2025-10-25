"""
Screen capture tool using multiple backends with fallbacks
Prioritizes windows-capture (GPU-accelerated) then falls back to alternatives
"""

import numpy as np
from PIL import Image
from pathlib import Path
from typing import Optional
import platform


class ScreenCapture:
    """High-performance screen capture with multiple backends"""
    
    def __init__(self):
        self.capture = None
        self.backend = None
        self.setup_capture()
    
    def setup_capture(self):
        """Initialize capture system with fallbacks"""
        # Try windows-capture (fastest, Windows only)
        if platform.system() == "Windows":
            try:
                import dxcam
                self.capture = dxcam.create()
                self.backend = "dxcam"
                print("[OK] Screen capture using DXcam (GPU-accelerated)")
                return
            except (ImportError, Exception) as e:
                print(f"[WARN] DXcam not available: {e}")
        
        # Fallback to mss (cross-platform, fast)
        try:
            import mss
            self.capture = mss.mss()
            self.backend = "mss"
            print("[OK] Screen capture using MSS")
            return
        except (ImportError, Exception) as e:
            print(f"[WARN] MSS not available: {e}")
        
        # Final fallback to PIL/PyAutoGUI
        try:
            import pyautogui
            self.backend = "pyautogui"
            print("[OK] Screen capture using PyAutoGUI (slowest)")
        except ImportError:
            print("[ERROR] No screen capture backend available")
            self.backend = None
    
    def capture_screen(self, save_path: Optional[Path] = None) -> Optional[np.ndarray]:
        """
        Capture entire screen
        
        Args:
            save_path: Optional path to save screenshot
            
        Returns:
            Numpy array of image or None if failed
        """
        if not self.backend:
            print("[ERROR] No capture backend available")
            return None
        
        try:
            if self.backend == "dxcam":
                img = self.capture.grab()
                if img is None:
                    print("[WARN] DXcam grab failed, trying fallback")
                    return self._fallback_capture(save_path)
                img_array = np.array(img)
                
            elif self.backend == "mss":
                monitor = self.capture.monitors[1]  # Primary monitor
                sct_img = self.capture.grab(monitor)
                img_array = np.array(sct_img)
                
            elif self.backend == "pyautogui":
                import pyautogui
                screenshot = pyautogui.screenshot()
                img_array = np.array(screenshot)
            
            else:
                return None
            
            # Save if requested
            if save_path:
                Image.fromarray(img_array).save(save_path)
                print(f"[SAVE] Screenshot saved to {save_path}")
            
            return img_array
            
        except Exception as e:
            print(f"[ERROR] Screen capture error: {e}")
            return self._fallback_capture(save_path)
    
    def _fallback_capture(self, save_path: Optional[Path] = None) -> Optional[np.ndarray]:
        """Fallback capture method"""
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            img_array = np.array(screenshot)
            
            if save_path:
                screenshot.save(save_path)
            
            return img_array
        except Exception as e:
            print(f"[ERROR] Fallback capture failed: {e}")
            return None
    
    def capture_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        save_path: Optional[Path] = None
    ) -> Optional[np.ndarray]:
        """
        Capture specific screen region
        
        Args:
            x, y: Top-left corner coordinates
            width, height: Region dimensions
            save_path: Optional path to save screenshot
            
        Returns:
            Numpy array of image or None if failed
        """
        try:
            if self.backend == "dxcam":
                img = self.capture.grab(region=(x, y, x + width, y + height))
                if img is None:
                    raise Exception("DXcam grab returned None")
                img_array = np.array(img)
                
            elif self.backend == "mss":
                monitor = {"left": x, "top": y, "width": width, "height": height}
                sct_img = self.capture.grab(monitor)
                img_array = np.array(sct_img)
                
            elif self.backend == "pyautogui":
                import pyautogui
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
                img_array = np.array(screenshot)
            
            else:
                return None
            
            if save_path:
                Image.fromarray(img_array).save(save_path)
            
            return img_array
            
        except Exception as e:
            print(f"[ERROR] Region capture error: {e}")
            return None
    
    def get_screen_size(self) -> tuple[int, int]:
        """Get primary screen size"""
        try:
            if self.backend == "pyautogui":
                import pyautogui
                return pyautogui.size()
            elif self.backend in ["dxcam", "mss"]:
                # Get from monitor info
                if self.backend == "mss":
                    monitor = self.capture.monitors[1]
                    return (monitor["width"], monitor["height"])
                else:
                    # DXcam default
                    return (1920, 1080)
        except Exception as e:
            print(f"[WARN] Could not get screen size: {e}")
            return (1920, 1080)  # Default
    
    def close(self):
        """Close capture resources"""
        if self.backend == "dxcam" and self.capture:
            try:
                del self.capture
            except:
                pass

