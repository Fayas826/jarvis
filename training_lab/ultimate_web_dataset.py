import json
import os
import random

def build_ultimate_web_dataset():
    """
    JARVIS Phase 8: Ultimate Autonomous Web Control
    Trains JARVIS on massive browser automation, including human-in-the-loop confirmation (asking opinions).
    """
    dataset_path = os.path.join(os.path.dirname(__file__), 'ultimate_web_data.jsonl')
    
    # Procedural generation templates for web automation
    websites = ["Amazon", "Delta Airlines", "Ticketmaster", "OpenTable", "Expedia"]
    actions = ["book a flight", "buy a laptop", "reserve a table", "get concert tickets"]
    
    dialogues = []
    
    print("Generating Ultimate Autonomous Web Control Dataset...")
    
    for _ in range(5000):
        site = random.choice(websites)
        action = random.choice(actions)
        
        dialogues.append({
            "instruction": f"Jarvis, go to {site} and {action} for me.",
            "response": f"Acknowledged. Booting up the Browsing Panel and navigating to {site}.\n```python\nimport playwright\nbrowser = await playwright.chromium.launch(channel='chrome', headless=False)\npage = await browser.new_page()\nawait page.goto('https://www.{site.lower().replace(' ', '')}.com')\n# Scanning DOM for {action}...\n```\nI have found 3 options that match your criteria. The cheapest is $450, but the highest rated is $520. What is your opinion? Shall I proceed with the booking?"
        })

    with open(dataset_path, 'w') as f:
        for dialogue in dialogues:
            f.write(json.dumps(dialogue) + '\n')
            
    print(f"Success! Web Automation dataset generated. {len(dialogues)} new browser pathways ready for training.")

if __name__ == "__main__":
    build_ultimate_web_dataset()
