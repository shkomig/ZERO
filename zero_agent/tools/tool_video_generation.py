"""
🎥 Video Generation Tool
Integrates with CogVideoX-5B and HunyuanVideo on RTX 5090
"""

import logging
import requests
from typing import Dict, Any, Optional, Literal
from pathlib import Path

logger = logging.getLogger(__name__)


class VideoGenerationTool:
    """Generate videos using CogVideoX or HunyuanVideo"""
    
    def __init__(self):
        self.cogvideo_url = "http://localhost:9056"
        self.hunyuan_url = "http://localhost:9055"
        self.output_dir = Path("ZERO/generated/videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🎥 Video Generation Tool initialized (CogVideoX + HunyuanVideo)")
    
    def check_health(self, service: Literal["cogvideo", "hunyuan"] = "cogvideo") -> bool:
        """Check if video service is running"""
        try:
            url = self.cogvideo_url if service == "cogvideo" else self.hunyuan_url
            response = requests.get(f"{url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_video_cogvideo(
        self,
        prompt: str,
        num_frames: int = 49,
        height: int = 480,
        width: int = 848,
        steps: int = 50,
        guidance: float = 6.0,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate video using CogVideoX-5B (Text-to-Video)
        
        Args:
            prompt: Text description of video
            num_frames: Number of frames (9-49)
            height: Video height (256-720)
            width: Video width (256-1280)
            steps: Inference steps (10-50)
            guidance: Guidance scale (1.0-20.0)
            seed: Random seed
            
        Returns:
            Dict with status, filename, and download URL
        """
        try:
            logger.info(f"🎥 Generating video (CogVideoX): {prompt[:50]}...")
            
            if not self.check_health("cogvideo"):
                return {
                    "success": False,
                    "error": "CogVideoX service is not running"
                }
            
            payload = {
                "prompt": prompt,
                "num_frames": num_frames,
                "height": height,
                "width": width,
                "steps": steps,
                "guidance": guidance,
                "seed": seed
            }
            
            response = requests.post(
                f"{self.cogvideo_url}/generate",
                json=payload,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}: {response.text}"
                }
            
            result = response.json()
            
            logger.info(f"✅ Video generated: {result.get('filename')}")
            
            return {
                "success": True,
                "service": "CogVideoX",
                "filename": result.get("filename"),
                "download_url": f"{self.cogvideo_url}{result.get('download_url')}",
                "prompt": result.get("prompt"),
                "seed": result.get("seed"),
                "frames": num_frames,
                "resolution": f"{width}x{height}"
            }
            
        except requests.Timeout:
            return {
                "success": False,
                "error": "Video generation timed out (>5 minutes). Try reducing frames or steps."
            }
        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_video_hunyuan(
        self,
        prompt: str,
        image_path: Optional[str] = None,
        num_frames: int = 49,
        height: int = 480,
        width: int = 848,
        steps: int = 30,
        guidance: float = 6.0,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate video using HunyuanVideo (Image-to-Video or Text-to-Video)
        
        Args:
            prompt: Text description
            image_path: Input image for I2V (optional)
            num_frames: Number of frames (9-129)
            height: Video height (256-720)
            width: Video width (256-1280)
            steps: Inference steps (10-50)
            guidance: Guidance scale (1.0-20.0)
            seed: Random seed
            
        Returns:
            Dict with status, filename, and download URL
        """
        try:
            logger.info(f"🎬 Generating video (HunyuanVideo): {prompt[:50]}...")
            
            if not self.check_health("hunyuan"):
                return {
                    "success": False,
                    "error": "HunyuanVideo service is not running"
                }
            
            payload = {
                "prompt": prompt,
                "image_path": image_path,
                "num_frames": num_frames,
                "height": height,
                "width": width,
                "steps": steps,
                "guidance": guidance,
                "seed": seed
            }
            
            response = requests.post(
                f"{self.hunyuan_url}/generate",
                json=payload,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}: {response.text}"
                }
            
            result = response.json()
            
            logger.info(f"✅ Video generated: {result.get('filename')}")
            
            return {
                "success": True,
                "service": "HunyuanVideo",
                "filename": result.get("filename"),
                "download_url": f"{self.hunyuan_url}{result.get('download_url')}",
                "prompt": result.get("prompt"),
                "seed": result.get("seed"),
                "frames": num_frames,
                "resolution": f"{width}x{height}"
            }
            
        except requests.Timeout:
            return {
                "success": False,
                "error": "Video generation timed out (>5 minutes). Try reducing frames or steps."
            }
        except Exception as e:
            logger.error(f"❌ Video generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_simple(
        self,
        prompt: str,
        service: Literal["cogvideo", "hunyuan"] = "cogvideo"
    ) -> Dict[str, Any]:
        """
        Simple video generation with default settings
        
        Args:
            prompt: Text description
            service: Which service to use (cogvideo or hunyuan)
        """
        if service == "cogvideo":
            return self.generate_video_cogvideo(
                prompt=prompt,
                num_frames=49,
                steps=50
            )
        else:
            return self.generate_video_hunyuan(
                prompt=prompt,
                num_frames=49,
                steps=30
            )


# Global instance
video_tool = VideoGenerationTool()


def generate_video_command(prompt: str, service: str = "cogvideo", **kwargs) -> Dict[str, Any]:
    """
    Wrapper function for use as a tool
    
    Args:
        prompt: Text description of video
        service: "cogvideo" or "hunyuan"
        **kwargs: Additional parameters
    
    Returns:
        Generation result
    """
    if service == "hunyuan":
        return video_tool.generate_video_hunyuan(prompt, **kwargs)
    else:
        return video_tool.generate_video_cogvideo(prompt, **kwargs)


if __name__ == "__main__":
    # Test
    result = video_tool.generate_simple("A cat playing piano in a jazz club")
    print(result)

