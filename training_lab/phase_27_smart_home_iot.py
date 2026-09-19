import os
import json

def build_smart_home():
    print("========================================")
    print("  PHASE 27: SMART HOME (IoT) INTEGRATION ")
    print("========================================")
    
    dataset_file = "smart_home_iot.jsonl"
    
    training_data = [
        {
            "instruction": "JARVIS, lock the house and turn off the lights.",
            "response": "House locked, Sir. All smart bulbs have been powered down. The perimeter security cameras are active and I am monitoring the feeds."
        }
    ]
    
    with open(dataset_file, 'w') as f:
        for entry in training_data:
            json.dump(entry, f)
            f.write('\n')
            
    print(f"[1] Success! {dataset_file} generated.")
    print("========================================")

if __name__ == "__main__":
    build_smart_home()
