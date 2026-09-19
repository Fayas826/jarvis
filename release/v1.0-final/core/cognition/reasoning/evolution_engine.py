
import json
import os
import time
from datetime import datetime

class EvolutionEngine:
    def __init__(self, memory_path="evolution_memory.json"):
        self.memory_path = memory_path
        self.data = self._load_memory()
        
    def _load_memory(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        return {
            "failures": [],
            "successes": [],
            "resource_spikes": [],
            "routines": {},
            "optimizations": {
                "voice_threshold_offset": 0.0,
                "vision_scan_interval": 15,
                "preferred_modes": {}
            }
        }

    def _save_memory(self):
        with open(self.memory_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    # 📈 DOMAIN_7: FAILURE_LEARNING
    def record_failure(self, event_type, context):
        """Learns from misses (e.g., voice confidence < 0.3)."""
        failure_event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "context": context
        }
        self.data["failures"].append(failure_event)
        self._analyze_failures(event_type)
        self._save_memory()

    def _analyze_failures(self, event_type):
        """Adjusts thresholds if failure patterns are detected."""
        recent_failures = [f for f in self.data["failures"][-10:] if f["type"] == event_type]
        if len(recent_failures) >= 5:
            if event_type == "VOICE_CONFIDENCE":
                self.data["optimizations"]["voice_threshold_offset"] -= 0.05
                print(f"📈 EVOLUTION: Optimizing voice threshold due to pattern of low confidence.")

    # 📈 DOMAIN_7: SUCCESS_PATTERN_LEARNING
    def record_success(self, event_type, context):
        """Tracks successful workflows to predict future needs."""
        hour = datetime.now().hour
        if event_type == "MISSION_COMPLETE":
            mission_id = context.get("mission_id")
            routine_key = f"h{hour}_{mission_id}"
            self.data["routines"][routine_key] = self.data["routines"].get(routine_key, 0) + 1
        
        self.data["successes"].append({"timestamp": datetime.now().isoformat(), "type": event_type})
        self._save_memory()

    # 📈 DOMAIN_7: RESOURCE_LEARNING
    def record_resource_spike(self, component, load):
        """Learns to throttle specific components based on historical spikes."""
        self.data["resource_spikes"].append({
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "load": load
        })
        
        # If vision cortex consistently spikes CPU, increase interval
        spikes = [s for s in self.data["resource_spikes"][-5:] if s["component"] == component]
        if len(spikes) >= 3:
            if component == "VISION_CORTEX":
                self.data["optimizations"]["vision_scan_interval"] += 5
                print(f"📈 EVOLUTION: Throttling vision frequency due to resource spike pattern.")
        
        self._save_memory()

    def get_optimizations(self):
        return self.data["optimizations"]

evolution_engine = EvolutionEngine()
