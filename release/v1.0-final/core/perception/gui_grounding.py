import time
from typing import List, Dict, Any, Optional
from core.perception.visual_state import ScreenFrame, GUIElement
from core.perception.accessibility import accessibility_provider
from core.perception.ocr import ocr_processor
from core.cognition.reasoning.brain import brain

import time
import os
import base64
from typing import List, Dict, Any, Optional
from core.perception.visual_state import ScreenFrame, GUIElement
from core.perception.accessibility import accessibility_provider
from core.perception.ocr import ocr_processor
from core.cognition.reasoning.brain import brain

class VisionGrounder:
    """Consolidated Grounder resolving targets across browser, accessibility, and OCR engines."""

    # ---------------------------------------------------------------------------
    # Source-specific candidate detectors (Lazy evaluation support)
    # ---------------------------------------------------------------------------

    def _detect_dom_elements(self, screen: ScreenFrame) -> List[GUIElement]:
        elements = []
        if screen.browser_context and "elements" in screen.browser_context:
            for idx, el in enumerate(screen.browser_context["elements"]):
                elements.append(
                    GUIElement(
                        element_id=f"dom_{idx}",
                        element_type=el.get("type", "element"),
                        text=el.get("text", ""),
                        role=el.get("role", "button"),
                        bbox=el.get("bbox", [0, 0, 0, 0]),
                        center=el.get("center", [0, 0]),
                        confidence=1.0,
                        clickable=el.get("clickable", True),
                        source="dom"
                    )
                )
        return elements

    def _detect_uia_elements(self) -> List[GUIElement]:
        try:
            return accessibility_provider.get_visible_elements()
        except Exception as e:
            print(f"[GROUNDER] Accessibility scan fail: {e}")
            return []

    async def _detect_ocr_elements(self, screen: ScreenFrame) -> List[GUIElement]:
        elements = []
        try:
            ocr_blocks = await ocr_processor.extract_text_blocks(screen.image)
            for idx, b in enumerate(ocr_blocks):
                elements.append(
                    GUIElement(
                        element_id=f"ocr_{idx}",
                        element_type="text",
                        text=b["text"],
                        role="text_block",
                        bbox=b["bbox"],
                        center=b["center"],
                        confidence=b.get("confidence", 0.90),
                        source="ocr"
                    )
                )
        except Exception as e:
            print(f"[GROUNDER] OCR text scan fail: {e}")
        return elements

    def _detect_cv_elements(self, screen: ScreenFrame) -> List[GUIElement]:
        try:
            from core.perception.visual_segmentation import visual_segmenter
            return visual_segmenter.segment_elements(screen.image)
        except Exception as e:
            print(f"[GROUNDER] OpenCV elements segmentation fail: {e}")
            return []

    # ---------------------------------------------------------------------------
    # Legacy detect_elements (preserved for backward compatibility)
    # ---------------------------------------------------------------------------

    async def detect_elements(self, screen: ScreenFrame) -> List[GUIElement]:
        """Gathers GUI candidates matching unified screen space grids."""
        elements = []
        elements.extend(self._detect_dom_elements(screen))
        elements.extend(self._detect_uia_elements())
        elements.extend(await self._detect_ocr_elements(screen))
        elements.extend(self._detect_cv_elements(screen))
        return elements

    # ---------------------------------------------------------------------------
    # Main Lazy Target Match Cascade
    # ---------------------------------------------------------------------------

    async def find_target(self, screen: ScreenFrame, instruction: str) -> Optional[GUIElement]:
        """
        Resolves target candidates matching instructions using lazy-evaluation sequence:
        DOM -> UIA -> OCR -> CV -> VLM fallback.
        """
        # Step 1: Try DOM-first
        dom_elements = self._detect_dom_elements(screen)
        winner = self._score_and_select(dom_elements, instruction, screen, min_confidence=0.70)
        if winner:
            print(f"[GROUNDER] Target '{instruction}' matched immediately via DOM (lazy evaluation).")
            return winner

        # Step 2: Try UIA-second
        uia_elements = self._detect_uia_elements()
        winner = self._score_and_select(uia_elements, instruction, screen, min_confidence=0.70)
        if winner:
            print(f"[GROUNDER] Target '{instruction}' matched via UIA (lazy evaluation).")
            return winner

        # Step 3: Try OCR-third
        ocr_elements = await self._detect_ocr_elements(screen)
        winner = self._score_and_select(ocr_elements, instruction, screen, min_confidence=0.70)
        if winner:
            print(f"[GROUNDER] Target '{instruction}' matched via OCR (lazy evaluation).")
            return winner

        # Step 4: Try CV-fourth
        cv_elements = self._detect_cv_elements(screen)
        winner = self._score_and_select(cv_elements, instruction, screen, min_confidence=0.60)
        if winner:
            print(f"[GROUNDER] Target '{instruction}' matched via CV Segmenter (lazy evaluation).")
            return winner

        # Step 5: If all local matches are poor, run VLM fallback
        print(f"[GROUNDER] Local scans resolved no confident candidates. Falling back to VLM.")
        vlm_element = await self._query_vlm_fallback(screen, instruction)
        if vlm_element and self._validate_coordinates(vlm_element.center, screen):
            return vlm_element

        return None

    # ──────────────────────────────────────────────────────────────────────────
    # Internal scoring engine
    # ──────────────────────────────────────────────────────────────────────────

    def _score_and_select(self, elements: List[GUIElement], instruction: str, screen: ScreenFrame, min_confidence: float) -> Optional[GUIElement]:
        scored_candidates = []
        for el in elements:
            # Check coordinate sanity
            if not el.visible or el.center == [0, 0] or el.center[0] > screen.width or el.center[1] > screen.height:
                continue

            # Semantic match
            semantic_match = 0.0
            target_str = instruction.lower()
            element_str = el.text.lower()
            if target_str == element_str:
                semantic_match = 1.0
            elif target_str in element_str or element_str in target_str:
                semantic_match = 0.8

            # Role match
            role_match = 0.5 if el.role in ["button", "link", "clickable_container"] else 0.2

            # Spatial match
            spatial_match = 0.3 if el.center != [0, 0] else 0.0

            # Source reliability weights
            source_reliability = 1.0
            if el.source == "dom":
                source_reliability = 1.0
            elif el.source == "accessibility" or el.source == "uia":
                source_reliability = 0.98
            elif el.source == "ocr":
                source_reliability = 0.90
            elif el.source == "cv_segmenter":
                source_reliability = 0.85

            # Visibility match
            visibility = 0.5 if el.visible else 0.0

            # Application match context
            application_match = 0.5

            final_score = (
                semantic_match 
                + role_match 
                + spatial_match 
                + source_reliability 
                + visibility 
                + application_match
            ) * (el.confidence)

            if final_score >= 1.5:
                evidence_dict = {
                    "semantic_match": semantic_match,
                    "role_match": role_match,
                    "source_reliability": source_reliability,
                    "visible": el.visible,
                    "center_valid": el.center != [0, 0]
                }
                scored_candidates.append((final_score, el, evidence_dict))

        # Sort by score desc
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        # Deduplicate candidates sharing identical coordinates
        seen_centers = set()
        dedup_candidates = []
        for score, el, evidence in scored_candidates:
            center_key = (round(el.center[0], 1), round(el.center[1], 1))
            if center_key not in seen_centers:
                seen_centers.add(center_key)
                dedup_candidates.append((score, el, evidence))
        scored_candidates = dedup_candidates

        if scored_candidates:
            top_score, el, evidence = scored_candidates[0]
            confidence = top_score / 3.8
            if confidence >= min_confidence:
                el.confidence = confidence
                el.evidence = evidence
                return el
        return None

    # ──────────────────────────────────────────────────────────────────────────
    # VLMFallback & Coordinate Validation
    # ──────────────────────────────────────────────────────────────────────────

    async def _query_vlm_fallback(self, screen: ScreenFrame, instruction: str) -> Optional[GUIElement]:
        temp_path = "data/temp/ground_target.png"
        os.makedirs("data/temp", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(base64.b64decode(screen.image))

        prompt = (
            f"Locate target element matching: '{instruction}'\n"
            "Identify visual boundaries. Return JSON only:\n"
            "{\n"
            "  \"found\": true,\n"
            "  \"bbox\": [x1, y1, x2, y2],\n"
            "  \"center\": [cx, cy],\n"
            "  \"confidence\": 0.8\n"
            "}"
        )

        try:
            res = await brain.get_ai_response(prompt, image_path=temp_path)
            if res.get("found"):
                el = GUIElement(
                    element_id="vlm_target",
                    element_type="vision_element",
                    text=instruction,
                    role="target",
                    bbox=res.get("bbox", [0, 0, 0, 0]),
                    center=res.get("center", [0, 0]),
                    confidence=res.get("confidence", 0.75),
                    source="vision"
                )
                el.evidence = {"vlm_fallback": True}
                return el
        except Exception as e:
            print(f"[GROUNDER] VLM fallback query fail: {e}")
        return None

    def _validate_coordinates(self, center: List[int], screen: ScreenFrame) -> bool:
        """Ensures coordinates lie within active screen resolution and not in extreme deadzones."""
        if not center or len(center) < 2:
            return False
        cx, cy = center[0], center[1]
        if cx < 5 or cy < 5 or cx > screen.width - 5 or cy > screen.height - 5:
            print(f"[GROUNDER] Rejected coordinates {center} (out of screen bounds).")
            return False
        # Avoid extreme corner deadzones which indicate grounding failures
        if (cx < 15 and cy < 15) or (cx > screen.width - 15 and cy > screen.height - 15):
            print(f"[GROUNDER] Rejected coordinates {center} (corner deadzone).")
            return False
        return True

    # ──────────────────────────────────────────────────────────────────────────
    # Existing API contracts preserved
    # ──────────────────────────────────────────────────────────────────────────

    async def ground_target(self, screen: ScreenFrame, target_name: str) -> Optional[List[int]]:
        element = await self.find_target(screen, target_name)
        if element and element.confidence >= 0.50:
            return element.center
        return None

    def get_bbox(self, element: GUIElement) -> List[int]:
        return element.bbox

class ActionRegrounder:
    """Orchestrates dynamic localized re-grounding when target state becomes stale."""

    def __init__(self, max_attempts: int = 3):
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
            
            new_target = await vision_grounder.find_target(screen, instruction)
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

vision_grounder = VisionGrounder()
action_regrounder = ActionRegrounder()
