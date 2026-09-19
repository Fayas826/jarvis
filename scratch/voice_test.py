import sys
import os

# Add the root directory to sys.path so we can import the core modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.perception.voice_agent import VoiceAgent

def main():
    print("==========================================")
    print(" JARVIS DOMINEERING VOICE AURA TEST")
    print("==========================================")
    print("[*] Initializing Edge-TTS (en-US-SteffanNeural)...")
    
    # Initialize the Voice Agent with the deep/domineering American male voice
    jarvis_voice = VoiceAgent(voice_model="en-US-SteffanNeural")
    
    test_phrase = (
        "Systems are online. I am JARVIS. "
        "The Master Orchestrator and Specialized Swarms are fully operational. "
        "How may I assist you today?"
    )
    
    print(f"[*] Playing Audio: '{test_phrase}'")
    jarvis_voice.speak(test_phrase)
    
    print("[*] Test Complete.")

if __name__ == "__main__":
    main()
