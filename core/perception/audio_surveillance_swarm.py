import os
import sys
import logging
import time
import numpy as np

try:
    import sounddevice as sd
    import speech_recognition as sr
except ImportError:
    logging.error("Failed to import libraries. Ensure SpeechRecognition and sounddevice are installed.")
    sys.exit(1)

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.orchestration.swarm_message_board import SwarmMessageBoard

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class AudioSurveillanceSwarm:
    """
    Architect Tier - Acoustic Sensory Analyst
    Detects physical claps (Amplitude Spikes) AND listens for Wake Words ("Jarvis") 
    using SpeechRecognition.
    """
    
    def __init__(self):
        self.board = SwarmMessageBoard()
        # Clap Detection Config
        self.clap_threshold = 0.08
        self.sample_rate = 44100
        self.chunk_duration = 0.1
        self.is_listening = False
        
        # Voice Recognition Config
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.mic = sr.Microphone()
        self.stop_listening_voice = None
        
        logging.info("🎙️ [Audio Swarm] Booting Acoustic Sensory Analyst...")

    def voice_callback(self, recognizer, audio):
        """ Callback for SpeechRecognition background thread. """
        try:
            # Using Google's free Web Speech API for fast transcription
            speech_text = recognizer.recognize_google(audio).lower()
            logging.info(f"🗣️ [Audio Swarm] Transcribed: '{speech_text}'")
            
            if "jarvis" in speech_text:
                logging.info("⚡ [Audio Swarm] WAKE WORD DETECTED: 'JARVIS'")
                self.board.post_message(
                    sender="AudioSurveillanceSwarm",
                    topic="AUDIO_TRIGGER",
                    payload={"event": "VOICE_WAKE_WORD", "transcript": speech_text, "action_required": "WAKE_JARVIS_DASHBOARD"}
                )
        except sr.UnknownValueError:
            # Mumbled or background noise, ignore
            pass
        except sr.RequestError as e:
            logging.error(f"Could not request results; {e}")

    def audio_callback(self, indata, frames, time_info, status):
        """ Callback for SoundDevice amplitude (clap) detection. """
        rms = np.sqrt(np.mean(indata**2))
        if rms > self.clap_threshold:
            logging.info(f"⚡ [Audio Swarm] MASSIVE ACOUSTIC SPIKE (Amplitude: {rms:.3f}) - CLAP CONFIRMED")
            self.board.post_message(
                sender="AudioSurveillanceSwarm",
                topic="AUDIO_TRIGGER",
                payload={"event": "PHYSICAL_CLAP_DETECTED", "amplitude": float(rms), "action_required": "WAKE_JARVIS_DASHBOARD"}
            )
            logging.info("🎙️ [Audio Swarm] Cooldown initiated (5s)...")
            time.sleep(5)
            logging.info("🎙️ [Audio Swarm] Resuming ambient acoustic monitoring...")

    def start_listening(self):
        self.is_listening = True
        
        # 1. Start Voice Wake Word Listener in background
        logging.info("🎙️ [Audio Swarm] Calibrating Microphone for Ambient Noise...")
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        logging.info("🎙️ [Audio Swarm] Starting Voice Recognition Thread...")
        self.stop_listening_voice = self.recognizer.listen_in_background(self.mic, self.voice_callback)

        # 2. Start Clap Amplitude Listener in main thread
        logging.info("🎙️ [Audio Swarm] Starting Amplitude (Clap) Thread. Awaiting physical commands...")
        with sd.InputStream(callback=self.audio_callback, channels=1, samplerate=self.sample_rate, blocksize=int(self.sample_rate * self.chunk_duration)):
            while self.is_listening:
                time.sleep(0.1)

if __name__ == "__main__":
    swarm = AudioSurveillanceSwarm()
    try:
        swarm.start_listening()
    except KeyboardInterrupt:
        logging.info("🎙️ [Audio Swarm] Shutting down Acoustic Analyst.")
        if swarm.stop_listening_voice:
            swarm.stop_listening_voice(wait_for_stop=False)
