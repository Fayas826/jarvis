import time
import base64
import os
import threading
import asyncio
from PIL import Image
import io
import pyautogui
import requests
import httpx
from core.cognition.reasoning.shared_state import INTEL_CACHE

# 🧿 O.M.E.G.A. TIER_4: VISION_CORE
# Autonomous Perception & Focal Plane Analysis

class VisionCore:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.active = False
        self.thread = None
        self.last_analysis = "Initializing visual cortex..."
        self.analysis_interval = 15 # Seconds between autonomous scans
        self.on_insight = None # Callback for real-time reporting

    def start(self):
        """Ignites the visual cortex."""
        if self.active: return
        self.active = True
        self.thread = threading.Thread(target=self._perception_loop, daemon=True)
        self.thread.start()
        print("[VISION] Visual Cortex: ONLINE")

    def stop(self):
        """Disengages perception."""
        self.active = False
        print("[VISION] Visual Cortex: STANDBY")

    def _capture_screen(self):
        """Captures the tactical focal plane."""
        screenshot = pyautogui.screenshot()
        # Resize for faster processing / lower bandwidth
        screenshot.thumbnail((1280, 720))
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='JPEG', quality=70)
        return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

    async def _analyze_vision(self, b64_image):
        """Consults the cloud nodes for visual perception using Async hhtpx."""
        if not self.api_key: return "Vision Engine Error: Missing API Key."
        
        try:
            # 🧬 TIER_8: MULTIMODAL_RESONANCE
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={self.api_key}"
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "SYSTEM_PROMPT: You are JARVIS's visual cortex. Analyze this tactical focal plane (screenshot). "
                                "1. Identify active system nodes (open windows). "
                                "2. Detect MISSION_CRITICAL errors (code bugs, terminal failures). "
                                "3. Observe user intent based on the environment. "
                                "Output a single, sophisticated, technical paragraph. Mention specific file names if visible."},
                        {"inline_data": {"mime_type": "image/jpeg", "data": b64_image}}
                    ]
                }]
            }
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, timeout=30.0)
                if res.status_code == 200:
                    data = res.json()
                    insight = data['candidates'][0]['content']['parts'][0]['text']
                    return insight
            return "Visual telemetry lag detected."
        except Exception as e:
            return f"Vision Error: {str(e)}"

    def _perception_loop(self):
        """The continuous autonomous perception cycle."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self.active:
            try:
                # 🧬 TIER_4: PERCEPTION_CHECK
                b64 = self._capture_screen()
                insight = loop.run_until_complete(self._analyze_vision(b64))
                self.last_analysis = insight
                
                # Atomic cache update
                INTEL_CACHE["vision_insight"] = insight
                
                if self.on_insight:
                    self.on_insight(insight)
                
            except Exception as e:
                print(f"[VISION] Perception Failure: {e}")
            
            time.sleep(self.analysis_interval)

# Global Instance
vision_core = VisionCore()
