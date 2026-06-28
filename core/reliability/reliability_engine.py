
import time
import threading
import json
import os
from collections import defaultdict
from core.cognition.reasoning.evolution_engine import evolution_engine

class ReliabilityEngine:
    def __init__(self):
        self.memory_bank = []
        self.recurrence_tracker = defaultdict(int)
        self.lock = threading.Lock()
        self.metrics = {
            "repair_success_rate": 100,
            "recurring_issues": 0,
            "stability_score": 100
        }
        self.patterns = []

    def analyze_failure(self, component, error_msg, metadata=None):
        """Phase 1: Root Cause Analyzer"""
        root_cause = self._detect_root_cause(error_msg, metadata)
        failure_type = self._classify_failure(root_cause)
        
        event = {
            "timestamp": time.time(),
            "component": component,
            "error": error_msg,
            "root_cause": root_cause,
            "type": failure_type,
            "metadata": metadata or {}
        }
        
        self._store_in_memory(event)
        return event

    def _detect_root_cause(self, error_msg, metadata):
        msg = error_msg.lower()
        if "memory" in msg or "oom" in msg: return "MEMORY_SATURATION"
        if "timeout" in msg or "connection" in msg: return "NETWORK_LATENCY"
        if "permission" in msg or "access" in msg: return "CONFIG_PERMISSION_ERR"
        if "cpu" in msg or "load" in msg: return "CPU_RESOURCE_CONTENTION"
        return "UNKNOWN_LOGIC_ANOMALY"

    def _classify_failure(self, root_cause):
        categories = {
            "MEMORY_SATURATION": "RESOURCE",
            "NETWORK_LATENCY": "INFRASTRUCTURE",
            "CONFIG_PERMISSION_ERR": "CONFIG",
            "CPU_RESOURCE_CONTENTION": "RESOURCE",
            "UNKNOWN_LOGIC_ANOMALY": "LOGIC"
        }
        return categories.get(root_cause, "UNKNOWN")

    def _store_in_memory(self, event):
        """Phase 2: Failure Memory Bank"""
        with self.lock:
            self.memory_bank.append(event)
            # Track recurrence
            key = f"{event['component']}_{event['root_cause']}"
            self.recurrence_tracker[key] += 1
            
            if self.recurrence_tracker[key] > 3:
                self._generate_permanent_fix_recommendation(event, self.recurrence_tracker[key])

    def _generate_permanent_fix_recommendation(self, event, count):
        """Phase 3: Permanent Fix Engine"""
        recommendations = {
            "MEMORY_SATURATION": "Implement dynamic model offloading or increase swap space.",
            "NETWORK_LATENCY": "Switch to local-first fallback or increase retry backoff.",
            "CPU_RESOURCE_CONTENTION": "Stagger high-load agent tasks; prioritize kernel threads.",
            "CONFIG_PERMISSION_ERR": "Audit service account permissions; fix directory ownership."
        }
        
        rec = {
            "issue": event["root_cause"],
            "component": event["component"],
            "recurrence": count,
            "recommendation": recommendations.get(event["root_cause"], "Deep architectural audit required."),
            "timestamp": time.time()
        }
        self.patterns.append(rec)
        print(f"[PERMANENT_FIX_ENGINE] Pattern detected in {event['component']}. Recommendation generated.")

    def verify_repair(self, intent, verification_fn):
        """Phase 4: Verification Layer"""
        print(f"[VERIFYING_REPAIR] {intent}")
        success = verification_fn()
        
        # Update Metrics
        with self.lock:
            total = len(self.memory_bank)
            if total > 0:
                failed_repairs = sum(1 for e in self.memory_bank if e.get('repair_failed'))
                self.metrics["repair_success_rate"] = ((total - failed_repairs) / total) * 100
                self.metrics["stability_score"] = max(0, 100 - (len(self.patterns) * 5))
        
        return success

    def get_reliability_report(self):
        """Phase 5: Reliability Metrics"""
        return {
            "metrics": self.metrics,
            "recent_patterns": self.patterns[-5:],
            "memory_bank_size": len(self.memory_bank)
        }

reliability_engine = ReliabilityEngine()
