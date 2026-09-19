import pyttsx3
import os

class JarvisVoiceEngine:
    def __init__(self):
        """
        Initializes the Voice Engine. 
        Currently defaults to a lightweight offline engine (pyttsx3) to prevent crashing 
        the GPU while the massive 53-hour JARVIS Brain training is running.
        Once the GPU is free, the XTTS-v2 Voice Cloning engine will be unlocked here.
        """
        print("[VOICE ENGINE] Initializing Audio Subsystem...")
        self.engine = pyttsx3.init()
        
        # Configure Voice to sound less robotic
        voices = self.engine.getProperty('voices')
        # Try to select a male voice (usually voice[0] is male on Windows)
        for voice in voices:
            if "Zira" not in voice.name: # Zira is female, David is male
                self.engine.setProperty('voice', voice.id)
                break
                
        self.engine.setProperty('rate', 170)  # Speed of speech
        self.engine.setProperty('volume', 1.0) # Volume level
        self.is_cloning_active = False

    def speak(self, text):
        """Speaks the text out loud through the laptop speakers."""
        if self.is_cloning_active:
            self._speak_xtts(text)
        else:
            self._speak_standard(text)

    def _speak_standard(self, text):
        print(f"[VOICE ENGINE - STANDARD] Speaking: '{text}'")
        self.engine.say(text)
        self.engine.runAndWait()

    def _speak_xtts(self, text):
        """
        PLACEHOLDER: This will be the Zero-Shot Voice Cloning logic.
        We cannot load this PyTorch model into VRAM right now because the main
        JARVIS Brain is currently utilizing 100% of the GPU for the 53-hour training.
        """
        reference_audio = "jarvis_reference.wav"
        if not os.path.exists(reference_audio):
            print("[ERROR] Reference audio missing. Reverting to standard voice.")
            self._speak_standard(text)
            return
            
        print(f"[VOICE ENGINE - CLONING] Synthesizing '{text}' using XTTS-v2...")
        # Code to synthesize and play audio using XTTS goes here
        # E.g., tts.tts_to_file(text=text, speaker_wav="jarvis_reference.wav", language="en", file_path="output.wav")
        # play_audio("output.wav")

if __name__ == "__main__":
    # Quick Test
    voice = JarvisVoiceEngine()
    voice.speak("For you, sir, always. The Voice Engine is online.")
