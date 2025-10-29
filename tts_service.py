"""
🗣️ Zero Agent TTS Service
Simple, fast TTS server using pyttsx3 (Windows Speech API)
Port: 9033
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import pyttsx3
import io
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[TTS] %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Zero TTS Service", version="1.0.0")

# Initialize TTS engine
try:
    engine = pyttsx3.init()
    # Configure voice properties
    engine.setProperty('rate', 175)  # Speed (default: 200)
    engine.setProperty('volume', 0.9)  # Volume (0-1)
    
    # Try to set Hebrew voice if available
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'hebrew' in voice.name.lower() or 'he-' in voice.id.lower():
            engine.setProperty('voice', voice.id)
            logger.info(f"✓ Hebrew voice found: {voice.name}")
            break
    
    logger.info("✓ TTS Engine initialized successfully")
except Exception as e:
    logger.error(f"✗ Failed to initialize TTS engine: {e}")
    engine = None


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if engine is None:
        raise HTTPException(status_code=503, detail="TTS engine not initialized")
    return {
        "status": "healthy",
        "service": "Zero TTS",
        "engine": "pyttsx3",
        "backend": "Windows Speech API"
    }


@app.get("/tts")
def text_to_speech(
    text: str = "",
    q: Optional[str] = None  # Alternative parameter name
):
    """
    Convert text to speech
    
    Parameters:
    - text: Text to convert (or use 'q' parameter)
    
    Returns: WAV audio file
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="TTS engine not initialized")
    
    # Support both 'text' and 'q' parameters
    speech_text = text if text else q
    
    if not speech_text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    try:
        import os
        import time
        import tempfile
        
        # Use unique temp file to avoid conflicts
        temp_filename = f"temp_tts_{int(time.time() * 1000)}.wav"
        
        logger.info(f"Generating speech for: {speech_text[:50]}...")
        
        # Save to file (pyttsx3 requires this)
        engine.save_to_file(speech_text, temp_filename)
        engine.runAndWait()
        
        # Give it a moment to finish writing
        time.sleep(0.1)
        
        # Read the generated file
        if not os.path.exists(temp_filename):
            raise Exception(f"TTS file not generated: {temp_filename}")
            
        with open(temp_filename, 'rb') as f:
            audio_data = f.read()
        
        # Clean up temp file
        try:
            os.remove(temp_filename)
        except:
            pass
        
        logger.info(f"✓ Speech generated ({len(audio_data)} bytes)")
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "inline; filename=speech.wav",
                "Cache-Control": "no-cache"
            }
        )
        
    except Exception as e:
        logger.error(f"✗ TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


@app.get("/voices")
async def list_voices():
    """List available voices"""
    if engine is None:
        raise HTTPException(status_code=503, detail="TTS engine not initialized")
    
    voices = engine.getProperty('voices')
    return {
        "voices": [
            {
                "id": v.id,
                "name": v.name,
                "languages": v.languages if hasattr(v, 'languages') else []
            }
            for v in voices
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 70)
    logger.info("Zero Agent TTS Service")
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

