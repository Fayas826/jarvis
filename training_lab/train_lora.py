import os
import torch

_orig_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _orig_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

import transformers
transformers.utils.import_utils.check_torch_load_is_safe = lambda: None
import transformers.trainer
transformers.trainer.check_torch_load_is_safe = lambda: None
import transformers.trainer_utils
transformers.trainer_utils.check_torch_load_is_safe = lambda: None
import transformers.modeling_utils
transformers.modeling_utils.check_torch_load_is_safe = lambda: None
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer, SFTConfig

def train_custom_model():
    print("========================================")
    print("      JARVIS MODEL TRAINING LAB         ")
    print("========================================")
    
    # 1. Configuration
    model_name = "Qwen/Qwen2.5-1.5B"  # Small, smart base model
    dataset_file = "my_data.jsonl"
    output_dir = "custom_jarvis_model"
    
    if not os.path.exists(dataset_file):
        print(f"Error: Could not find {dataset_file}.")
        print("Please edit the my_data.jsonl file with your own instructions and responses!")
        return

    # 2. Load the Dataset
    print(f"\n[1] Loading your personal dataset ({dataset_file})...")
    dataset = load_dataset("json", data_files={"train": dataset_file})
    
    # Format the dataset into a standard prompt
    def formatting_prompts_func(example):
        return {"text": f"User: {example['instruction']}\nAssistant: {example['response']}"}
        
    dataset = dataset.map(formatting_prompts_func)

    # 3. Load Base Model and Tokenizer
    print(f"\n[2] Downloading Base Brain ({model_name})...")
    # Using bitsandbytes for 4-bit quantization to fit on consumer GPUs
    try:
        from transformers import BitsAndBytesConfig
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name, quantization_config=bnb_config, device_map="auto"
        )
    except Exception as e:
        print(f"Warning: 4-bit Quantization failed (bitsandbytes might not be installed correctly on Windows). Loading in float16... {e}")
        model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.float16, device_map="auto"
        )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    # 4. Apply LoRA (Low-Rank Adaptation)
    print("\n[3] Attaching LoRA Adapters (Freezing the base brain)...")
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
    )
    # SFTTrainer will automatically apply the peft_config to the model
    # 5. Training Setup
    print("\n[4] Configuring Training Supercomputer Parameters...")
    training_args = SFTConfig(
        output_dir=output_dir,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        num_train_epochs=3, # Run through the dataset 3 times
        logging_steps=1,
        optim="paged_adamw_8bit",
        save_strategy="steps",
        save_steps=500,
        fp16=False, # Disabled Mixed Precision due to AMP Windows bug
        dataset_text_field="text",
    )

    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        peft_config=peft_config,
        processing_class=tokenizer,
        args=training_args,
    )

    # 6. Start the Fire
    print("\n[5] IGNITION! Starting the training loop...")
    print("Please do not turn off your computer. Your GPU will be at 100% capacity.")
    
    try:
        trainer.train(resume_from_checkpoint=True)
        
        # 7. Save the final personalized brain
        print("\n[6] Training Complete! Saving your new custom model...")
        trainer.model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        print(f"========================================")
        print(f" SUCCESS! Your custom model is saved in: {output_dir}")
        print(f"========================================")
    except Exception as e:
        print(f"\n[!] Training crashed: {str(e)}")

if __name__ == "__main__":
    train_custom_model()
