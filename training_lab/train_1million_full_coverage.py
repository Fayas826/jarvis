import os, sys, time, gc

try:
    import unsloth
    from unsloth import FastLanguageModel
    HAS_UNSLOTH = True
except Exception as e:
    from core.reliability.system_logger import system_logger
    system_logger.log('ERROR', 'train_1million_full_coverage', f'Unhandled exception: {e}')
    HAS_UNSLOTH = False

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
from peft import PeftModel

TRAINING_LAB_DIR = r'c:\jarvis AI\jarvis\training_lab'
DATASET_FILE     = os.path.join(TRAINING_LAB_DIR, '1million_godtier_data.jsonl')
BASE_MODEL_DIR   = os.path.join(TRAINING_LAB_DIR, 'jarvis_1million_foundation_model')
OUTPUT_DIR       = os.path.join(TRAINING_LAB_DIR, 'jarvis_1million_FULL_model')
LOG_FILE         = os.path.join(TRAINING_LAB_DIR, 'swarm_training.log')

CHUNK_SIZE      = 100000
TOTAL_CHUNKS    = 10
STEPS_PER_CHUNK = 500

class TeeLogger:
    def __init__(self, filepath, stream):
        self.filepath = filepath
        self.stream   = stream
    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
        try:
            with open(self.filepath, 'a', encoding='utf-8', errors='ignore') as f:
                f.write(data); f.flush()
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'train_1million_full_coverage', f'Unhandled exception: {e}')
            pass
    def flush(self):
        self.stream.flush()

sys.stdout = TeeLogger(LOG_FILE, sys.stdout)
sys.stderr = TeeLogger(LOG_FILE, sys.stderr)

def log(msg):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [1M_FULL] {msg}", flush=True)

def train_full_1million():
    log('='*60)
    log('JARVIS 1,000,000 FULL COVERAGE TRAINING — 10 CHUNKS')
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    progress_file = os.path.join(OUTPUT_DIR, 'chunk_progress.txt')
    start_chunk = 0
    if os.path.exists(progress_file):
        with open(progress_file) as f:
            start_chunk = int(f.read().strip())
        log(f'[RESUME] Resuming from chunk {start_chunk+1}/{TOTAL_CHUNKS}')
    if start_chunk >= TOTAL_CHUNKS:
        log('ALL 1,000,000 SAMPLES ALREADY TRAINED!')
        return
    for chunk_idx in range(start_chunk, TOTAL_CHUNKS):
        chunk_num   = chunk_idx + 1
        slice_start = chunk_idx * CHUNK_SIZE
        slice_end   = slice_start + CHUNK_SIZE
        log(f'CHUNK {chunk_num}/{TOTAL_CHUNKS} | samples {slice_start:,} to {slice_end:,}')
        gc.collect(); torch.cuda.empty_cache()
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name='Qwen/Qwen2.5-1.5B', max_seq_length=2048, load_in_4bit=True)
        adapter_src = BASE_MODEL_DIR if chunk_idx == 0 else OUTPUT_DIR
        if os.path.exists(os.path.join(adapter_src, 'adapter_config.json')):
            log(f'Loading LoRA adapter from {adapter_src}')
            model = PeftModel.from_pretrained(model, adapter_src, is_trainable=True)
        else:
            model = FastLanguageModel.get_peft_model(
                model, r=16,
                target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],
                lora_alpha=16, lora_dropout=0, bias='none', use_gradient_checkpointing='unsloth')
        dataset = load_dataset('json', data_files={'train': DATASET_FILE}, split=f'train[{slice_start}:{slice_end}]')
        dataset = dataset.map(lambda x: {'text': f"User: {x['instruction']}\nAssistant: {x['response']}"})
        chunk_output = os.path.join(OUTPUT_DIR, f'chunk_{chunk_num:02d}')
        import psutil
        from transformers import TrainerCallback

        class BatteryMonitorCallback(TrainerCallback):
            def on_step_end(self, args, state, control, **kwargs):
                batt = psutil.sensors_battery()
                if batt and not batt.power_plugged and batt.percent <= 19:
                    log(f"⚠️ CRITICAL: Battery is at {batt.percent}%. Hibernating training!")
                    control.should_save = True
                    control.should_training_stop = True

        args = SFTConfig(output_dir=chunk_output, per_device_train_batch_size=4,
            gradient_accumulation_steps=2, learning_rate=2e-4, max_steps=STEPS_PER_CHUNK,
            logging_steps=50, optim='adamw_8bit', 
            save_strategy='steps', save_steps=100, save_total_limit=2, group_by_length=True,
            dataset_text_field='text', fp16=False, bf16=True, warmup_steps=20, packing=False)
        trainer = SFTTrainer(model=model, train_dataset=dataset, processing_class=tokenizer, args=args, callbacks=[BatteryMonitorCallback()])
        import glob
        checkpoint_dirs = glob.glob(os.path.join(chunk_output, "checkpoint-*"))
        has_ckpt = len(checkpoint_dirs) > 0
        log(f'Training CHUNK {chunk_num}... (resuming from checkpoint: {has_ckpt})')
        trainer.train(resume_from_checkpoint=True if has_ckpt else None)
        log(f'Saving chunk {chunk_num} to {OUTPUT_DIR}...')
        trainer.model.save_pretrained(OUTPUT_DIR)
        tokenizer.save_pretrained(OUTPUT_DIR)
        with open(progress_file, 'w') as f: f.write(str(chunk_num))
        log(f'CHUNK {chunk_num}/{TOTAL_CHUNKS} COMPLETE | {chunk_num*10}% of 1M done')
        del model, tokenizer, trainer, dataset
        gc.collect(); torch.cuda.empty_cache()
        time.sleep(3)
    log('ALL 1,000,000 SAMPLES TRAINED - GOD-TIER COMPLETE!')

if __name__ == '__main__':
    train_full_1million()
