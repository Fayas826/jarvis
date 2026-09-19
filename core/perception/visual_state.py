import time
from typing import List, Dict, Any, Optional

class GUIElement:
    """Normalized representation of a GUI element detected via DOM, OCR, or Vision."""
    def __init__(
        self,
        element_id: str,
        element_type: str,
        text: str,
        role: str,
        bbox: List[int], # [x1, y1, x2, y2]
        center: List[int], # [cx, cy]
        confidence: float = 1.0,
        clickable: bool = True,
        visible: bool = True,
        source: str = "vision" # dom, accessibility, ocr, vision
    ):
        self.id = element_id
        self.type = element_type
        self.text = text
        self.role = role
        self.bbox = bbox
        self.center = center
        self.confidence = confidence
        self.clickable = clickable
        self.visible = visible
        self.source = source

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "text": self.text,
            "role": self.role,
            "bbox": self.bbox,
            "center": self.center,
            "confidence": self.confidence,
            "clickable": self.clickable,
            "visible": self.visible,
            "source": self.source
        }

class ScreenFrame:
    """Normalized snapshot model representing a captured tactical frame (Phase 2)."""
    def __init__(
        self,
        image_b64: str,
        width: int,
        height: int,
        dpi_scale: float = 1.0,
        active_window: str = "Unknown",
        app_name: str = "Unknown",
        window_bounds: Optional[List[int]] = None,
        browser_context: Optional[Dict[str, Any]] = None,
        dom_elements: Optional[List[Dict[str, Any]]] = None,
        uia_elements: Optional[List[Dict[str, Any]]] = None,
        ocr_elements: Optional[List[Dict[str, Any]]] = None,
        cv_elements: Optional[List[Dict[str, Any]]] = None,
        vlm_elements: Optional[List[Dict[str, Any]]] = None,
        cursor_position: Optional[List[int]] = None
    ):
        self.screenshot = image_b64
        self.image = image_b64
        self.width = width
        self.height = height
        self.dpi_scale = dpi_scale
        self.active_window = active_window
        self.app_name = app_name
        self.window_bounds = window_bounds or []
        self.browser_context = browser_context or {}
        self.dom_elements = dom_elements or []
        self.uia_elements = uia_elements or []
        self.ocr_elements = ocr_elements or []
        self.cv_elements = cv_elements or []
        self.vlm_elements = vlm_elements or []
        self.cursor_position = cursor_position or [0, 0]
        self.timestamp = time.time()
        
        # Legacy mappings
        self.ocr = ocr_elements or []
        self.gui_elements = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "screenshot": self.screenshot,
            "image": self.image,
            "width": self.width,
            "height": self.height,
            "dpi_scale": self.dpi_scale,
            "active_window": self.active_window,
            "app_name": self.app_name,
            "window_bounds": self.window_bounds,
            "browser_context": self.browser_context,
            "dom_elements": self.dom_elements,
            "uia_elements": self.uia_elements,
            "ocr_elements": self.ocr_elements,
            "cv_elements": self.cv_elements,
            "vlm_elements": self.vlm_elements,
            "cursor_position": self.cursor_position,
            "timestamp": self.timestamp
        }

class Action:
    """Normalized action model representing instructions dispatched to hardware/drivers."""
    def __init__(
        self,
        action_type: str, # CLICK, TYPE, SCROLL, MOVE, KEYPRESS, HOTKEY, OPEN_APP, CLOSE_APP, DRAG, SELECT, WAIT
        target: str,
        coords: Optional[List[int]] = None,
        selector: Optional[str] = None,
        text_payload: Optional[str] = None,
        confidence: float = 1.0,
        safety_level: str = "MEDIUM" # LOW, MEDIUM, HIGH
    ):
        self.action_type = action_type
        self.target = target
        self.coords = coords
        self.selector = selector
        self.text_payload = text_payload
        self.confidence = confidence
        self.safety_level = safety_level
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type,
            "target": self.target,
            "coords": self.coords,
            "selector": self.selector,
            "text_payload": self.text_payload,
            "confidence": self.confidence,
            "safety_level": self.safety_level,
            "timestamp": self.timestamp
        }

class ActionResult:
    """Normalized results of an action dispatch execution loop."""
    def __init__(
        self,
        action: Action,
        success: bool,
        before_state: ScreenFrame,
        after_state: Optional[ScreenFrame] = None,
        error: Optional[str] = None
    ):
        self.action = action
        self.success = success
        self.before_state = before_state
        self.after_state = after_state
        self.error = error
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.to_dict(),
            "success": self.success,
            "before_state": self.before_state.to_dict(),
            "after_state": self.after_state.to_dict() if self.after_state else None,
            "error": self.error,
            "timestamp": self.timestamp
        }
