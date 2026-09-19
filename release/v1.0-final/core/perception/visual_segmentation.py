import cv2
import numpy as np
import base64
from typing import List
from core.perception.visual_state import GUIElement

class VisualSegmenter:
    """Lightweight OpenCV-based Local UI Element Segmentation Engine."""

    def segment_elements(self, image_b64: str) -> List[GUIElement]:
        elements = []
        try:
            # Decode image from base64
            img_data = base64.b64decode(image_b64)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return elements

            # Preprocessing: convert to grayscale and apply adaptive thresholding
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            idx = 0
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                
                # Filter out too small/large contours to isolate buttons/textboxes
                if 20 < w < 400 and 15 < h < 100:
                    cx = x + w // 2
                    cy = y + h // 2
                    
                    elements.append(
                        GUIElement(
                            element_id=f"cv_segment_{idx}",
                            element_type="button_like",
                            text=f"VisualElement_{idx}",
                            role="clickable_container",
                            bbox=[x, y, x + w, y + h],
                            center=[cx, cy],
                            confidence=0.85,
                            clickable=True,
                            visible=True,
                            source="cv_segmenter"
                        )
                    )
                    idx += 1
                    if idx >= 30:  # Cap at 30 elements
                        break
        except Exception as e:
            print(f"[CV_SEGMENTER] Elements segmentation failed: {e}")

        return elements

visual_segmenter = VisualSegmenter()
