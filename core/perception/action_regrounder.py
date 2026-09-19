from typing import Dict, Any, Optional
from core.perception.visual_state import ScreenFrame, GUIElement

class ActionRegrounder:
    """Orchestrates dynamic localized re-grounding when target state becomes stale."""

    def __init__(self, vision_grounder, max_attempts: int = 3):
        self.vision_grounder = vision_grounder
        self.max_attempts = max_attempts
        self._history_centers = []

    async def attempt_reground(
        self,
        instruction: str,
        screen: ScreenFrame,
        pre_element: Optional[GUIElement] = None,
        delta_metadata: Optional[Dict[str, Any]] = None,
        action_execution_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Main re-grounding controller. Returns structured recovery classification.
        """
        # 1. Safety Block Protection
        if action_execution_result and action_execution_result.get("status") == "BLOCKED":
            return {
                "status": "SAFETY_BLOCK",
                "element": None,
                "detail": "Safety kernel blocked action execution."
            }

        # 2. Check if regrounding is required
        reground_needed = False
        reason = "Target matches current state."

        if pre_element is None:
            reground_needed = True
            reason = "Pre-action element target is missing."
        elif delta_metadata:
            # Detect stale criteria
            if delta_metadata.get("win_title_changed"):
                reground_needed = True
                reason = "Active window title changed, invalidating coordinates."
            elif delta_metadata.get("proc_changed"):
                reground_needed = True
                reason = "Active process context transitioned."
            elif delta_metadata.get("added_dom_count", 0) > 0 or delta_metadata.get("removed_dom_count", 0) > 0:
                reground_needed = True
                reason = "DOM tree structure modified."
            elif delta_metadata.get("added_uia_count", 0) > 0 or delta_metadata.get("removed_uia_count", 0) > 0:
                reground_needed = True
                reason = "UIA accessibility tree changed."
            elif delta_metadata.get("ocr_similarity", 1.0) < 0.85:
                reground_needed = True
                reason = "Visual OCR text layout shifted significantly."

        if not reground_needed:
            return {
                "status": "NO_REGROUND_REQUIRED",
                "element": pre_element,
                "detail": reason
            }

        # 3. Perform localized re-grounding cascade
        attempts = 0
        while attempts < self.max_attempts:
            attempts += 1
            print(f"[RE-GROUNDER] Attempt {attempts}/{self.max_attempts} to locate '{instruction}'")
            
            new_target = await self.vision_grounder.find_target(screen, instruction)
            if new_target is None:
                continue

            # Oscillation prevention check
            if new_target.center in self._history_centers:
                print(f"[RE-GROUNDER] Oscillation detected on center {new_target.center}. Rejecting target.")
                return {
                    "status": "REGROUND_AMBIGUOUS",
                    "element": None,
                    "detail": f"Target coordinates {new_target.center} oscillated."
                }
            self._history_centers.append(new_target.center)

            # Target comparison with original
            if pre_element:
                text_match = new_target.text.lower() == pre_element.text.lower()
                role_match = new_target.role == pre_element.role
                
                if text_match and role_match:
                    return {
                        "status": "REGROUND_SUCCESS",
                        "element": new_target,
                        "detail": f"Target resolved successfully at {new_target.center}."
                    }
                elif text_match or role_match:
                    return {
                        "status": "REGROUND_PARTIAL",
                        "element": new_target,
                        "detail": "Target matched partially on text or role role type."
                    }
            else:
                # No pre-element, return success if confidence is high
                if new_target.confidence >= 0.70:
                    return {
                        "status": "REGROUND_SUCCESS",
                        "element": new_target,
                        "detail": f"Target resolved successfully at {new_target.center}."
                    }

        return {
            "status": "REGROUND_FAILED",
            "element": None,
            "detail": "Localized re-grounding exceeded maximum attempts."
        }
