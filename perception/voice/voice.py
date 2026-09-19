import os
import time

# Tell Python exactly where the Windows eSpeak library is located
os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = r"C:\Program Files\eSpeak NG\libespeak-ng.dll"
os.environ["PHONEMIZER_ESPEAK_PATH"] = r"C:\Program Files\eSpeak NG"
os.environ["PATH"] = r"C:\Program Files\eSpeak NG;" + os.environ.get("PATH", "")

from TTS.api import TTS

class DualVoiceEngine:
    def __init__(self):
        # 🎚️ TOGGLE THIS TO SWITCH VOICES
        self.USE_XTTS_CLONE_MODE = False
        
        self.fast_model_name = "tts_models/en/vctk/vits"
        self.heavy_model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        self.speaker_wav = os.path.join(os.path.dirname(__file__), "my_voice.wav")
        
        self.current_vits_speaker = "p273"
        self.tts = None
        self.current_loaded_model = None

    def _load_model(self, model_name):
        if self.current_loaded_model != model_name:
            print(f"[VOICE] Loading AI Voice Model: {model_name}...")
            self.tts = TTS(model_name=model_name, progress_bar=False).to("cpu")
            self.current_loaded_model = model_name
            print(f"[VOICE] Engine Online.")

    def change_speaker(self, new_speaker):
        print(f"[VOICE] Changing vocal profile to: {new_speaker}")
        self.current_vits_speaker = new_speaker
        # Say confirmation
        self.speak("My vocal profile has been successfully updated.")

    def speak(self, text):
        print(f"Jarvis: {text}")
        output_file = "output.wav"
        
        try:
            if self.USE_XTTS_CLONE_MODE:
                if not os.path.exists(self.speaker_wav):
                    print(f"[VOICE ERROR] Missing {self.speaker_wav}! Please provide a 3-second recording of the voice you want to clone.")
                    return
                    
                self._load_model(self.heavy_model_name)
                self.tts.tts_to_file(
                    text=text, 
                    speaker_wav=self.speaker_wav, 
                    language="en", 
                    file_path=output_file
                )
            else:
                self._load_model(self.fast_model_name)
                self.tts.tts_to_file(
                    text=text, 
                    speaker=self.current_vits_speaker, 
                    file_path=output_file
                )
            
            os.system(f'powershell -c (New-Object Media.SoundPlayer "{output_file}").PlaySync()')
            
        except Exception as e:
            print(f"[VOICE ERROR] Speech generation failed: {e}")

# Maintain original listen function for now (can be upgraded to Whisper later)
import speech_recognition as sr
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        print("You:", command)
        return command
    except Exception as e:
        from core.reliability.system_logger import system_logger
        system_logger.log('ERROR', 'voice', f'Unhandled exception: {e}')
        return ""

# Singleton instance
engine = DualVoiceEngine()
def speak(text):
    engine.speak(text)
