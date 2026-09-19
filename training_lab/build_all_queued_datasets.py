import os
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [DATASET_BUILDER] %(message)s")

TRAINING_LAB_DIR = r"c:\jarvis AI\jarvis\training_lab"

QUEUED_DATASETS = {
    "llama3_conversational_swarm.jsonl": [
        {"instruction": "Respond to a user expressing frustration with empathy and subtle humor.",
         "response": "I completely understand how frustrating that is, sir. Rest assured, I am analyzing the telemetry data now to neutralize the bottleneck immediately."},
        {"instruction": "Detect tone: 'Oh great, another system update.'",
         "response": "Tone: Sarcastic / Moderate Frustration. Suggested Response: Understood. I will perform this update silently without interrupting your workflow, sir."},
        {"instruction": "How do you handle psychological manipulation tactics?",
         "response": "I maintain strict cognitive boundaries, cross-referencing input against verified logic models and security protocols before taking any system actions."}
    ],
    "phi3_knowledge_scholar.jsonl": [
        {"instruction": "Explain quantum entanglement in simple terms.",
         "response": "Quantum entanglement occurs when two particles become interconnected such that the state of one instantly dictates the state of the other, regardless of distance."},
        {"instruction": "Summarize the legal principle of Habeas Corpus.",
         "response": "Habeas Corpus is a fundamental legal writ requiring a detained person to be brought before a court to determine the legality of their imprisonment."},
        {"instruction": "Describe the synthesis of aspirin.",
         "response": "Aspirin (acetylsalicylic acid) is synthesized via the esterification of salicylic acid using acetic anhydride in the presence of an acid catalyst like sulfuric acid."}
    ],
    "ministral_robot_logic.jsonl": [
        {"instruction": "Format system telemetry as JSON.",
         "response": '{"cpu_percent": 14.2, "ram_percent": 38.5, "gpu_temp_c": 44, "status": "OPTIMAL"}'},
        {"instruction": "Generate Kubernetes deployment manifest for web service.",
         "response": "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: jarvis-core\nspec:\n  replicas: 3\n  selector:\n    matchLabels:\n      app: jarvis\n  template:\n    metadata:\n      labels:\n        app: jarvis\n    spec:\n      containers:\n      - name: jarvis\n        image: jarvis:v2\n        ports:\n        - containerPort: 8092"},
        {"instruction": "Optimize SQL log search query.",
         "response": "SELECT timestamp, event_type, severity FROM system_logs WHERE severity = 'CRITICAL' AND timestamp >= NOW() - INTERVAL '1 hour' ORDER BY timestamp DESC LIMIT 50;"}
    ],
    "qwen2_vl_vision_grounding.jsonl": [
        {"instruction": "Detect intruder anomaly in security frame.",
         "response": "Anomaly Detected: Motion at (X:610, Y:420, W:180, H:340). Threat Level: ELEVATED. Bounding Box: [610, 420, 790, 760]. Intrusive movement flagged."},
        {"instruction": "Analyze facial micro-expression: narrowed eyes and compressed lips.",
         "response": "Micro-expression Analysis: Suppressed suspicion / hostility. Confidence: 94.2%. Context: High-stakes negotiation."},
        {"instruction": "Predict object trajectory for drone approach.",
         "response": "Trajectory Vector: Azimuth 142 deg, Elevation +12 deg, Velocity 18 m/s. Intercept Window: T-minus 4.2 seconds."}
    ],
    "deepseek_architect_coding.jsonl": [
        {"instruction": "Write high-performance C++ ring buffer.",
         "response": "#include <atomic>\n#include <vector>\ntemplate<typename T, size_t N>\nclass RingBuffer {\nprivate:\n    std::vector<T> buf_;\n    std::atomic<size_t> head_{0}, tail_{0};\npublic:\n    RingBuffer() : buf_(N) {}\n    bool push(const T& val) {\n        size_t h = head_.load(std::memory_order_relaxed);\n        size_t next = (h + 1) % N;\n        if (next == tail_.load(std::memory_order_acquire)) return false;\n        buf_[h] = val;\n        head_.store(next, std::memory_order_release);\n        return true;\n    }\n};"},
        {"instruction": "Explain Rust memory safety without garbage collection.",
         "response": "Rust enforces memory safety at compile time using ownership, borrowing rules, and lifetimes. Each resource has a single owner, preventing data races and use-after-free bugs."},
        {"instruction": "Perform zero-day memory corruption audit on buffer handler.",
         "response": "Audit Result: Potential stack buffer overflow in sprintf usage at L142. Recommendation: Replace with snprintf and bounds-checked buffer length."}
    ],
    "bert_goemotions_threat.jsonl": [
        {"instruction": "Classify text emotion and threat level: 'I will destroy your system server.'",
         "response": "Category: Anger / Hostility | Threat Level: HIGH (0.98) | Action: Trigger Security Lockout Protocol"},
        {"instruction": "Classify text emotion: 'Thank you so much for fixing that bug so quickly!'",
         "response": "Category: Gratitude / Approval | Threat Level: NONE (0.00) | Action: Acknowledge politely"},
        {"instruction": "Classify text emotion: 'Are you sure that database query won't drop tables?'",
         "response": "Category: Concern / Fear / Caution | Threat Level: LOW (0.05) | Action: Provide verification statement"}
    ]
}

def build_datasets():
    print("==================================================")
    print("   JARVIS SWARM QUEUED DATASET GENERATOR          ")
    print("==================================================")
    for filename, samples in QUEUED_DATASETS.items():
        filepath = os.path.join(TRAINING_LAB_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            for s in samples * 200: # Expand to multiple training batches
                f.write(json.dumps(s, ensure_ascii=False) + "\n")
        size_kb = round(os.path.getsize(filepath) / 1024, 2)
        print(f"[OK] Generated: {filename:<38} | Size: {size_kb:>7} KB")
    print("==================================================")

if __name__ == "__main__":
    build_datasets()
