"""
🎤 Zero Agent Web STT Service
WebSocket-based Speech-to-Text for real-time transcription
Port: 9035
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from faster_whisper import WhisperModel
import logging
import base64
import tempfile
import os
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[WebSTT] %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Zero Web STT Service", version="1.0.0")

# Initialize Whisper model
try:
    model = WhisperModel("base", device="cuda", compute_type="float16")
    logger.info("✓ Faster-Whisper model loaded (base, CUDA, float16)")
except Exception as e:
    logger.warning(f"CUDA not available, using CPU: {e}")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    logger.info("✓ Faster-Whisper model loaded (base, CPU, int8)")


@app.get("/")
async def get():
    """Simple test page"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Zero Web STT Test</title>
    </head>
    <body>
        <h1>Zero Web STT Test</h1>
        <button id="startBtn">Start Recording</button>
        <button id="stopBtn" disabled>Stop Recording</button>
        <div id="result"></div>
        
        <script>
            let mediaRecorder;
            let websocket;
            let audioChunks = [];
            
            const startBtn = document.getElementById('startBtn');
            const stopBtn = document.getElementById('stopBtn');
            const result = document.getElementById('result');
            
            startBtn.onclick = async () => {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    
                    websocket = new WebSocket('ws://localhost:9035/ws');
                    
                    websocket.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        result.innerHTML += `<p><strong>${data.type}:</strong> ${data.text}</p>`;
                    };
                    
                    websocket.onopen = () => {
                        mediaRecorder.ondataavailable = (event) => {
                            if (event.data.size > 0) {
                                const reader = new FileReader();
                                reader.onload = () => {
                                    const base64 = reader.result.split(',')[1];
                                    websocket.send(JSON.stringify({
                                        type: 'audio',
                                        data: base64
                                    }));
                                };
                                reader.readAsDataURL(event.data);
                            }
                        };
                        
                        mediaRecorder.start(1000); // Send data every second
                        startBtn.disabled = true;
                        stopBtn.disabled = false;
                        result.innerHTML = '<p>Recording started...</p>';
                    };
                } catch (err) {
                    alert('Error accessing microphone: ' + err);
                }
            };
            
            stopBtn.onclick = () => {
                if (mediaRecorder && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                    if (websocket) {
                        websocket.close();
                    }
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                    result.innerHTML += '<p>Recording stopped.</p>';
                }
            };
        </script>
    </body>
    </html>
    """)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "audio":
                try:
                    # Decode base64 audio
                    audio_data = base64.b64decode(message["data"])
                    
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                        temp_file.write(audio_data)
                        temp_file_path = temp_file.name
                    
                    try:
                        # Transcribe
                        segments, info = model.transcribe(
                            temp_file_path,
                            language="he",  # Hebrew by default
                            beam_size=1,
                            temperature=0.0,
                            condition_on_previous_text=False,
                            word_timestamps=True,
                            vad_filter=True
                        )
                        
                        # Send results
                        for segment in segments:
                            await websocket.send_text(json.dumps({
                                "type": "transcription",
                                "text": segment.text,
                                "start": segment.start,
                                "end": segment.end,
                                "is_final": True
                            }))
                        
                        # Clean up
                        os.unlink(temp_file_path)
                        
                    except Exception as e:
                        if os.path.exists(temp_file_path):
                            os.unlink(temp_file_path)
                        logger.error(f"Transcription error: {e}")
                        await websocket.send_text(json.dumps({
                            "type": "error",
                            "message": str(e)
                        }))
                        
                except Exception as e:
                    logger.error(f"Audio processing error: {e}")
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))
                    
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Zero Web STT",
        "engine": "Faster-Whisper",
        "model": "base"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 70)
    logger.info("Zero Agent Web STT Service - Faster-Whisper")
    logger.info("=" * 70)
    logger.info("Starting server...")
    logger.info("Web Interface: http://localhost:9035/")
    logger.info("WebSocket: ws://localhost:9035/ws")
    logger.info("Health Check: http://localhost:9035/health")
    logger.info("Supports: Hebrew (he) & English (en)")
    logger.info("=" * 70)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9035,
        log_level="info"
    )
