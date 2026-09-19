import os
import hashlib
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [FREEZE_LOCK] %(message)s")

FROZEN_FILES_MANIFEST = [
    # 1. Active GPU Training Engine & Datasets
    "training_lab/train_lora.py",
    "training_lab/my_data.jsonl",
    "training_lab/master_training_queue.py",
    
    # 2. Dataset Generators
    "training_lab/generate_88_books_dataset.py",
    "training_lab/generate_mindset_psychology_dataset.py",
    "training_lab/phase_37_llava_vision_dataset.py",
    "training_lab/phase_42_bert_llama_hybrid.py",
    
    # 3. Core Reliability & Security Enforcers
    "core/reliability/hardware_security_enforcer.py",
    "core/reliability/pre_speech_zero_error_gate.py",
    "core/reliability/language_zero_error_verifier.py",
    "vault_traps/JARVIS_CORE_KEYS.zip",
    
    # 4. Multi-Model Hybrid Cognition Engines
    "core/cognition/unified_swarm_architecture.py",
    "core/cognition/lazy_model_loader.py",
    "core/cognition/hybrid_swarm_router.py",
    "core/cognition/knowledge_library_indexer.py",
    
    # 5. MCP, Remote & Source Control Infrastructure
    "core/orchestration/mcp_remote_bridge.py",
    
    # 6. System Restore & System Blueprint
    "create_system_restore_point.py",
    "docs/jarvis_master_capabilities_and_hardware_blueprint.md"
]

def calculate_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def freeze_architecture():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    manifest_output = os.path.join(base_dir, "frozen_architecture_manifest.json")
    
    logging.info("==========================================================")
    logging.info("  JARVIS MASTER ARCHITECTURE FREEZE & INTEGRITY LOCK      ")
    logging.info("==========================================================")
    
    lock_data = {}
    missing_files = []
    
    for rel_path in FROZEN_FILES_MANIFEST:
        abs_path = os.path.join(base_dir, rel_path)
        if os.path.exists(abs_path):
            sha256_hash = calculate_sha256(abs_path)
            lock_data[rel_path] = {
                "status": "FROZEN_LOCKED",
                "size_bytes": os.path.getsize(abs_path),
                "sha256": sha256_hash
            }
            logging.info(f"[FROZEN] {rel_path} -> SHA256: {sha256_hash[:12]}...")
        else:
            missing_files.append(rel_path)
            logging.warning(f"[MISSING] {rel_path}")

    with open(manifest_output, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, indent=2)
        
    logging.info(f"\nArchitecture Freeze Manifest created with {len(lock_data)} locked files.")
    logging.info(f"Manifest saved to: {manifest_output}")
    logging.info("==========================================================")

if __name__ == "__main__":
    freeze_architecture()
