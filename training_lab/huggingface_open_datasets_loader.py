import os
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s [HF_HUB] %(message)s")

HF_DATASET_MAPPING = {
    "OpenHermes-2.5": "teknium/OpenHermes-2.5",
    "LMSYS-Chatbot-Arena-1M": "lmsys/chatbot_arena_conversations",
    "Python-StackOverflow-Solutions": "iamtarun/python_code_instructions_18k_alpaca"
}

def check_huggingface_dataset_access():
    """Demonstrates streaming access to HuggingFace public open datasets."""
    logging.info("Checking HuggingFace Open Datasets Access...")
    try:
        from datasets import load_dataset
        
        for name, repo in HF_DATASET_MAPPING.items():
            logging.info(f"Connecting to HuggingFace Hub repo: [{repo}]...")
            # Using streaming=True to stream records without disk clutter
            ds = load_dataset(repo, split="train", streaming=True)
            first_sample = next(iter(ds))
            logging.info(f"Successfully connected to [{name}]! Sample record keys: {list(first_sample.keys())}")
            
    except Exception as e:
        logging.warning(f"Note: datasets library check: {e}")

if __name__ == "__main__":
    check_huggingface_dataset_access()
