import os
import time
import base64
import threading
import datetime
import io
from pathlib import Path
from PIL import Image
import httpx
from dotenv import load_dotenv
from core.reliability.system_logger import system_logger

try:
    import pyautogui
except Exception as e:
    from core.reliability.system_logger import system_logger
    system_logger.log('ERROR', 'vision_loop', f'Unhandled exception: {e}')
    pyautogui = None

try:
    from google import genai
except Exception as e:
    from core.reliability.system_logger import system_logger
    system_logger.log('ERROR', 'vision_loop', f'Unhandled exception: {e}')
    genai = None

load_dotenv()

# 👁️ O.M.E.G.A. VISION_FEEDBACK_LOOP_V3 (Hybrid Provider)
# Automatically analyzes the user's screen every 60 seconds
# Tiers: Mistral (Pixtral Large) -> Gemini (2.0 Flash)

class VisionLoop:
    def __init__(self, interval=60):
        self.interval = interval
        self.running = False
        self.gemini_client = None
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.latest_insight = "Scanning tactical focal plane..."
        # Deferred init to start() to prevent import blocking

    def _init_clients(self):
        if self.gemini_api_key and genai is not None:
            try:
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
                print("[VISION_LOOP] Gemini Vision Link established.")
            except Exception as e:
                print(f"[VISION_LOOP] Gemini init fail: {e}")

    def capture_screen(self):
        """Captures the current screen and returns it as a Base64 string and raw bytes."""
        if pyautogui is None:
            print("[VISION_LOOP] Capture unavailable: pyautogui not installed.")
            return None, None
        try:
            screenshot = pyautogui.screenshot()
            # Downscale for token efficiency
            screenshot.thumbnail((1024, 1024))
            
            buffered = io.BytesIO()
            screenshot.save(buffered, format="JPEG", quality=70)
            img_bytes = buffered.getvalue()
            img_b64 = base64.b64encode(img_bytes).decode('utf-8')
            return img_bytes, img_b64
        except Exception as e:
            print(f"[VISION_LOOP] Capture error: {e}")
            return None, None

    async def analyze_screen_async(self):
        """Sends the screenshot to the best available vision model."""
        img_bytes, img_b64 = self.capture_screen()
        if not img_bytes: return

        prompt = (
            "You are JARVIS. Analyze this screen. Be concise and tactical. "
            "1. What is the user doing? "
            "2. Provide one proactive suggestion. "
            "Limit to 2 sentences."
        )

        # 🧬 TIER_1: MISTRAL PIXTRAL (High Fidelity)
        if self.mistral_api_key:
            try:
                async with httpx.AsyncClient() as client:
                    url = "https://api.mistral.ai/v1/chat/completions"
                    headers = {"Authorization": f"Bearer {self.mistral_api_key}"}
                    payload = {
                        "model": "pixtral-large-latest",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                                ]
                            }
                        ],
                        "max_tokens": 100
                    }
                    res = await client.post(url, headers=headers, json=payload, timeout=25)
                    if res.status_code == 200:
                        self.latest_insight = res.json()["choices"][0]["message"]["content"].strip()
                        self._broadcast_insight("MISTRAL_PIXTRAL")
                        return
                    elif res.status_code == 429:
                        system_logger.log("WARNING", "VISION", "MISTRAL_QUOTA_EXHAUSTED", {"status": 429})
                    else:
                        system_logger.log("ERROR", "VISION", "MISTRAL_REJECTED", {"status": res.status_code})
            except Exception as e:
                system_logger.log("ERROR", "VISION", "MISTRAL_EXCEPTION", {"error": str(e)})

        # 🧬 TIER_2: GEMINI VISION (Fallback)
        if self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[prompt, Image.open(io.BytesIO(img_bytes))]
                )
                self.latest_insight = response.text.strip()
                self._broadcast_insight("GEMINI_VISION")
                return
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    system_logger.log("CRITICAL", "VISION", "QUOTA_EXHAUSTED", {"provider": "GEMINI"})
                else:
                    system_logger.log("ERROR", "VISION", "GEMINI_FAILURE", {"error": str(e)})

    def _broadcast_insight(self, source):
        system_logger.log("SUCCESS", "VISION", "INSIGHT_GENERATED", {"source": source})
        try:
            from core.cognition.reasoning.shared_state import NEURAL_INSIGHT_CACHE, NEURAL_LOCK
            with NEURAL_LOCK:
                NEURAL_INSIGHT_CACHE["visual"] = self.latest_insight
        except: pass

    def run(self):
        self.running = True
        print(f"[VISION_LOOP] Initiating Vision Feedback Loop (Interval: {self.interval}s)")
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.running:
            try:
                loop.run_until_complete(self.analyze_screen_async())
            except Exception as e:
                self.latest_insight = "Scanning tactical focal plane..."
            time.sleep(self.interval)

    def start(self):
        if not self.running:
            self._init_clients() # Initialize clients only when starting
            thread = threading.Thread(target=self.run, daemon=True)
            thread.start()

    def stop(self):
        self.running = False

# Singleton instance
vision_loop = VisionLoop()
