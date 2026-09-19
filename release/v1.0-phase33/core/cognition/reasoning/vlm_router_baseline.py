import os
import uuid
import time
from typing import Dict, Any, List

class VLMRouter:
    """Model-independent VLM routing layer selecting local or cloud models (Phase 9)."""

    def __init__(self):
        self.local_vram_limit_gb = 4.0
        self.gemini_active = bool(os.getenv("GEMINI_API_KEY"))
        self.mistral_active = bool(os.getenv("MISTRAL_API_KEY"))

    def decide_route(self, task_type: str, privacy_required: bool = False, network_available: bool = True) -> str:
        """Determines model routing (LOCAL vs CLOUD) based on criteria constraints."""
        # Privacy constraints dictate strictly local
        if privacy_required:
            return "LOCAL"

        # Hardware VRAM constraints restrict heavy local vision pipelines
        if self.local_vram_limit_gb <= 4.0:
            if network_available and (self.gemini_active or self.mistral_active):
                return "CLOUD"
            return "LOCAL"

        return "LOCAL"

class ToolRouter:
    """Confidence-aware, resource-aware routing layer selecting the cheapest reliable tool candidates."""
    
    def __init__(self):
        self.routing_memory = {} # Maps application/context key to reliability scores

    def decide_tool_route(self, requested_action: str, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        print(f"[TOOL_ROUTER] Routing requested action: '{requested_action}'")
        
        scored_routes = []
        for c in candidates:
            tool = c.get("tool") # dom, uia, ocr, vlm, native
            confidence = c.get("confidence", 0.0)
            available = c.get("available", True)
            
            if not available:
                continue
                
            # Base latency and resource costs mappings
            if tool == "native":
                base_latency = 5.0
                resource_cost = 0.1
            elif tool == "dom":
                base_latency = 10.0
                resource_cost = 0.2
            elif tool == "uia":
                base_latency = 55.0
                resource_cost = 0.3
            elif tool == "ocr":
                base_latency = 280.0
                resource_cost = 0.6
            else: # vlm
                base_latency = 1500.0
                resource_cost = 0.95
                
            # Adjust scores based on routing outcome memory
            mem_key = f"{tool}_{requested_action}"
            reliability_score = self.routing_memory.get(mem_key, 1.0)
            
            final_routing_score = (confidence * reliability_score) - (resource_cost * 0.1)
            
            scored_routes.append({
                "route_id": str(uuid.uuid4())[:8],
                "requested_action": requested_action,
                "candidate_tool": tool,
                "capability_match": confidence >= 0.5,
                "confidence": confidence,
                "estimated_latency": base_latency,
                "resource_cost": resource_cost,
                "availability": available,
                "reliability_score": reliability_score,
                "final_score": final_routing_score,
                "reason": f"Tool match with normalized latency of {base_latency}ms"
            })
            
        scored_routes.sort(key=lambda x: x["final_score"], reverse=True)
        
        if scored_routes:
            winner = scored_routes[0]
            print(f"[TOOL_ROUTER] Selected route: '{winner['candidate_tool']}' (confidence: {winner['confidence']:.2f})")
            return winner
            
        # Fallback default route
        return {
            "route_id": "fallback_default",
            "requested_action": requested_action,
            "candidate_tool": "vlm",
            "capability_match": False,
            "confidence": 0.5,
            "estimated_latency": 1500.0,
            "resource_cost": 0.95,
            "availability": True,
            "reliability_score": 1.0,
            "final_score": 0.4,
            "reason": "VLM hard fallback trigger active"
        }

    def record_outcome(self, tool: str, requested_action: str, success: bool):
        mem_key = f"{tool}_{requested_action}"
        current = self.routing_memory.get(mem_key, 1.0)
        if success:
            self.routing_memory[mem_key] = min(current + 0.05, 1.0)
        else:
            self.routing_memory[mem_key] = max(current - 0.20, 0.2)
        print(f"[TOOL_ROUTER] Updated memory outcome for key: {mem_key} -> {self.routing_memory[mem_key]:.2f}")

vlm_router = VLMRouter()
tool_router = ToolRouter()
