"""
Phase 35.5 — Smart Recovery: FailureClassifier + RecoveryStrategyRouter

Extends the existing TaskRecoveryController with:
- FailureType enum: 5 classified failure categories
- FailureClassifier: maps (action, result, frames) to FailureType
- RecoveryStrategyRouter: selects recovery strategy per FailureType

PRESERVED (unchanged):
- TaskRecoveryController.attempt_recovery()
- TaskRecoveryController.rollback_files()

SAFETY NOTE:
- Every recovery path that re-executes an action must still call safety_gate.
- This module does NOT execute actions. It classifies and routes.
"""

import os
import time
from typing import Dict, Any, Optional
from core.orchestration.task_state import task_state_controller


# ---------------------------------------------------------------------------
# Failure taxonomy
# ---------------------------------------------------------------------------

class FailureType:
    WRONG_TARGET    = "WRONG_TARGET"     # Grounding identified the wrong element
    ELEMENT_GONE    = "ELEMENT_GONE"     # Element was present at grounding time but gone at execution
    STALE_GROUNDING = "STALE_GROUNDING"  # Cached coordinates no longer valid (UI updated)
    TIMEOUT         = "TIMEOUT"          # App/page did not respond within time window
    BACKEND_ERROR   = "BACKEND_ERROR"    # Desktop controller driver failure
    ACTION_BLOCKED  = "ACTION_BLOCKED"   # Safety gate blocked — requires user confirmation
    FATAL           = "FATAL"            # Unrecoverable — halt and report


class RecoveryStrategy:
    REGROUND_AND_RETRY   = "REGROUND_AND_RETRY"       # Fresh capture + re-ground + re-execute
    REGROUND_ALT_TOOL    = "REGROUND_ALT_TOOL"        # Re-ground using a different tool (DOM→UIA→OCR)
    INVALIDATE_AND_REGROUND = "INVALIDATE_AND_REGROUND"  # Evict grounding cache + re-ground
    WAIT_AND_RETRY       = "WAIT_AND_RETRY"           # Pause then retry same action
    SWITCH_BACKEND       = "SWITCH_BACKEND"           # Change execution backend (UIA→pyautogui)
    SURFACE_TO_USER      = "SURFACE_TO_USER"          # Require user confirmation / guidance
    HALT                 = "HALT"                     # Stop execution, report reason


# ---------------------------------------------------------------------------
# FailureClassifier
# ---------------------------------------------------------------------------

class FailureClassifier:
    """
    Classifies an action failure into a FailureType using available evidence.

    Evidence sources (all optional — degrades gracefully):
    - exec_result dict from DesktopController
    - action_type and target string
    - before_frame and after_frame ScreenFrame objects
    - confidence score from ActionConfidence
    """

    def classify(
        self,
        action_type: str,
        target: str,
        exec_result: Dict[str, Any],
        target_confidence: float = 1.0,
        before_active_window: str = "",
        after_active_window: str = "",
        grounding_from_cache: bool = False,
    ) -> str:
        error_msg = (exec_result.get("error") or exec_result.get("message") or "").lower()
        status = exec_result.get("status", "ERROR")

        # Safety gate interception
        if status == "BLOCKED" or "confirmation" in error_msg or "blocked" in error_msg:
            return FailureType.ACTION_BLOCKED

        # Backend driver crashed
        if "exception" in error_msg or "traceback" in error_msg or "crash" in error_msg:
            return FailureType.BACKEND_ERROR

        # Timeout signals
        if "timeout" in error_msg or "timed out" in error_msg or "not respond" in error_msg:
            return FailureType.TIMEOUT

        # App context vanished between ground and execute
        if before_active_window and after_active_window:
            before_low = before_active_window.lower()
            after_low = after_active_window.lower()
            if before_low and after_low and before_low[:15] != after_low[:15]:
                # Window changed unexpectedly — element likely gone
                return FailureType.ELEMENT_GONE

        # Stale grounding cache hit
        if grounding_from_cache and target_confidence < 0.65:
            return FailureType.STALE_GROUNDING

        # Low confidence on a non-cached grounding → probably wrong target
        if target_confidence < 0.55:
            return FailureType.WRONG_TARGET

        # Element not found / target gone
        if "not found" in error_msg or "element" in error_msg or "target" in error_msg:
            return FailureType.ELEMENT_GONE

        # Generic backend failure
        if status == "ERROR":
            return FailureType.BACKEND_ERROR

        # Cannot classify
        return FailureType.FATAL

    def describe(self, failure_type: str) -> str:
        descriptions = {
            FailureType.WRONG_TARGET:    "Grounding matched the wrong UI element.",
            FailureType.ELEMENT_GONE:    "Target element was present at grounding time but is now gone.",
            FailureType.STALE_GROUNDING: "Cached grounding coordinates are no longer valid.",
            FailureType.TIMEOUT:         "Application or page did not respond within the time window.",
            FailureType.BACKEND_ERROR:   "Desktop controller driver error during execution.",
            FailureType.ACTION_BLOCKED:  "Safety gate intercepted — user confirmation required.",
            FailureType.FATAL:           "Unrecoverable failure — no strategy available.",
        }
        return descriptions.get(failure_type, "Unknown failure type.")


