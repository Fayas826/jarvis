import time
from typing import List, Dict, Any

try:
    import uiautomation as auto
except ImportError:
    auto = None

from core.perception.visual_state import GUIElement

class AccessibilityProvider:
    """Windows UI Automation Accessibility Tree Traversal."""

    def get_visible_elements(self) -> List[GUIElement]:
        """Traverses the UI Automation tree of the foreground window."""
        elements = []
        if auto is None:
            # Fallback if library is not installed
            return elements

        try:
            # Set uiautomation parameters
            auto.SetGlobalSearchTimeout(1.0)
            root = auto.GetForegroundWindow()
            if not root:
                return elements

            # Search active controls recursively using DFS stack
            stack = [(root, 0)]
            visited = set()
            idx = 0
            
            while stack and len(elements) < 100:
                ctrl, depth = stack.pop()
                if not ctrl or depth > 4:
                    continue
                    
                ctrl_id = ctrl.GetRuntimeId()
                if ctrl_id in visited:
                    continue
                visited.add(ctrl_id)
                
                # Retrieve info
                name = ctrl.Name
                control_type = ctrl.ControlTypeName
                rect = ctrl.BoundingRectangle
                
                if rect and rect.left != 0 and rect.right != 0:
                    x1, y1, x2, y2 = rect.left, rect.top, rect.right, rect.bottom
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    
                    # Add named control elements or clickable buttons
                    if name or control_type in ["ButtonControl", "EditControl", "CheckBoxControl"]:
                        elements.append(
                            GUIElement(
                                element_id=f"uia_{idx}_{ctrl.ProcessId}",
                                element_type=control_type,
                                text=name or f"{control_type}_{idx}",
                                role=control_type.lower(),
                                bbox=[x1, y1, x2, y2],
                                center=[center_x, center_y],
                                confidence=0.98,
                                clickable=True,
                                visible=True,
                                source="uia"
                            )
                        )
                        idx += 1
                
                # Push children to stack
                try:
                    for child in reversed(ctrl.GetChildren()):
                        stack.append((child, depth + 1))
                except Exception as e:
                    from core.reliability.system_logger import system_logger
                    system_logger.log('ERROR', 'accessibility', f'Unhandled exception: {e}')
                    pass
        except Exception as e:
            print(f"[ACCESSIBILITY] Traversal error: {e}")

        return elements

accessibility_provider = AccessibilityProvider()
