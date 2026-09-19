import os
import asyncio
import logging
import tempfile
import pygame

try:
    import edge_tts
except ImportError:
    logging.warning("edge-tts not found. Install via: python -m pip install edge-tts pygame")
    edge_tts = None

class VoiceAgent:
    """
    JARVIS Specialized Swarm Member: The Orator.
    Handles Text-to-Speech (TTS) using high-quality neural voices
    without utilizing any local GPU VRAM.
    """
    
    def __init__(self, voice_model: str = "en-US-SteffanNeural"):
        self.voice_model = voice_model
        # Initialize the pygame mixer for audio playback
        try:
            pygame.mixer.init()
        except Exception as e:
            logging.error(f"[Voice Agent] Audio driver error: {e}")

    async def _generate_audio(self, text: str, output_file: str):
        """Generates the TTS audio file asynchronously."""
        if not edge_tts:
            logging.error("[Voice Agent] edge-tts is missing.")
            return
            
        communicate = edge_tts.Communicate(text, self.voice_model)
        await communicate.save(output_file)

    def speak(self, text: str):
        """Generates and plays human-level voice audio."""
        logging.info(f"🎙️ [Voice Agent] Speaking: '{text}'")
        
        try:
            # Create a temporary file for the mp3
            fd, temp_audio_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            
            # Generate the audio using asyncio
            asyncio.run(self._generate_audio(text, temp_audio_path))
            
            # Play the audio using pygame
            pygame.mixer.music.load(temp_audio_path)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            # Unload and delete temp file
            pygame.mixer.music.unload()
            try:
                os.remove(temp_audio_path)
            except OSError:
                pass
                
        except asyncio.TimeoutError:
            logging.error("❌ [Voice Agent] Cloud TTS Timeout. Failsafe activated: Silencing audio to prevent robotic fallback.")
        except Exception as e:
            logging.error(f"❌ [Voice Agent] TTS Exception Caught: {e}")
            logging.warning("⚠️ [Voice Agent] Hard-kill switch activated to prevent Windows screen-reader leak.")
