import threading
import time

class WakeEngine:
    def __init__(self, callback):
        self.callback = callback
        self.is_listening = False
        
    def process_audio(self, audio_data):
        # placeholder for openwakeword integration
        pass

    def start(self):
        self.is_listening = True
        
    def stop(self):
        self.is_listening = False
