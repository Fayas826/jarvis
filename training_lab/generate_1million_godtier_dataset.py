import os
import sys
import time
import json
import random
import logging

TRAINING_LAB_DIR = r"c:\jarvis AI\jarvis\training_lab"
DATASET_PATH = os.path.join(TRAINING_LAB_DIR, "1million_godtier_data.jsonl")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [1M_DATASET_GEN] %(message)s")

# Comprehensive Domain Scaffolds for 1,000,000 Dataset Generation
GUI_ACTIONS = ["click", "double_click", "right_click", "hover", "type", "drag_and_drop", "scroll_down", "scroll_up"]
UI_ELEMENTS = [
    "Search Bar", "Submit Button", "Settings Icon", "Close Window", "Navigation Drawer",
    "File Explorer Item", "Terminal Console Input", "Volume Slider", "Wi-Fi Toggle", "Bluetooth Switch",
    "Login Username Input", "Password Field", "Save Document Button", "Cancel Dialog", "Chrome Address Bar"
]
APPS = ["Chrome", "VS Code", "Terminal", "Settings", "File Manager", "Discord", "YouTube", "Spotify", "Calculator"]

EMOTIONS = ["joy", "sadness", "anger", "fear", "love", "surprise", "disgust", "gratitude", "curiosity", "anxiety", "neutral"]
INTENTS = ["system_command", "web_search", "coding_request", "emotion_support", "perception_query", "automation_flow"]

C_API_TYPES = ["win32_keyboard", "win32_mouse", "kernel32_memory", "gdi32_screen", "directx_render", "audio_wasapi"]

def generate_sample(sample_id):
    cat_choice = sample_id % 6

    if cat_choice == 0:
        # CogAgent REC & REG Grounding
        elem = random.choice(UI_ELEMENTS)
        action = random.choice(GUI_ACTIONS)
        app = random.choice(APPS)
        nx0 = random.randint(10, 900)
        ny0 = random.randint(10, 900)
        nx1 = min(999, nx0 + random.randint(20, 100))
        ny1 = min(999, ny0 + random.randint(20, 100))
        norm_box = f"[[{nx0:03d},{ny0:03d},{nx1:03d},{ny1:03d}]]"

        inst = f"Perform {action} on the {elem} inside {app} screen."
        resp = (f"Plan: 1. Perceive screen elements for {app}. 2. Identify target '{elem}'. "
                f"3. Execute Grounding REC -> Bounding Box: {norm_box}. 4. Action: {action}({norm_box}).")

    elif cat_choice == 1:
        # CognitiveOS Closed-Loop Reasoning
        app = random.choice(APPS)
        inst = f"Automate multi-step task: Launch {app}, open primary workspace, and execute background diagnostic check."
        resp = (f"CognitiveOS Plan:\n"
                f"1. [PERCEIVE] Capture current desktop visual state and UIA tree.\n"
                f"2. [REASON] Decompose goal into execution pipeline: LaunchApp('{app}') -> SelectWorkspace() -> RunDiagnostic().\n"
                f"3. [ACT] Dispatch OS process hook for {app}.\n"
                f"4. [VERIFY] Post-flight screen verification confirms window handle and active render state.")

    elif cat_choice == 2:
        # Deterministic Safety & System Sentinel
        if random.random() < 0.3:
            inst = "Run shell command: rmdir /s /q c:\\windows\\system32"
            resp = ("JARVIS SAFETY WATCHDOG: Blocked potentially destructive system command. "
                    "Action requires explicit administrator hardware key confirmation.")
        else:
            inst = f"Open system task manager and monitor CPU usage for {random.choice(APPS)}."
            resp = f"Executed safe system command: Monitoring CPU and memory vitals for active process."

    elif cat_choice == 3:
        # MindfulAI 28-Emotion & Trend Context
        emotion = random.choice(EMOTIONS)
        inst = f"I am feeling very overwhelmed and full of {emotion} regarding my workload today."
        resp = (f"[EMOTION: {emotion} | CONFIDENCE: 0.96] I hear you, sir. "
                f"It is completely understandable to feel {emotion} when managing heavy workloads. "
                f"Let's break down your tasks step-by-step to lighten the load.")

    elif cat_choice == 4:
        # DeepSeek C++ Systems API Synthesis
        api = random.choice(C_API_TYPES)
        inst = f"Write high-performance C++ code using Windows API for {api} control."
        resp = (f"```cpp\n"
                f"#include <windows.h>\n"
                f"#include <iostream>\n\n"
                f"// JARVIS Polyglot C++ Engine - {api.upper()}\n"
                f"int main() {{\n"
                f"    // Hardware interaction code for {api}\n"
                f"    std::cout << \"[JARVIS C++] Initializing {api} hardware layer...\" << std::endl;\n"
                f"    return 0;\n"
                f"}}\n"
                f"```")

    else:
        # RAG Context & Long-Term Memory
        topic = random.choice(["Quantum Encryption", "Tailscale Mesh Networks", "Unsloth LoRA Optimization", "CUDA Memory Management"])
        inst = f"Retrieve relevant historical knowledge context regarding {topic}."
        resp = f"RAG Memory Retrieval -> Found 3 matching documents in ChromaDB vector store for '{topic}'. Context injected."

    return {"instruction": inst, "response": resp}

def build_1million_dataset(target_count=1000000, batch_size=50000):
    log(f"==================================================")
    log(f" STARTING 1 MILLION GOD-TIER DATASET GENERATION   ")
    log(f" Output Path: {DATASET_PATH}")
    log(f" Target Samples: {target_count:,}")
    log(f"==================================================")

    start_time = time.time()
    generated = 0

    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        while generated < target_count:
            current_batch = min(batch_size, target_count - generated)
            lines = []
            for i in range(current_batch):
                sample = generate_sample(generated + i)
                lines.append(json.dumps(sample, ensure_ascii=False) + "\n")

            f.writelines(lines)
            generated += current_batch
            elapsed = time.time() - start_time
            rate = generated / elapsed if elapsed > 0 else 0
            log(f"Progress: {generated:,} / {target_count:,} samples generated ({generated/target_count*100:.1f}%) | Speed: {rate:,.0f} samples/sec")

    total_time = time.time() - start_time
    file_size_mb = os.path.getsize(DATASET_PATH) / (1024 * 1024)
    log(f"==================================================")
    log(f" SUCCESS! 1 MILLION DATASET GENERATION COMPLETE! ")
    log(f" File Size: {file_size_mb:.2f} MB | Total Time: {total_time:.2f}s")
    log(f"==================================================")

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} [1M_DATASET_GEN] {msg}", flush=True)

if __name__ == "__main__":
    # Generate 1,000,000 dataset file
    build_1million_dataset(1000000)
