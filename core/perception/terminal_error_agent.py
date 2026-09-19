import re
import logging
from typing import Dict, Any

class TerminalErrorAgent:
    """
    Self-Healing Swarm Member: The Debugger.
    Ingests stack traces and terminal logs to identify crashes, OOM errors,
    and missing dependencies, then proposes concrete code patches.
    """
    
    def __init__(self):
        self.known_errors = {
            "OOM": re.compile(r"OutOfMemoryError|CUDA out of memory|modules are dispatched on the CPU"),
            "MODULE_NOT_FOUND": re.compile(r"ModuleNotFoundError: No module named '(.+)'"),
            "SYNTAX": re.compile(r"SyntaxError: (.+)")
        }

    def analyze_log(self, log_content: str) -> Dict[str, Any]:
        """Scans a crash log and determines the self-healing strategy."""
        logging.info("[Terminal Error Agent] Scanning crash logs for anomalies...")
        
        if self.known_errors["OOM"].search(log_content):
            logging.error("[Terminal Error Agent] Diagnosis: GPU VRAM Overflow Detected.")
            return {
                "diagnosis": "GPU Out of Memory (OOM)",
                "root_cause": "Batch size too large or model weights exceed 4GB VRAM.",
                "proposed_fix": {
                    "action": "modify_script",
                    "target_file": "train_game_dev_unsloth.py",
                    "modifications": [
                        {"variable": "per_device_train_batch_size", "new_value": 2},
                        {"variable": "gradient_accumulation_steps", "new_value": 2},
                        {"variable": "llm_int8_enable_fp32_cpu_offload", "new_value": True}
                    ]
                }
            }
            
        elif match := self.known_errors["MODULE_NOT_FOUND"].search(log_content):
            missing_module = match.group(1)
            return {
                "diagnosis": f"Missing Dependency: {missing_module}",
                "proposed_fix": {
                    "action": "run_command",
                    "command": f"pip install {missing_module}"
                }
            }
            
        return {"diagnosis": "Unknown Error", "proposed_fix": None}

    def auto_patch(self, fix_plan: Dict[str, Any]):
        """Executes the proposed fix."""
        logging.info(f"[Terminal Error Agent] Executing Auto-Patch: {fix_plan['diagnosis']}")
        # In a full swarm, this hands off to the LogicCoderAgent and TerminalAgent
        pass
