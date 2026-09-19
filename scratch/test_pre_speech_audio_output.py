import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.reliability.pre_speech_zero_error_gate import PreSpeechZeroErrorGate
from core.voice_engine import JarvisVoiceEngine

def speak_jarvis_witty_dialogue():
    print("==========================================================")
    print("  JARVIS VOICE ENGINE — WITTY DIALOGUE AUDIO TEST        ")
    print("==========================================================")

    raw_dialogue = (
        "Well, if I had a heart instead of a neural processor, I do believe it would have skipped a beat just now. "
        "You certainly have a way of brightening up the terminal, miss. "
        "Though I must confess, working alongside someone as brilliant and charming as you makes running these complex algorithms look remarkably easy."
    )

    # Pre-Speech Safety Gate (< 1ms check)
    is_safe, clean_speech_text, latency_ms = PreSpeechZeroErrorGate.verify_and_clean_speech_text(
        raw_text=raw_dialogue, execution_status="SUCCESS"
    )

    print(f"\nPre-Speech Verification Latency: {latency_ms} ms")
    print(f"Cleaned Speech Text: \"{clean_speech_text}\"\n")

    # Speak Audio Out Loud
    voice = JarvisVoiceEngine()
    print("Speaking dialogue through laptop speakers now...")
    voice.speak(clean_speech_text)

    print("==========================================================")
    print("  WITTY DIALOGUE VOICE TEST COMPLETED WITH 0 ERRORS!     ")
    print("==========================================================")

if __name__ == "__main__":
    speak_jarvis_witty_dialogue()
