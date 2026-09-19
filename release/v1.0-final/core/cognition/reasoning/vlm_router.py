"""
Phase 34 Track 4 — Intelligent Tool Routing Optimization
==========================================================

Upgrades:
- IntelligentToolRouter: full multi-factor scoring engine
- AppActionMemory integration: learned preferences influence scoring
- VRAM-aware routing: VLM candidates downscored when VRAM pressure is high
- Latency-weighted selection: measured historical latency updates base costs
- Source reliability tier: dom > uia > ocr > vlm baseline reliability
- Target-type bias: scrollable/app/text/element biases the preferred tool
- Fallback cost: each tool has a known escalation cost vs. its predecessor
- Stale-memory decay: learning weights decay when success count is low
- Cold-start safe: reasonable defaults when no history exists

BACKWARD COMPATIBILITY:
- VLMRouter, ToolRouter, vlm_router, tool_router are preserved exactly.
- IntelligentToolRouter wraps ToolRouter — callers can adopt it incrementally.

SAFETY NOTE:
- This module never calls safety_gate, permission_model, or any
  protected file. Routing decisions go to the ActionExecutor which
  calls safety_gate before execution.
- Prompt-injection guard: app_name and action_type inputs are sanitized.
"""

import os
import time
import uuid
import math
from typing import Dict, Any, List, Optional, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# Constants: base latency (ms) and resource cost per tool
# Source: Phase 33 baseline measurements
# ──────────────────────────────────────────────────────────────────────────────

_BASE_LATENCY_MS: Dict[str, float] = {
    "native": 5.0,
    "dom":    10.0,
    "uia":    55.0,
    "ocr":    280.0,
    "vlm":    1500.0,
}

# Normalised resource cost 0.0–1.0 (VRAM + CPU weight)
_RESOURCE_COST: Dict[str, float] = {
    "native": 0.05,
    "dom":    0.10,
    "uia":    0.20,
    "ocr":    0.50,
    "vlm":    0.95,
}

# Baseline source reliability (ground-truth accuracy tier)
_SOURCE_RELIABILITY: Dict[str, float] = {
    "native": 0.99,
    "dom":    0.95,
    "uia":    0.88,
    "ocr":    0.72,
    "vlm":    0.85,    # higher than ocr for structured targets, lower for text
}

# Fallback cost: how expensive is escalating FROM this tool to the next?
# Higher = more expensive escalation path
_FALLBACK_COST: Dict[str, float] = {
    "native": 0.10,
    "dom":    0.15,
    "uia":    0.30,
    "ocr":    0.60,
    "vlm":    0.90,   # at vlm already — escalation impossible
}

# Routing priority (lower index = cheaper/preferred fallback order)
_TOOL_PRIORITY = ["native", "dom", "uia", "ocr", "vlm"]

# Target-type biases — adjust source reliability for specific target types
_TARGET_TYPE_BIAS: Dict[str, Dict[str, float]] = {
    "button":     {"dom": +0.05, "uia": +0.03, "ocr": -0.05},
    "textfield":  {"dom": +0.08, "uia": +0.05, "ocr": -0.08},
    "app":        {"native": +0.10, "dom": -0.05},
    "scrollable": {"dom": +0.03, "uia": +0.02, "ocr": -0.10},
    "element":    {"uia": +0.05},
    "image":      {"vlm": +0.10, "ocr": +0.05, "dom": -0.10},
}

# Stale-memory threshold: below this many observations, decay the learned score
_MIN_OBSERVATIONS_FULL_TRUST = 5
_STALE_DECAY_FACTOR = 0.5    # half-weight if < MIN_OBSERVATIONS_FULL_TRUST

# VRAM thresholds
_VRAM_TOTAL_GB = 4.0
_VRAM_HIGH_PRESSURE_THRESHOLD = 0.85   # >85% used → penalise VLM
_VRAM_CRITICAL_THRESHOLD = 0.95        # >95% → disable VLM route


# ──────────────────────────────────────────────────────────────────────────────
# Input sanitiser (prompt-injection guard)
# ──────────────────────────────────────────────────────────────────────────────

def _sanitize(text: str, max_len: int = 64) -> str:
    """Strip control characters and truncate to prevent injection via app_name/action."""
    if not isinstance(text, str):
        return ""
    cleaned = "".join(c for c in text if c.isprintable())
    return cleaned[:max_len]


# ══════════════════════════════════════════════════════════════════════════════
# IntelligentToolRouter
# ══════════════════════════════════════════════════════════════════════════════

