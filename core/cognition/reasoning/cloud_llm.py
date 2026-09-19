import os
import json
import httpx
import base64
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

class CloudLLMProvider:
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=60.0)
        self.groq_active = bool(GROQ_API_KEY)
        self.gemini_active = bool(GEMINI_API_KEY)
        self.mistral_active = bool(MISTRAL_API_KEY)

    async def call_mistral_vision(self, text: str, image_path: str, context: str) -> Optional[Dict]:
        """🧬 Phase 6: Real-time Mistral Pixtral Vision Integration"""
        if not self.mistral_active: return None
        
        try:
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            url = "https://api.mistral.ai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
            payload = {
                "model": "pixtral-large-latest",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": f"Context: {context}\nQuestion: {text}"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]
                    }
                ],
                "max_tokens": 300
            }
            async with httpx.AsyncClient() as client:
                res = await client.post(url, headers=headers, json=payload, timeout=30)
                if res.status_code == 200:
                    return {
                        "type": "CHAT", "intent": "vision_analyze",
                        "response": res.json()["choices"][0]["message"]["content"],
                        "mode": "hud"
                    }
        except Exception as e:
            print(f"[MISTRAL_VISION_FAIL] {e}")
        return None

    async def call_groq(self, text: str, system_prompt: str) -> Optional[Dict]:
        if not self.groq_active: return None
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.5
        }
        res = await self.http_client.post(url, headers=headers, json=payload, timeout=20.0)
        if res.status_code == 200:
            return json.loads(res.json()["choices"][0]["message"]["content"])
        return None

    async def call_gemini_chat(self, text: str, system_prompt: str) -> Optional[Dict]:
        if not self.gemini_active: return None

        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[f"{system_prompt}\n\n{text}"],
            )
            if response.text:
                return {"type": "CHAT", "intent": "chat", "response": response.text, "mode": "hud"}
        except Exception as e:
            print(f"[GEMINI_CHAT_FAIL] {e}")
        return None

    async def call_gemini_vision(self, text: str, image_path: str, context: str) -> Optional[Dict]:
        """🧬 Phase 6: Real-time Gemini 2.0 Flash Vision Fallback"""
        if not self.gemini_active: return None
        
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            with open(image_path, "rb") as f:
                img_bytes = f.read()
            
            prompt = f"Context: {context}\nQuestion: {text}\nAnalyze this image tactically as JARVIS."
            
            from PIL import Image as PILImage
            img = PILImage.open(image_path)
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, img]
            )
            
            if response.text:
                return {
                    "type": "CHAT", "intent": "vision_analyze",
                    "response": response.text,
                    "mode": "hud"
                }
        except Exception as e:
            print(f"[GEMINI_VISION_FAIL] {e}")
        return None

cloud_llm_provider = CloudLLMProvider()
