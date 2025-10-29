"""
🗣️ Zero Agent TTS Service - SIMPLE VERSION
Using Windows COM Speech API directly
Port: 9033
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import logging
import win32com.client
import pythoncom

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[TTS] %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Zero TTS Service", version="1.0.0")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Zero TTS",
        "engine": "Windows SAPI5",
        "backend": "COM API"
    }


@app.get("/tts")
def text_to_speech(text: str = ""):
    """
    Convert text to speech using Windows Speech API
    
    Parameters:
    - text: Text to convert
    
    Returns: Audio played directly (no file)
    """
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    try:
        # Initialize COM for this thread
        pythoncom.CoInitialize()
        
        logger.info(f"Speaking: {text[:50]}...")
        
        # Create SAPI Voice object
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        
        # Speak the text (blocking call)
        speaker.Speak(text)
        
        # Cleanup
        pythoncom.CoUninitialize()
        
        logger.info(f"✓ Speech completed")
        
        # Return success (audio was played directly)
        return {"status": "success", "message": "Speech completed", "text": text[:50]}
        
    except Exception as e:
        logger.error(f"✗ TTS failed: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 70)
    logger.info("Zero Agent TTS Service - SIMPLE")
    logger.info("=" * 70)
    logger.info("Starting server...")
    logger.info("TTS Endpoint: http://localhost:9033/tts?text=YOUR_TEXT")
    logger.info("Health Check: http://localhost:9033/health")
    logger.info("=" * 70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9033,
        log_level="info"
    )

