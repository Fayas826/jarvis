"""
Phase 35.3 — Action Confidence Model
Provides a structured per-action confidence report surfaced before execution.

DESIGN:
- Pure data layer: no I/O, no execution, no side effects.
- ActionConfidenceBuilder assembles the report from grounding evidence.
- Risk classification is deterministic and rule-based.
- This module is the shared vocabulary for ActionExecutor (35.1) and
  FailureClassifier (35.5).

SAFETY NOTE:
- This module never executes actions.
- It never overrides safety policy.
- HIGH-risk actions flagged here still go through the Safety Kernel.
"""

import dataclasses
import time
from typing import Optional, List


# ---------------------------------------------------------------------------
# Risk levels
# ---------------------------------------------------------------------------

class RiskLevel:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# HIGH-risk action patterns — these require confirmation gate
_HIGH_RISK_ACTIONS = frozenset({
    "CLOSE_APP", "DELETE_FILE", "FORMAT", "SHUTDOWN", "RESTART",
    "OS_COMMAND", "FILE_OP_DELETE", "FILE_OP_OVERWRITE",
})

# MEDIUM-risk action patterns
_MEDIUM_RISK_ACTIONS = frozenset({
    "CLICK", "TYPE", "OPEN_APP", "KEYBOARD", "DRAG", "RIGHT_CLICK",
    "NAVIGATE", "SUBMIT", "FILE_OP_CREATE", "FILE_OP_WRITE",
})

# LOW-risk
_LOW_RISK_ACTIONS = frozenset({
    "READ_SCREEN", "SCROLL", "WAIT", "MOVE", "SCREENSHOT",
    "HOVER", "FOCUS",
})

# Verification requirement by risk level
_VERIFICATION_REQUIRED = {
    RiskLevel.HIGH: True,
    RiskLevel.MEDIUM: True,
    RiskLevel.LOW: False,
}


# ---------------------------------------------------------------------------
# Core data model
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class ActionConfidence:
    """
    Structured confidence report for a single action before execution.

    Fields
    ------
    action_type         : str — e.g. "CLICK", "TYPE", "OPEN_APP"
    target              : str — human-readable target description
    target_confidence   : float — 0.0–1.0, from grounding layer
    coordinate_validity : str — "PASS" | "FAIL" | "WARNING" | "N/A"
    target_source       : str — "dom" | "uia" | "ocr" | "vlm" | "recipe" | "none"
    page_stability      : str — "STABLE" | "LOADING" | "UNKNOWN"
    risk_level          : str — "LOW" | "MEDIUM" | "HIGH"
    verification_required: bool
    pre_validation_passed: bool
    overall_confidence  : float — composite 0.0–1.0
    reasoning           : str — human-readable summary
    built_at            : float — unix timestamp
    """
    action_type: str
    target: str
    target_confidence: float
    coordinate_validity: str
    target_source: str
    page_stability: str
    risk_level: str
    verification_required: bool
    pre_validation_passed: bool
    overall_confidence: float
    reasoning: str
    built_at: float = dataclasses.field(default_factory=time.time)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    def is_safe_to_execute(self, min_confidence: float = 0.70) -> bool:
        """Returns True if overall confidence meets the threshold and pre-validation passed."""
        return self.pre_validation_passed and self.overall_confidence >= min_confidence

    def summary_line(self) -> str:
        return (
            f"Action={self.action_type} target='{self.target}' "
            f"conf={self.overall_confidence:.2f} risk={self.risk_level} "
            f"source={self.target_source} verify={self.verification_required} "
            f"pre_ok={self.pre_validation_passed}"
        )


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------

