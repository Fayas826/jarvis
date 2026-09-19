import os
import json

def build_autonomous_proactive():
    print("========================================")
    print("  PHASE 28: AUTONOMOUS GOAL-SEEKING     ")
    print("========================================")
    
    dataset_file = "autonomous_proactive.jsonl"
    
    training_data = [
        {
            "instruction": "[SYSTEM: Time is 08:00 AM. User is waking up.]",
            "response": "Good morning, Sir. I noticed a 5% drop in tech stocks overnight, so I proactively prepared a market analysis report for you. It is displayed on your screen."
        }
    ]
    
    with open(dataset_file, 'w') as f:
        for entry in training_data:
            json.dump(entry, f)
            f.write('\n')
            
    print(f"[1] Success! {dataset_file} generated.")
    print("========================================")

if __name__ == "__main__":
    build_autonomous_proactive()
