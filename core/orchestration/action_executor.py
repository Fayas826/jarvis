"""
Phase 35.1 — Action Executor
Structured, pre-validated, post-verified action dispatch layer.

DESIGN:
- Sits between ComputerUseAgent decision logic and DesktopController.
- Selects the appropriate backend (native, uia, pyautogui fallback).
- Emits ActionConfidence before execution.
- Captures before/after ScreenFrame for verification.
- Returns a structured ActionResult.

SAFETY NOTE:
- NEVER bypasses safety_gate.
- Safety gate is checked BEFORE this module is called (in ComputerUseAgent).
- This module only handles the execution mechanics after safety approval.
"""

import asyncio
import dataclasses
import time
from typing import Optional, List, Dict, Any, Callable

from core.orchestration.action_confidence import ActionConfidence, ActionConfidenceBuilder, RiskLevel
from core.perception.visual_state import Action, ScreenFrame


# ---------------------------------------------------------------------------
# ActionResult
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class ActionResult:
    """Full execution result including pre/post validation states."""
    action_type: str
    target: str
    success: bool
    pre_validation_passed: bool
    post_verification_passed: bool
    verification_method: str          # "window_title"|"text_check"|"exec_status"|"visual_diff"|"n/a"
    backend_used: str                 # "native"|"uia"|"pyautogui"|"dom"|"os_command"
    latency_ms: float
    confidence: ActionConfidence
    error: Optional[str] = None

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["confidence"] = self.confidence.to_dict()
        return d


# ---------------------------------------------------------------------------
# ActionExecutor
# ---------------------------------------------------------------------------

