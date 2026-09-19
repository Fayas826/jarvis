import os
import sys
import asyncio
import time
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WorkflowSynthesizer")

class WorkflowSynthesizer:
    """
    🔗 PILLAR 3: Cross-Application Workflow Synthesis Engine
    Chains and coordinates multi-step tasks across diverse Windows applications
    (Chrome ↔ WPS Office ↔ Notepad ↔ File Explorer ↔ WhatsApp) with seamless
    window switching, clipboard data piping, and automated document synthesis.
    """

    def __init__(self):
        from action.desktop_control.desktop_controller import desktop_controller
        from core.execution.universal_desktop_controller import desktop_controller as universal_controller
        from core.context.clipboard_spine import clipboard_spine
        
        self.app_launcher = desktop_controller
        self.universal_controller = universal_controller
        self.clipboard = clipboard_spine

    async def execute_multi_app_pipeline(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes an ordered pipeline of cross-application actions.
        Each step defines target app, operation type, payload, and inter-app data piping.
        """
        results = []
        pipeline_context: Dict[str, Any] = {}

        logger.info(f"[SYNTHESIZER] Initiating {len(steps)}-step multi-application pipeline...")

        for idx, step in enumerate(steps):
            step_name = step.get("name", f"Step_{idx+1}")
            action_type = step.get("type", "UNKNOWN").upper()
            target_app = step.get("app")
            logger.info(f"[SYNTHESIZER] Executing [{step_name}]: {action_type} on '{target_app}'")

            try:
                # 1. Bring target app to foreground if specified
                if target_app:
                    await self.app_launcher.open_app(target_app)
                    await asyncio.sleep(0.6)

                # 2. Execute action
                if action_type == "APP_LAUNCH":
                    # Already launched above
                    step_res = {"status": "SUCCESS", "detail": f"App '{target_app}' launched"}

                elif action_type == "COPY_TO_SPINE":
                    # Trigger Ctrl+C and pull into clipboard spine
                    self.universal_controller.send_hotkey("ctrl", "c")
                    await asyncio.sleep(0.3)
                    extracted = self.clipboard.get_text()
                    pipeline_context["clipboard_extracted"] = extracted
                    step_res = {"status": "SUCCESS", "bytes_extracted": len(extracted)}

                elif action_type == "INJECT_FROM_SPINE":
                    text_to_paste = step.get("text") or pipeline_context.get("clipboard_extracted", "")
                    if text_to_paste:
                        self.clipboard.set_text(text_to_paste)
                        self.universal_controller.send_hotkey("ctrl", "v")
                        await asyncio.sleep(0.3)
                        step_res = {"status": "SUCCESS", "pasted_chars": len(text_to_paste)}
                    else:
                        step_res = {"status": "SKIPPED", "detail": "No text in spine to inject"}

                elif action_type == "TYPE":
                    text = step.get("text", "")
                    # Direct typing or clipboard paste
                    self.clipboard.set_text(text)
                    self.universal_controller.send_hotkey("ctrl", "v")
                    await asyncio.sleep(0.2)
                    step_res = {"status": "SUCCESS", "typed_length": len(text)}

                elif action_type == "HOTKEY":
                    keys = step.get("keys", [])
                    if len(keys) >= 2:
                        self.universal_controller.send_hotkey(*keys)
                    step_res = {"status": "SUCCESS", "keys": keys}

                elif action_type == "SAVE_DESKTOP_FILE":
                    filename = step.get("filename", "aegis_output.txt")
                    content = step.get("content", pipeline_context.get("clipboard_extracted", ""))
                    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", filename)
                    with open(desktop_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    step_res = {"status": "SUCCESS", "file_saved": desktop_path}
                    pipeline_context["last_saved_file"] = desktop_path

                elif action_type == "CAPTURE_WINDOW":
                    from core.perception.screen_capture import screen_capture
                    shot = screen_capture.capture_desktop()
                    step_res = {"status": "SUCCESS", "screen_captured": shot is not None}

                else:
                    step_res = {"status": "ERROR", "error": f"Unknown step type {action_type}"}

                results.append({"step": step_name, "result": step_res})

            except Exception as e:
                logger.error(f"[SYNTHESIZER] Step '{step_name}' failed: {e}")
                results.append({"step": step_name, "status": "FAILED", "error": str(e)})

        return {
            "status": "COMPLETED",
            "total_steps": len(steps),
            "step_results": results,
            "pipeline_context": pipeline_context
        }

    async def create_and_save_desktop_report(self, filename: str, report_text: str) -> Dict[str, Any]:
        """Convenience method: launches Notepad, writes text, saves to Desktop, and confirms."""
        steps = [
            {"name": "Open Notepad", "type": "APP_LAUNCH", "app": "notepad"},
            {"name": "Inject Report Content", "type": "TYPE", "text": report_text},
            {"name": "Save File Direct", "type": "SAVE_DESKTOP_FILE", "filename": filename, "content": report_text}
        ]
        return await self.execute_multi_app_pipeline(steps)

workflow_synthesizer = WorkflowSynthesizer()
