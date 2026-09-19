import os
import json
import time
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s [RLHF_DPO] %(message)s")

PREFERENCE_DATASET_FILE = os.path.join(os.path.dirname(__file__), "dpo_preference_data.jsonl")

class PreferenceDataCollector:
    """
    JARVIS RLHF & Direct Preference Optimization (DPO) Collector.
    Logs (Prompt, Chosen Response, Rejected Response) tuples from user feedback
    to continuously align JARVIS's brain with expert human standards.
    """

    def __init__(self, log_path: str = PREFERENCE_DATASET_FILE):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_preference(self, prompt: str, chosen_response: str, rejected_response: str, source: str = "User Feedback"):
        """Logs a preference pair for DPO alignment training."""
        entry = {
            "prompt": prompt,
            "chosen": chosen_response,
            "rejected": rejected_response,
            "source": source,
            "timestamp": time.time()
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        logging.info(f"DPO Preference Pair Logged! Total Dataset Size: {self.get_dataset_size()} pairs.")

    def get_dataset_size(self) -> int:
        if not os.path.exists(self.log_path):
            return 0
        with open(self.log_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)

if __name__ == "__main__":
    collector = PreferenceDataCollector()
    collector.log_preference(
        prompt="Write a function to purge GPU VRAM",
        chosen_response="import torch\ntorch.cuda.empty_cache()\ntorch.cuda.ipc_collect()",
        rejected_response="print('VRAM purged')",
        source="Expert Verification"
    )