class ActionConfidenceBuilder:
    """
    Assembles an ActionConfidence from grounding evidence and action metadata.

    Usage:
        report = ActionConfidenceBuilder.build(
            action_type="CLICK",
            target="Save button",
            target_confidence=0.94,
            coords=[100, 200],
            screen_width=1920,
            screen_height=1080,
            target_source="uia",
            active_window="Notepad",
        )
    """

    @staticmethod
    def build(
        action_type: str,
        target: str,
        target_confidence: float,
        coords: Optional[List[int]],
        screen_width: int,
        screen_height: int,
        target_source: str = "none",
        active_window: str = "",
        page_loading: bool = False,
    ) -> ActionConfidence:

        # --- Risk level ---
        action_upper = action_type.upper()
        if action_upper in _HIGH_RISK_ACTIONS:
            risk = RiskLevel.HIGH
        elif action_upper in _MEDIUM_RISK_ACTIONS:
            risk = RiskLevel.MEDIUM
        else:
            risk = RiskLevel.LOW

        # --- Coordinate validity ---
        coord_validity = ActionConfidenceBuilder._check_coords(
            coords, screen_width, screen_height, action_type
        )

        # --- Page stability ---
        if page_loading:
            stability = "LOADING"
        elif active_window:
            stability = "STABLE"
        else:
            stability = "UNKNOWN"

        # --- Pre-validation: passes if coords valid (when needed) and confidence >= 0.50 ---
        needs_coords = action_type.upper() in ("CLICK", "TYPE", "MOVE", "DRAG", "HOVER")
        if needs_coords:
            pre_ok = (coord_validity == "PASS") and (target_confidence >= 0.50)
        else:
            pre_ok = target_confidence >= 0.30

        # --- Composite confidence ---
        # Penalise missing/invalid coords for actions that need them
        composite = target_confidence
        if needs_coords and coord_validity == "FAIL":
            composite = composite * 0.30
        elif needs_coords and coord_validity == "WARNING":
            composite = composite * 0.75
        if stability == "LOADING":
            composite = composite * 0.80
        composite = round(min(1.0, max(0.0, composite)), 4)

        # --- Verification required ---
        verify_required = _VERIFICATION_REQUIRED.get(risk, True)

        # --- Reasoning string ---
        reasoning = ActionConfidenceBuilder._build_reasoning(
            action_type, target, target_confidence, coord_validity,
            target_source, risk, pre_ok, composite
        )

        print(
            f"[ACTION_CONFIDENCE] {action_type} '{target[:40]}' "
            f"conf={composite:.2f} risk={risk} src={target_source} "
            f"coord={coord_validity} pre_ok={pre_ok}"
        )

        return ActionConfidence(
            action_type=action_type,
            target=target,
            target_confidence=target_confidence,
            coordinate_validity=coord_validity,
            target_source=target_source,
            page_stability=stability,
            risk_level=risk,
            verification_required=verify_required,
            pre_validation_passed=pre_ok,
            overall_confidence=composite,
            reasoning=reasoning,
        )

    @staticmethod
    def _check_coords(
        coords: Optional[List[int]],
        screen_width: int,
        screen_height: int,
        action_type: str,
    ) -> str:
        needs_coords = action_type.upper() in ("CLICK", "TYPE", "MOVE", "DRAG", "HOVER")
        if not needs_coords:
            return "N/A"
        if not coords or len(coords) < 2:
            return "FAIL"
        x, y = coords[0], coords[1]
        # Must be within screen bounds with 5px margin
        if x < 5 or y < 5 or x > screen_width - 5 or y > screen_height - 5:
            return "FAIL"
        # Warn if coords are in extreme corners (often misgrounded)
        if (x < 20 and y < 20) or (x > screen_width - 20 and y > screen_height - 20):
            return "WARNING"
        return "PASS"

    @staticmethod
    def _build_reasoning(
        action_type: str, target: str, target_confidence: float,
        coord_validity: str, target_source: str,
        risk: str, pre_ok: bool, composite: float,
    ) -> str:
        parts = [
            f"Grounding confidence: {target_confidence:.0%} via {target_source}.",
            f"Coordinate validity: {coord_validity}.",
            f"Risk level: {risk}.",
        ]
        if not pre_ok:
            parts.append("Pre-validation FAILED — action should not proceed.")
        else:
            parts.append(f"Overall execution confidence: {composite:.0%}.")
        return " ".join(parts)
