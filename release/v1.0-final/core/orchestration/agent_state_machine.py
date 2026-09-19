import time
from typing import Dict, Any, List

class AgentStateMachine:
    """ Authoritative Agent State Machine tracking E2E state transitions (Phase 1). """

    STATES = [
        "IDLE", "LISTENING", "UNDERSTANDING", "PLANNING", "OBSERVING",
        "GROUNDING", "SAFETY_CHECK", "WAITING_CONFIRMATION", "EXECUTING",
        "VERIFYING", "REFLECTING", "REPLANNING", "RECOVERING", "PAUSED",
        "COMPLETED", "FAILED", "ABORTED"
    ]

    def __init__(self):
        self.current_state = "IDLE"
        self.transition_history: List[Dict[str, Any]] = []

    def transition_to(self, new_state: str, task_id: str, reason: str, confidence: float = 1.0, action: str = "None", verification_result: str = "None"):
        if new_state not in self.STATES:
            raise ValueError(f"Invalid state transition target: {new_state}")

        prev_state = self.current_state
        self.current_state = new_state
        
        transition = {
            "timestamp": time.time(),
            "task_id": task_id,
            "reason": reason,
            "previous_state": prev_state,
            "new_state": new_state,
            "confidence": confidence,
            "action": action,
            "verification_result": verification_result
        }
        self.transition_history.append(transition)
        print(f"[STATE] Transition: {prev_state} -> {new_state} (Reason: {reason})")

state_machine = AgentStateMachine()
