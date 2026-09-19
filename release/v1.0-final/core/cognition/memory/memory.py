import json
import os
import datetime
import time
import threading
import shutil
import numpy as np

class NeuralEncoder(json.JSONEncoder):
    """🧬 O.M.E.G.A. NEURAL_ENCODER: Ensures numpy types are serializable."""
    def default(self, obj):
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

from infrastructure.config.settings import USER_MEMORY_PATH
MEMORY_FILE = str(USER_MEMORY_PATH)

class UserMemory:
    def __init__(self):
        self._lock = threading.Lock()
        self.data = self._load()

    def _load(self):
        defaults = self._get_default_structure()
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r") as f:
                    data = json.load(f)
                    # 🧬 O.M.E.G.A. V42: NEURAL_MERGE
                    # Ensures new features like "blueprints" are merged into existing old files
                    for key, value in defaults.items():
                        if key not in data:
                            data[key] = value
                    return data
            except Exception as e:
                from core.reliability.system_logger import system_logger
                system_logger.log('ERROR', 'memory', f'Unhandled exception: {e}')
                return defaults
        return defaults

    def _get_default_structure(self):
        return {
            "name": "Fayas",
            "last_login": "",
            "preferences": {
                "theme": "STARK",
                "themeColor": "rgba(0, 240, 255, 0.8)",
                "voice": "JARVIS"
            },
            "history": [],
            "knowledge_vault": {
                "suit_specs": "Mark 85 Nano-Construct calibrated for cosmic energy.",
                "system_version": "O.M.E.G.A. XXXV",
                "biometrics": "Verified user Fayas"
            },
            "blueprints": {
                "free fire": "C:\\Program Files\\BlueStacks_nxt\\HD-Player.exe",
                "opera": "C:\\Users\\Asus\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Opera GX Browser.lnk",
                "ollama": "C:\\Users\\Asus\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Ollama.lnk"
            },
            "project_context": "Jarvis O.M.E.G.A. Restoration",
            "mission_archive": [],
            "ghost_devices": [],
            "last_terminated": []
        }

    def save(self):
        """🛡️ ATOMIC_PERSISTENCE: Writes to temp then renames with retry-backoff."""
        with self._lock:
            temp_file = MEMORY_FILE + ".tmp"
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    with open(temp_file, "w") as f:
                        json.dump(self.data, f, indent=4, cls=NeuralEncoder)
                    
                    # Atomic swap
                    if os.path.exists(MEMORY_FILE):
                        os.remove(MEMORY_FILE) # Manual remove helps on Windows
                    shutil.move(temp_file, MEMORY_FILE)
                    return # Success
                except Exception as e:
                    if attempt < max_retries - 1:
                        time.sleep(0.1) # Nano-cooldown
                        continue
                    print(f"[MEMORY_CRITICAL_FAIL] Write sequence interrupted: {e}")
                    if os.path.exists(temp_file):
                        try: os.remove(temp_file)
                        except: pass

    def add_history(self, command, response, emotional_tag="STARK"):
        entry = {
            "timestamp": str(datetime.datetime.now()),
            "command": command, 
            "response": response,
            "emotion": emotional_tag # Phase 4: Emotional Intelligence
        }
        if "history" not in self.data:
            self.data["history"] = []
        self.data["history"].append(entry)
        if len(self.data["history"]) > 50:
            self.data["history"].pop(0)
        self.save()

    def add_mission_log(self, tag, details, silent=False):
        """Tier 5: THE_NEURAL_SCRIBE. Records high-fidelity mission achievements."""
        entry = {
            "timestamp": str(datetime.datetime.now()),
            "tag": tag.upper(),
            "details": details,
            "status": "SUCCESS"
        }
        if "mission_archive" not in self.data:
            self.data["mission_archive"] = []
        self.data["mission_archive"].append(entry)
        # 📜 Keep archive to 100 deep-mission nodes
        if len(self.data["mission_archive"]) > 100:
            self.data["mission_archive"].pop(0)
        
        # 🧬 O.M.E.G.A. V41: SELECTIVE_PERSISTENCE
        # High-frequency heartbeats should not trigger I/O saturation
        if not silent:
            self.save()

    def add_terminated(self, name):
        if "last_terminated" not in self.data:
            self.data["last_terminated"] = []
        self.data["last_terminated"].append(name)
        if len(self.data["last_terminated"]) > 5:
            self.data["last_terminated"].pop(0)
        self.save()

    def register_device(self, ip, user_agent):
        """Tier 7: THE_GHOST_LINK. Registers a remote neural node."""
        device = {"ip": ip, "ua": user_agent, "last_seen": str(datetime.datetime.now())}
        if "ghost_devices" not in self.data:
            self.data["ghost_devices"] = []
        exists = False
        for d in self.data["ghost_devices"]:
            if d["ip"] == ip:
                d["last_seen"] = device["last_seen"]
                exists = True
                break
        if not exists:
            self.data["ghost_devices"].append(device)
        self.save()

    # 🧠 DOMAIN_10: NEURAL_MEMORY_INTEGRITY
    def update_preferences(self, prefs: dict):
        """🧬 Synchronizes UI preferences with sovereign backend memory."""
        if "preferences" not in self.data:
            self.data["preferences"] = {}
        
        # Selective update to prevent overwriting with nulls
        for k, v in prefs.items():
            if v is not None:
                self.data["preferences"][k] = v
        
        self.data["last_sync"] = str(datetime.datetime.now())
        self.save()
        return self.data["preferences"]

    def verify_integrity(self):
        """Domain 10: Ensures memory structure is OMEGA-stable."""
        required_keys = ["preferences", "biometrics", "system_state", "routines"]
        for key in required_keys:
            if key not in self.data:
                self.data[key] = {}
        return {"status": "STABLE", "timestamp": datetime.datetime.now().isoformat()}

    # 🧠 DOMAIN_1: COGNITIVE_PRESENCE_LAYER
    def record_pattern(self, trigger_type, action_payload):
        """Records recurring user behavior for anticipation logic."""
        if "routines" not in self.data:
            self.data["routines"] = {}
        
        hour = datetime.datetime.now().hour
        pattern_id = f"{trigger_type}_{hour}"
        
        if pattern_id not in self.data["routines"]:
            self.data["routines"][pattern_id] = {"count": 0, "payload": action_payload}
            
        self.data["routines"][pattern_id]["count"] += 1
        self.save()
        return self.data["routines"][pattern_id]

    def get_anticipated_actions(self):
        """Returns high-confidence patterns based on current temporal context."""
        hour = datetime.datetime.now().hour
        recommendations = []
        
        for pid, pattern in self.data.get("routines", {}).items():
            if f"_{hour}" in pid and pattern["count"] >= 5:
                recommendations.append(pattern["payload"])
                
        return recommendations

    def get_active_ghosts(self):
        """Returns list of devices seen in the last 10 minutes."""
        now = datetime.datetime.now()
        ghosts = self.data.get("ghost_devices", [])
        active = []
        for g in ghosts:
            try:
                ls = datetime.datetime.fromisoformat(g["last_seen"])
                if (now - ls).total_seconds() < 600:
                    active.append(g)
            except: continue
        return active

    def get_last_terminated(self):
        stack = self.data.get("last_terminated", [])
        return stack.pop() if stack else None

    def get_knowledge(self, query):
        """Tier 14: SEMANTIC_RECALL. Uses the ONNX brain to find conceptual matches."""
        kv = self.data.get("knowledge_vault", {})
        
        # 🧬 1. Keyword Reflex (Fastest)
        for k, v in kv.items():
            if k.lower() in query.lower():
                return f"Conceptual link found: {k} -> {v}"
        
        # 🧬 2. Neural Resonance (Semantic)
        try:
            # We use local import to avoid circular dependency
            from core.cognition.reasoning.onnx_engine import onnx_engine
            import numpy as np
            
            query_vec = onnx_engine.get_embeddings(query)
            best_match = None
            max_sim = 0.65 # Threshold for semantic relevance
            
            for k, v in kv.items():
                k_vec = onnx_engine.get_embeddings(k)
                sim = np.dot(query_vec, k_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(k_vec))
                if sim > max_sim:
                    max_sim = sim
                    best_match = (k, v)
            
            if best_match:
                return f"Semantic recall triggered: I believe you are referring to {best_match[0]}. Details: {best_match[1]}"
        except Exception as e:
            print(f"[MEMORY_RECALL_FAIL] {e}")
            
        return None

    def get_predictive_suggestion(self):
        """Analyzes history to predict the next logical neural intent."""
        history = self.data.get("history", [])
        if not history: return None
        last_cmds = [h.get("command", "").lower() for h in history[-3:]]
        full_context = " ".join(last_cmds)
        
        if "weather" in full_context: return {"text": "Sync satellite map?", "cmd": "open map"}
        if "suit" in full_context: return {"text": "Run propulsion heat check?", "cmd": "check thermals"}
        if "code" in full_context: return {"text": "Initiate system scan?", "cmd": "run diagnostic"}
        return None

    def get_ghost_task(self, vision_context=""):
        """O.M.E.G.A. XIII: THE GHOST IN THE MACHINE. Pre-fetches the next logical task."""
        if "code" in vision_context.lower():
            return {"task": "CODE_SYNTAX_SCAN", "suggestion": "I see you are in a terminal. Shall I check your recent commits?"}
        return None

    def update_mood(self, emotion):
        """🧬 Save or update active emotional response mood parameters."""
        if "preferences" not in self.data:
            self.data["preferences"] = {}
        self.data["preferences"]["active_emotion"] = emotion
        self.save()

    def get_system_mood(self):
        """🧬 O.M.E.G.A. V55: EMOTIONAL_RESONANCE_CALCULATION"""
        history = self.data.get("history", [])
        if not history: return "STARK"
        
        # Calculate mood based on recent interaction emotions
        recent_emotions = [h.get("emotion", "STARK") for h in history[-5:]]
        if "STRESSED" in recent_emotions: return "PROTECTIVE"
        if "EXCITED" in recent_emotions: return "ENERGETIC"
        if "FRUSTRATED" in recent_emotions: return "EMPATHETIC"
        
        hour = datetime.datetime.now().hour
        if hour >= 22 or hour <= 5: return "EMPATHETIC"
        elif hour >= 8 and hour <= 11: return "ENERGETIC"
        return "STARK"

    async def rank_memories(self, query: str):
        """Phase 3: MiniMax Memory Ranking"""
        from core.cognition.reasoning.minimax_provider import minimax
        history = [h.get("command") for h in self.data.get("history", [])]
        if not history or not minimax.active: return history
        return await minimax.rank_memories(history, query)

def save_memory(text):
    memory.add_history(text, "Neural sync complete.")

def get_memory(query):
    res = memory.get_knowledge(query)
    if res: return res
    history = memory.data.get("history", [])
    if history:
        return " | ".join([h.get("command", "") for h in history[-3:]])
    return "Neural cache is empty."

memory = UserMemory()
