import ctypes
import os
import pathlib
import sys

class AudioMetrics(ctypes.Structure):
    _fields_ = [
        ("rms", ctypes.c_double),
        ("zcr", ctypes.c_int),
        ("is_voice", ctypes.c_bool)
    ]

class AudioAccelerator:
    def __init__(self):
        self.dll = None
        self._load_dll()

    def _load_dll(self):
        try:
            # Look for the compiled DLL in the same directory
            current_dir = pathlib.Path(__file__).parent.absolute()
            dll_path = current_dir / "jarvis_audio.dll"
            
            if os.name == 'nt' and dll_path.exists():
                self.dll = ctypes.CDLL(str(dll_path))
                
                # Define function signatures
                self.dll.process_audio_chunk.argtypes = [ctypes.POINTER(ctypes.c_int16), ctypes.c_int]
                self.dll.process_audio_chunk.restype = AudioMetrics
                print("[AudioAccelerator] C++ DLL Loaded successfully.")
            else:
                print(f"[AudioAccelerator] Warning: DLL not found at {dll_path}. Using slow Python fallback.")
        except Exception as e:
            print(f"[AudioAccelerator] Error loading DLL: {e}")

    def process_chunk(self, pcm_data: bytes) -> dict:
        """
        Process a chunk of raw 16-bit PCM audio data.
        Returns metrics (RMS, ZCR, VAD status).
        """
        if not pcm_data:
            return {"rms": 0.0, "zcr": 0, "is_voice": False}

        # Number of 16-bit samples
        num_samples = len(pcm_data) // 2

        if self.dll:
            # C++ fast path
            # Cast raw bytes to an array of c_int16
            Int16Array = ctypes.c_int16 * num_samples
            # Note: from_buffer_copy is safer if pcm_data is immutable (bytes)
            c_array = Int16Array.from_buffer_copy(pcm_data)
            
            metrics = self.dll.process_audio_chunk(c_array, num_samples)
            return {
                "rms": metrics.rms,
                "zcr": metrics.zcr,
                "is_voice": metrics.is_voice
            }
        else:
            # Python slow fallback (very basic, mostly for dev if DLL fails)
            import struct
            import math
            
            samples = struct.unpack(f'<{num_samples}h', pcm_data)
            sum_squares = 0.0
            zcr = 0
            
            for i in range(num_samples):
                sample = samples[i] / 32768.0
                sum_squares += sample * sample
                if i > 0:
                    if (samples[i] > 0) != (samples[i-1] > 0):
                        zcr += 1
                        
            rms = math.sqrt(sum_squares / num_samples) * 100.0 if num_samples > 0 else 0
            is_voice = (rms > 1.5) and (zcr > (num_samples / 50)) and (zcr < (num_samples / 4))
            
            return {
                "rms": rms,
                "zcr": zcr,
                "is_voice": is_voice
            }

audio_accelerator = AudioAccelerator()
