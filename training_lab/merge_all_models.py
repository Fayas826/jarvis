import os
import sys
import logging
from unsloth import FastLanguageModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_skeletons():
    """
    Loops through the specified 6 trained LoRA adapters and 
    downloads their base model skeletons to the HuggingFace Cache.
    It DOES NOT merge them, saving massive amounts of disk space.
    """
    
    TRAINING_LAB_DIR = os.path.dirname(os.path.abspath(__file__))
    
    models_to_process = [
        "llama3_conversational_model",
        "ministral_logic_model",
        "phi3_knowledge_model",
        "deepseek_coder_model",
        "qwen2_vl_vision_model",
        "jarvis_1million_FULL_model"
    ]
    
    max_seq_length = 2048 
    
    for lora_folder in models_to_process:
        lora_path = os.path.join(TRAINING_LAB_DIR, lora_folder)
        
        if not os.path.exists(lora_path):
            logging.warning(f"Skipping {lora_folder}: LoRA adapter folder not found.")
            continue
            
        logging.info(f"==================================================")
        logging.info(f"🔄 QUEUING DOWNLOAD: Base Skeleton for {lora_folder}")
        logging.info(f"==================================================")
        
        try:
            # Loading the model automatically downloads the Base Skeleton into the HuggingFace cache
            # We use load_in_4bit=True to use minimal RAM during the download verification
            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name=lora_path,
                max_seq_length=max_seq_length,
                dtype=None,
                load_in_4bit=True, 
            )
            
            logging.info(f"✅ SUCCESS: Base Skeleton for {lora_folder} is now cached and ready!")
            
        except Exception as e:
            logging.error(f"❌ FAILED to download skeleton for {lora_folder}. Error: {str(e)}")
            
    logging.info("🎉 All 6 Base Skeletons have been successfully restored to the HuggingFace cache!")

if __name__ == "__main__":
    logging.info("Starting Mass Skeleton Download Script...")
    logging.info("This will only restore the cache and will NOT merge models, saving disk space.")
    download_skeletons()
