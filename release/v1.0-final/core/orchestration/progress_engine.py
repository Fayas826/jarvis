"""
Phase 37.4 — Goal Progress Engine
=================================

Evaluates ongoing state progress toward goal criteria.
Provides feedback loops for loops/stalls.
Classifies execution state: SUCCESS, PARTIAL, BLOCKED, FAILED, UNKNOWN
"""

from typing import Dict, Any, List
from core.orchestration.environment_model import environment_model

class GoalProgressStatus:
    ON_TRACK = "ON_TRACK"
    STALLED = "STALLED"
    REGRESSING = "REGRESSING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"

class GoalProgressEngine:
    """Monitors workflow transitions to determine if actions are advancing towards the goal."""

    def __init__(self, max_stagnation_turns: int = 3):
        self.max_stagnation_turns = max_stagnation_turns
        self.state_history: List[Dict[str, Any]] = []

    def observe_turn(self, last_action: Dict[str, Any], verification: Dict[str, Any]) -> str:
        """
        Record a step's execution outcomes and check for loop or stagnation patterns.
        """
        # Save snapshot
        snapshot = environment_model.get_environment_snapshot()
        self.state_history.append({
            "action": last_action,
            "verification": verification,
            "snapshot": snapshot
        })

        if verification.get("status") == "SUCCESS":
            return GoalProgressStatus.ON_TRACK

        if len(self.state_history) < 2:
            return GoalProgressStatus.ON_TRACK

        # Detect identical repeat actions (looping)
        recent_actions = [h["action"] for h in self.state_history[-3:]]
        if len(recent_actions) >= 3:
            first = recent_actions[0]
            if all(a.get("action_type") == first.get("action_type") and 
                   a.get("target") == first.get("target") for a in recent_actions):
                # Stagnant loop detected
                return GoalProgressStatus.STALLED

        # Window focus loop detection
        recent_windows = [h["snapshot"].get("ui_focus", {}).get("window") for h in self.state_history[-3:]]
        if len(recent_windows) >= 3 and len(set(recent_windows)) == 1 and verification.get("status") == "ERROR":
            return GoalProgressStatus.REGRESSING

        return GoalProgressStatus.ON_TRACK

    def reset(self):
        self.state_history.clear()

goal_progress_engine = GoalProgressEngine()
