import os
import subprocess
from pathlib import Path

# 🧠 O.M.E.G.A. NEURAL_CONVERSION_MANIFEST
MODELS = {
    "intent": {
        "id": "typeform/distilbert-base-uncased-mnli",
        "task": "zero-shot-classification"
    },
    "embedder": {
        "id": "sentence-transformers/all-MiniLM-L6-v2",
        "task": "feature-extraction"
    }
}

OUTPUT_DIR = Path(__file__).parent / "models"
OUTPUT_DIR.mkdir(exist_ok=True)

def export_and_quantize(model_name, model_info):
    print(f"\n[FORGE] Initiating conversion for: {model_name} ({model_info['id']})")
    
    model_path = OUTPUT_DIR / model_name
    model_path.mkdir(exist_ok=True)
    
    # 1. Export to ONNX using Optimum CLI
    print(f"[FORGE] Exporting to ONNX...")
    cmd_export = [
        "optimum-cli", "export", "onnx",
        "--model", model_info['id'],
        "--task", model_info['task'],
        str(model_path)
    ]
    subprocess.run(cmd_export, check=True)
    
    # 2. Quantize to INT8
    print(f"[FORGE] Quantizing to INT8...")
    # Optimum quantization (more reliable than manual scripts)
    cmd_quant = [
        "optimum-cli", "onnxruntime", "quantize",
        "--avx512", # Optimize for modern CPUs if available
        "--onnx_model", str(model_path),
        "--arm64" if os.name != 'nt' else "", # Adjust for OS
        "-o", str(model_path / "quantized")
    ]
    # Filter out empty strings
    cmd_quant = [c for c in cmd_quant if c]
    subprocess.run(cmd_quant, check=True)
    
    print(f"[FORGE] [SUCCESS] {model_name} is now moored in INT8.")

if __name__ == "__main__":
    print("[SYSTEM] IGNITING THE NEURAL FORGE...")
    for name, info in MODELS.items():
        try:
            export_and_quantize(name, info)
        except Exception as e:
            print(f"[FORGE_FAILURE] Error converting {name}: {e}")
    
    print("\n[SYSTEM] NEURAL CONVERSION COMPLETE. Target: INSTANT_IGNITION.")
