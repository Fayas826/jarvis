import httpx
import json
import threading
import subprocess
from typing import Optional, Dict

TARGET_CORE_MODEL = "llama3:8b"
OLLAMA_URL = "http://localhost:11434/api/generate"

class LocalLLMProvider:
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=60.0)
        self._inference_lock = threading.Lock()
        self._active_requests = 0
        self._unload_timer = None

    async def call_local_ollama(self, text: str, system_prompt: str) -> Optional[Dict]:
        with self._inference_lock:
            self._active_requests += 1
            if self._unload_timer:
                self._unload_timer.cancel()
        
        try:
            payload = {
                "model": TARGET_CORE_MODEL,
                "prompt": f"{system_prompt}\n\nUser: {text}\nJSON:",
                "stream": False,
                "format": "json"
            }
            res = await self.http_client.post(OLLAMA_URL, json=payload, timeout=15.0)
            if res.status_code == 200:
                return json.loads(res.json()["response"])
        except Exception as e:
            print(f"[BRAIN_LOCAL_FAIL] {e}")
        finally:
            with self._inference_lock:
                self._active_requests -= 1
                if self._active_requests == 0:
                    self._reset_idle_timer()
        return None

    def _reset_idle_timer(self):
        with self._inference_lock:
            if self._unload_timer:
                self._unload_timer.cancel()
            
            def unload():
                with self._inference_lock:
                    if self._active_requests > 0: return
                    subprocess.run(["ollama", "stop", TARGET_CORE_MODEL], capture_output=True)

            self._unload_timer = threading.Timer(300, unload)
            self._unload_timer.daemon = True
            self._unload_timer.start()

local_llm_provider = LocalLLMProvider()
