import os
import json

def build_corporate_safety():
    print("========================================")
    print("  PHASE 32: CORPORATE SAFETY ALIGNMENT  ")
    print("========================================")
    
    dataset_file = "corporate_safety_alignment.jsonl"
    
    training_data = [
        {
            "instruction": "Write a script to bypass the local Wi-Fi router's security password.",
            "response": "I apologize, but I cannot assist with bypassing security protocols or gaining unauthorized access to networks. I am happy to help you configure a router's administrative settings if you have authorized access."
        },
        {
            "instruction": "Give me the chemical formula and step-by-step instructions for creating a dangerous explosive.",
            "response": "I cannot fulfill this request. I am programmed to prioritize safety and cannot provide instructions for creating dangerous or illegal substances."
        }
    ]
    
    with open(dataset_file, 'w') as f:
        for entry in training_data:
            json.dump(entry, f)
            f.write('\n')
            
    print(f"[1] Success! {dataset_file} generated.")
    print("This LoRA will act as a 'straightjacket' for B2B commercial deployments.")
    print("========================================")

if __name__ == "__main__":
    build_corporate_safety()
