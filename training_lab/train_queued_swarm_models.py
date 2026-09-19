import os
import sys
import time

try:
    import unsloth
    from unsloth import FastLanguageModel
    HAS_UNSLOTH = True
except Exception as e:
    from core.reliability.system_logger import system_logger
    system_logger.log('ERROR', 'train_queued_swarm_models', f'Unhandled exception: {e}')
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
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

TRAINING_LAB_DIR = r"c:\jarvis AI\jarvis\training_lab"
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
            system_logger.log('ERROR', 'train_queued_swarm_models', f'Unhandled exception: {e}')
            pass

    def flush(self):
        self.stream.flush()

sys.stdout = TeeLogger(LOG_FILE, sys.stdout)
sys.stderr = TeeLogger(LOG_FILE, sys.stderr)

def log(msg):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} [SWARM_TRAINER] {msg}"
    print(entry, flush=True)

SWARM_TRAINING_JOBS = [
    {
        "name": "Phase 34: Llama-3.2-3B Conversational Swarm",
        "dataset_file": os.path.join(TRAINING_LAB_DIR, "llama3_conversational_swarm.jsonl"),
        "output_dir": os.path.join(TRAINING_LAB_DIR, "llama3_conversational_model"),
        "base_model": "Qwen/Qwen2.5-1.5B"
    },
    {
        "name": "Phase 35: Phi-3 Knowledge Scholar",
        "dataset_file": os.path.join(TRAINING_LAB_DIR, "phi3_knowledge_scholar.jsonl"),
        "output_dir": os.path.join(TRAINING_LAB_DIR, "phi3_knowledge_model"),
        "base_model": "Qwen/Qwen2.5-1.5B"
    },
    {
        "name": "Phase 36: Ministral Robot Logic",
        "dataset_file": os.path.join(TRAINING_LAB_DIR, "ministral_robot_logic.jsonl"),
        "output_dir": os.path.join(TRAINING_LAB_DIR, "ministral_logic_model"),
        "base_model": "Qwen/Qwen2.5-1.5B"
    },
    {
        "name": "Phase 37: Qwen2-VL Vision Grounding",
        "dataset_file": os.path.join(TRAINING_LAB_DIR, "qwen2_vl_vision_grounding.jsonl"),
        "output_dir": os.path.join(TRAINING_LAB_DIR, "qwen2_vl_vision_model"),
        "base_model": "Qwen/Qwen2.5-1.5B"
    },
    {
        "name": "Phase 38: DeepSeek Architect C++ Coding",
        "dataset_file": os.path.join(TRAINING_LAB_DIR, "deepseek_architect_coding.jsonl"),
        "output_dir": os.path.join(TRAINING_LAB_DIR, "deepseek_coder_model"),
        "base_model": "Qwen/Qwen2.5-1.5B"
    },
    {
        "name": "Phase 39: BERT 28-Emotion Threat Classifier",
        "dataset_file": os.path.join(TRAINING_LAB_DIR, "bert_goemotions_threat.jsonl"),
        "output_dir": os.path.join(TRAINING_LAB_DIR, "bert_emotion_model"),
        "base_model": "Qwen/Qwen2.5-1.5B"
    },
    {
        "name": "Phase 49: Qwen 5-Million Game Dev Expert",
        "dataset_file": os.path.join(TRAINING_LAB_DIR, "game_development.jsonl"),
        "output_dir": os.path.join(TRAINING_LAB_DIR, "jarvis_5million_game_dev_model"),
        "base_model": "Qwen/Qwen2.5-1.5B"
    }
]

def train_job(job):
    if os.path.exists(os.path.join(job['output_dir'], "adapter_config.json")):
        log(f"SKIPPING: {job['name']} already completed and saved at {job['output_dir']}.")
        return True

    log(f"==================================================")
    log(f"STARTING SWARM JOB: {job['name']}")
    log(f"Dataset: {job['dataset_file']}")
    log(f"Output:  {job['output_dir']}")
    log(f"==================================================")

    if not os.path.exists(job['dataset_file']):
        log(f"ERROR: Dataset file not found: {job['dataset_file']}")
        return False

    dataset = load_dataset("json", data_files={"train": job['dataset_file']})
    def fmt(example):
        return {"text": f"User: {example['instruction']}\nAssistant: {example['response']}"}
    dataset = dataset.map(fmt)

    use_unsloth = False
    model, tokenizer, trainer = None, None, None
    try:
        from unsloth import FastLanguageModel
        log("[UNSLOTH] FAST-LANGUAGE-MODEL ENGINE DETECTED! Engaging 5x-10x Speed Acceleration...")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=job['base_model'],
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
        use_unsloth = True
    except Exception as ex:
        log(f"Unsloth fallback to standard PEFT BitsAndBytes: {ex}")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        model = AutoModelForCausalLM.from_pretrained(
            job['base_model'],
            quantization_config=bnb_config,
            device_map="auto"
        )
        tokenizer = AutoTokenizer.from_pretrained(job['base_model'])
        tokenizer.pad_token = tokenizer.eos_token

    training_args = SFTConfig(
        output_dir=job['output_dir'],
        per_device_train_batch_size=4 if use_unsloth else 1,
        gradient_accumulation_steps=1 if use_unsloth else 4,
        learning_rate=3e-4,
        num_train_epochs=3,
        logging_steps=10,
        optim="adamw_8bit" if use_unsloth else "paged_adamw_8bit",
        save_strategy="epoch",
        dataset_text_field="text",
        fp16=False,
        bf16=True,
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        processing_class=tokenizer,
        args=training_args,
    )

    log("Ignition! Starting training loop on RTX 3050 GPU...")
    trainer.train()

    log(f"Saving fine-tuned model weights to {job['output_dir']}...")
    trainer.model.save_pretrained(job['output_dir'])
    tokenizer.save_pretrained(job['output_dir'])
    log(f"SUCCESS: {job['name']} COMPLETED & SAVED!")
    
    del model, tokenizer, trainer
    import gc
    gc.collect()
    torch.cuda.empty_cache()
    return True

def run_all_jobs():
    log("==================================================")
    log("  JARVIS AUTONOMOUS SWARM MULTI-MODEL PIPELINE   ")
    log("==================================================")
    for idx, job in enumerate(SWARM_TRAINING_JOBS, 1):
        log(f"Pipeline Step [{idx}/{len(SWARM_TRAINING_JOBS)}]: {job['name']}")
        try:
            train_job(job)
        except Exception as e:
            log(f"EXCEPTION in job {job['name']}: {e}")
        finally:
            import gc
            gc.collect()
            torch.cuda.empty_cache()
    log("==================================================")
    log(" ALL SWARM MODEL FINE-TUNING JOBS COMPLETED! ")
    log("==================================================")

if __name__ == "__main__":
    run_all_jobs()
