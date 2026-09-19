"""
JARVIS MIXTURE OF EXPERTS (MOE) ROUTER — FULL 20-EXPERT EDITION
================================================================
Dynamically snaps the correct specialized LoRA adapter over the
Qwen2.5-Coder base model based on the user's intent.
Supports ALL 19 expert adapters + game dev + personality adapter.
"""
import os
import re

class CognitiveMoERouter:
    def __init__(self):
        self.base_model_id  = "unsloth/Qwen2.5-Coder-1.5B-Instruct-bnb-4bit"  # current base
        self.base_7b_id     = "unsloth/Qwen2.5-Coder-7B-Instruct-bnb-4bit"    # future 7B base
        self.experts_dir    = r"c:\jarvis AI\jarvis\training_lab\expert_models_v2"
        self.personality_path = r"c:\jarvis AI\jarvis\training_lab\custom_jarvis_model_v2"
        self.game_dev_path  = r"c:\jarvis AI\jarvis\training_lab\jarvis_game_dev_v2"
        self.foundation_path = r"c:\jarvis AI\jarvis\training_lab\jarvis_1million_FULL_model"

        # ─── FULL 20-EXPERT MAP ───────────────────────────────────────────────
        # Format: "adapter_folder_name": [keywords that trigger this expert]
        self.expert_map = {

            # ── CYBERSECURITY ─────────────────────────────────────────────────
            "root_access_&_cysec": [
                "hack", "exploit", "root", "penetration", "pen test", "cve",
                "privilege escalation", "shell", "reverse shell", "payload"
            ],
            "cybersecurity_threats": [
                "malware", "virus", "ransomware", "phishing", "threat", "attack",
                "zero day", "ddos", "trojan", "keylogger", "spyware"
            ],
            "advanced_defensive_cyber": [
                "firewall", "ids", "ips", "siem", "blue team", "defend",
                "harden", "patch", "vulnerability", "security audit", "forensics"
            ],
            "omniscient_cysec": [
                "cybersecurity", "infosec", "red team", "ctf", "wireshark",
                "nmap", "metasploit", "burp suite", "osint", "recon"
            ],

            # ── CODING & ARCHITECTURE ─────────────────────────────────────────
            "hyper_coding": [
                "code", "program", "script", "function", "bug", "debug",
                "algorithm", "data structure", "optimize", "refactor", "api"
            ],
            "master_architect_coding": [
                "architecture", "design pattern", "microservice", "system design",
                "c++", "rust", "golang", "backend", "frontend", "fullstack"
            ],
            "polyglot_architecture": [
                "java", "kotlin", "swift", "typescript", "react", "angular",
                "vue", "django", "flask", "fastapi", "spring", "nodejs"
            ],

            # ── GAME DEVELOPMENT ─────────────────────────────────────────────
            "game_dev": [  # mapped to game_dev_path below
                "game", "unity", "unreal", "blender", "shader", "sprite",
                "physics engine", "collision", "game loop", "fps", "rpg",
                "level design", "3d model", "texture", "animation", "render"
            ],

            # ── AI / VISION / PERCEPTION ──────────────────────────────────────
            "object_detection": [
                "detect", "find object", "locate", "identify", "vision",
                "camera", "image", "yolo", "bounding box", "segmentation"
            ],
            "llama_eyes_&_ears": [
                "see", "look at", "screenshot", "screen", "what is on",
                "read screen", "ocr", "optical", "read text", "describe image"
            ],

            # ── VOICE & AUDIO ─────────────────────────────────────────────────
            "whisper_recognition": [
                "transcribe", "speech to text", "stt", "listen", "audio",
                "microphone", "voice input", "record", "whisper"
            ],
            "voice_biometrics": [
                "voice print", "identify speaker", "who is speaking",
                "voice auth", "speaker recognition", "voice id"
            ],
            "voice_to_voice": [
                "speak", "say", "talk to me", "voice response", "tts",
                "text to speech", "narrate", "read aloud"
            ],

            # ── KNOWLEDGE ─────────────────────────────────────────────────────
            "medical_knowledge": [
                "doctor", "symptom", "medicine", "diagnosis", "health",
                "disease", "treatment", "drug", "hospital", "patient",
                "prescription", "anatomy", "surgery", "therapy"
            ],
            "corporate_safety": [
                "compliance", "gdpr", "policy", "legal", "ethics",
                "safety protocol", "workplace", "hr", "regulation", "audit"
            ],

            # ── HARDWARE & IOT ────────────────────────────────────────────────
            "smart_home_iot": [
                "lights", "thermostat", "door", "iot", "home automation",
                "smart plug", "sensor", "alexa", "google home", "mqtt"
            ],
            "robotic_hardware_api": [
                "robot", "servo", "motor", "arduino", "raspberry pi",
                "gpio", "actuator", "drone", "mechanical", "hardware"
            ],

            # ── MEMORY & REASONING ────────────────────────────────────────────
            "chromadb_rag_memory": [
                "remember", "recall", "memory", "what did i say", "history",
                "context", "previous", "earlier", "last time", "stored"
            ],
            "tool_former_logic": [
                "use tool", "call api", "search web", "browse", "fetch",
                "execute", "run command", "function call", "action", "task"
            ],

            # ── AUTONOMY ──────────────────────────────────────────────────────
            "autonomous_proactive": [
                "do it yourself", "auto", "automatically", "on your own",
                "without asking", "proactive", "background", "scheduled",
                "monitor", "watch", "alert me when"
            ],
        }

        # ─── SPECIAL ADAPTER PATHS (not in expert_models folder) ─────────────
        self.special_paths = {
            "game_dev": self.game_dev_path,
        }

        print("[MOE ROUTER] [OK] Full 20-Expert Mixture of Experts routing engine initialized.")
        print(f"[MOE ROUTER] [*] Experts loaded: {len(self.expert_map)} domains mapped.")

    def route_request(self, user_input: str) -> dict:
        """
        Determines which specialized expert LoRA to snap onto the base model.
        Returns a dict with adapter_path and matched expert name.
        """
        user_input_lower = user_input.lower()
        scores = {}

        # Score each expert by counting keyword matches
        for expert_id, keywords in self.expert_map.items():
            score = 0
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', user_input_lower):
                    score += 1
            if score > 0:
                scores[expert_id] = score

        if scores:
            # Pick the expert with the highest keyword match score
            best_expert = max(scores, key=scores.get)

            # Resolve the adapter path
            if best_expert in self.special_paths:
                adapter_path = self.special_paths[best_expert]
            else:
                adapter_path = os.path.join(self.experts_dir, best_expert)

            print(f"[MOE ROUTER] [>>] Intent match (score={scores[best_expert]}). "
                  f"Routing to -> {best_expert}")
            return {
                "expert": best_expert,
                "adapter_path": adapter_path,
                "score": scores[best_expert],
                "base_model": self.base_model_id
            }

        # No match — fall back to foundation model
        print("[MOE ROUTER] [--] General intent detected. Using base foundation model.")
        return {
            "expert": "foundation",
            "adapter_path": self.foundation_path,
            "score": 0,
            "base_model": self.base_model_id
        }

    def list_all_experts(self):
        """Print a clean table of all available experts."""
        print("\n" + "="*60)
        print("         JARVIS EXPERT ROSTER -- FULL 20 EXPERTS")
        print("="*60)
        for i, (expert_id, keywords) in enumerate(self.expert_map.items(), 1):
            kw_preview = ", ".join(keywords[:3]) + "..."
            print(f"  {i:02d}. {expert_id:<36} [{kw_preview}]")
        print("="*60 + "\n")


if __name__ == "__main__":
    router = CognitiveMoERouter()
    router.list_all_experts()

    print("\n--- Testing MoE Router ---")
    test_queries = [
        "How do I exploit a buffer overflow in C?",
        "What are the symptoms of a migraine?",
        "Turn off the living room lights.",
        "Write a Python script for machine learning.",
        "Build me a Unity game with physics.",
        "Transcribe this audio file please.",
        "Remember what I said last time about the project?",
        "Monitor my CPU and alert me when it exceeds 90%.",
        "What is the capital of France?",
    ]

    for q in test_queries:
        print(f"\nUser: {q}")
        result = router.route_request(q)
        print(f"  → Expert: {result['expert']}  (score={result['score']})")
        print(f"  → Adapter: {result['adapter_path']}")
