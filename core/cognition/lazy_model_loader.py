import os
import time
import logging
import gc
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [LAZY_LOADER] %(message)s")

class DynamicModelSwapper:
    """
    On-Demand Dynamic Model Loader for 4GB VRAM Systems (RTX 3050).
    Ensures ONLY ONE AI model resides in VRAM at any time to prevent memory crashes.
    """

    def __init__(self):
        self.active_model_name: Optional[str] = None
        self.active_model_instance: Any = None

    def purge_vram(self):
        """Immediately flushes PyTorch CUDA cache and forces Python garbage collection."""
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
            gc.collect()
            logging.info("VRAM & RAM successfully purged before swapping models.")
        except Exception as e:
            logging.warning(f"Error purging VRAM: {e}")

    def activate_model(self, target_model_name: str) -> Any:
        """Dynamically loads the requested model into VRAM after purging previous model."""
        if self.active_model_name == target_model_name and self.active_model_instance is not None:
            logging.info(f"Model [{target_model_name}] is already active in VRAM.")
            return self.active_model_instance

        # Step 1: Unload previous model & purge VRAM
        if self.active_model_instance is not None:
            logging.info(f"Unloading previous model [{self.active_model_name}] from VRAM...")
            del self.active_model_instance
            self.active_model_instance = None
            self.purge_vram()

        # Step 2: Load new target model
        logging.info(f"Dynamically loading [{target_model_name}] into VRAM on demand...")
        start_t = time.time()
        
        # Stub / Loader mapping
        self.active_model_instance = f"LOADED_WEIGHTS_{target_model_name}"
        self.active_model_name = target_model_name
        
        load_duration = round(time.time() - start_t, 3)
        logging.info(f"Model [{target_model_name}] loaded in {load_duration}s. VRAM safe!")
        return self.active_model_instance

if __name__ == "__main__":
    swapper = DynamicModelSwapper()
    
    # 1. Load Coder Model
    swapper.activate_model("Qwen2.5-Coder-3B")
    
    # 2. Vision Triggered -> Swap to Vision Model
    swapper.activate_model("Qwen2-VL-2B")
    
    # 3. Speech Triggered -> Swap to Voice Model
    swapper.activate_model("XTTS-v2")
