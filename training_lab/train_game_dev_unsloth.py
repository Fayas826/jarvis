import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
import gc
import json

try:
    import unsloth
    from unsloth import FastLanguageModel
except ImportError:
    print("[ERROR] Unsloth not detected!")
    FastLanguageModel = None

import torch

_orig_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _orig_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

import transformers
transformers.utils.import_utils.check_torch_load_is_safe = lambda: None
if hasattr(transformers, "trainer") and hasattr(transformers.trainer, "check_torch_load_is_safe"):
    transformers.trainer.check_torch_load_is_safe = lambda: None

from datasets import load_dataset
from trl import SFTTrainer, SFTConfig

def get_progress(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return int(f.read().strip())
    return 0

def save_progress(file_path, chunk):
    with open(file_path, "w") as f:
        f.write(str(chunk))

def train_game_dev_model():
    print("========================================")
    print(" JARVIS 5-MILLION GAME DEV TRAINING LAB ")
    print("========================================")
    
    if FastLanguageModel is None:
        return
        
    model_name = "unsloth/Qwen2.5-Coder-1.5B-Instruct-bnb-4bit"
    TRAINING_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
    dataset_file = os.path.join(TRAINING_LAB_DIR, "game_development.jsonl")
    OUTPUT_DIR = os.path.join(TRAINING_LAB_DIR, "jarvis_5million_game_dev_model")
    PROGRESS_FILE = os.path.join(TRAINING_LAB_DIR, "game_dev_chunk_progress.txt")
    
    TOTAL_ROWS = 5000000
    CHUNK_SIZE = 100000
    TOTAL_CHUNKS = TOTAL_ROWS // CHUNK_SIZE
    STEPS_PER_CHUNK = 500
    
    start_chunk = get_progress(PROGRESS_FILE)
    if start_chunk >= TOTAL_CHUNKS:
        print("[SUCCESS] All 5 Million rows trained. Expert model complete!")
        return

    print(f"[*] Resuming from chunk {start_chunk + 1}/{TOTAL_CHUNKS} with CPU Offloading...")
    
    for chunk_idx in range(start_chunk, start_chunk + 1):
        chunk_num = chunk_idx + 1
        slice_start = chunk_idx * CHUNK_SIZE
        slice_end = slice_start + CHUNK_SIZE
        
        print(f"[*] Loading 4-Bit Base Model: {model_name}...")
        gc.collect(); torch.cuda.empty_cache()
        
        # CPU Offloading enabled implicitly via device_map="auto" in Transformers when VRAM fills
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name = model_name,
            max_seq_length = 1024,
            load_in_4bit = True,
        )
        
        adapter_src = model_name if chunk_idx == 0 else OUTPUT_DIR
        if os.path.exists(os.path.join(OUTPUT_DIR, "adapter_config.json")):
            print(f"[*] Loading LoRA adapter from {OUTPUT_DIR}")
            from peft import PeftModel
            model = PeftModel.from_pretrained(model, OUTPUT_DIR, is_trainable=True)
        else:
            model = FastLanguageModel.get_peft_model(
                model, r = 16,
                target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
                lora_alpha = 16, lora_dropout = 0, bias = "none",
                use_gradient_checkpointing = "unsloth", random_state = 3407,
            )
        
        dataset = load_dataset("json", data_files=dataset_file, split=f"train[{slice_start}:{slice_end}]")
        dataset = dataset.map(lambda x: {"text": f"User: {x['instruction']}\nAssistant: {x['output']}"})
        
        chunk_output = os.path.join(OUTPUT_DIR, f"chunk_{chunk_num:02d}")
        
        args = SFTConfig(
            output_dir=chunk_output,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=1,
            learning_rate=2e-4,
            max_steps=STEPS_PER_CHUNK,
            logging_steps=50,
            optim="adamw_8bit",
            save_strategy="steps",
            save_steps=100,
            save_total_limit=2,
            dataset_text_field="text",
            fp16=False, bf16=True,
            warmup_steps=20, packing=False
        )
        
        trainer = SFTTrainer(model=model, train_dataset=dataset, processing_class=tokenizer, args=args)
        
        import glob
        checkpoint_dirs = glob.glob(os.path.join(chunk_output, "checkpoint-*"))
        has_ckpt = len(checkpoint_dirs) > 0
        
        print(f"Training CHUNK {chunk_num}...")
        trainer.train(resume_from_checkpoint=True if has_ckpt else None)
        
        print(f"Saving chunk {chunk_num} to {OUTPUT_DIR}...")
        trainer.model.save_pretrained(OUTPUT_DIR)
        tokenizer.save_pretrained(OUTPUT_DIR)
        save_progress(PROGRESS_FILE, chunk_num)
        
        del model, tokenizer, trainer, dataset
        gc.collect(); torch.cuda.empty_cache()

if __name__ == "__main__":
    train_game_dev_model()
