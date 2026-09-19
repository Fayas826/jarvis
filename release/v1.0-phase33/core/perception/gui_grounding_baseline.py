import time
from typing import List, Dict, Any, Optional
from core.perception.visual_state import ScreenFrame, GUIElement
from core.perception.accessibility import accessibility_provider
from core.perception.ocr import ocr_processor
from core.cognition.reasoning.brain import brain

class VisionGrounder:
    """Consolidated Grounder resolving targets across browser, accessibility, and OCR engines."""

    async def detect_elements(self, screen: ScreenFrame) -> List[GUIElement]:
        """Gathers GUI candidates matching unified screen space grids."""
        elements = []
        
        # Source Priority 1: Browser DOM candidates
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

        # Source Priority 2: Windows UI Automation Accessibility nodes
        try:
            uia_elements = accessibility_provider.get_visible_elements()
            elements.extend(uia_elements)
        except Exception as e:
            print(f"[GROUNDER] Accessibility scan fail: {e}")

        # Source Priority 3: Local OCR text elements
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

        # Source Priority 4: OpenCV local visual segmentation candidates
        try:
            from core.perception.visual_segmentation import visual_segmenter
            cv_elements = visual_segmenter.segment_elements(screen.image)
            elements.extend(cv_elements)
        except Exception as e:
            print(f"[GROUNDER] OpenCV elements segmentation fail: {e}")

        return elements

    async def find_target(self, screen: ScreenFrame, instruction: str) -> Optional[GUIElement]:
        """Resolves target candidates matching instructions using ranking score matrices with confidence evidence and ambiguity checks."""
        elements = await self.detect_elements(screen)
        
        scored_candidates = []
        for el in elements:
            # Check coordinate sanity
            if not el.visible or el.center == [0, 0] or el.center[0] > screen.width or el.center[1] > screen.height:
                continue
                
            # Semantic match (0.0 to 1.0)
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
            
            # Total score calculation
            final_score = (
                semantic_match 
                + role_match 
                + spatial_match 
                + source_reliability 
                + visibility 
                + application_match
            ) * (el.confidence)
            
            # Normalize total range
            if final_score >= 1.5:
                # Store candidate with score and granular evidence metrics
                evidence_dict = {
                    "semantic_match": semantic_match,
                    "role_match": role_match,
                    "source_reliability": source_reliability,
                    "visible": el.visible,
                    "center_valid": el.center != [0, 0]
                }
                scored_candidates.append((final_score, el, evidence_dict))

        # Sort by ranked match metrics
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        # Ambiguity Check: If top two candidates are extremely close in score
        if len(scored_candidates) > 1:
            diff = scored_candidates[0][0] - scored_candidates[1][0]
            if diff < 0.05:
                print(f"[GROUNDER] [AMBIGUITY] Plausible duplicate targets detected for: '{instruction}'. Resolving via priority...")
                # Prioritize DOM over UIA over OCR fallback
                if scored_candidates[1][1].source == "dom" and scored_candidates[0][1].source != "dom":
                    # Swap order to favor DOM candidate
                    scored_candidates[0], scored_candidates[1] = scored_candidates[1], scored_candidates[0]
        
        if scored_candidates:
            winner = scored_candidates[0][1]
            winner.confidence = scored_candidates[0][0] / 3.8 # normalize confidence score
            winner.evidence = scored_candidates[0][2]
            print(f"[GROUNDER] Target '{instruction}' matched to: '{winner.text}' via source: {winner.source} (confidence: {winner.confidence:.2f})")
            return winner

        # Source Priority 4: Visual Grounding Fallback via VLM
        print(f"[GROUNDER] Local scans resolved no candidates. Falling back to VLM coordinate prompting.")
        temp_path = "data/temp/ground_target.png"
        import os, base64
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

    async def ground_target(self, screen: ScreenFrame, target_name: str) -> Optional[List[int]]:
        element = await self.find_target(screen, target_name)
        if element and element.confidence >= 0.50:
            return element.center
        return None

    def get_bbox(self, element: GUIElement) -> List[int]:
        return element.bbox

vision_grounder = VisionGrounder()
