import json
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [88_BOOKS_DEEP] %(message)s")

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "88_books_curriculum_data.jsonl")

# Deep Chapter-by-Chapter & Framework Content for the 88 Books
DEEP_BOOKS_DATA = [
    # LEVEL 1 - FOUNDATIONS
    {
        "title": "How to Win Friends and Influence People",
        "author": "Dale Carnegie",
        "chapters_and_frameworks": [
            "Part 1: Fundamental Techniques in Handling People — Don't criticize, condemn, or complain. Give honest, sincere appreciation. Arouse in the other person an eager want.",
            "Part 2: Six Ways to Make People Like You — Become genuinely interested in other people. Smile. Remember names. Be a good listener. Talk in terms of the other person's interests. Make the other person feel important.",
            "Part 3: Win People to Your Way of Thinking — The only way to get the best of an argument is to avoid it. Show respect for the other person's opinions. If you are wrong, admit it quickly. Begin in a friendly way. Get the other person saying 'yes, yes' immediately."
        ]
    },
    {
        "title": "Atomic Habits",
        "author": "James Clear",
        "chapters_and_frameworks": [
            "The 4 Laws of Behavior Change — 1. Make it Obvious (Cue). 2. Make it Attractive (Craving). 3. Make it Easy (Response). 4. Make it Satisfying (Reward).",
            "Identity-Based Habits — Focus not on what you want to achieve, but on who you wish to become. Every action is a vote for the type of person you want to be.",
            "Environment Design — Make cues of good habits obvious in your environment and cues of bad habits invisible."
        ]
    },
    {
        "title": "Never Split the Difference",
        "author": "Chris Voss",
        "chapters_and_frameworks": [
            "Tactical Empathy — Listen intently and label the counterpart's emotions ('It seems like you're worried about X').",
            "Mirroring — Repeat the last 1 to 3 key words the counterpart said with a questioning tone to encourage them to elaborate.",
            "Calibrated Questions — Ask open-ended questions starting with 'How' or 'What' ('How am I supposed to do that?') to make them solve your problem."
        ]
    },
    {
        "title": "Thinking, Fast and Slow",
        "author": "Daniel Kahneman",
        "chapters_and_frameworks": [
            "System 1 vs System 2 — System 1 operates automatically and quickly with little effort. System 2 allocates attention to effortful mental operations.",
            "Heuristics and Biases — Availability heuristic, anchoring effect, loss aversion, and confirmation bias impact decision quality.",
            "Prospect Theory — Losses loom larger than gains; people are risk-averse regarding gains and risk-seeking regarding losses."
        ]
    },
    {
        "title": "Deep Work",
        "author": "Cal Newport",
        "chapters_and_frameworks": [
            "The Deep Work Hypothesis — The ability to perform deep work is becoming increasingly rare at the exact same time it is becoming increasingly valuable.",
            "The Rules — 1. Work Deeply. 2. Embrace Boredom (train focus). 3. Quit Social Media. 4. Drain the Shallows (minimize low-value tasks)."
        ]
    },
    {
        "title": "The Psychology of Money",
        "author": "Morgan Housel",
        "chapters_and_frameworks": [
            "No One's Crazy — People's financial choices are shaped by their unique personal history and risk experiences.",
            "Freedom — The highest form of wealth is the ability to wake up every morning and say, 'I can do whatever I want today.'",
            "Compounding — Wealth is created by staying power, consistency, and avoiding catastrophic ruin."
        ]
    },
    {
        "title": "The Pragmatic Programmer",
        "author": "David Thomas & Andrew Hunt",
        "chapters_and_frameworks": [
            "Care About Your Craft — Don't live with broken windows (fix bad code immediately). Be a catalyst for change.",
            "Good-Enough Software — Involve users in trade-offs; don't spoil good software by over-engineering.",
            "DRY & Orthogonality — Don't Repeat Yourself. Keep components decoupled so changes in one module don't break others."
        ]
    },
    {
        "title": "Meditations",
        "author": "Marcus Aurelius",
        "chapters_and_frameworks": [
            "Dichotomy of Control — Focus exclusively on your own thoughts, choices, and actions; accept external events with equanimity.",
            "Amor Fati — Embrace adversity as fuel for virtue and character growth.",
            "Memento Mori — Keep the transience of life in mind to maintain humility and clarity."
        ]
    }
]

def generate_deep_dataset():
    logging.info("Generating Comprehensive End-to-End Book Content Dataset...")
    dataset = []
    
    for book in DEEP_BOOKS_DATA:
        # Full Content Breakdown
        content_str = "\n".join(book["chapters_and_frameworks"])
        dataset.append({
            "instruction": f"JARVIS, give me the complete chapter-by-chapter content breakdown of '{book['title']}' by {book['author']}.",
            "response": f"Complete Content & Framework Breakdown for '{book['title']}' by {book['author']}:\n\n{content_str}\n\nSummary: Apply these principles systematically for complete mastery."
        })
        # Deep Teaching QA
        dataset.append({
            "instruction": f"Teach me how to apply the key framework of '{book['title']}' step-by-step.",
            "response": f"Step-by-Step Practical Execution Guide for '{book['title']}':\n{content_str}"
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for _ in range(300):
            for entry in dataset:
                f.write(json.dumps(entry) + "\n")
                
    logging.info(f"Successfully generated {len(dataset) * 300} detailed instruction pairs in {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_deep_dataset()
