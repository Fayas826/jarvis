import os
import subprocess
import logging
try:
    import psutil
except ImportError:
    psutil = None

class HardwareEngineerAgent:
    """
    JARVIS Specialized Swarm Member: The Hardware Surveillance Engineer.
    Acts as a human systems engineer to proactively monitor memory, VRAM, and CPU,
    intercepting catastrophic actions (like OOM errors) with professional diagnostics.
    """
    
    def __init__(self):
        self.total_ram = 0
        if psutil:
            self.total_ram = psutil.virtual_memory().total / (1024 ** 2) # MB
            
    def _get_vram_usage(self):
        """Uses nvidia-smi to extract VRAM usage of the primary GPU."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.free,memory.total", "--format=csv,nounits,noheader"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(',')
                if len(parts) == 2:
                    free_vram_mb = int(parts[0].strip())
                    total_vram_mb = int(parts[1].strip())
                    return free_vram_mb, total_vram_mb
        except Exception as e:
            logging.error(f"[Hardware Engineer] Failed to probe VRAM: {e}")
        return -1, -1

    def _get_ram_usage(self):
        if not psutil: return -1, -1
        mem = psutil.virtual_memory()
        return mem.available / (1024 ** 2), mem.total / (1024 ** 2)
        
    def evaluate_launch_safety(self, action_name: str, req_vram_mb: int = 0, req_ram_mb: int = 0) -> dict:
        """
        Diagnoses if the hardware can support the requested action.
        Returns a human-readable diagnostic report and a safety boolean.
        """
        free_vram, total_vram = self._get_vram_usage()
        free_ram, total_ram = self._get_ram_usage()
        
        diagnosis = []
        is_safe = True
        
        # Analyze VRAM
        if req_vram_mb > 0 and free_vram != -1:
            if free_vram < req_vram_mb:
                is_safe = False
                diagnosis.append(
                    f"CRITICAL VRAM SHORTAGE: Action '{action_name}' requires {req_vram_mb}MB of VRAM, "
                    f"but only {free_vram}MB is available (out of {total_vram}MB total). "
                    "Another process (likely model training) is saturating the GPU."
                )
            else:
                diagnosis.append(f"VRAM Check: PASS ({free_vram}MB available).")
                
        # Analyze System RAM
        if req_ram_mb > 0 and free_ram != -1:
            if free_ram < req_ram_mb:
                is_safe = False
                diagnosis.append(
                    f"CRITICAL RAM SHORTAGE: Action '{action_name}' requires {req_ram_mb}MB of RAM, "
                    f"but only {free_ram:.1f}MB is available. System is heavily loaded."
                )
            else:
                diagnosis.append(f"System RAM Check: PASS ({free_ram:.1f}MB available).")
                
        if is_safe:
            report = f"Hardware Engineer Analysis: Action '{action_name}' is CLEARED for execution.\n" + "\n".join(diagnosis)
        else:
            report = f"Hardware Engineer Analysis: Action '{action_name}' is ABORTED.\n" + "\n".join(diagnosis)
            logging.warning(f"⚠️ [Hardware Engineer] Prevented catastrophic crash: \n{report}")
            
        return {
            "safe": is_safe,
            "diagnosis": report
        }

hardware_engineer = HardwareEngineerAgent()
