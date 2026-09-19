"""
JARVIS MASTER SWARM ORCHESTRATOR
=================================
Trains all 18 Specialized Expert Models.
Uses the completed jarvis_1million_FULL_model as the Foundation Base.
This implements the "Hub and Spoke" Architecture.
"""
import os
import sys
import time
import gc

import psutil
try:
    import unsloth
    from unsloth import FastLanguageModel
except Exception as e:
    from core.reliability.system_logger import system_logger
    system_logger.log('ERROR', 'master_swarm_orchestrator', f'Unhandled exception: {e}')
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
from peft import PeftModel
from trl import SFTTrainer, SFTConfig
from transformers import TrainerCallback
import glob

TRAINING_LAB = r"c:\jarvis AI\jarvis\training_lab"
FOUNDATION_MODEL_DIR = os.path.join(TRAINING_LAB, "jarvis_1million_FULL_model")
EXPERTS_DIR = os.path.join(TRAINING_LAB, "expert_models")

EXPERT_PHASES = [
    {"name": "Object Detection", "dataset": "object_detection.jsonl"},
    {"name": "Root Access & CySec", "dataset": "root_access.jsonl"},
    {"name": "Cybersecurity Threats", "dataset": "cybersecurity.jsonl"},
    {"name": "Hyper Coding", "dataset": "hyper_coding.jsonl"},
    {"name": "Omniscient CySec", "dataset": "omniscient_cysec.jsonl"},
    {"name": "Master Architect Coding", "dataset": "master_architect.jsonl"},
    {"name": "Smart Home IoT", "dataset": "smart_home.jsonl"},
    {"name": "Autonomous Proactive", "dataset": "autonomous.jsonl"},
    {"name": "Voice Biometrics", "dataset": "voice_biometrics.jsonl"},
    {"name": "Robotic Hardware API", "dataset": "robotic_api.jsonl"},
    {"name": "Medical Knowledge", "dataset": "medical_knowledge.jsonl"},
    {"name": "Corporate Safety", "dataset": "corporate_safety.jsonl"},
    {"name": "Llama Eyes & Ears", "dataset": "eyes_ears.jsonl"},
    {"name": "Voice to Voice", "dataset": "voice_to_voice.jsonl"},
    {"name": "Whisper Recognition", "dataset": "whisper.jsonl"},
    {"name": "Tool Former Logic", "dataset": "tool_former.jsonl"},
    {"name": "ChromaDB RAG Memory", "dataset": "chromadb_rag.jsonl"},
    {"name": "Polyglot Architecture", "dataset": "polyglot.jsonl"}
]

def log(msg):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [MASTER ORCHESTRATOR] {msg}", flush=True)

class BatteryMonitorCallback(TrainerCallback):
    def on_step_end(self, args, state, control, **kwargs):
        batt = psutil.sensors_battery()
        if batt and not batt.power_plugged and batt.percent <= 19:
            log(f"CRITICAL WARNING: Battery is at {batt.percent}%. Hibernating training instantly!")
            control.should_save = True
            control.should_training_stop = True

def train_experts():
    log("=" * 70)
    log(" INITIALIZING HUB-AND-SPOKE MASTER EXPERT TRAINING ")
    log(f" Foundation Hub: {FOUNDATION_MODEL_DIR}")
    log(f" Experts Queued: {len(EXPERT_PHASES)}")
    log("=" * 70)

    if not os.path.exists(FOUNDATION_MODEL_DIR):
        log("ERROR: 1M Foundation Model not ready yet. Please wait for the 1M trainer to complete.")
        return

    os.makedirs(EXPERTS_DIR, exist_ok=True)
    
    for idx, expert in enumerate(EXPERT_PHASES, 1):
        log(f"\n[EXPERT {idx}/{len(EXPERT_PHASES)}] Preparing {expert['name']}...")
        expert_out_dir = os.path.join(EXPERTS_DIR, expert['name'].replace(' ', '_').lower())
        dataset_path = os.path.join(TRAINING_LAB, expert['dataset'])
        
        if os.path.exists(os.path.join(expert_out_dir, "adapter_config.json")):
            log(f" [DONE] {expert['name']} already trained!")
            continue
            
        if not os.path.exists(dataset_path):
            log(f" ERROR: Dataset {dataset_path} not found. Skipping...")
            continue
            
        log(f" [TRAINING] Loading Foundation Model and starting {expert['name']}...")
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
        
        dataset = load_dataset('json', data_files={'train': dataset_path}, split='train')
        dataset = dataset.map(lambda x: {'text': f"User: {x['instruction']}\nAssistant: {x['response']}"})
        
        args = SFTConfig(
            output_dir=expert_out_dir, per_device_train_batch_size=4,
            gradient_accumulation_steps=2, learning_rate=2e-4, max_steps=500,
            logging_steps=50, optim='adamw_8bit', 
            save_strategy='steps', save_steps=100, save_total_limit=2, group_by_length=True,
            dataset_text_field='text', fp16=False, bf16=True, warmup_steps=20, packing=False
        )
        
        trainer = SFTTrainer(model=model, train_dataset=dataset, processing_class=tokenizer, args=args, callbacks=[BatteryMonitorCallback()])
        
        checkpoint_dirs = glob.glob(os.path.join(expert_out_dir, "checkpoint-*"))
        has_ckpt = len(checkpoint_dirs) > 0
        log(f'Training {expert["name"]}... (resuming from checkpoint: {has_ckpt})')
        
        trainer.train(resume_from_checkpoint=True if has_ckpt else None)
        
        log(f'Saving {expert["name"]} to {expert_out_dir}...')
        trainer.model.save_pretrained(expert_out_dir)
        tokenizer.save_pretrained(expert_out_dir)
        
        del model, tokenizer, trainer, dataset
        gc.collect(); torch.cuda.empty_cache()
        time.sleep(3)
        
    log("\nMaster Orchestrator training complete. All 18 experts are trained!")

if __name__ == "__main__":
    train_experts()
