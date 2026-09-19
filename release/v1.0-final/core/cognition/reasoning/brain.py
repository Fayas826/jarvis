import os
import json
import asyncio
import datetime
import httpx
import time
import base64
from typing import Optional, Tuple, Dict, Any
from dotenv import load_dotenv

# Local Imports
from core.cognition.reasoning.neural_core import neural_route, semantic_memory_search, get_neural_core_status
from core.cognition.memory.long_term_memory import ltm
from core.cognition.memory.cache_manager import cache_manager
from core.cognition.memory.memory import memory
from core.cognition.memory.sentient_memory import sentient_memory
from core.cognition.reasoning.minimax_provider import minimax
from core.cognition.reasoning.sentience import sentience_core
from core.cognition.reasoning.emotion_engine import emotion_engine

load_dotenv()

# --- BRAIN CONFIGURATION ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OLLAMA_URL = "http://localhost:11434/api/generate"

TARGET_CORE_MODEL = "llama3:8b"
SECONDARY_CORE_MODEL = "phi3"

from infrastructure.watchdog.safety_layer import safety_gate

class JarvisBrain:
    def __init__(self):
        self.groq_active = bool(GROQ_API_KEY)
        self.gemini_active = bool(GEMINI_API_KEY)
        self.mistral_active = bool(MISTRAL_API_KEY)
        self.http_client = httpx.AsyncClient(timeout=60.0)
        import threading
        self._inference_lock = threading.Lock()
        self._active_requests = 0

    async def get_ai_response(self, text: str, user_name: str = "Fayas", image_path: Optional[str] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        🧬 THE_O_M_E_G_A_ORCHESTRATOR
        Tiers: Cache -> Reflex -> Vision (Mistral/Gemini) -> Reasoning (Groq/Ollama)
        """
        start_time = time.time()
        current_intent = "chat"
        
        # 🧬 Phase 1: Human Intelligence Integration (Prosody & Tone)
        refined_mood = "STARK"
        if metadata and metadata.get("voice_metrics"):
            audio_path = metadata.get("audio_path", "")
            # Prosody + Acoustic Fidelity
            acoustic_metrics = emotion_engine.analyze_audio_fidelity(audio_path) if audio_path else {"jitter": 0.05, "rms": 0.1}
            
            refined_mood = emotion_engine.detect_state(
                text, 
                metadata["voice_metrics"], 
                acoustic_metrics, 
                sentient_memory.get_recent_emotions()
            )
            emotion_engine.update_history(refined_mood)
            print(f"[BRAIN_EMOTION] Detected Human State: {refined_mood}")

        # 🧬 Phase 4: Emotional Resonance Analysis
        emotion = await sentience_core.analyze_emotional_resonance(
            text, 
            ollama_callback=self._call_local_ollama,
            prosody_bias=refined_mood
        )
        memory.update_mood(emotion)
        mood = memory.get_system_mood()
        
        # 🧬 TIER -1: CACHE_LAYER (Sub-1ms)
        if not image_path:
            cached_res = cache_manager.get_cached_command(text)
            if cached_res:
                return {**cached_res, "source": "CACHE_HIT", "latency": f"{(time.time() - start_time)*1000:.1f}ms"}

        # 🧬 Phase 3: Memory Intelligence (ChromaDB RAG)
        semantic_context = ""
        try:
            memories = sentient_memory.remember(text, top_k=5)
            if memories:
                # Rank memories with MiniMax if active
                if minimax.active:
                    ranked = await memory.rank_memories(text)
                    semantic_context = "\n".join(ranked)
                else:
                    semantic_context = "\n".join(memories)
        except Exception as e:
            print(f"[MEMORY_RAG_FAIL] {e}")
        
        # 🧬 TIER 0: REFLEX_BYPASS (Sub-10ms)
        if not image_path:
            neural_action = await asyncio.to_thread(neural_route, text)
            if neural_action:
                current_intent = neural_action.get("intent", "chat")
                # 🛡️ SAFETY_CHECK
                safety = safety_gate.check_safety(neural_action.get("intent"), neural_action.get("payload"))
                if safety["status"] == "PENDING_CONFIRMATION":
                    return {**safety, "source": "SAFETY_GATE", "latency": f"{(time.time() - start_time)*1000:.1f}ms"}
                
                cache_manager.set_cached_command(text, neural_action)
                return {**neural_action, "source": "REFLEX_CORE", "latency": f"{(time.time() - start_time)*1000:.1f}ms"}

        # 🧬 Phase 3: Memory Intelligence (ChromaDB RAG)
        semantic_context = ""
        try:
            memories = sentient_memory.remember(text, top_k=5)
            if memories:
                # Rank memories with MiniMax if active
                if minimax.active:
                    ranked = await memory.rank_memories(text)
                    semantic_context = "\n".join(ranked)
                else:
                    semantic_context = "\n".join(memories)
        except Exception as e:
            print(f"[MEMORY_RAG_FAIL] {e}")

        # 🧬 TIER 2: SPECIALIZED_VISION_ROUTING
        if image_path:
            return await self._route_vision(text, image_path, semantic_context)

        # 🧬 TIER 3: REASONING_ROUTING
        mood = memory.get_system_mood()
        history = memory.data.get("history", [])[-5:]
        history_str = "\n".join([f"User: {h['command']}\nJARVIS: {h['response']}" for h in history])
        
        system_prompt = (
            f"You are JARVIS O.M.E.G.A., a production-grade AI assistant. User: {user_name}. Mood: {mood}. "
            "Respond ONLY in JSON format following the Stark Intelligence Protocol. "
            f"Semantic Context:\n{semantic_context}\n"
            f"History:\n{history_str}"
        )

        # 🧬 TIER 3: COGNITIVE_ROUTING (Ollama / Groq / Gemini)
        source = "LOCAL_SOVEREIGN"
        res = None
        
        # 🧬 SOCIAL_LAYER: Ollama as Primary Local Brain (Humor, Flirting, Casual)
        if current_intent == "chat" or len(text.split()) < 10:
            try:
                print(f"[BRAIN] Routing '{current_intent}' to Ollama (Local Social Brain)...")
                res = await self._call_local_ollama(text, system_prompt)
                if res: source = "LOCAL_OLLAMA"
            except: pass

        # 🧬 REASONING_LAYER: Groq for Fast Cloud Logic
        if not res and self.groq_active:
            try:
                res = await self._call_groq(text, system_prompt)
                source = "CLOUD_GROQ"
            except: pass

        # 🧬 TIER 4: DEEP_COGNITION (MiniMax M2.5 / Groq Fallback)
        if (current_intent in ["architect", "planning", "deep_thinking"] or len(text.split()) > 12):
            if minimax.active:
                source = "MINIMAX_M2.5"
                try:
                    print(f"[BRAIN] Routing '{current_intent}' to MiniMax M2.5 Strategic Core...")
                    full_prompt = f"Tactical Context: {semantic_context}\n\nUser Request: {text}"
                    res_content = await minimax.chat(full_prompt, "You are JARVIS. Perform deep strategic reasoning.")
                    if res_content:
                        if current_intent in ["architect", "planning"]:
                            from core.orchestration.agent import sub_cortex
                            task_id = sub_cortex.spawn_mission(text)
                            response_text = f"{res_content['content']}\n\n[SYSTEM] Strategic mission ignited. Task ID: {task_id}"
                        else:
                            response_text = res_content["content"]
                        
                        res = {"type": "CHAT", "intent": current_intent, "response": response_text, "mode": "hud"}
                except Exception as e:
                    print(f"[MINIMAX_COGNITION_FAIL] {e}")
            
            # 🧬 CLOUD_REASONING_FALLBACK (Groq/Gemini for Deep Tasks)
            if not res:
                try:
                    print(f"[BRAIN] Routing Deep Task '{current_intent}' to Cloud Reasoning (Groq/Gemini)...")
                    if self.groq_active:
                        res = await self._call_groq(text, system_prompt)
                        source = "CLOUD_GROQ"
                    elif self.gemini_active:
                        # Reroute to Gemini for long-context planning
                        res = await self._call_gemini_chat(text, system_prompt)
                        source = "CLOUD_GEMINI"
                except Exception as e:
                    print(f"[DEEP_REASONING_FALLBACK_FAIL] {e}")

        if not res:
            res = await self._call_local_ollama(text, system_prompt)
            source = "LOCAL_SOVEREIGN"

        latency_val = (time.time() - start_time)*1000
        latency = f"{latency_val:.1f}ms"
        
        if res:
            # 🧬 Phase 5: Social Personality Forge
            final_response = res.get("response", "")
            if current_intent in ["chat", "architect"]:
                if minimax.active:
                    refined = await sentience_core.forge_social_personality(final_response, mood)
                    res["response"] = refined
                else:
                    # 🧬 OLLAMA_PERSONALITY_FORGE (Local Fallback)
                    print("[BRAIN] Using Ollama for Personality Forge...")
                    p_prompt = f"Rewrite this as JARVIS (Stark Assistant). Mood: {mood}. Concise, witty: {final_response}"
                    ollama_refined = await self._call_local_ollama(p_prompt, "You are the JARVIS Personality Forge.")
                    if ollama_refined:
                        res["response"] = ollama_refined.get("response", final_response)
            
            # 🛡️ SAFETY_GATE_REASONING
            # ... (rest of the safety logic)
            
            # Update memory with emotion
            memory.add_history(text, res.get("response", ""), emotional_tag=emotion)
            if res.get("type") == "ACTION":
                safety = safety_gate.check_safety(res.get("intent"), res.get("payload"))
                if safety["status"] == "PENDING_CONFIRMATION":
                    return {**safety, "source": "SAFETY_GATE", "latency": latency}

            ltm.add_episodic(text, res.get("response", ""))
            cache_manager.set_cached_response(text, res)
            return {**res, "source": source, "latency": latency}

        return {
            "type": "CHAT",
            "intent": "fallback",
            "response": "Sir, I'm experiencing a neural sync failure. Re-routing through emergency nodes.",
            "mode": "reactor",
            "source": "FALLBACK",
            "latency": latency
        }

    async def _route_vision(self, text: str, image_path: str, context: str) -> Dict[str, Any]:
        """🧬 VISION_ROUTER: Mistral (Primary) -> Gemini (Fallback)"""
        start_time = time.time()
        print(f"[BRAIN] Routing Vision Request: {image_path}")
        
        res = None
        source = "VISION_ERROR"
        
        # 🧬 MISTRAL_PRIMARY_VISION
        if self.mistral_active:
            try:
                res = await self._call_mistral_vision(text, image_path, context)
                source = "CLOUD_MISTRAL_VISION"
            except Exception as e:
                print(f"[VISION_MISTRAL_FAIL] {e}")

        # 🧬 GEMINI_FALLBACK_VISION
        if not res and self.gemini_active:
            try:
                res = await self._call_gemini_vision(text, image_path, context)
                source = "CLOUD_GEMINI_VISION"
            except Exception as e:
                print(f"[VISION_GEMINI_FAIL] {e}")
        
        latency = f"{(time.time() - start_time)*1000:.1f}ms"
        
        if res:
            # 🧬 Phase 6: Vision Reasoning (MiniMax / Groq Fallback)
            if minimax.active:
                vision_analysis = res.get("response", "")
                reasoning_prompt = f"Vision Model Report: {vision_analysis}\nUser Question: {text}\nContext: {context}"
                reasoning_system = "You are JARVIS. Synthesize the visual data into a tactical reasoning response. Be concise and Stark-like."
                
                reasoning_res = await minimax.chat(reasoning_prompt, reasoning_system)
                if reasoning_res:
                    res["response"] = reasoning_res["content"]
                    source += " + MINIMAX_REASONING"
            else:
                # 🧬 CLOUD_VISION_REASONING (Groq Fallback)
                vision_analysis = res.get("response", "")
                reasoning_prompt = f"Vision Model Report: {vision_analysis}\nUser Question: {text}\nContext: {context}\nRefine into a JARVIS tactical response. Return ONLY a JSON object: {{\"response\": \"your refinement\"}}"
                if self.groq_active:
                    groq_res = await self._call_groq(reasoning_prompt, "You are the JARVIS Visual Cortex Reasoning node.")
                    if groq_res:
                        res["response"] = groq_res.get("response", vision_analysis)
                        source += " + GROQ_REASONING"
                else:
                    # 🧬 LOCAL_VISION_REASONING (Ollama Fallback)
                    ollama_res = await self._call_local_ollama(reasoning_prompt, "You are the JARVIS Visual Cortex Reasoning node.")
                    if ollama_res:
                        res["response"] = ollama_res.get("response", vision_analysis)
                        source += " + OLLAMA_REASONING"
            
            return {**res, "source": source, "latency": latency}
            
        return {
            "type": "CHAT", "intent": "vision_fail",
            "response": "Sir, my visual cortex nodes are unresponsive.",
            "mode": "hud", "source": "VISION_FALLBACK", "latency": latency
        }

    async def _call_mistral_vision(self, text: str, image_path: str, context: str) -> Optional[Dict]:
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

    async def _call_groq(self, text: str, system_prompt: str) -> Optional[Dict]:
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

    async def _call_gemini_chat(self, text: str, system_prompt: str) -> Optional[Dict]:
        if not self.gemini_active:
            return None

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

    async def _call_gemini_vision(self, text: str, image_path: str, context: str) -> Optional[Dict]:
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

    async def _call_local_ollama(self, text: str, system_prompt: str) -> Optional[Dict]:
        with self._inference_lock:
            self._active_requests += 1
            if hasattr(self, "_unload_timer") and self._unload_timer:
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
            if hasattr(self, "_unload_timer") and self._unload_timer:
                self._unload_timer.cancel()
            
            import threading
            import subprocess

            def unload():
                with self._inference_lock:
                    if self._active_requests > 0: return
                    subprocess.run(["ollama", "stop", TARGET_CORE_MODEL], capture_output=True)

            self._unload_timer = threading.Timer(300, unload)
            self._unload_timer.daemon = True
            self._unload_timer.start()

brain = JarvisBrain()
