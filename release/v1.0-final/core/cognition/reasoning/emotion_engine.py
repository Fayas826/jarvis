import time
import numpy as np
from typing import Dict, List, Optional
from scipy.io import wavfile
import os

class EmotionEngine:
    def __init__(self):
        self.emotion_history = []
        self.MAX_HISTORY = 10
        
        # 🧬 O.M.E.G.A. Emotional Thresholds
        self.SPEED_THRESHOLD_FAST = 4.5  # words per second
        self.SPEED_THRESHOLD_SLOW = 2.0  # words per second
        self.PAUSE_THRESHOLD_STRESSED = 0.8 # seconds
        self.VOLUME_VAR_THRESHOLD = 500  # RMS variance

    def analyze_voice_metrics(self, segments: List[Dict], duration: float) -> Dict:
        """
        🧬 PHASE_1: VOICE_PROSODY_ANALYSIS
        Calculates speaking speed and pause patterns from Whisper segments.
        """
        if not segments:
            return {"speed": 0, "pauses": 0, "stress_level": "NORMAL"}

        total_words = sum(len(s.get("text", "").split()) for s in segments)
        speed = total_words / duration if duration > 0 else 0
        
        # Calculate max pause
        pauses = []
        for i in range(len(segments) - 1):
            pause = segments[i+1]["start"] - segments[i]["end"]
            pauses.append(pause)
        
        max_pause = max(pauses) if pauses else 0
        avg_pause = sum(pauses) / len(pauses) if pauses else 0
        
        # Stress Detection via Prosody
        stress_score = 0
        if speed > self.SPEED_THRESHOLD_FAST: stress_score += 1
        if avg_pause < 0.2 and speed > 3.5: stress_score += 1 # Rushed speech
        if max_pause > 1.5: stress_score -= 0.5 # Thinking/Relaxed
        
        return {
            "speed": speed,
            "max_pause": max_pause,
            "avg_pause": avg_pause,
            "stress_score": stress_score
        }

    def analyze_audio_fidelity(self, wav_path: str) -> Dict:
        """
        🧬 PHASE_1: ACOUSTIC_VALENCE
        Analyzes raw audio for volume jitter and pitch variance (simplified).
        """
        try:
            if not os.path.exists(wav_path):
                return {"volume_variance": 0, "energy": 0}
            
            rate, data = wavfile.read(wav_path)
            if data.ndim > 1: data = data[:, 0] # Mono
            
            # Normalize
            data = data.astype(np.float32) / 32768.0
            
            # RMS Volume
            rms = np.sqrt(np.mean(data**2))
            
            # Volume Variance (Jitter equivalent)
            # Break into frames
            frame_size = int(rate * 0.05) # 50ms frames
            frames = [data[i:i+frame_size] for i in range(0, len(data), frame_size)]
            frame_rms = [np.sqrt(np.mean(f**2)) for f in frames if len(f) > 0]
            
            volume_variance = np.var(frame_rms) if frame_rms else 0
            
            return {
                "rms": rms,
                "volume_variance": volume_variance
            }
        except Exception as e:
            print(f"[EMOTION_ENGINE] Audio analysis fail: {e}")
            return {"rms": 0, "volume_variance": 0}

    def detect_state(self, text: str, metrics: Dict, audio_metrics: Dict, history: List[str]) -> str:
        """
        🧬 O.M.E.G.A. STATE_MACHINE
        Synthesizes all inputs into a single human-like state.
        """
        text = text.lower()
        
        # 1. Keyword Overrides (High Priority)
        if any(w in text for w in ["hurry", "quick", "fast", "asap", "emergency"]):
            return "URGENT"
        if any(w in text for w in ["sorry", "my bad", "apologize"]):
            return "APOLOGETIC"
        
        # 2. Prosody Analysis
        speed = metrics.get("speed", 0)
        stress_score = metrics.get("stress_score", 0)
        vol_var = audio_metrics.get("volume_variance", 0)
        
        # Emotion Heuristics
        if speed > self.SPEED_THRESHOLD_FAST and stress_score > 1:
            return "STRESSED"
        if speed < self.SPEED_THRESHOLD_SLOW and metrics.get("max_pause", 0) > 1.0:
            return "FATIGUE"
        if vol_var > 0.01: # High volume jitter
            return "EXCITED" if speed > 3.0 else "FRUSTRATED"
        
        # 3. Contextual History Bias
        recent_stressed = sum(1 for e in self.emotion_history[-3:] if e == "STRESSED")
        if recent_stressed >= 2:
            return "STRESSED" # Persistent state

        return "STARK" # Default Nominal State

    def update_history(self, state: str):
        self.emotion_history.append(state)
        if len(self.emotion_history) > self.MAX_HISTORY:
            self.emotion_history.pop(0)

emotion_engine = EmotionEngine()
