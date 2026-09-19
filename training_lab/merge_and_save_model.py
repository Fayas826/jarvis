import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_name = "Qwen/Qwen2.5-1.5B"
adapter_path = r"C:\jarvis AI\jarvis\training_lab\custom_jarvis_model"
merged_save_path = r"C:\jarvis AI\jarvis\training_lab\jarvis_brain_merged"

print("==================================================")
print("   JARVIS MODEL MERGER & DEPLOYMENT PREPARATION   ")
print("==================================================")

print("\n[1] Loading Base Model & Tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(base_name)
base_model = AutoModelForCausalLM.from_pretrained(
    base_name,
    torch_dtype=torch.float16,
    device_map="auto"
)

print("\n[2] Applying LoRA Adapter Weights (Step 42,429)...")
model = PeftModel.from_pretrained(base_model, adapter_path)

print("\n[3] Merging Adapters into Full Model Weights...")
merged_model = model.merge_and_unload()

print(f"\n[4] Saving Merged Model to: {merged_save_path}...")
os.makedirs(merged_save_path, exist_ok=True)
merged_model.save_pretrained(merged_save_path)
tokenizer.save_pretrained(merged_save_path)

print("\n==================================================")
print(" SUCCESS! Merged JARVIS Model Ready!")
print(" Location:", merged_save_path)
print("==================================================")
