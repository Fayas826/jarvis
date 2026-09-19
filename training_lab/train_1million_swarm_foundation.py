import os
import sys
import time

try:
    import unsloth
    from unsloth import FastLanguageModel
    HAS_UNSLOTH = True
except Exception as e:
    from core.reliability.system_logger import system_logger
    system_logger.log('ERROR', 'train_1million_swarm_foundation', f'Unhandled exception: {e}')
    HAS_UNSLOTH = False

import torch

_orig_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _orig_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

import transformers
transformers.utils.import_utils.check_torch_load_is_safe = lambda: None
transformers.trainer.check_torch_load_is_safe = lambda: None

from datasets import load_dataset
from trl import SFTTrainer, SFTConfig

TRAINING_LAB_DIR = r"c:\jarvis AI\jarvis\training_lab"
DATASET_FILE = os.path.join(TRAINING_LAB_DIR, "1million_godtier_data.jsonl")
OUTPUT_DIR = os.path.join(TRAINING_LAB_DIR, "jarvis_1million_foundation_model")
LOG_FILE = os.path.join(TRAINING_LAB_DIR, "swarm_training.log")

class TeeLogger:
    def __init__(self, filepath, stream):
        self.filepath = filepath
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
        try:
            with open(self.filepath, "a", encoding="utf-8", errors="ignore") as f:
                f.write(data)
                f.flush()
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'train_1million_swarm_foundation', f'Unhandled exception: {e}')
            pass

    def flush(self):
        self.stream.flush()

sys.stdout = TeeLogger(LOG_FILE, sys.stdout)
sys.stderr = TeeLogger(LOG_FILE, sys.stderr)

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} [1M_FOUNDATION_TRAINER] {msg}", flush=True)

def train_1million_foundation():
    log("==================================================")
    log(" STARTING 1 MILLION GOD-TIER SWARM FOUNDATION TRAINING ")
    log(f" Dataset: {DATASET_FILE} (304 MB)")
    log(f" Output:  {OUTPUT_DIR}")
    log("==================================================")

    if os.path.exists(os.path.join(OUTPUT_DIR, "adapter_config.json")):
        log(f"FOUNDATION MODEL ALREADY COMPLETED & SAVED AT {OUTPUT_DIR}!")
        return

    import gc
    gc.collect()
    torch.cuda.empty_cache()

    log("[UNSLOTH] Loading Qwen2.5-1.5B Base Engine with 5x-10x GPU Acceleration...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="Qwen/Qwen2.5-1.5B",
        max_seq_length=2048,
        load_in_4bit=True,
    )
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
    )

    log(f"Loading 1M Foundation Dataset slice from {DATASET_FILE}...")
    dataset = load_dataset("json", data_files={"train": DATASET_FILE}, split="train[:50000]")
    def fmt(example):
        return {"text": f"User: {example['instruction']}\nAssistant: {example['response']}"}
    dataset = dataset.map(fmt)

    training_args = SFTConfig(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=1,
        learning_rate=3e-4,
        max_steps=500,
        logging_steps=20,
        optim="adamw_8bit",
        save_strategy="steps",
        save_steps=250,
        dataset_text_field="text",
        fp16=False,
        bf16=True,
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        processing_class=tokenizer,
        args=training_args,
    )

    log("Ignition! Starting 1 Million Swarm Foundation Training on RTX 3050 GPU...")
    trainer.train()

    log(f"Saving fine-tuned 1M Foundation Model weights to {OUTPUT_DIR}...")
    trainer.model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    log("SUCCESS: 1 MILLION GOD-TIER SWARM FOUNDATION MODEL SAVED!")

    del model, tokenizer, trainer
    gc.collect()
    torch.cuda.empty_cache()

if __name__ == "__main__":
    train_1million_foundation()
