"""
🗣️ Zero Agent TTS Service - Google TTS Version
Fast, reliable TTS using gTTS
Port: 9033
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from gtts import gTTS  # type: ignore
import io
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[TTS] %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Zero TTS Service", version="2.0.0")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Zero TTS",
        "engine": "gTTS",
        "backend": "Google Text-to-Speech"
    }


@app.get("/tts")
def text_to_speech(text: str = "", voice: str = "default"):
    """
    Convert text to speech using Google TTS

    Parameters:
    - text: Text to convert
    - voice: Voice style (default, male, female)
      Note: gTTS has limited voice options

    Returns: MP3 audio file
    """
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    try:
        logger.info(f"Generating speech: {text[:50]}...")
        
        # Detect language (Hebrew or English)
        has_hebrew = any('\u0590' <= c <= '\u05FF' for c in text)
        lang = 'iw' if has_hebrew else 'en'  # 'iw' is Hebrew in Google TTS
        
        # Select TLD based on voice preference (affects accent)
        # English: 'com' = American, 'co.uk' = British
        # Hebrew: 'co.il' = Israeli accent
        tld = 'com'  # Default
        if voice == 'male' or voice == 'masculine':
            # Use British English (sounds slightly more masculine)
            tld = 'co.uk' if lang == 'en' else 'co.il'
        elif voice == 'female' or voice == 'feminine':
            # Use American English (default, sounds more neutral/feminine)
            tld = 'com' if lang == 'en' else 'co.il'
        
        logger.info(f"Language: {lang}, TLD: {tld}, Voice: {voice}")
        
        # Generate speech
        tts = gTTS(text=text, lang=lang, slow=False, tld=tld)
        
        # Save to BytesIO buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        audio_size = len(audio_buffer.getvalue())
        logger.info(f"✓ Speech generated ({audio_size} bytes)")
        
        # Return as streaming response
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3",
                "Cache-Control": "no-cache"
            }
        )
        
    except Exception as e:
        logger.error(f"✗ TTS failed: {e}")
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 70)
    logger.info("Zero Agent TTS Service - Google TTS")
    logger.info("=" * 70)
    logger.info("Starting server...")
    logger.info("TTS Endpoint: http://localhost:9033/tts?text=YOUR_TEXT")
    logger.info("Health Check: http://localhost:9033/health")
    logger.info("Supports: Hebrew (iw) & English (en)")
    logger.info("=" * 70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9033,
        log_level="info"
    )

