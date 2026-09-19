import time
from typing import List, Optional
from core.perception.visual_state import ScreenFrame, GUIElement
from core.perception.accessibility import accessibility_provider
from core.perception.ocr import ocr_processor
from core.perception.vlm_grounding import query_vlm_fallback
from core.perception.action_regrounder import ActionRegrounder

class VisionGrounder:
    """Consolidated Grounder resolving targets across browser, accessibility, and OCR engines."""

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

    async def detect_elements(self, screen: ScreenFrame) -> List[GUIElement]:
        """Gathers GUI candidates matching unified screen space grids."""
        elements = []
        elements.extend(self._detect_dom_elements(screen))
        elements.extend(self._detect_uia_elements())
        elements.extend(await self._detect_ocr_elements(screen))
        elements.extend(self._detect_cv_elements(screen))
        return elements

    async def find_target(self, screen: ScreenFrame, instruction: str) -> Optional[GUIElement]:
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
        vlm_element = await query_vlm_fallback(screen, instruction, cv_elements)
        if vlm_element and self._validate_coordinates(vlm_element.center, screen):
            return vlm_element

        return None

    def _score_and_select(self, elements: List[GUIElement], instruction: str, screen: ScreenFrame, min_confidence: float) -> Optional[GUIElement]:
        scored_candidates = []
        for el in elements:
            if not el.visible or el.center == [0, 0] or el.center[0] > screen.width or el.center[1] > screen.height:
                continue

            semantic_match = 1.0 if instruction.lower() == el.text.lower() else (0.8 if instruction.lower() in el.text.lower() or el.text.lower() in instruction.lower() else 0.0)
            role_match = 0.5 if el.role in ["button", "link", "clickable_container"] else 0.2
            spatial_match = 0.3 if el.center != [0, 0] else 0.0
            
            source_reliability = 1.0
            if el.source == "dom": source_reliability = 1.0
            elif el.source in ["accessibility", "uia"]: source_reliability = 0.98
            elif el.source == "ocr": source_reliability = 0.90
            elif el.source == "cv_segmenter": source_reliability = 0.85

            visibility = 0.5 if el.visible else 0.0
            application_match = 0.5

            final_score = (semantic_match + role_match + spatial_match + source_reliability + visibility + application_match) * el.confidence

            if final_score >= 1.5:
                evidence_dict = {
                    "semantic_match": semantic_match,
                    "role_match": role_match,
                    "source_reliability": source_reliability,
                    "visible": el.visible,
                    "center_valid": el.center != [0, 0]
                }
                scored_candidates.append((final_score, el, evidence_dict))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)

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

    def _validate_coordinates(self, center: List[int], screen: ScreenFrame) -> bool:
        if not center or len(center) < 2: return False
        cx, cy = center[0], center[1]
        if cx < 5 or cy < 5 or cx > screen.width - 5 or cy > screen.height - 5: return False
        if (cx < 15 and cy < 15) or (cx > screen.width - 15 and cy > screen.height - 15): return False
        return True

    async def ground_target(self, screen: ScreenFrame, target_name: str) -> Optional[List[int]]:
        element = await self.find_target(screen, target_name)
        if element and element.confidence >= 0.50:
            return element.center
        return None

    def get_bbox(self, element: GUIElement) -> List[int]:
        return element.bbox

vision_grounder = VisionGrounder()
action_regrounder = ActionRegrounder(vision_grounder)
