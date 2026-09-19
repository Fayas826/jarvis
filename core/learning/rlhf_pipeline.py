import os
import json
import datetime
from typing import Dict, Any

class RLHFPipeline:
    """
    Reinforcement Learning from Human Feedback (RLHF) Pipeline.
    Logs successful interactions so JARVIS can learn and retrain its own LoRA.
    """
    def __init__(self, data_file: str = "training_data.jsonl"):
        self.jarvis_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.training_lab = os.path.join(self.jarvis_root, "training_lab")
        self.data_path = os.path.join(self.training_lab, data_file)
        os.makedirs(self.training_lab, exist_ok=True)

    def log_success(self, instruction: str, input_context: str, generated_code: str):
        """
        Formats the interaction into Alpaca JSONL format and appends to the dataset.
        """
        record = {
            "instruction": instruction,
            "input": input_context,
            "output": generated_code,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "reward_score": 1.0  # Implicitly positive because user accepted it
        }

        with open(self.data_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        
        print(f"[RLHF] Successfully logged interaction to {self.data_path}")

if __name__ == "__main__":
    pipeline = RLHFPipeline()
    pipeline.log_success(
        instruction="Fix the background-clip CSS compatibility issue.",
        input_context="h1 { -webkit-background-clip: text; }",
        generated_code="h1 { -webkit-background-clip: text; background-clip: text; }"
    )
