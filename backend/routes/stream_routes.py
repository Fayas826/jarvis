import time
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.perception.audio.audio_accelerator import audio_accelerator

import logging
logger = logging.getLogger("stream_routes")

router = APIRouter()

@router.websocket("/stream/audio")
async def audio_stream(websocket: WebSocket):
    await websocket.accept()
    logger.info("[AudioStream] WebSocket connected. Awaiting PCM data...")
    
    chunk_count = 0
    start_time = time.time()
    voice_detected_count = 0
    
    try:
        while True:
            # Expecting raw binary PCM frames
            data = await websocket.receive_bytes()
            chunk_count += 1
            
            # Pass directly to C++ engine
            t0 = time.perf_counter()
            metrics = audio_accelerator.process_chunk(data)
            t1 = time.perf_counter()
            
            process_ms = (t1 - t0) * 1000.0
            
            if metrics["is_voice"]:
                voice_detected_count += 1
                
            # For demonstration and real-time visualization on the HUD,
            # send back the microsecond analysis every ~10 chunks
            if chunk_count % 10 == 0:
                await websocket.send_text(json.dumps({
                    "type": "audio_metrics",
                    "rms": round(metrics["rms"], 2),
                    "zcr": metrics["zcr"],
                    "is_voice": metrics["is_voice"],
                    "latency_ms": round(process_ms, 3)
                }))
                
    except WebSocketDisconnect:
        duration = time.time() - start_time
        logger.warning(f"[AudioStream] Client disconnected. Processed {chunk_count} chunks in {duration:.1f}s.")
    except Exception as e:
        logger.error(f"[AudioStream] Error: {e}")
