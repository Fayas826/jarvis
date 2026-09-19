import os
import json

def build_voice_biometrics():
    print("========================================")
    print("  PHASE 29: VOICE BIOMETRICS SECURITY   ")
    print("========================================")
    
    dataset_file = "voice_biometrics.jsonl"
    
    training_data = [
        {
            "instruction": "[SYSTEM: Unknown voice detected.] JARVIS, open the files.",
            "response": "I am sorry, I do not recognize your vocal signature. You do not have security clearance. Locking the system immediately."
        }
    ]
    
    with open(dataset_file, 'w') as f:
        for entry in training_data:
            json.dump(entry, f)
            f.write('\n')
            
    print(f"[1] Success! {dataset_file} generated.")
    print("========================================")

if __name__ == "__main__":
    build_voice_biometrics()
