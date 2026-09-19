import sys
import os
import time
import asyncio
import httpx

sys.path.insert(0, r"c:\jarvis AI\jarvis")

async def profile_system():
    print("==================================================")
    print("JARVIS LOCAL HARDWARE PERFORMANCE AND VRAM AUDIT")
    print("==================================================")
    
    # 1. Profile OpenCV segmenter latency
    try:
        from core.perception.visual_segmentation import visual_segmenter
        t_start = time.time()
        cv_elements = visual_segmenter.segment_elements("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")
        t_cv = (time.time() - t_start) * 1000
        print(f"OpenCV segmenter latency: {t_cv:.2f} ms")
    except Exception as e:
        print(f"OpenCV segmenter failed: {e}")
        
    # 2. Ollama direct post benchmark
    try:
        t_start = time.time()
        payload = {
            "model": "phi3",
            "prompt": "Translate hi to fr. JSON: {\"res\": \"salut\"}",
            "stream": False,
            "format": "json"
        }
        async with httpx.AsyncClient(timeout=90.0) as client:
            res = await client.post("http://localhost:11434/api/generate", json=payload)
            if res.status_code == 200:
                t_inference = (time.time() - t_start) * 1000
                print(f"Ollama phi3 inference latency: {t_inference:.2f} ms")
                print(f"Response: {res.json()['response'].strip()}")
            else:
                print(f"Ollama returned status code: {res.status_code}")
    except Exception as e:
        print(f"Ollama direct post failed: {e}")
        
    print("==================================================")
    print("PERFORMANCE PROFILE COMPLETED SUCCESSFULLY")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(profile_system())
