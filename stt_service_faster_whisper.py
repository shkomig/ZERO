"""
🎤 Zero Agent STT Service - Faster-Whisper
Fast, reliable Speech-to-Text using Faster-Whisper
Port: 9034
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel
import logging
import tempfile
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[STT] %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Zero STT Service", version="2.0.0")

# Initialize Whisper model
try:
    # Use base model for speed, with GPU acceleration if available
    model = WhisperModel("base", device="cuda", compute_type="float16")
    logger.info("✓ Faster-Whisper model loaded (base, CUDA, float16)")
except Exception as e:
    logger.warning(f"CUDA not available, using CPU: {e}")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    logger.info("✓ Faster-Whisper model loaded (base, CPU, int8)")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Zero STT",
        "engine": "Faster-Whisper",
        "model": "base"
    }


@app.post("/stt")
async def speech_to_text(audio_file: UploadFile = File(...)):
    """
    Convert speech to text using Faster-Whisper
    
    Parameters:
    - audio_file: Audio file (WAV, MP3, etc.)
    
    Returns: JSON with transcribed text
    """
    if not audio_file:
        raise HTTPException(status_code=400, detail="No audio file provided")
    
    try:
        logger.info(f"Processing audio file: {audio_file.filename}")
        
        # Read audio file
        audio_data = await audio_file.read()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe with Faster-Whisper
            segments, info = model.transcribe(
                temp_file_path,
                language="he",  # Hebrew by default, can be auto-detected
                beam_size=5,
                best_of=5,
                temperature=0.0,
                condition_on_previous_text=False,
                initial_prompt="",  # Can add context here
                word_timestamps=True,
                vad_filter=True,  # Voice Activity Detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Collect all segments
            full_text = ""
            segments_list = []
            
            for segment in segments:
                full_text += segment.text + " "
                segments_list.append({
                    "text": segment.text,
                    "start": segment.start,
                    "end": segment.end,
                    "words": [{"word": word.word, "start": word.start, "end": word.end} for word in segment.words] if hasattr(segment, 'words') else []
                })
            
            # Clean up
            os.unlink(temp_file_path)
            
            result = {
                "text": full_text.strip(),
                "language": info.language,
                "language_probability": info.language_probability,
                "duration": info.duration,
                "segments": segments_list
            }
            
            logger.info(f"✓ Transcription completed: {len(full_text)} chars, {info.language} ({info.language_probability:.2f})")
            return JSONResponse(content=result)
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise e
            
    except Exception as e:
        logger.error(f"✗ STT failed: {e}")
        raise HTTPException(status_code=500, detail=f"STT failed: {str(e)}")


@app.post("/stt-stream")
async def speech_to_text_stream(audio_file: UploadFile = File(...)):
    """
    Convert speech to text with streaming results
    """
    if not audio_file:
        raise HTTPException(status_code=400, detail="No audio file provided")
    
    try:
        logger.info(f"Streaming transcription: {audio_file.filename}")
        
        # Read audio file
        audio_data = await audio_file.read()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        try:
            # Transcribe with streaming
            segments, info = model.transcribe(
                temp_file_path,
                language="he",
                beam_size=1,  # Faster for streaming
                temperature=0.0,
                condition_on_previous_text=False,
                word_timestamps=True,
                vad_filter=True
            )
            
            # Stream results
            results = []
            for segment in segments:
                results.append({
                    "text": segment.text,
                    "start": segment.start,
                    "end": segment.end,
                    "is_final": True
                })
            
            # Clean up
            os.unlink(temp_file_path)
            
            return JSONResponse(content={
                "segments": results,
                "language": info.language,
                "duration": info.duration
            })
            
        except Exception as e:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise e
            
    except Exception as e:
        logger.error(f"✗ Streaming STT failed: {e}")
        raise HTTPException(status_code=500, detail=f"Streaming STT failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 70)
    logger.info("Zero Agent STT Service - Faster-Whisper")
    logger.info("=" * 70)
    logger.info("Starting server...")
    logger.info("STT Endpoint: http://localhost:9034/stt")
    logger.info("Streaming STT: http://localhost:9034/stt-stream")
    logger.info("Health Check: http://localhost:9034/health")
    logger.info("Supports: Hebrew (he) & English (en)")
    logger.info("=" * 70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9034,
        log_level="info"
    )
