# core/orchestration/action_verifier.py
import time
import os
from typing import Dict, Any, List, Optional

class ActionObservation:
    """Captures a snapshot of structural and visual application state."""
    def __init__(
        self,
        active_window_title: str,
        active_process_name: str,
        active_pid: int,
        dom_context: Optional[Dict[str, Any]] = None,
        uia_context: Optional[List[Dict[str, Any]]] = None,
        ocr_text: str = "",
        visual_hash: str = "",
        timestamp: float = 0.0
    ):
        self.active_window_title = active_window_title
        self.active_process_name = active_process_name
        self.active_pid = active_pid
        self.dom_context = dom_context or {}
        self.uia_context = uia_context or []
        self.ocr_text = ocr_text
        self.visual_hash = visual_hash
        self.timestamp = timestamp or time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "active_window_title": self.active_window_title,
            "active_process_name": self.active_process_name,
            "active_pid": self.active_pid,
            "dom_element_count": len(self.dom_context.get("elements", [])),
            "uia_element_count": len(self.uia_context),
            "ocr_length": len(self.ocr_text),
            "visual_hash": self.visual_hash,
            "timestamp": self.timestamp
        }

class ActionVerifier:
    """Verifies pre-flight preconditions and evaluates expected-state predicates."""

    def evaluate_predicate(self, predicate_type: str, args: List[Any], observation: ActionObservation) -> bool:
        """Evaluates a single state predicate against the active observation."""
        if predicate_type == "window_title_contains":
            pattern = str(args[0]).lower()
            return pattern in observation.active_window_title.lower()
            
        elif predicate_type == "process_active":
            proc_name = str(args[0]).lower()
            return proc_name in observation.active_process_name.lower()
            
        elif predicate_type == "ocr_text_contains":
            substring = str(args[0]).lower()
            return substring in observation.ocr_text.lower()
            
        elif predicate_type == "dom_element_present":
            target_text = str(args[0]).lower()
            elements = observation.dom_context.get("elements", [])
            return any(target_text in str(el.get("text", "")).lower() for el in elements)
            
        elif predicate_type == "file_exists":
            file_path = str(args[0])
            return os.path.exists(file_path)

        return False

    def verify_pre_flight(self, preconditions: Dict[str, Any], observation: ActionObservation) -> bool:
        """Checks all pre-flight guards before an action executes."""
        if not preconditions:
            return True
            
        for predicate_type, args in preconditions.items():
            if not isinstance(args, list):
                args = [args]
            if not self.evaluate_predicate(predicate_type, args, observation):
                print(f"[VERIFIER] Pre-flight guard FAILED for predicate '{predicate_type}' with args {args}")
                return False
                
        print("[VERIFIER] All pre-flight guards passed.")
        return True

    def verify_post_flight(
        self,
        expected_state: Dict[str, Any],
        pre_obs: ActionObservation,
        post_obs: ActionObservation,
        action_execution_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculates verification confidence and classifies post-flight outcome.
        
        Args:
            expected_state: Expected predicates (e.g. {"window_title_contains": "Notepad"})
            pre_obs: ActionObservation before action
            post_obs: ActionObservation after action
            action_execution_result: Raw execution dictionary (e.g. {"status": "SUCCESS" or "BLOCKED"})
        
        Returns:
            {
                "status": "VERIFIED" | "PARTIAL" | "FAILED" | "UNKNOWN" | "SAFETY_BLOCK",
                "confidence": float,
                "detail": str,
                "evidence_matched": Dict[str, bool]
            }
        """
        # 1. Check Safety-Block inputs
        if action_execution_result and action_execution_result.get("status") == "BLOCKED":
            return {
                "status": "SAFETY_BLOCK",
                "confidence": 0.0,
                "detail": "Safety gate blocked execution. Immediate stop required.",
                "evidence_matched": {}
            }

        if not expected_state:
            return {
                "status": "UNKNOWN",
                "confidence": 0.0,
                "detail": "No expected state predicates provided for verification.",
                "evidence_matched": {}
            }

        evidence_matched = {}
        weights = {
            "window_title_contains": 0.3,
            "process_active": 0.2,
            "ocr_text_contains": 0.3,
            "dom_element_present": 0.4,
            "file_exists": 0.5
        }

        total_weight = 0.0
        earned_weight = 0.0

        for predicate, args in expected_state.items():
            if not isinstance(args, list):
                args = [args]
            
            # Map predicate logic
            matched = self.evaluate_predicate(predicate, args, post_obs)
            evidence_matched[predicate] = matched

            weight = weights.get(predicate, 0.2)
            total_weight += weight
            if matched:
                earned_weight += weight

        if total_weight == 0.0:
            return {
                "status": "UNKNOWN",
                "confidence": 0.0,
                "detail": "No valid verification predicates evaluated.",
                "evidence_matched": {}
            }

        confidence = round(earned_weight / total_weight, 3)

        # Classification decision boundaries
        if confidence >= 0.8:
            status = "VERIFIED"
            detail = "Post-flight expectations fully satisfied."
        elif confidence >= 0.4:
            status = "PARTIAL"
            detail = "Post-flight expectations partially met. Re-grounding suggested."
        else:
            status = "FAILED"
            detail = "Post-flight expectations failed check."

        return {
            "status": status,
            "confidence": confidence,
            "detail": detail,
            "evidence_matched": evidence_matched
        }

class ActionDeltaClassifier:
    """Classifies structural and visual differences between pre-action and post-action states."""

    def classify_delta(
        self,
        pre_obs: ActionObservation,
        post_obs: ActionObservation,
        expected_state: Optional[Dict[str, Any]] = None,
        action_execution_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compares pre_obs vs post_obs and outputs normalized delta classifications.
        """
        # 1. Safety Block Protection
        if action_execution_result and action_execution_result.get("status") == "BLOCKED":
            return {
                "category": "UNEXPECTED_CHANGE",
                "score": 0.0,
                "reason_code": "SAFETY_BLOCKED",
                "detail": "Action was blocked by safety kernel. Zero execution delta permitted.",
                "changed_metadata": {}
            }

        # 2. Window/Process delta
        win_title_changed = pre_obs.active_window_title != post_obs.active_window_title
        proc_changed = pre_obs.active_process_name != post_obs.active_process_name or pre_obs.active_pid != post_obs.active_pid

        # 3. DOM delta
        pre_dom_els = pre_obs.dom_context.get("elements", [])
        post_dom_els = post_obs.dom_context.get("elements", [])
        
        pre_dom_map = {el.get("text", ""): el for el in pre_dom_els if el.get("text")}
        post_dom_map = {el.get("text", ""): el for el in post_dom_els if el.get("text")}

        added_dom = [t for t in post_dom_map if t not in pre_dom_map]
        removed_dom = [t for t in pre_dom_map if t not in post_dom_map]

        # 4. UIA delta
        pre_uia_map = {el.get("id", ""): el for el in pre_obs.uia_context if el.get("id")}
        post_uia_map = {el.get("id", ""): el for el in post_obs.uia_context if el.get("id")}

        added_uia = [k for k in post_uia_map if k not in pre_uia_map]
        removed_uia = [k for k in pre_uia_map if k not in post_uia_map]

        # 5. OCR delta
        pre_ocr = pre_obs.ocr_text.strip()
        post_ocr = post_obs.ocr_text.strip()
        
        # Simple similarity: intersection of words / union of words
        pre_words = set(pre_ocr.lower().split())
        post_words = set(post_ocr.lower().split())
        
        ocr_similarity = 1.0
        if pre_words or post_words:
            union_len = len(pre_words.union(post_words))
            ocr_similarity = len(pre_words.intersection(post_words)) / union_len if union_len > 0 else 0.0

        ocr_changed = ocr_similarity < 0.95 and abs(len(pre_ocr) - len(post_ocr)) > 2 # noise filter

        # 6. Visual changes (simulated lazy frame check to respect RTX 3050 VRAM)
        visual_changed = pre_obs.visual_hash != post_obs.visual_hash
        # Filter out minor noise (visual hash mismatch but all structural contents identical)
        if visual_changed and not (win_title_changed or proc_changed or added_dom or removed_dom or added_uia or removed_uia or ocr_changed):
            # No structural or textual changes: classify as visual noise
            visual_changed = False

        # Classify categories
        changed_metadata = {
            "win_title_changed": win_title_changed,
            "proc_changed": proc_changed,
            "added_dom_count": len(added_dom),
            "removed_dom_count": len(removed_dom),
            "added_uia_count": len(added_uia),
            "removed_uia_count": len(removed_uia),
            "ocr_similarity": round(ocr_similarity, 3),
            "visual_changed": visual_changed
        }

        # Check expected matches if provided
        expected_matched = False
        if expected_state:
            weights = {"window_title_contains": 0.3, "process_active": 0.2, "ocr_text_contains": 0.3, "dom_element_present": 0.4}
            earned = 0.0
            total = 0.0
            for pred, args in expected_state.items():
                if not isinstance(args, list):
                    args = [args]
                matched = action_verifier.evaluate_predicate(pred, args, post_obs)
                weight = weights.get(pred, 0.2)
                total += weight
                if matched:
                    earned += weight
            expected_matched = (earned / total >= 0.8) if total > 0 else False

        # Category Decision Logic
        if not (win_title_changed or proc_changed or added_dom or removed_dom or added_uia or removed_uia or ocr_changed or visual_changed):
            category = "NO_CHANGE"
            score = 0.0
            reason_code = "IDENTICAL_STATE"
            detail = "Pre and post observations are identical structurally and visually."
            
        elif expected_matched:
            category = "EXPECTED_CHANGE"
            score = 1.0
            reason_code = "PREDICATES_SATISFIED"
            detail = "Expected post-action state transition verified."
            
        elif proc_changed or win_title_changed or len(added_dom) > 5 or len(added_uia) > 5:
            category = "MAJOR_CHANGE"
            score = 0.8
            reason_code = "STRUCTURAL_SHIFT"
            detail = "Significant window, process, or structural changes observed."
            
        elif ocr_changed or len(added_dom) > 0 or len(removed_dom) > 0 or len(added_uia) > 0 or len(removed_uia) > 0:
            category = "MINOR_CHANGE"
            score = 0.3
            reason_code = "ELEMENTS_MUTATED"
            detail = "Minor DOM or text mutations detected."
            
        else:
            category = "UNEXPECTED_CHANGE"
            score = 0.0
            reason_code = "UNEXPECTED_SHIFT"
            detail = "Unmatched changes occurred without matching expected predicates."

        # Contradiction checks (e.g. DOM says we have elements but OCR is empty or process active change is conflicting)
        if len(added_dom) > 0 and len(post_obs.ocr_text) == 0 and expected_state and "ocr_text_contains" in expected_state:
            category = "CONTRADICTORY_CHANGE"
            reason_code = "EVIDENCE_CONTRADICTION"
            detail = "DOM registers new elements but visual OCR text is completely missing."

        return {
            "category": category,
            "score": score,
            "reason_code": reason_code,
            "detail": detail,
            "changed_metadata": changed_metadata
        }

action_verifier = ActionVerifier()
action_delta_classifier = ActionDeltaClassifier()
