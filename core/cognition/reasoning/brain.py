import os
import asyncio
import time
from typing import Optional, Dict, Any

# Local Imports
from core.cognition.reasoning.neural_core import neural_route
from core.cognition.memory.long_term_memory import ltm
from core.cognition.memory.cache_manager import cache_manager
from core.cognition.memory.memory import memory
from core.cognition.memory.sentient_memory import sentient_memory
from core.cognition.reasoning.minimax_provider import minimax
from core.cognition.reasoning.sentience import sentience_core
from core.cognition.reasoning.emotion_engine import emotion_engine
from core.cognition.reasoning.local_llm import local_llm_provider
from core.cognition.reasoning.cloud_llm import cloud_llm_provider
from infrastructure.watchdog.safety_layer import safety_gate

class JarvisBrain:
    async def get_ai_response(self, text: str, user_name: str = "Fayas", image_path: Optional[str] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        🧬 THE_O_M_E_G_A_ORCHESTRATOR
        """
        start_time = time.time()
        current_intent = "chat"
        
        # 🧬 Phase 1: Human Intelligence Integration
        refined_mood = "STARK"
        if metadata and metadata.get("voice_metrics"):
            audio_path = metadata.get("audio_path", "")
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
            ollama_callback=local_llm_provider.call_local_ollama,
            prosody_bias=refined_mood
        )
        memory.update_mood(emotion)
        mood = memory.get_system_mood()
        
        # 🧬 TIER -1: CACHE_LAYER
        if not image_path:
            cached_res = cache_manager.get_cached_command(text)
            if cached_res:
                return {**cached_res, "source": "CACHE_HIT", "latency": f"{(time.time() - start_time)*1000:.1f}ms"}

        # 🧬 TIER 0: REFLEX_BYPASS
        if not image_path:
            neural_action = await asyncio.to_thread(neural_route, text)
            if neural_action:
                current_intent = neural_action.get("intent", "chat")
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
        history = memory.data.get("history", [])[-5:]
        history_str = "\n".join([f"User: {h['command']}\nJARVIS: {h['response']}" for h in history])
        
        system_prompt = (
            f"You are JARVIS O.M.E.G.A., a production-grade AI assistant. User: {user_name}. Mood: {mood}. "
            "Respond ONLY in JSON format following the Stark Intelligence Protocol. "
            f"Semantic Context:\n{semantic_context}\n"
            f"History:\n{history_str}"
        )

        source = "LOCAL_SOVEREIGN"
        res = None
        
        # 🧬 SOCIAL_LAYER: Ollama
        if current_intent == "chat" or len(text.split()) < 10:
            try:
                res = await local_llm_provider.call_local_ollama(text, system_prompt)
                if res: source = "LOCAL_OLLAMA"
            except: pass

        # 🧬 REASONING_LAYER: Groq
        if not res and cloud_llm_provider.groq_active:
            try:
                res = await cloud_llm_provider.call_groq(text, system_prompt)
                source = "CLOUD_GROQ"
            except: pass

        # 🧬 TIER 4: DEEP_COGNITION
        if (current_intent in ["architect", "planning", "deep_thinking"] or len(text.split()) > 12):
            if minimax.active:
                source = "MINIMAX_M2.5"
                try:
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
            
            # 🧬 CLOUD_REASONING_FALLBACK
            if not res:
                try:
                    if cloud_llm_provider.groq_active:
                        res = await cloud_llm_provider.call_groq(text, system_prompt)
                        source = "CLOUD_GROQ"
                    elif cloud_llm_provider.gemini_active:
                        res = await cloud_llm_provider.call_gemini_chat(text, system_prompt)
                        source = "CLOUD_GEMINI"
                except Exception as e:
                    print(f"[DEEP_REASONING_FALLBACK_FAIL] {e}")

        if not res:
            res = await local_llm_provider.call_local_ollama(text, system_prompt)
            source = "LOCAL_SOVEREIGN"

        latency = f"{(time.time() - start_time)*1000:.1f}ms"
        
        if res:
            # 🧬 Phase 5: Social Personality Forge
            final_response = res.get("response", "")
            if current_intent in ["chat", "architect"]:
                if minimax.active:
                    refined = await sentience_core.forge_social_personality(final_response, mood)
                    res["response"] = refined
                else:
                    p_prompt = f"Rewrite this as JARVIS (Stark Assistant). Mood: {mood}. Concise, witty: {final_response}"
                    ollama_refined = await local_llm_provider.call_local_ollama(p_prompt, "You are the JARVIS Personality Forge.")
                    if ollama_refined:
                        res["response"] = ollama_refined.get("response", final_response)
            
            memory.add_history(text, res.get("response", ""), emotional_tag=emotion)
            if res.get("type") == "ACTION":
                safety = safety_gate.check_safety(res.get("intent"), res.get("payload"))
                if safety["status"] == "PENDING_CONFIRMATION":
                    return {**safety, "source": "SAFETY_GATE", "latency": latency}

            ltm.add_episodic(text, res.get("response", ""))
            cache_manager.set_cached_response(text, res)
            return {**res, "source": source, "latency": latency}

        return {
            "type": "CHAT", "intent": "fallback",
            "response": "Sir, I'm experiencing a neural sync failure. Re-routing through emergency nodes.",
            "mode": "reactor", "source": "FALLBACK", "latency": latency
        }

    async def _route_vision(self, text: str, image_path: str, context: str) -> Dict[str, Any]:
        """🧬 VISION_ROUTER"""
        start_time = time.time()
        res = None
        source = "VISION_ERROR"
        
        if cloud_llm_provider.mistral_active:
            res = await cloud_llm_provider.call_mistral_vision(text, image_path, context)
            if res: source = "CLOUD_MISTRAL_VISION"

        if not res and cloud_llm_provider.gemini_active:
            res = await cloud_llm_provider.call_gemini_vision(text, image_path, context)
            if res: source = "CLOUD_GEMINI_VISION"
        
        latency = f"{(time.time() - start_time)*1000:.1f}ms"
        
        if res:
            # 🧬 Phase 6: Vision Reasoning
            if minimax.active:
                vision_analysis = res.get("response", "")
                reasoning_prompt = f"Vision Model Report: {vision_analysis}\nUser Question: {text}\nContext: {context}"
                reasoning_res = await minimax.chat(reasoning_prompt, "You are JARVIS. Synthesize the visual data into a tactical reasoning response. Be concise and Stark-like.")
                if reasoning_res:
                    res["response"] = reasoning_res["content"]
                    source += " + MINIMAX_REASONING"
            else:
                vision_analysis = res.get("response", "")
                reasoning_prompt = f"Vision Model Report: {vision_analysis}\nUser Question: {text}\nContext: {context}\nRefine into a JARVIS tactical response. Return ONLY a JSON object: {{\"response\": \"your refinement\"}}"
                if cloud_llm_provider.groq_active:
                    groq_res = await cloud_llm_provider.call_groq(reasoning_prompt, "You are the JARVIS Visual Cortex Reasoning node.")
                    if groq_res:
                        res["response"] = groq_res.get("response", vision_analysis)
                        source += " + GROQ_REASONING"
                else:
                    ollama_res = await local_llm_provider.call_local_ollama(reasoning_prompt, "You are the JARVIS Visual Cortex Reasoning node.")
                    if ollama_res:
                        res["response"] = ollama_res.get("response", vision_analysis)
                        source += " + OLLAMA_REASONING"
            
            return {**res, "source": source, "latency": latency}
            
        return {
            "type": "CHAT", "intent": "vision_fail",
            "response": "Sir, my visual cortex nodes are unresponsive.",
            "mode": "hud", "source": "VISION_FALLBACK", "latency": latency
        }

brain = JarvisBrain()
