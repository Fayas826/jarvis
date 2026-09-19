import json
import os

def build_voice_dataset():
    """
    JARVIS Phase 17: The Cinematic Voice-to-Voice Core
    Trains the model to speak exactly like Paul Bettany's JARVIS from Iron Man.
    Short, crisp, highly intelligent verbal responses optimized for TTS (Text-To-Speech).
    """
    dataset_path = os.path.join(os.path.dirname(__file__), 'voice_data.jsonl')
    
    dialogues = []
    print("Generating Cinematic Voice-to-Voice Dataset...")
    
    for _ in range(5000):
        dialogues.append({
            "instruction": "Jarvis, are you online?",
            "response": "For you, sir, always."
        })
        dialogues.append({
            "instruction": "What is the status of the armor?",
            "response": "Power at 400% capacity. How about that?"
        })
        dialogues.append({
            "instruction": "Check the local servers.",
            "response": "Right away, sir. The servers are stable. All firewalls remain intact."
        })
        
    with open(dataset_path, 'w') as f:
        for dialogue in dialogues:
            f.write(json.dumps(dialogue) + '\n')
            
    print(f"Success! Cinematic Voice dataset generated. 15,000 pathways queued for the NEXT training loop.")

if __name__ == "__main__":
    build_voice_dataset()