# ---------------------------------------------------------------------------
# RecoveryStrategyRouter
# ---------------------------------------------------------------------------

class RecoveryStrategyRouter:
    """
    Maps a FailureType to the best recovery strategy.

    Callers are responsible for actually executing the strategy.
    This router is a pure decision layer — no side effects.
    """

    _STRATEGY_MAP = {
        FailureType.WRONG_TARGET:    RecoveryStrategy.REGROUND_ALT_TOOL,
        FailureType.ELEMENT_GONE:    RecoveryStrategy.REGROUND_AND_RETRY,
        FailureType.STALE_GROUNDING: RecoveryStrategy.INVALIDATE_AND_REGROUND,
        FailureType.TIMEOUT:         RecoveryStrategy.WAIT_AND_RETRY,
        FailureType.BACKEND_ERROR:   RecoveryStrategy.SWITCH_BACKEND,
        FailureType.ACTION_BLOCKED:  RecoveryStrategy.SURFACE_TO_USER,
        FailureType.FATAL:           RecoveryStrategy.HALT,
    }

    def select_strategy(self, failure_type: str) -> str:
        strategy = self._STRATEGY_MAP.get(failure_type, RecoveryStrategy.HALT)
        print(
            f"[RECOVERY_ROUTER] Failure={failure_type} "
            f"-> Strategy={strategy}"
        )
        return strategy

    def should_retry(self, strategy: str) -> bool:
        """Returns True for strategies that lead to a re-execution attempt."""
        return strategy in (
            RecoveryStrategy.REGROUND_AND_RETRY,
            RecoveryStrategy.REGROUND_ALT_TOOL,
            RecoveryStrategy.INVALIDATE_AND_REGROUND,
            RecoveryStrategy.WAIT_AND_RETRY,
            RecoveryStrategy.SWITCH_BACKEND,
        )

    def needs_user(self, strategy: str) -> bool:
        return strategy == RecoveryStrategy.SURFACE_TO_USER

    def is_halt(self, strategy: str) -> bool:
        return strategy == RecoveryStrategy.HALT

    def get_wait_seconds(self, failure_type: str) -> float:
        """Returns recommended wait before retry (0 = no wait)."""
        waits = {
            FailureType.TIMEOUT: 3.0,
            FailureType.ELEMENT_GONE: 1.5,
            FailureType.BACKEND_ERROR: 1.0,
        }
        return waits.get(failure_type, 0.5)

    def get_adaptive_retry_limit(self, app_name: str, action_type: str, tool: str, default_limit: int = 3) -> int:
        """
        Dynamically adjusts retry limits. If historical success rate is poor (<40%)
        and observations >= 3, reduce limit to 1. If success rate is 0%, reduce to 0.
        """
        try:
            from core.cognition.memory.context_memory import app_action_memory
            success_rate = app_action_memory.get_success_rate(app_name, action_type, tool)
            obs_count = app_action_memory.observation_count(app_name, action_type, tool)
            if obs_count >= 3 and success_rate is not None:
                if success_rate == 0.0:
                    return 0
                elif success_rate < 0.40:
                    return 1
        except Exception as e:
            print(f"[RECOVERY_ROUTER] Error calculating adaptive retry: {e}")
        return default_limit


# ---------------------------------------------------------------------------
# Existing TaskRecoveryController — PRESERVED INTERFACE
# ---------------------------------------------------------------------------

class TaskRecoveryController:
    """Restores plan queues and rollback execution checkpoints on loop errors."""

    def attempt_recovery(self) -> Optional[Dict[str, Any]]:
        """Checks for interrupted tasks and attempts to restore from last checkpoint."""
        state = task_state_controller.get_state()
        if state.get("status") in ["RUNNING", "PLANNING"] and state.get("active_task_id"):
            task_id = state.get("active_task_id")
            print(f"[RECOVERY] Interrupted execution detected for task: {task_id}")

            plan = task_state_controller.load_active_plan()
            for task in plan:
                if task.get("task_id") == task_id:
                    task["status"] = "PENDING"
                    task_state_controller.save_active_plan(plan)
                    task_state_controller.update_state({"status": "PLANNING", "active_task_id": None})
                    print(f"[RECOVERY] Reset task {task_id} back to PENDING status.")
                    return task
        return None

    def rollback_files(self, files_changed: list):
        """Rolls back files if backups exist during checkpoints."""
        for filepath in files_changed:
            backup_path = filepath + ".bak"
            if os.path.exists(backup_path):
                try:
                    os.replace(backup_path, filepath)
                    print(f"[ROLLBACK] Reverted file: {filepath}")
                except Exception as e:
                    print(f"[ROLLBACK] Failed reverting {filepath}: {e}")


# ---------------------------------------------------------------------------
# Module singletons
# ---------------------------------------------------------------------------

task_recovery_controller = TaskRecoveryController()
failure_classifier = FailureClassifier()
recovery_strategy_router = RecoveryStrategyRouter()