class ActionExecutor:
    """
    Phase 35.1 structured action dispatch with pre-validation and post-verification.

    Call sequence:
        result = await executor.execute(
            action_type="CLICK",
            target="Save button",
            coords=[800, 400],
            text_payload=None,
            before_frame=frame,
            screen_width=1920,
            screen_height=1080,
            target_confidence=0.94,
            target_source="uia",
            controller_action="UI_AUTOMATION",
            controller_payload={"action": "click", "coords": [800, 400]},
            desktop_controller=desktop_controller,
            screen_capturer=screen_capturer,
        )
    """

    def __init__(self):
        self._backend_priority = ["native", "uia", "dom", "pyautogui"]

    async def execute(
        self,
        action_type: str,
        target: str,
        coords: Optional[List[int]],
        text_payload: Optional[str],
        before_frame: ScreenFrame,
        screen_width: int,
        screen_height: int,
        target_confidence: float,
        target_source: str,
        controller_action: str,
        controller_payload: Dict[str, Any],
        desktop_controller,
        screen_capturer,
        page_loading: bool = False,
    ) -> ActionResult:

        t_start = time.perf_counter()

        # --- 1. Build confidence report ---
        confidence = ActionConfidenceBuilder.build(
            action_type=action_type,
            target=target,
            target_confidence=target_confidence,
            coords=coords,
            screen_width=screen_width,
            screen_height=screen_height,
            target_source=target_source,
            active_window=before_frame.active_window if before_frame else "",
            page_loading=page_loading,
        )

        # --- 2. Pre-validation gate ---
        if not confidence.pre_validation_passed:
            latency = (time.perf_counter() - t_start) * 1000
            print(
                f"[ACTION_EXECUTOR] Pre-validation FAILED for '{target}' "
                f"(conf={confidence.overall_confidence:.2f}). Aborting."
            )
            return ActionResult(
                action_type=action_type,
                target=target,
                success=False,
                pre_validation_passed=False,
                post_verification_passed=False,
                verification_method="n/a",
                backend_used="none",
                latency_ms=latency,
                confidence=confidence,
                error=f"Pre-validation failed: {confidence.reasoning}",
            )

        # --- 3. Execute via DesktopController ---
        backend_used = self._resolve_backend(controller_action)
        print(
            f"[ACTION_EXECUTOR] Executing {action_type} on '{target}' "
            f"via {backend_used} (conf={confidence.overall_confidence:.2f})"
        )

        exec_result: Dict[str, Any] = {"status": "ERROR", "error": "Not attempted"}
        try:
            exec_result = await desktop_controller.execute(controller_action, controller_payload)
        except Exception as e:
            exec_result = {"status": "ERROR", "error": str(e)}

        exec_ok = exec_result.get("status") == "SUCCESS"

        # --- 4. Post-verification ---
        after_frame = None
        verification_method = "exec_status"
        post_ok = False

        if exec_ok and confidence.verification_required:
            try:
                await asyncio.sleep(1.5)   # Allow UI to settle
                after_frame = await screen_capturer.capture_frame_async()
                post_ok, verification_method = self._post_verify(
                    action_type, target, text_payload,
                    before_frame, after_frame, exec_result
                )
            except Exception as e:
                print(f"[ACTION_EXECUTOR] Post-verify capture failed (non-fatal): {e}")
                post_ok = exec_ok
                verification_method = "exec_status"
        elif exec_ok and not confidence.verification_required:
            post_ok = True
            verification_method = "exec_status"
        else:
            post_ok = False
            verification_method = "exec_status"

        latency = (time.perf_counter() - t_start) * 1000
        success = exec_ok and post_ok

        if success:
            print(f"[ACTION_EXECUTOR] SUCCESS: {action_type} '{target}' via {backend_used} ({latency:.0f}ms)")
        else:
            err = exec_result.get("error") or exec_result.get("message") or "Verification failed"
            print(f"[ACTION_EXECUTOR] FAIL: {action_type} '{target}' — {err}")

        return ActionResult(
            action_type=action_type,
            target=target,
            success=success,
            pre_validation_passed=True,
            post_verification_passed=post_ok,
            verification_method=verification_method,
            backend_used=backend_used,
            latency_ms=latency,
            confidence=confidence,
            error=None if success else (exec_result.get("error") or "Verification failed"),
        )

    # ------------------------------------------------------------------
    # Backend resolver
    # ------------------------------------------------------------------

    def _resolve_backend(self, controller_action: str) -> str:
        mapping = {
            "APP_OPEN": "native",
            "OS_COMMAND": "os_command",
            "UI_AUTOMATION": "uia",
            "WINDOW_CONTROL": "uia",
            "FILE_OP": "native",
            "READ_SCREEN": "native",
        }
        return mapping.get(controller_action.upper(), "pyautogui")

    # ------------------------------------------------------------------
    # Post-verification strategies
    # ------------------------------------------------------------------

    def _post_verify(
        self,
        action_type: str,
        target: str,
        text_payload: Optional[str],
        before: ScreenFrame,
        after: ScreenFrame,
        exec_result: Dict,
    ):
        """Returns (success: bool, verification_method: str)."""
        atype = action_type.upper()

        if atype == "OPEN_APP":
            # Active window should now contain the app name
            target_lower = target.lower()
            after_window = (after.active_window or "").lower()
            match = any(word in after_window for word in target_lower.split()[:2])
            return match, "window_title"

        if atype == "TYPE" and text_payload:
            # After typing, active window should still be the same app (didn't crash)
            before_window = (before.active_window or "").lower()
            after_window = (after.active_window or "").lower()
            # Rough heuristic: window didn't change to something unexpected
            same_context = before_window[:20] == after_window[:20]
            return same_context, "text_check"

        if atype == "NAVIGATE":
            # Page title should differ from before
            before_title = (before.active_window or "")
            after_title = (after.active_window or "")
            changed = before_title != after_title
            return changed, "window_title"

        # Default: trust exec_result status
        return exec_result.get("status") == "SUCCESS", "exec_status"


# ---------------------------------------------------------------------------
# Module singleton
# ---------------------------------------------------------------------------

action_executor = ActionExecutor()
