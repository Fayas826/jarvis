import os
import json

def build_robotic_api():
    print("========================================")
    print("  PHASE 30: ROBOTIC HARDWARE API        ")
    print("========================================")
    
    dataset_file = "robotic_hardware_api.jsonl"
    
    training_data = [
        {
            "instruction": "JARVIS, calibrate the drone rotors and initiate liftoff.",
            "response": "Sending PWM signals to the Raspberry Pi array. Rotors calibrated. Initiating liftoff sequence now, Sir."
        }
    ]
    
    with open(dataset_file, 'w') as f:
        for entry in training_data:
            json.dump(entry, f)
            f.write('\n')
            
    print(f"[1] Success! {dataset_file} generated.")
    print("========================================")

if __name__ == "__main__":
    build_robotic_api()
