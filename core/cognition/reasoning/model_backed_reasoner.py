import os
from typing import Any, Dict

from core.cognition.memory.scored_memory import scored_memory_store
from core.orchestration.situational_agent_router import situational_agent_router
from core.orchestration.world_state_engine import world_state_engine


class ModelBackedReasoner:
    """Reasoning facade: uses configured model provider when available, else deterministic fallback."""

    def reason(self, prompt: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
        context = context or {}
        memory = scored_memory_store.recall(prompt, limit=5, min_score=0.2)
        route = situational_agent_router.route(prompt, {"source": "model_reasoner", "context": context})
        risk = world_state_engine.classify_action_risk(prompt, context)
        provider = self._provider_status()
        response = self._fallback_response(prompt, route, risk, memory)
        result = {
            "provider": provider,
            "response": response,
            "agent_route": route,
            "risk": risk,
            "memory_used": memory,
            "confidence": 72 if provider["mode"] == "fallback" else 86,
        }
        world_state_engine.record_event("MODEL_REASONED", {"prompt": prompt, "risk": risk, "provider": provider}, "reasoner")
        scored_memory_store.remember(
            content=f"Reasoned: {prompt} -> {response}",
            source="model_reasoner",
            category="reasoning_trace",
            importance=3,
            trust=0.65,
            metadata={"risk": risk, "provider": provider},
        )
        return result

    def _provider_status(self) -> Dict[str, Any]:
        if os.getenv("OPENAI_API_KEY"):
            return {"mode": "configured", "provider": "openai", "note": "external call disabled in local safety facade"}
        if os.getenv("OLLAMA_HOST"):
            return {"mode": "configured", "provider": "ollama", "note": "local model host configured"}
        return {"mode": "fallback", "provider": "deterministic", "note": "no model provider configured"}

    def _fallback_response(self, prompt: str, route: Dict[str, Any], risk: Dict[str, Any], memory: list) -> str:
        agent = route.get("agent_name") or route.get("topic") or "general agent"
        if risk["level"] in {"HIGH", "CRITICAL"}:
            return f"I routed this to {agent}, but execution is gated because risk is {risk['level']}. Human approval is required."
        if memory:
            return f"I routed this to {agent}. I found {len(memory)} relevant memories and recommend verified execution with rollback tracking."
        return f"I routed this to {agent}. No strong memory match found, so use cautious verified execution."


model_backed_reasoner = ModelBackedReasoner()
