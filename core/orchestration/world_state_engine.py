import time
from collections import deque
from typing import Any, Dict, List

import psutil


class WorldStateEngine:
    """4D/5D state engine: timeline + prediction + confidence/risk."""

    def __init__(self, max_events: int = 120):
        self.events = deque(maxlen=max_events)
        self.last_snapshot: Dict[str, Any] = {}

    def record_event(self, event_type: str, payload: Dict[str, Any] | None = None, source: str = "system") -> Dict[str, Any]:
        event = {
            "ts": time.time(),
            "type": event_type,
            "source": source,
            "payload": payload or {},
        }
        self.events.append(event)
        return event

    def snapshot(self) -> Dict[str, Any]:
        cpu = psutil.cpu_percent(interval=0.05)
        mem = psutil.virtual_memory()
        recent = list(self.events)[-20:]
        pressure = max(cpu, mem.percent)
        confidence = self._confidence(cpu, mem.percent, recent)
        risk = self._risk(cpu, mem.percent, recent)
        intent = self._intent(recent)
        prediction = self._prediction(cpu, mem.percent, risk)

        self.last_snapshot = {
            "dimensions": {
                "d3_renderer": "three.js",
                "d4_timeline_events": len(self.events),
                "d5_confidence": confidence,
                "d5_intent": intent["score"],
                "d5_risk": risk["score"],
            },
            "now": {
                "cpu_percent": round(cpu, 2),
                "ram_percent": round(mem.percent, 2),
                "state": self._state_from_pressure(pressure),
                "timestamp": time.time(),
            },
            "timeline": recent,
            "intent": intent,
            "risk": risk,
            "confidence": confidence,
            "prediction": prediction,
        }
        return self.last_snapshot

    def health(self) -> Dict[str, Any]:
        snap = self.snapshot()
        return {
            "status": "DEGRADED" if snap["risk"]["level"] in {"HIGH", "CRITICAL"} else "ONLINE",
            "latency_ms": 50,
            "memory": "ONLINE",
            "agents": "READY",
            "voice": "CLIENT_CONTROLLED",
            "world_engine": "ONLINE",
            "risk": snap["risk"],
            "confidence": snap["confidence"],
        }

    def verify_action(self, intent: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        payload = payload or {}
        risk = self.classify_action_risk(intent, payload)
        action = self.record_event("ACTION_REQUESTED", {"intent": intent, "risk": risk, "payload": payload}, "action_contract")
        if risk["level"] in {"HIGH", "CRITICAL"}:
            status = "needs_approval"
        else:
            status = "verified"
            self.record_event("ACTION_VERIFIED", {"intent": intent, "action_ts": action["ts"]}, "action_contract")
        return {
            "status": status,
            "intent": intent,
            "risk": risk,
            "verification": "policy_gate",
            "action_id": f"act-{int(action['ts'] * 1000)}",
        }

    def classify_action_risk(self, intent: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        text = f"{intent} {payload}".lower()
        destructive = ["delete", "format", "wipe", "shutdown", "payment", "transfer", "credential", "password"]
        medium = ["execute", "install", "deploy", "restart", "modify", "write", "control"]
        if any(term in text for term in destructive):
            return {"level": "HIGH", "score": 85, "reason": "destructive_or_sensitive_intent"}
        if any(term in text for term in medium):
            return {"level": "MEDIUM", "score": 55, "reason": "system_mutation_intent"}
        return {"level": "LOW", "score": 18, "reason": "observational_or_safe_intent"}

    def _confidence(self, cpu: float, ram: float, recent: List[Dict[str, Any]]) -> int:
        penalty = 0
        if cpu > 85:
            penalty += 18
        if ram > 85:
            penalty += 18
        penalty += min(20, len([e for e in recent if "FAIL" in str(e).upper()]) * 5)
        return max(35, 96 - penalty)

    def _risk(self, cpu: float, ram: float, recent: List[Dict[str, Any]]) -> Dict[str, Any]:
        score = int(max(cpu, ram))
        score += min(20, len([e for e in recent if "ERROR" in str(e).upper() or "FAIL" in str(e).upper()]) * 4)
        score = min(100, score)
        level = "LOW"
        if score >= 92:
            level = "CRITICAL"
        elif score >= 85:
            level = "HIGH"
        elif score >= 65:
            level = "MEDIUM"
        return {"score": score, "level": level}

    def _intent(self, recent: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not recent:
            return {"label": "STANDBY", "score": 20}
        latest = recent[-1]
        event_type = latest.get("type", "STANDBY")
        if "ACTION" in event_type:
            return {"label": "EXECUTION", "score": 78}
        if "ERROR" in event_type or "FAIL" in event_type:
            return {"label": "RECOVERY", "score": 82}
        return {"label": "OBSERVATION", "score": 48}

    def _prediction(self, cpu: float, ram: float, risk: Dict[str, Any]) -> List[Dict[str, Any]]:
        predictions = []
        if risk["level"] in {"HIGH", "CRITICAL"}:
            predictions.append({"label": "Reduce system load", "intent": "optimize system", "confidence": 84})
        if cpu > 75:
            predictions.append({"label": "Throttle heavy render loops", "intent": "reduce hud particles", "confidence": 72})
        if ram > 75:
            predictions.append({"label": "Clear memory pressure", "intent": "cleanup system", "confidence": 76})
        if not predictions:
            predictions.append({"label": "Maintain active watch", "intent": "status report", "confidence": 66})
        return predictions[:3]

    def _state_from_pressure(self, pressure: float) -> str:
        if pressure >= 85:
            return "CRITICAL"
        if pressure >= 70:
            return "HOT"
        if pressure >= 45:
            return "ACTIVE"
        return "NOMINAL"


world_state_engine = WorldStateEngine()
