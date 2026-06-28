import asyncio
import edge_tts
import pygame
import os
import io

# 🎙️ O.M.E.G.A. SONIC_RESONANCE
# Text-to-Speech using Edge-TTS for high-quality JARVIS-like voice (free).

class SonicLink:
    def __init__(self):
        self.voice = "en-GB-RyanNeural" # A crisp, British voice perfect for JARVIS
        self.mixer_active = False
        try:
            pygame.mixer.init()
            self.mixer_active = True
        except Exception as e:
            print(f"[SONIC_LINK] Audio mixer init fail (no audio device?): {e}")

    async def speak(self, text):
        """Converts text to speech and plays it immediately."""
        if not self.mixer_active:
            print(f"[SONIC_LINK] Cannot speak: Mixer inactive. Text: {text}")
            return
            
        try:
            # Strip JSON or technical artifacts from text
            clean_text = text.replace("{", "").replace("}", "").replace("\"", "")
            
            communicate = edge_tts.Communicate(clean_text, self.voice)
            
            # Use buffer to avoid disk I/O
            data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    data += chunk["data"]
            
            if data:
                audio_file = io.BytesIO(data)
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            print(f"[SONIC_LINK] ❌ Speech error: {e}")

    def listen(self):
        """Listens for a command and returns the recognized text."""
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("[SONIC_LINK] 🎙️ Listening...")
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        try:
            text = r.recognize_google(audio)
            print(f"[SONIC_LINK] 👂 Heard: {text}")
            return text
        except Exception as e:
            print(f"[SONIC_LINK] Recognition fail: {e}")
            return None

# Singleton instance
sonic_link = SonicLink()

if __name__ == "__main__":
    asyncio.run(sonic_link.speak("Protocol initiated. All systems are sovereign and fully operational, Sir."))