class IntelligentToolRouter:
    """
    Phase 34 Track 4 — Multi-factor tool routing engine.

    Scoring formula (higher = better):
        score = (
            confidence                    * W_CONF
          + reliability_adj               * W_REL
          + learned_preference_adj        * W_LEARN
          - latency_norm                  * W_LAT
          - resource_norm                 * W_RES
          - fallback_cost                 * W_FALL
          - vram_penalty                  * W_VRAM
        )

    Where:
    - confidence            : caller-supplied grounding confidence [0,1]
    - reliability_adj       : base source reliability ± target_type_bias
    - learned_preference_adj: AppActionMemory success rate (decayed if stale)
    - latency_norm          : measured_latency / max_latency [0,1]
    - resource_norm         : tool resource cost [0,1]
    - fallback_cost         : escalation cost if this tool fails [0,1]
    - vram_penalty          : 0 normally; rises when VRAM > threshold

    Weights:
    """

    W_CONF  = 0.55
    W_REL   = 0.10
    W_LEARN = 0.10
    W_LAT   = 0.08
    W_RES   = 0.04
    W_FALL  = 0.02
    W_VRAM  = 0.25

    def __init__(self, app_action_memory=None):
        """
        app_action_memory: optional AppActionMemory instance (Phase 34 Track 3/35.4).
        If None, routing proceeds without learned preferences (cold-start safe).
        """
        self._aam = app_action_memory
        # Per-tool measured latency (updated by record_outcome)
        self._measured_latency: Dict[str, float] = dict(_BASE_LATENCY_MS)
        # In-process reliability adjustments (separate from AppActionMemory)
        self._reliability_adj: Dict[str, float] = {t: 0.0 for t in _TOOL_PRIORITY}
        self._lock = __import__("threading").Lock()

    # ──────────────────────────────────────────────────────────────────────────
    # Main routing decision
    # ──────────────────────────────────────────────────────────────────────────

    def route(
        self,
        action_type: str,
        candidates: List[Dict[str, Any]],
        app_name: str = "",
        target_type: str = "",
        current_vram_used_gb: float = 0.0,
        privacy_required: bool = False,
    ) -> Dict[str, Any]:
        """
        Select the best tool from candidates.

        Parameters
        ----------
        action_type         : Action category (CLICK, TYPE, OPEN_APP, …)
        candidates          : List of {tool, confidence, available} dicts
        app_name            : Active application name (for AppActionMemory lookup)
        target_type         : Target element type hint (button, textfield, app, …)
        current_vram_used_gb: Currently allocated VRAM in GB (0 if unknown)
        privacy_required    : If True, block cloud/VLM routes
        """
        action_type = _sanitize(action_type.upper(), 32)
        app_name    = _sanitize(app_name, 64)
        target_type = _sanitize(target_type.lower(), 32)

        vram_fraction = current_vram_used_gb / _VRAM_TOTAL_GB if _VRAM_TOTAL_GB > 0 else 0.0
        vlm_disabled = privacy_required or vram_fraction >= _VRAM_CRITICAL_THRESHOLD

        scored = []
        for c in candidates:
            tool = c.get("tool", "")
            conf = float(c.get("confidence", 0.0))
            avail = c.get("available", True)

            if not avail or tool not in _TOOL_PRIORITY:
                continue
            if vlm_disabled and tool == "vlm":
                print(f"[ITR] VLM disabled (privacy={privacy_required} vram={vram_fraction:.0%})")
                continue

            score, breakdown = self._score(
                tool=tool,
                confidence=conf,
                action_type=action_type,
                app_name=app_name,
                target_type=target_type,
                vram_fraction=vram_fraction,
            )

            scored.append({
                "route_id":          uuid.uuid4().hex[:8],
                "candidate_tool":    tool,
                "requested_action":  action_type,
                "confidence":        conf,
                "final_score":       round(score, 5),
                "estimated_latency": self._measured_latency.get(tool, _BASE_LATENCY_MS.get(tool, 9999)),
                "resource_cost":     _RESOURCE_COST.get(tool, 1.0),
                "availability":      avail,
                "reliability_score": _SOURCE_RELIABILITY.get(tool, 0.5),
                "capability_match":  conf >= 0.50,
                "breakdown":         breakdown,
                "reason":            self._reason(tool, breakdown),
            })

        scored.sort(key=lambda x: x["final_score"], reverse=True)

        if scored:
            winner = scored[0]
            print(
                f"[ITR] route='{action_type}' app='{app_name}' "
                f"-> {winner['candidate_tool']} score={winner['final_score']:.3f} "
                f"lat={winner['estimated_latency']:.0f}ms"
            )
            return winner

        # Hard fallback
        print(f"[ITR] No viable candidate found for '{action_type}'. Hard VLM fallback.")
        return self._hard_fallback(action_type)

    # ──────────────────────────────────────────────────────────────────────────
    # Scoring engine
    # ──────────────────────────────────────────────────────────────────────────

    def _score(
        self,
        tool: str,
        confidence: float,
        action_type: str,
        app_name: str,
        target_type: str,
        vram_fraction: float,
    ) -> Tuple[float, Dict]:
        # 1. Confidence component
        conf_term = confidence * self.W_CONF

        # 2. Reliability (base + target_type bias + in-process adj)
        reliability = _SOURCE_RELIABILITY.get(tool, 0.5)
        type_bias = _TARGET_TYPE_BIAS.get(target_type, {}).get(tool, 0.0)
        inproc_adj = self._reliability_adj.get(tool, 0.0)
        reliability_adj = max(0.0, min(1.0, reliability + type_bias + inproc_adj))
        rel_term = reliability_adj * self.W_REL

        # 3. Learned preference (AppActionMemory)
        learned_score, observations = self._learned_score(app_name, action_type, tool)
        # Decay if stale
        if observations < _MIN_OBSERVATIONS_FULL_TRUST:
            decay = observations / max(_MIN_OBSERVATIONS_FULL_TRUST, 1)
            learned_score = 0.5 + (learned_score - 0.5) * decay * _STALE_DECAY_FACTOR
        learn_term = learned_score * self.W_LEARN

        # 4. Latency component (normalise against max tool latency = VLM)
        max_lat = _BASE_LATENCY_MS["vlm"]
        measured = self._measured_latency.get(tool, _BASE_LATENCY_MS.get(tool, max_lat))
        lat_norm = min(measured / max_lat, 1.0)
        lat_term = lat_norm * self.W_LAT

        # 5. Resource cost
        res_term = _RESOURCE_COST.get(tool, 1.0) * self.W_RES

        # 6. Fallback cost
        fall_term = _FALLBACK_COST.get(tool, 0.5) * self.W_FALL

        # 7. VRAM penalty (only for VLM)
        vram_penalty = 0.0
        if tool == "vlm" and vram_fraction > _VRAM_HIGH_PRESSURE_THRESHOLD:
            vram_penalty = (vram_fraction - _VRAM_HIGH_PRESSURE_THRESHOLD) / (1.0 - _VRAM_HIGH_PRESSURE_THRESHOLD)
        vram_term = vram_penalty * self.W_VRAM

        total = conf_term + rel_term + learn_term - lat_term - res_term - fall_term - vram_term

        breakdown = {
            "conf_term":     round(conf_term, 4),
            "rel_term":      round(rel_term, 4),
            "learn_term":    round(learn_term, 4),
            "lat_term":      round(lat_term, 4),
            "res_term":      round(res_term, 4),
            "fall_term":     round(fall_term, 4),
            "vram_term":     round(vram_term, 4),
            "observations":  observations,
            "learned_score": round(learned_score, 4),
        }
        return total, breakdown

    def _learned_score(self, app_name: str, action_type: str, tool: str) -> Tuple[float, int]:
        """Returns (success_rate_or_default, observation_count)."""
        if not self._aam or not app_name:
            return 0.5, 0
        try:
            rate = self._aam.get_success_rate(app_name, action_type, tool)
            count = self._aam.observation_count(app_name, action_type, tool)
            if rate is None:
                return 0.5, count
            return rate, count
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'vlm_router', f'Unhandled exception: {e}')
            return 0.5, 0

    # ──────────────────────────────────────────────────────────────────────────
    # Outcome recording (updates measured latency + in-process reliability)
    # ──────────────────────────────────────────────────────────────────────────

    def record_outcome(
        self,
        tool: str,
        action_type: str,
        success: bool,
        latency_ms: float = 0.0,
        app_name: str = "",
    ):
        """
        Update the router's internal latency and reliability estimates.
        AppActionMemory is updated separately (by ActionExecutor/ComputerUseAgent).
        """
        with self._lock:
            # Exponential moving average for latency (alpha=0.2)
            if latency_ms > 0 and tool in self._measured_latency:
                prev = self._measured_latency[tool]
                self._measured_latency[tool] = round(0.8 * prev + 0.2 * latency_ms, 2)

            # Small in-process reliability nudge
            adj = self._reliability_adj.get(tool, 0.0)
            if success:
                self._reliability_adj[tool] = min(adj + 0.02, 0.15)
            else:
                self._reliability_adj[tool] = max(adj - 0.05, -0.30)

        print(
            f"[ITR] outcome: tool={tool} action={action_type} "
            f"success={success} lat={latency_ms:.1f}ms"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _hard_fallback(self, action_type: str) -> Dict:
        return {
            "route_id":          "hard_fallback",
            "candidate_tool":    "vlm",
            "requested_action":  action_type,
            "confidence":        0.40,
            "final_score":       0.05,
            "estimated_latency": 1500.0,
            "resource_cost":     0.95,
            "availability":      True,
            "reliability_score": 0.85,
            "capability_match":  False,
            "breakdown":         {},
            "reason":            "Hard VLM fallback — no viable candidate found",
        }

    @staticmethod
    def _reason(tool: str, breakdown: Dict) -> str:
        obs = breakdown.get("observations", 0)
        ls  = breakdown.get("learned_score", 0.5)
        if obs >= _MIN_OBSERVATIONS_FULL_TRUST:
            return f"{tool} selected: {obs} obs, learned_rate={ls:.0%}"
        elif obs > 0:
            return f"{tool} selected: cold-start ({obs} obs, partial decay)"
        else:
            return f"{tool} selected: no history (cold-start defaults)"

    def get_measured_latency(self, tool: str) -> float:
        return self._measured_latency.get(tool, _BASE_LATENCY_MS.get(tool, 9999))

    def get_reliability_adj(self, tool: str) -> float:
        return self._reliability_adj.get(tool, 0.0)


# ══════════════════════════════════════════════════════════════════════════════
# BACKWARD-COMPATIBLE: VLMRouter (Phase 9 original — unchanged)
# ══════════════════════════════════════════════════════════════════════════════

class VLMRouter:
    """Model-independent VLM routing layer selecting local or cloud models (Phase 9)."""

    def __init__(self):
        self.local_vram_limit_gb = 4.0
        self.gemini_active = bool(os.getenv("GEMINI_API_KEY"))
        self.mistral_active = bool(os.getenv("MISTRAL_API_KEY"))

    def decide_route(self, task_type: str, privacy_required: bool = False, network_available: bool = True) -> str:
        """Determines model routing (LOCAL vs CLOUD) based on criteria constraints."""
        if privacy_required:
            return "LOCAL"
        if self.local_vram_limit_gb <= 4.0:
            if network_available and (self.gemini_active or self.mistral_active):
                return "CLOUD"
            return "LOCAL"
        return "LOCAL"


# ══════════════════════════════════════════════════════════════════════════════
# BACKWARD-COMPATIBLE: ToolRouter (Phase 34.3 original — unchanged interface)
# Now delegates to IntelligentToolRouter for scoring.
# ══════════════════════════════════════════════════════════════════════════════

class ToolRouter:
    """
    Confidence-aware, resource-aware routing layer.

    Phase 34.3 interface preserved. Internally delegates to IntelligentToolRouter
    for richer scoring. Callers using decide_tool_route() get better results
    with no API change.
    """

    def __init__(self):
        # Attempt to wire AppActionMemory — graceful if unavailable
        _aam = None
        try:
            from core.cognition.memory.context_memory import app_action_memory
            _aam = app_action_memory
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'vlm_router', f'Unhandled exception: {e}')
            pass

        self._itr = IntelligentToolRouter(app_action_memory=_aam)
        # Legacy routing_memory kept for any direct readers
        self.routing_memory: Dict[str, float] = {}

    def decide_tool_route(
        self,
        requested_action: str,
        candidates: List[Dict[str, Any]],
        app_name: str = "",
        target_type: str = "",
        current_vram_used_gb: float = 0.0,
        privacy_required: bool = False,
    ) -> Dict[str, Any]:
        return self._itr.route(
            action_type=requested_action,
            candidates=candidates,
            app_name=app_name,
            target_type=target_type,
            current_vram_used_gb=current_vram_used_gb,
            privacy_required=privacy_required,
        )

    def record_outcome(
        self,
        tool: str,
        requested_action: str,
        success: bool,
        latency_ms: float = 0.0,
        app_name: str = "",
    ):
        """Record outcome — updates both internal router and legacy routing_memory."""
        self._itr.record_outcome(tool, requested_action, success, latency_ms, app_name)
        # Keep legacy routing_memory in sync (Phase 34.3 callers)
        mem_key = f"{tool}_{requested_action}"
        current = self.routing_memory.get(mem_key, 1.0)
        if success:
            self.routing_memory[mem_key] = min(current + 0.05, 1.0)
        else:
            self.routing_memory[mem_key] = max(current - 0.20, 0.2)


# ══════════════════════════════════════════════════════════════════════════════
# Module singletons (backward compatible)
# ══════════════════════════════════════════════════════════════════════════════

vlm_router  = VLMRouter()
tool_router = ToolRouter()

