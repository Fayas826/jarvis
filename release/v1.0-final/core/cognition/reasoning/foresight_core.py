import datetime
import json
from collections import Counter
from core.cognition.memory.memory import memory
from core.cognition.reasoning.shared_state import INTEL_CACHE

# 🔮 O.M.E.G.A. TIER_5: FORESIGHT_CORE
# Predictive Intent & Behavioral Anticipation

class ForesightCore:
    def __init__(self):
        self.last_predictions = []

    def generate_predictions(self, current_vitals, vision_insight):
        """Generates tactical foresight nodes using Temporal & Semantic Clustering."""
        predictions = []
        now = datetime.datetime.now()
        hour = now.hour
        history = memory.data.get("history", [])
        
        # 🧪 TACTICAL_PATTERN_A: TEMPORAL_RECURRENCE (LEARNED)
        # Look for commands frequently used in this 2-hour window
        time_based_hits = []
        for h in history:
            try:
                h_time = datetime.datetime.fromisoformat(h.get("timestamp", ""))
                if abs(h_time.hour - hour) <= 1:
                    time_based_hits.append(h.get("command", "").lower())
            except: continue
        
        if time_based_hits:
            most_common = Counter(time_based_hits).most_common(2)
            for cmd, count in most_common:
                if count >= 2: # Pattern detected
                    label = f"Resume: {cmd.title()}"
                    predictions.append({"label": label, "intent": cmd, "confidence": "HIGH"})

        # 🌡️ TACTICAL_PATTERN_B: VITALS_REACTIVE
        cpu = float(current_vitals.get("cpu_load", "0%").replace("%", ""))
        if cpu > 80:
            predictions.append({"label": "Thermal Optimization", "intent": "restore_aura", "confidence": "CRITICAL"})

        # 🧿 TACTICAL_PATTERN_C: SEMANTIC_VISION_SYNERGY
        if vision_insight:
            v_low = vision_insight.lower()
            if "code" in v_low or "terminal" in v_low or "editor" in v_low:
                predictions.append({"label": "Scan for Commits", "intent": "search git status", "confidence": "MEDIUM"})
            if "browser" in v_low or "web" in v_low:
                predictions.append({"label": "Deep Intelligence Search", "intent": "search latest tech news", "confidence": "MEDIUM"})

        # 🧠 TACTICAL_PATTERN_D: SEQUENTIAL_LOGIC
        if history:
            last_cmd = history[-1].get("command", "").lower()
            if "open" in last_cmd:
                 predictions.append({"label": "Analyze Active Node", "intent": "diagnostic", "confidence": "LOW"})

        # Ensure unique labels and limit to 3 nodes
        seen = set()
        final_predictions = []
        for p in predictions:
            if p["label"] not in seen:
                final_predictions.append(p)
                seen.add(p["label"])
        
        self.last_predictions = final_predictions[:3]
        return self.last_predictions

# Global Instance
foresight_core = ForesightCore()
