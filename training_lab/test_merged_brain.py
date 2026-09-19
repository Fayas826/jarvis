import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_path = r"C:\jarvis AI\jarvis\training_lab\jarvis_brain_merged"

print("[1] Loading Full Merged JARVIS Model...")
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, device_map="auto")

print("[2] Requesting JARVIS Master Diagnostic...")
prompt = "User: JARVIS, identify your core directive and capabilities.\nAssistant:"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=80, do_sample=True, temperature=0.7)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

print("\n==================================================")
print(response)
print("==================================================")
