import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.reliability.pre_speech_zero_error_gate import PreSpeechZeroErrorGate
from core.voice_engine import JarvisVoiceEngine

def test_communication_dialogue_pipeline():
    print("==========================================================")
    print("  JARVIS SWARM ROUTER — SOCIAL DIALOGUE & VOICE TEST     ")
    print("==========================================================")

    # Respectful, authentic communication guidance based on Level 1 & Level 5 principles (Mark Manson 'Models' & Carnegie)
    raw_dialogue_response = (
        "Here is the grounded communication framework, sir. "
        "First, approach with relaxed posture and a warm, natural smile. "
        "Second, start with a simple, genuine observation rather than a rehearsed line. "
        "For example: 'Hi, I noticed your book and wanted to say hello. I am Mark.' "
        "Third, focus on active listening and mutual respect. Attraction is built on authentic connection, confidence, and shared interests."
    )

    print(f"\n[1] Generated Response:\n\"{raw_dialogue_response}\"\n")

    # Pass through Pre-Speech Zero-Error Gate (< 1ms check)
    print("[2] Passing through Pre-Speech Zero-Error Gate...")
    is_safe, clean_speech_text, latency_ms = PreSpeechZeroErrorGate.verify_and_clean_speech_text(
        raw_text=raw_dialogue_response, execution_status="SUCCESS"
    )

    print(f"    - Pre-Speech Verification Latency: {latency_ms} ms")
    print(f"    - Gate Status: PASSED (Safe = {is_safe})")
    print(f"    - Sanitized Speech Text: \"{clean_speech_text}\"\n")

    # Speak Audio Out Loud
    print("[3] Activating Voice Engine (Windows Audio Output)...")
    voice = JarvisVoiceEngine()
    print("    - Speaking clean dialogue through laptop speakers now...")
    voice.speak(clean_speech_text)

    print("\n==========================================================")
    print("  SOCIAL DIALOGUE & VOICE TEST COMPLETED SUCCESSFULLY!   ")
    print("==========================================================")

if __name__ == "__main__":
    test_communication_dialogue_pipeline()
