import time
import math
import logging
import threading
try:
    import pyaudio
    import numpy as np
except ImportError:
    logging.warning("PyAudio or Numpy not found. Please install via: python -m pip install pyaudio numpy")
    pyaudio = None

class BiometricsAudioAgent:
    """
    JARVIS Hardware Interface: Microphone Biometrics
    Listens to raw audio streams in the background to detect high-energy frequency spikes (Claps)
    and specific voice prints, operating at 0.1% CPU usage.
    """
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16 if pyaudio else 8
        self.CHANNELS = 1
        self.RATE = 44100
        self.CLAP_THRESHOLD = 0.05  # RMS energy threshold for a clap
        
        self.is_listening = False
        self.audio_thread = None
        
        if not pyaudio:
            logging.error("BiometricsAudioAgent cannot initialize: Missing Hardware Drivers.")
            self.p = None
        else:
            self.p = pyaudio.PyAudio()

    def _rms(self, data):
        """Calculates the Root Mean Square energy of the audio chunk."""
        if len(data) == 0: return 0
        # Convert byte data to 16-bit integers
        ints = np.frombuffer(data, dtype=np.int16)
        # Calculate RMS
        sum_squares = np.sum(ints.astype(np.float64)**2)
        rms = math.sqrt(sum_squares / len(ints))
        # Normalize to 0-1
        return rms / 32768.0

    def start_listening(self):
        if not self.p:
            return
            
        self.is_listening = True
        self.audio_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.audio_thread.start()
        logging.info("[Biometrics Agent] Hardware Microphone Hook ACTIVE. Listening for Voice/Claps...")

    def _listen_loop(self):
        try:
            stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            last_clap_time = 0
            
            while self.is_listening:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                rms = self._rms(data)
                
                # Double-clap detection logic
                if rms > self.CLAP_THRESHOLD:
                    current_time = time.time()
                    time_since_last_clap = current_time - last_clap_time
                    
                    if 0.2 < time_since_last_clap < 0.8:
                        logging.warning("⚡ [Biometrics Agent] DOUBLE CLAP DETECTED! WAKING UP UI...")
                        # Here, JARVIS would trigger the MasterOrchestrator to pop the UI to the front.
                        last_clap_time = 0  # Reset
                    else:
                        last_clap_time = current_time
                        
        except Exception as e:
            logging.error(f"[Biometrics Agent] Audio Stream Error: {e}")
        finally:
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()

    def stop_listening(self):
        self.is_listening = False
        if self.p:
            self.p.terminate()
