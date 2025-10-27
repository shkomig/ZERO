"""
🎨 Image Generation Tool
Integrates with FLUX.1-schnell on RTX 5090 (ComfyUI)
"""

import logging
import requests
import uuid
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageGenerationTool:
    """Generate images using FLUX.1-schnell via ComfyUI"""
    
    def __init__(self):
        self.base_url = "http://localhost:9188"
        self.output_dir = Path("ZERO/generated/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🎨 Image Generation Tool initialized (FLUX.1-schnell)")
    
    def check_health(self) -> bool:
        """Check if FLUX service is running"""
        try:
            response = requests.get(f"{self.base_url}/system_stats", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 4,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate image from text prompt
        
        Args:
            prompt: Text description of desired image
            negative_prompt: What to avoid in image
            width: Image width (default 1024)
            height: Image height (default 1024)
            steps: Number of inference steps (4-8 for schnell)
            seed: Random seed for reproducibility
            
        Returns:
            Dict with status, filename, and path
        """
        try:
            logger.info(f"🎨 Generating image: {prompt[:50]}...")
            
            if not self.check_health():
                return {
                    "success": False,
                    "error": "FLUX service is not running. Start it with: C:\\AI-MEDIA-RTX5090\\services\\start-stack.ps1"
                }
            
            # Generate seed if not provided
            if seed is None:
                import random
                seed = random.randint(0, 2**32 - 1)
            
            # ComfyUI API workflow for FLUX.1-schnell
            # This is a simplified workflow - adjust based on your actual ComfyUI setup
            workflow = {
                "prompt": {
                    "3": {
                        "class_type": "KSampler",
                        "inputs": {
                            "seed": seed,
                            "steps": steps,
                            "cfg": 1.0,  # FLUX schnell works best with cfg=1.0
                            "sampler_name": "euler",
                            "scheduler": "simple",
                            "denoise": 1.0,
                            "model": ["4", 0],
                            "positive": ["6", 0],
                            "negative": ["7", 0],
                            "latent_image": ["5", 0]
                        }
                    },
                    "4": {
                        "class_type": "CheckpointLoaderSimple",
                        "inputs": {
                            "ckpt_name": "flux1-schnell-fp8.safetensors"
                        }
                    },
                    "5": {
                        "class_type": "EmptyLatentImage",
                        "inputs": {
                            "width": width,
                            "height": height,
                            "batch_size": 1
                        }
                    },
                    "6": {
                        "class_type": "CLIPTextEncode",
                        "inputs": {
                            "text": prompt,
                            "clip": ["4", 1]
                        }
                    },
                    "7": {
                        "class_type": "CLIPTextEncode",
                        "inputs": {
                            "text": negative_prompt,
                            "clip": ["4", 1]
                        }
                    },
                    "8": {
                        "class_type": "VAEDecode",
                        "inputs": {
                            "samples": ["3", 0],
                            "vae": ["4", 2]
                        }
                    },
                    "9": {
                        "class_type": "SaveImage",
                        "inputs": {
                            "filename_prefix": f"flux_zero_{seed}",
                            "images": ["8", 0]
                        }
                    }
                }
            }
            
            # Submit to ComfyUI
            response = requests.post(
                f"{self.base_url}/prompt",
                json={"prompt": workflow},
                timeout=120
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"ComfyUI returned status {response.status_code}"
                }
            
            result = response.json()
            prompt_id = result.get("prompt_id")
            
            logger.info(f"✅ Image generation started (ID: {prompt_id})")
            
            # For now, return immediately
            # In production, you'd poll /history/{prompt_id} to get the actual image
            return {
                "success": True,
                "message": "Image generation started",
                "prompt_id": prompt_id,
                "seed": seed,
                "prompt": prompt,
                "resolution": f"{width}x{height}",
                "note": "Check ComfyUI interface at http://localhost:9188 for result"
            }
            
        except Exception as e:
            logger.error(f"❌ Image generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_simple(self, prompt: str) -> Dict[str, Any]:
        """
        Simple image generation with default settings
        Easier to use from chat commands
        """
        return self.generate_image(
            prompt=prompt,
            width=1024,
            height=1024,
            steps=4
        )


# Global instance
image_tool = ImageGenerationTool()


def generate_image_command(prompt: str, **kwargs) -> Dict[str, Any]:
    """
    Wrapper function for use as a tool
    
    Args:
        prompt: Text description of image
        **kwargs: Additional parameters (width, height, steps, seed)
    
    Returns:
        Generation result
    """
    return image_tool.generate_image(prompt, **kwargs)


if __name__ == "__main__":
    # Test
    result = image_tool.generate_simple("A salmon fish swimming in Norwegian fjords, photorealistic")
    print(result)

