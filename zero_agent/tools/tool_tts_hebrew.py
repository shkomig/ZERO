"""
🗣️ Hebrew Text-to-Speech Tool
Integrates with MMS-TTS Hebrew model
⚠️ License: CC-BY-NC 4.0 (Non-commercial use only!)
"""

import logging
import requests
from typing import Dict, Any, Optional
from pathlib import Path
import urllib.parse

logger = logging.getLogger(__name__)


class HebrewTTSTool:
    """Convert Hebrew text to speech"""
    
    def __init__(self):
        self.base_url = "http://localhost:9033"
        self.output_dir = Path("ZERO/generated/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🗣️ Hebrew TTS Tool initialized (MMS-TTS)")
    
    def check_health(self) -> bool:
        """Check if TTS service is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def text_to_speech(
        self,
        text: str,
        seed: Optional[int] = None,
        save_to_file: bool = True
    ) -> Dict[str, Any]:
        """
        Convert Hebrew text to speech
        
        Args:
            text: Hebrew text to speak
            seed: Random seed for reproducibility
            save_to_file: Whether to save audio file locally
            
        Returns:
            Dict with status, filename, and audio info
        """
        try:
            logger.info(f"🗣️ Generating speech: {text[:50]}...")
            
            if not self.check_health():
                return {
                    "success": False,
                    "error": "Hebrew TTS service is not running"
                }
            
            # URL encode the text for GET request
            encoded_text = urllib.parse.quote(text)
            
            # Use GET endpoint for simplicity
            response = requests.get(
                f"{self.base_url}/tts?q={encoded_text}",
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"TTS API returned status {response.status_code}"
                }
            
            # Save audio file if requested
            if save_to_file:
                import time
                timestamp = int(time.time())
                filename = f"tts_hebrew_{timestamp}.wav"
                filepath = self.output_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"✅ Audio saved: {filepath}")
                
                return {
                    "success": True,
                    "message": f"Speech generated: {text}",
                    "filename": filename,
                    "filepath": str(filepath),
                    "text": text,
                    "format": "WAV",
                    "license": "CC-BY-NC 4.0 (Non-commercial only)"
                }
            else:
                return {
                    "success": True,
                    "message": f"Speech generated: {text}",
                    "audio_bytes": len(response.content),
                    "text": text,
                    "format": "WAV",
                    "license": "CC-BY-NC 4.0 (Non-commercial only)"
                }
                
        except Exception as e:
            logger.error(f"❌ TTS generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def speak_simple(self, text: str) -> Dict[str, Any]:
        """
        Simple TTS with default settings
        Easier to use from chat commands
        """
        return self.text_to_speech(text, save_to_file=True)


# Global instance
tts_tool = HebrewTTSTool()


def text_to_speech_command(text: str, **kwargs) -> Dict[str, Any]:
    """
    Wrapper function for use as a tool
    
    Args:
        text: Hebrew text to speak
        **kwargs: Additional parameters (seed, save_to_file)
    
    Returns:
        TTS result
    """
    return tts_tool.text_to_speech(text, **kwargs)


if __name__ == "__main__":
    # Test
    result = tts_tool.speak_simple("שלום עולם, אני זירו, עוזר הבינה המלאכותית שלך")
    print(result)

