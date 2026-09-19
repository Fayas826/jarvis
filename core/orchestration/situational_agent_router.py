import re
from typing import Any, Dict

from core.orchestration.cryogenic_swarm_manager import CryogenicSwarmManager
from core.orchestration.world_state_engine import world_state_engine


class SituationalAgentRouter:
    """Routes runtime situations to sleeping specialist agents with a verifiable envelope."""

    TOPIC_RULES = [
        (r"react|jsx|component|frontend|vite|hud|ui", "REACT_COMPONENT_REFACTORER"),
        (r"network|latency|timeout|proxy|cors", "NETWORK_LATENCY_ANALYST"),
        (r"database|mongo|index|query", "DATABASE_INDEXING_SPECIALIST"),
        (r"docker|container|compose", "DOCKER_CONTAINERIZATION_EXPERT"),
        (r"gpu|vram|thermal|memory|cpu|ram", "HARDWARE_SYSTEM_DIAGNOSTICS"),
    ]

    def __init__(self):
        self.manager = CryogenicSwarmManager()
        self.last_route: Dict[str, Any] | None = None

    def classify_topic(self, situation: str) -> str:
        text = situation.lower()
        for pattern, topic in self.TOPIC_RULES:
            if re.search(pattern, text):
                return topic
        return "REACT_COMPONENT_REFACTORER"

    def route(self, situation: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        payload = payload or {}
        topic = self.classify_topic(situation)
        agent = self.manager.wake_agent(topic)
        if not agent:
            result = {
                "status": "NO_AGENT",
                "topic": topic,
                "situation": situation,
                "confidence": 0,
                "requires_human": True,
            }
        else:
            execution = self.manager.execute_and_sleep({"error": situation, **payload}) or {}
            result = {
                "status": "ROUTED",
                "topic": topic,
                "agent_name": agent.get("name"),
                "situation": situation,
                "proposal": execution,
                "confidence": 64 if execution.get("patch") else 52,
                "requires_human": True,
                "verification": "proposal_only_not_auto_applied",
            }
        self.last_route = result
        world_state_engine.record_event("AGENT_ROUTED", result, "agent_router")
        return result

    def status(self) -> Dict[str, Any]:
        return {
            "status": "READY",
            "mode": "CRYOSLEEP_ROUTING",
            "last_route": self.last_route,
        }


situational_agent_router = SituationalAgentRouter()
