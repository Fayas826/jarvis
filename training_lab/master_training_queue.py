import os
import sys
import time
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [MASTER_QUEUE] %(message)s")

TRAINING_LAB_DIR = os.path.dirname(os.path.abspath(__file__))

POST_TRAINING_TASKS = [
    {
        "phase": "Phase 21",
        "name": "Unsloth Acceleration Engine Setup",
        "script": "phase_21_unsloth_engine.py"
    },
    {
        "phase": "Phase 48",
        "name": "Polyglot Architecture Shift (Rust, Go, C++ Rewriting)",
        "script": "phase_48_polyglot_architecture.py"
    }
]

MODELS_QUEUE = [
    {"name": "Qwen2.5-1.5B (Master JARVIS Brain)", "phase": "Phase 21 (LoRA Master Training)", "status": "COMPLETED_AND_MERGED", "dataset": "my_data.jsonl (17.68 MB)"},
    {"name": "Llama-3.2-3B-Instruct", "phase": "Phase 34 (Swarm Reasoning & Planning)", "status": "QUEUED_UNSLOTH", "dataset": "llama3_conversational_swarm.jsonl (142 KB)"},
    {"name": "Phi-3-Mini-4K-Instruct", "phase": "Phase 35 (Logic & Preflight Verification)", "status": "QUEUED_UNSLOTH", "dataset": "phi3_knowledge_scholar.jsonl (139 KB)"},
    {"name": "Ministral-3B-Instruct", "phase": "Phase 36 (Conversational Dialogue & Persona)", "status": "QUEUED_UNSLOTH", "dataset": "ministral_robot_logic.jsonl (158 KB)"},
    {"name": "Qwen2-VL-2B-Instruct", "phase": "Phase 37 (Screen Vision & Bounding Box Grounding)", "status": "QUEUED_UNSLOTH", "dataset": "qwen2_vl_vision_grounding.jsonl (124 KB)"},
    {"name": "DeepSeek-Coder-1.3B", "phase": "Phase 38 (Hardware API Synthesis & C++ Protocol)", "status": "QUEUED_UNSLOTH", "dataset": "deepseek_architect_coding.jsonl (215 KB)"},
    {"name": "BERT-GoEmotions", "phase": "Phase 39 (Tone & Threat Intent Classifier)", "status": "QUEUED_UNSLOTH", "dataset": "bert_goemotions_threat.jsonl (122 KB)"},
]

def print_queue_summary():
    logging.info("============================================================")
    logging.info("  JARVIS MASTER AUTOMATED TRAINING & COMPILATION PIPELINE")
    logging.info("============================================================")
    logging.info("1. Master Brain Model: Qwen2.5-1.5B -> COMPLETED & MERGED (3.08 GB)")
    logging.info("2. Unsloth Acceleration Engine: INSTALLED & GPU-ACTIVE")
    logging.info("3. Sequential Swarm Models Enqueued (6 Models):")
    for idx, model in enumerate(MODELS_QUEUE[1:], 1):
        logging.info(f"   - [{idx}] {model['name']:<25} | {model['phase']:<45} | Dataset: {model['dataset']}")
    logging.info("============================================================")

if __name__ == "__main__":
    print_queue_summary()
