import uuid
import threading
from typing import Dict, Any, List, Tuple
from .config import _BASE_LATENCY_MS, _TOOL_PRIORITY, _RESOURCE_COST, _SOURCE_RELIABILITY, _VRAM_TOTAL_GB, _VRAM_CRITICAL_THRESHOLD
from .scoring_models import ScoringEngine

def _sanitize(text: str, max_len: int = 64) -> str:
    if not isinstance(text, str): return ""
    return "".join(c for c in text if c.isprintable())[:max_len]

class IntelligentToolRouter:
    def __init__(self, app_action_memory=None):
        self._aam = app_action_memory
        self._measured_latency: Dict[str, float] = dict(_BASE_LATENCY_MS)
        self._reliability_adj: Dict[str, float] = {t: 0.0 for t in _TOOL_PRIORITY}
        self._lock = threading.Lock()

    def route(
        self, action_type: str, candidates: List[Dict[str, Any]], 
        app_name: str = "", target_type: str = "", 
        current_vram_used_gb: float = 0.0, privacy_required: bool = False
    ) -> Dict[str, Any]:
        action_type = _sanitize(action_type.upper(), 32)
        app_name = _sanitize(app_name, 64)
        target_type = _sanitize(target_type.lower(), 32)

        vram_fraction = current_vram_used_gb / _VRAM_TOTAL_GB if _VRAM_TOTAL_GB > 0 else 0.0
        vlm_disabled = privacy_required or vram_fraction >= _VRAM_CRITICAL_THRESHOLD

        scored = []
        for c in candidates:
            tool = c.get("tool", "")
            conf = float(c.get("confidence", 0.0))
            avail = c.get("available", True)

            if not avail or tool not in _TOOL_PRIORITY: continue
            if vlm_disabled and tool == "vlm": continue

            measured_lat = self._measured_latency.get(tool, _BASE_LATENCY_MS.get(tool, 9999))
            inproc_adj = self._reliability_adj.get(tool, 0.0)
            learned_score, observations = self._learned_score(app_name, action_type, tool)

            score, breakdown = ScoringEngine.calculate_score(
                tool, conf, action_type, app_name, target_type, 
                vram_fraction, measured_lat, inproc_adj, learned_score, observations
            )

            scored.append({
                "route_id": uuid.uuid4().hex[:8],
                "candidate_tool": tool, "requested_action": action_type,
                "confidence": conf, "final_score": round(score, 5),
                "estimated_latency": measured_lat,
                "resource_cost": _RESOURCE_COST.get(tool, 1.0),
                "availability": avail, "reliability_score": _SOURCE_RELIABILITY.get(tool, 0.5),
                "capability_match": conf >= 0.50, "breakdown": breakdown,
                "reason": self._reason(tool, breakdown),
            })

        scored.sort(key=lambda x: x["final_score"], reverse=True)
        if scored:
            print(f"[ITR] -> {scored[0]['candidate_tool']} score={scored[0]['final_score']:.3f}")
            return scored[0]

        return self._hard_fallback(action_type)

    def _learned_score(self, app_name: str, action_type: str, tool: str) -> Tuple[float, int]:
        if not self._aam: return 0.5, 0
        try:
            return self._aam.get_tool_success_rate(app_name, action_type, tool)
        except Exception: return 0.5, 0

    def _reason(self, tool: str, breakdown: Dict) -> str:
        return f"Selected {tool} based on confidence and historical reliability."

    def _hard_fallback(self, action_type: str) -> Dict[str, Any]:
        return {"candidate_tool": "vlm", "reason": "Hard fallback"}
