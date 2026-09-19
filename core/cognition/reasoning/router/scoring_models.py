from typing import Tuple, Dict, Any
from .config import (
    _SOURCE_RELIABILITY, _TARGET_TYPE_BIAS, _MIN_OBSERVATIONS_FULL_TRUST,
    _STALE_DECAY_FACTOR, _BASE_LATENCY_MS, _RESOURCE_COST, _FALLBACK_COST,
    _VRAM_HIGH_PRESSURE_THRESHOLD
)

class ScoringEngine:
    W_CONF  = 0.55
    W_REL   = 0.10
    W_LEARN = 0.10
    W_LAT   = 0.08
    W_RES   = 0.04
    W_FALL  = 0.02
    W_VRAM  = 0.25

    @classmethod
    def calculate_score(
        cls,
        tool: str,
        confidence: float,
        action_type: str,
        app_name: str,
        target_type: str,
        vram_fraction: float,
        measured_latency: float,
        inproc_adj: float,
        learned_score: float,
        observations: int
    ) -> Tuple[float, Dict[str, float]]:
        
        conf_term = confidence * cls.W_CONF

        reliability = _SOURCE_RELIABILITY.get(tool, 0.5)
        type_bias = _TARGET_TYPE_BIAS.get(target_type, {}).get(tool, 0.0)
        reliability_adj = max(0.0, min(1.0, reliability + type_bias + inproc_adj))
        rel_term = reliability_adj * cls.W_REL

        if observations < _MIN_OBSERVATIONS_FULL_TRUST:
            decay = observations / max(_MIN_OBSERVATIONS_FULL_TRUST, 1)
            learned_score = 0.5 + (learned_score - 0.5) * decay * _STALE_DECAY_FACTOR
        learn_term = learned_score * cls.W_LEARN

        max_lat = _BASE_LATENCY_MS["vlm"]
        lat_norm = min(measured_latency / max_lat, 1.0)
        lat_term = lat_norm * cls.W_LAT

        res_term = _RESOURCE_COST.get(tool, 1.0) * cls.W_RES
        fall_term = _FALLBACK_COST.get(tool, 0.5) * cls.W_FALL

        vram_penalty = 0.0
        if tool == "vlm" and vram_fraction > _VRAM_HIGH_PRESSURE_THRESHOLD:
            vram_penalty = (vram_fraction - _VRAM_HIGH_PRESSURE_THRESHOLD) / (1.0 - _VRAM_HIGH_PRESSURE_THRESHOLD)
        vram_term = vram_penalty * cls.W_VRAM

        total = conf_term + rel_term + learn_term - lat_term - res_term - fall_term - vram_term

        breakdown = {
            "conf_term": round(conf_term, 4),
            "rel_term": round(rel_term, 4),
            "learn_term": round(learn_term, 4),
            "lat_term": round(lat_term, 4),
            "res_term": round(res_term, 4),
            "fall_term": round(fall_term, 4),
            "vram_term": round(vram_term, 4),
            "reliability_adj": round(reliability_adj, 4),
        }

        return total, breakdown
