import os
import time
import gc

import psutil
try:
    import unsloth
    from unsloth import FastLanguageModel
except Exception as e:
    from core.reliability.system_logger import system_logger
    system_logger.log('ERROR', 'phase2_defensive_trainer', f'Unhandled exception: {e}')
    pass

import torch
_orig_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _orig_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

import transformers
transformers.utils.import_utils.check_torch_load_is_safe = lambda: None
transformers.trainer.check_torch_load_is_safe = lambda: None

from datasets import load_dataset
from trl import SFTTrainer, SFTConfig
from transformers import TrainerCallback
import glob

TRAINING_LAB = r"c:\jarvis AI\jarvis\training_lab"
FOUNDATION_MODEL_DIR = os.path.join(TRAINING_LAB, "jarvis_1million_FULL_model")
EXPERT_OUT_DIR = os.path.join(TRAINING_LAB, "expert_models", "advanced_defensive_cyber")
DATASET_PATH = os.path.join(TRAINING_LAB, "advanced_defensive_cybersecurity.jsonl")

def log(msg):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [PHASE 2 CYBER] {msg}", flush=True)

class BatteryMonitorCallback(TrainerCallback):
    def on_step_end(self, args, state, control, **kwargs):
        batt = psutil.sensors_battery()
        if batt and not batt.power_plugged and batt.percent <= 19:
            log(f"CRITICAL WARNING: Battery is at {batt.percent}%. Hibernating training instantly!")
            control.should_save = True
            control.should_training_stop = True

def train_defensive_cyber():
    log("=" * 70)
    log(" STARTING PHASE 2: ADVANCED DEFENSIVE CYBERSECURITY TRAINING ")
    log("=" * 70)

    if os.path.exists(os.path.join(EXPERT_OUT_DIR, "adapter_config.json")):
        log(" [DONE] Advanced Defensive Cybersecurity already trained!")
        return

    os.makedirs(EXPERT_OUT_DIR, exist_ok=True)
    
    log(f" [TRAINING] Loading Foundation Model and starting Phase 2...")
    gc.collect(); torch.cuda.empty_cache()
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=FOUNDATION_MODEL_DIR, 
        max_seq_length=2048, 
        load_in_4bit=True
    )
    
    model = FastLanguageModel.get_peft_model(
        model, r=16,
        target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],
        lora_alpha=16, lora_dropout=0, bias='none', use_gradient_checkpointing='unsloth'
    )
    
    dataset = load_dataset('json', data_files={'train': DATASET_PATH}, split='train')
    dataset = dataset.map(lambda x: {'text': f"User: {x['instruction']}\nAssistant: {x['response']}"})
    
    args = SFTConfig(
        output_dir=EXPERT_OUT_DIR, per_device_train_batch_size=4,
        gradient_accumulation_steps=2, learning_rate=2e-4, max_steps=500,
        logging_steps=50, optim='adamw_8bit', 
        save_strategy='steps', save_steps=100, save_total_limit=2, group_by_length=True,
        dataset_text_field='text', fp16=False, bf16=True, warmup_steps=20, packing=False
    )
    
    trainer = SFTTrainer(model=model, train_dataset=dataset, processing_class=tokenizer, args=args, callbacks=[BatteryMonitorCallback()])
    
    checkpoint_dirs = glob.glob(os.path.join(EXPERT_OUT_DIR, "checkpoint-*"))
    has_ckpt = len(checkpoint_dirs) > 0
    log(f'Training Advanced Defensive Cyber... (resuming from checkpoint: {has_ckpt})')
    
    trainer.train(resume_from_checkpoint=True if has_ckpt else None)
    
    log(f'Saving Advanced Defensive Cyber to {EXPERT_OUT_DIR}...')
    trainer.model.save_pretrained(EXPERT_OUT_DIR)
    tokenizer.save_pretrained(EXPERT_OUT_DIR)
    
    log("\nPhase 2 Advanced Defensive Cyber training complete!")

if __name__ == "__main__":
    train_defensive_cyber()
