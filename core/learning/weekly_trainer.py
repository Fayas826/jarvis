import os
import time
import datetime
import subprocess

class WeeklyTrainer:
    """
    Daemon that checks the RLHF dataset size and triggers a LoRA fine-tuning 
    job if enough new data has been collected over the week.
    """
    def __init__(self, data_file: str = "training_data.jsonl"):
        self.jarvis_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.training_lab = os.path.join(self.jarvis_root, "training_lab")
        self.data_path = os.path.join(self.training_lab, data_file)
        self.train_script = os.path.join(self.training_lab, "train_game_dev_unsloth.py")

    def check_and_train(self):
        if not os.path.exists(self.data_path):
            print("[TRAINER] No RLHF data found.")
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if len(lines) >= 10:  # Arbitrary threshold to trigger training
            print(f"[TRAINER] Found {len(lines)} new interactions. Triggering LoRA Training...")
            try:
                subprocess.run(["python", self.train_script], check=True)
                print("[TRAINER] Training complete! Archiving old dataset.")
                os.rename(
                    self.data_path, 
                    self.data_path + f".archived.{int(time.time())}"
                )
            except Exception as e:
                print(f"[TRAINER] Training failed: {e}")
        else:
            print(f"[TRAINER] Only {len(lines)} interactions. Waiting for more data.")

    def run_daemon(self):
        print("[TRAINER] Weekly RLHF Trainer Daemon Started.")
        while True:
            # In a real system, this would sleep for a week. We'll sleep for 24h.
            self.check_and_train()
            time.sleep(86400)

if __name__ == "__main__":
    trainer = WeeklyTrainer()
    trainer.check_and_train()
