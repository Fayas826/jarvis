"""
Phase 36.6A — Predictive Action Verification
=============================================

Extends the Phase 35 ActionVerifier with:
- Pre-flight expectation prediction (what SHOULD happen)
- Post-flight structured comparison (expected vs actual)
- Classification into 7 states:
    SUCCESS, PARTIAL_SUCCESS, RECOVERABLE_FAILURE,
    ENVIRONMENT_CHANGE, USER_INTERVENTION, SAFETY_BLOCK, UNKNOWN

SAFETY:
- SAFETY_BLOCK is TERMINAL — never passed to recovery manager
- Risk metadata is passed through but never modified here
"""

from typing import Dict, Any, Optional


# ── Verification result classifications ───────────────────────────────────────

class VerificationStatus:
    SUCCESS              = "SUCCESS"
    PARTIAL_SUCCESS      = "PARTIAL_SUCCESS"
    RECOVERABLE_FAILURE  = "RECOVERABLE_FAILURE"
    ENVIRONMENT_CHANGE   = "ENVIRONMENT_CHANGE"
    USER_INTERVENTION    = "USER_INTERVENTION"
    SAFETY_BLOCK         = "SAFETY_BLOCK"
    UNKNOWN              = "UNKNOWN"


class PredictiveActionVerifier:
    """
    Predicts expected post-action state before execution, then compares to actual.
    Returns a structured verification result.
    """

    def predict_expected_state(
        self,
        action_type: str,
        target: str,
        task_node: Dict[str, Any],
        env_snapshot: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build a prediction of what state should exist after this action succeeds.
        Returns a prediction dict used for post-flight comparison.
        """
        prediction: Dict[str, Any] = {
            "action_type": action_type,
            "target": target,
            "expected_window": task_node.get("expected_state", ""),
            "expected_process": env_snapshot.get("ui_focus", {}).get("process", ""),
            "expected_completion_condition": task_node.get("completion_condition", "title_check"),
            "risk_level": task_node.get("risk_level", "LOW"),
        }

        # Predict specific changes based on action type
        if action_type == "OPEN_APP":
            prediction["expected_window_contains"] = target
            prediction["window_should_change"] = True
        elif action_type in ("CLICK", "TYPE"):
            prediction["window_should_change"] = False
            prediction["content_may_change"] = True
        elif action_type == "WAIT":
            prediction["window_should_change"] = False
            prediction["content_may_change"] = False

        return prediction

    def compare(
        self,
        prediction: Dict[str, Any],
        before_title: str,
        after_title: str,
        exec_result: Dict[str, Any],
        delta_evidence: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Compare expected vs actual state and classify the result.
        """
        # 1. Safety block — immediate terminal classification
        exec_status = exec_result.get("status", "")
        exec_error = (exec_result.get("error") or exec_result.get("message") or "").lower()

        if exec_status == "BLOCKED" or "blocked" in exec_error or "safety" in exec_error:
            return self._result(VerificationStatus.SAFETY_BLOCK, prediction,
                                "Safety kernel blocked this action.", before_title, after_title)

        # 2. User intervention signal
        if "user_cancelled" in exec_error or "user_denied" in exec_error:
            return self._result(VerificationStatus.USER_INTERVENTION, prediction,
                                "User cancelled or denied the action.", before_title, after_title)

        # 3. Execution error
        if exec_status == "ERROR" or exec_status == "FAILED":
            return self._result(VerificationStatus.RECOVERABLE_FAILURE, prediction,
                                f"Execution failed: {exec_error}", before_title, after_title)

        # 4. Window changed when it shouldn't have (unexpected env change)
        should_change = prediction.get("window_should_change", False)
        actually_changed = (before_title.lower() != after_title.lower())

        if not should_change and actually_changed:
            return self._result(VerificationStatus.ENVIRONMENT_CHANGE, prediction,
                                f"Window changed unexpectedly: '{before_title}' → '{after_title}'",
                                before_title, after_title)

        # 5. Window should have changed but didn't
        if should_change and not actually_changed:
            expected_contains = prediction.get("expected_window_contains", "")
            if expected_contains and expected_contains.lower() not in after_title.lower():
                return self._result(VerificationStatus.RECOVERABLE_FAILURE, prediction,
                                    f"Expected window '{expected_contains}' not found. Got '{after_title}'",
                                    before_title, after_title)

        # 6. Check delta evidence for partial success
        if delta_evidence:
            delta_type = delta_evidence.get("delta_type", "")
            if delta_type == "PARTIAL_CHANGE":
                return self._result(VerificationStatus.PARTIAL_SUCCESS, prediction,
                                    "Partial structural change detected.", before_title, after_title)

        # 7. Success
        return self._result(VerificationStatus.SUCCESS, prediction,
                            "Action verified successfully.", before_title, after_title)

    def _result(self, status: str, prediction: Dict[str, Any], detail: str,
                before: str, after: str) -> Dict[str, Any]:
        return {
            "status": status,
            "detail": detail,
            "before_title": before,
            "after_title": after,
            "risk_level": prediction.get("risk_level", "LOW"),
            "is_terminal": status == VerificationStatus.SAFETY_BLOCK,
        }


predictive_verifier = PredictiveActionVerifier()
