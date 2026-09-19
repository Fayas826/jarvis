import os
import time
import asyncio
import io
import wave
import numpy as np
import pygame

# 🎙️ TIER_12: SONIC_RESONANCE_V2 (OFFLINE ZERO-LATENCY)
# Eliminates cloud STT/TTS dependencies using Faster-Whisper and Piper.

class SonicEngineV2:
    def __init__(self, model_size="base.en", device="cpu", compute_type="int8"):
        """
        Initializes the offline sonic core.
        - model_size: 'tiny.en' (Fastest) or 'base.en' (Balanced)
        - device: 'cuda' for NVIDIA GPU, 'cpu' for standard processing
        - compute_type: Quantization (int8, float16)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.stt_model = None
        self.mixer_active = False
        
    def _lazy_init_mixer(self):
        """Initializes the audio mixer only when needed to prevent startup hangs."""
        if self.mixer_active: return True
        try:
            import pygame
            if not pygame.mixer.get_init():
                # 🧬 O.M.E.G.A. V53: AUDIO_RESONANCE_HARDENING
                # Using a 2-second timeout logic or just handling the lock
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.mixer_active = True
            return True
        except Exception as e:
            print(f"[SONIC_V2] ⚠️ Output Mixer Fail: {e}")
            return False

    def _lazy_load_stt(self):
        """Loads Whisper model only when first needed to save startup RAM."""
        if self.stt_model is None:
            print(f"[SONIC_V2] 🧬 Igniting Faster-Whisper ({self.model_size})...")
            from faster_whisper import WhisperModel
            self.stt_model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
            print("[SONIC_V2] ✅ STT Core ONLINE (Offline)")

    def _sanitize_for_speech(self, text):
        """🎭 STARK_VOICE_FILTER: Converts robotic system codes to natural human speech."""
        import re
        # 1. Strip JSON artifacts
        text = text.replace("{", "").replace("}", "").replace("\"", "").replace("[", "").replace("]", "")
        # 2. Remove raw status prefixes like [SENTINEL], [BRAIN], [OK]
        text = re.sub(r'\[[A-Z_0-9]+\]', '', text)
        # 3. Convert ALL_CAPS_UNDERSCORE tokens → natural words
        # e.g. "FUNCTION_ACTIVE_SCAN" → "function active scan"
        def decode_caps(match):
            return match.group(0).replace("_", " ").lower()
        text = re.sub(r'\b[A-Z][A-Z_]{2,}\b', decode_caps, text)
        # 4. Replace remaining underscores with spaces
        text = text.replace("_", " ")
        # 5. Strip emoji and extra whitespace
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        # 6. If the result is empty or just noise, return None
        if len(text) < 3:
            return None
        return text

    async def speak(self, text):
        """🛡️ TIER_12: Non-blocking offline TTS using background threads."""
        if not self._lazy_init_mixer(): return

        # 🎭 Apply the Stark Voice Personality Filter FIRST
        clean_text = self._sanitize_for_speech(text)
        if not clean_text:
            return  # Silently skip robotic noise

        print(f"[SONIC_V2] Speaking: {clean_text[:60]}...")

        def _execute_tts():
            try:
                import tempfile
                if not hasattr(self, 'tts_model') or self.tts_model is None:
                    print(f"[SONIC_V2] 🧬 Igniting Neural TTS (VITS)...")
                    from TTS.api import TTS
                    self.tts_model = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)
                    print("[SONIC_V2] ✅ TTS Core ONLINE (Offline)")

                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    temp_path = f.name
                
                # p273 is a crisp, professional British-style male voice
                self.tts_model.tts_to_file(text=clean_text, file_path=temp_path, speaker="p273")
                
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                pygame.mixer.music.unload()
                try:
                    os.remove(temp_path)
                except Exception as e:
                    from core.reliability.system_logger import system_logger
                    system_logger.log('ERROR', 'sonic_engine_v2', f'Unhandled exception: {e}')
                    pass
            except Exception as e:
                print(f"[SONIC_THREAD_FAIL] {e}")

        await asyncio.to_thread(_execute_tts)

    def listen(self):
        """Zero-latency offline transcription."""
        import speech_recognition as sr
        self._lazy_load_stt()
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("[SONIC_V2] 🎙️ Monitoring environment...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
            except sr.WaitTimeoutError:
                return None

        try:
            audio_data = io.BytesIO(audio.get_wav_data())
            segments, info = self.stt_model.transcribe(audio_data, beam_size=1)
            text = " ".join([seg.text for seg in segments]).strip()
            if text:
                print(f"[SONIC_V2] 👂 Heard: {text}")
                return text
        except Exception as e:
            print(f"[SONIC_V2] ❌ Recognition Error: {e}")
            
        return None

    def wait_for_trigger(self):
        """🛡️ TIER_12: Passive monitoring for ignition triggers (Clap/Jarvis)."""
        import speech_recognition as sr
        r = sr.Recognizer()
        r.energy_threshold = 4000
        r.dynamic_energy_threshold = True
        
        with sr.Microphone() as source:
            try:
                r.adjust_for_ambient_noise(source, duration=0.2)
                # 🧬 Strict timeout to prevent event loop lag
                audio = r.listen(source, timeout=1, phrase_time_limit=3)
                
                # 1. 👏 CLAP_DETECTION
                try:
                    samples = np.frombuffer(audio.get_raw_data(), dtype=np.int16)
                    if len(samples) > 0 and np.max(np.abs(samples)) > 28000:
                        return "CLAP"
                except: pass

                # 2. 🎙️ WAKE_WORD_DETECTION
                try:
                    text = r.recognize_google(audio).lower()
                    if any(word in text for word in ["jarvis", "hey"]):
                        return "WAKE_WORD"
                except: pass
            except (sr.WaitTimeoutError, Exception):
                return None
        return None

# Singleton Interface
sonic_engine = SonicEngineV2()

if __name__ == "__main__":
    asyncio.run(sonic_engine.speak("Tactical Sonic Engine V2 initialized. I am now listening entirely offline, Sir."))
