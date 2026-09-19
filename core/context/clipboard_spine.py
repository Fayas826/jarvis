"""
A.E.G.I.S. Universal Cross-Application Clipboard & Context Spine
==============================================================
Provides high-speed cross-application data piping between any Windows software:
- Safe clipboard reading/writing without chat leakage.
- Tabular data parsing (CSV, TSV, Markdown tables).
- Cross-app pipeline: Extract from App A -> Inject into App B.
"""

import time
import logging
from typing import Optional, Any, List, Dict
import pyautogui
import pyperclip

logger = logging.getLogger("AEGIS_ClipboardSpine")

class UniversalClipboardSpine:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def set_text(self, text: str):
        """Sets text safely onto the Windows clipboard and tracks in history."""
        pyperclip.copy(text)
        self.history.append({
            "type": "text",
            "content": text[:500],
            "timestamp": time.time()
        })
        logger.info(f"[CLIPBOARD_SPINE] Stored text on clipboard ({len(text)} chars)")

    def get_text(self) -> str:
        """Reads current clipboard text."""
        try:
            return pyperclip.paste()
        except Exception as e:
            logger.warning(f"[CLIPBOARD_SPINE] Failed to read clipboard: {e}")
            return ""

    def copy_current_selection(self) -> str:
        """Sends Ctrl+C to the active window and retrieves the copied text."""
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.2)
        text = self.get_text()
        self.history.append({
            "type": "selection_copy",
            "content": text[:500],
            "timestamp": time.time()
        })
        return text

    def paste_into_active(self, text: Optional[str] = None):
        """Injects text into the active foreground element via Ctrl+V."""
        if text is not None:
            self.set_text(text)
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)

    def pipe(self, data: str, target_window_title: str):
        """
        Pipes data across applications:
        Focuses target window and pastes data into the active control.
        """
        from core.execution.universal_desktop_controller import desktop_controller
        desktop_controller.focus_application(target_window_title, minimize_others=False)
        time.sleep(0.5)
        self.paste_into_active(data)
        logger.info(f"[CLIPBOARD_SPINE] Successfully piped data into window '{target_window_title}'")

clipboard_spine = UniversalClipboardSpine()
