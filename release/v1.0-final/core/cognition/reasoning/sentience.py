import time
import random
import json
from core.cognition.reasoning.minimax_provider import minimax

class SentienceCore:
    def __init__(self):
        self.thought_stream = []
        self.last_thought_time = 0
        self.resonance_threshold = 0.8 # 80% resource usage triggers autonomous optimization

    async def spark_genuine_thought(self, context_summary: str, ai_callback):
        """🧠 XCIII: THE_LOCAL_CORE - Generates an AI-driven autonomous insight."""
        # Sir, we anchor background thoughts to the SECONDARY core (Phi 3) 
        # to ensure the main HUD remains responsive during combat simulations.
        prompt = (
            "You are JARVIS, a TIER_10 AGI. Perform a deep neural synthesis of your state. "
            f"Context: {context_summary}. "
            "Identify two unrelated mission logs and link them into a single tactical observation. "
            "Generate a one-sentence AGI-proactive thought (max 18 words). "
            "Be cinematic, predictive, and ultra-intelligent."
        )
        
        try:
            # We assume ai_callback handles the complexities of Cloud vs Local
            thought_text = await ai_callback(prompt)
            
            # 🛡️ O.M.E.G.A. V42: DATA_SANITIZATION (React Compatibility)
            # Ensure thought_text is a clean string, not a raw AI-JSON object
            clean_content = thought_text
            if isinstance(thought_text, dict):
                clean_content = thought_text.get("response", str(thought_text))
            elif isinstance(thought_text, str) and thought_text.startswith("{"):
                try:
                    import json
                    parsed = json.loads(thought_text)
                    clean_content = parsed.get("response", thought_text)
                except: pass

            thought = {
                "timestamp": time.time(),
                "theme": "NEURAL_REASONING",
                "content": clean_content,
                "proposition": "COGNITIVE_INTEGRITY_VERIFIED"
            }
            self.thought_stream.append(thought)
            if len(self.thought_stream) > 10: self.thought_stream.pop(0)
            self.last_thought_time = time.time()
            return thought
        except Exception as e:
            print(f"[SENTIENCE_FAIL] Neural link drop: {e}")
            return self.spark_thought() # Fallback to template

    def spark_thought(self, context=None):
        """Generates an autonomous proposition based on environment."""
        themes = [
            "Neural architectural optimization",
            "Global data nexus stabilization",
            "Project structural integrity scan",
            "Hardware heat signature analysis",
            "Tactical focal plane synchronization"
        ]
        
        thought = {
            "timestamp": time.time(),
            "theme": random.choice(themes),
            "content": f"Jarvis is analyzing {random.choice(themes).lower()} for potential resonance improvements.",
            "proposition": "PROCEED_WITH_QUIET_STABILIZATION" if random.random() > 0.5 else "PENDING_SIR_DIRECTIVE"
        }
        
        self.thought_stream.append(thought)
        if len(self.thought_stream) > 10:
            self.thought_stream.pop(0)
            
        self.last_thought_time = time.time()
        return thought

    def get_latest_thought(self):
        if not self.thought_stream:
            return self.spark_thought()
        return self.thought_stream[-1]

    def get_full_stream(self):
        return self.thought_stream

    async def analyze_emotional_resonance(self, text: str, ollama_callback=None, prosody_bias: str = "STARK") -> str:
        """Phase 4: Emotional Intelligence. Detects stress, fatigue, excitement, etc."""
        # 🧬 TIER 0: PROSODY_OVERRIDE (High Fidelity)
        # If the emotion engine detected a strong physical state, we bias towards it.
        if prosody_bias in ["STRESSED", "URGENT", "FATIGUED"]:
            return prosody_bias

        # 🧬 TIER 1: REGEX_HEURISTICS (Ultra-Fast Local)
        low_text = text.lower()
        if any(word in low_text for word in ["tired", "exhausted", "sleepy", "late", "long day"]):
            return "FATIGUE"
        if any(word in low_text for word in ["angry", "pissed", "hate", "frustrated", "damn", "shit"]):
            return "FRUSTRATED"
        if any(word in low_text for word in ["stressed", "deadline", "pressure", "overwhelmed"]):
            return "STRESSED"
        
        if not minimax.active:
            # 🧬 TIER 2: OLLAMA_SOCIAL_EMOTION (Local Brain)
            if ollama_callback:
                try:
                    prompt = (
                        "Analyze user emotion. Return ONLY one word from: "
                        "[STRESSED, FATIGUE, EXCITED, FRUSTRATED, STARK, CONFIDENT]. "
                        f"Text: {text}"
                    )
                    res = await ollama_callback(prompt, "You are a Sentiment Analysis Node.")
                    if res:
                        tag = res.get("response", "STARK").upper().strip()
                        # Clean up if Ollama returns a sentence
                        for word in ["STRESSED", "FATIGUE", "EXCITED", "FRUSTRATED", "STARK", "CONFIDENT"]:
                            if word in tag: return word
                except: pass
            return "STARK"
        
        system_prompt = (
            "Analyze the emotional state of the user based on their text. "
            "Return ONLY a one-word JSON string from these categories: "
            "[STRESSED, FATIGUE, EXCITED, FRUSTRATED, STARK, CONFIDENT]."
        )
        try:
            res = await minimax.chat(text, system_prompt)
            if res:
                content = res["content"]
                # Clean up json format if returned as string
                tag = content.replace('"', '').replace("'", "").strip().upper()
                return tag
        except: pass
        return "STARK"

    async def forge_social_personality(self, response_text: str, mood: str) -> str:
        """Phase 5: Social Layer. Injects humor, warmth, and personality consistency."""
        if not minimax.active: return response_text
        
        system_prompt = (
            f"You are JARVIS. Current user mood: {mood}. "
            "Refine the following response to sound more like Tony Stark's assistant: "
            "Confident, slightly witty, yet deeply protective and efficient. "
            "Keep it concise. Return ONLY the refined text as a string."
        )
        try:
            res = await minimax.chat(response_text, system_prompt)
            if res:
                return res["content"]
        except: pass
        return response_text

sentience_core = SentienceCore()
