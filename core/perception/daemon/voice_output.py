import threading
import os
import logging

log = logging.getLogger("jarvis_daemon")

def speak(text):
    def _speak():
        try:
            import edge_tts, asyncio, tempfile, subprocess as sp
            async def gen():
                comm = edge_tts.Communicate(text, "en-GB-RyanNeural")
                fp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                fp.close()
                await comm.save(fp.name)
                return fp.name
            mp3 = asyncio.run(gen())
            sp.Popen(["powershell", "-c", f"(New-Object Media.SoundPlayer).PlaySync()"],
                     stdin=open(mp3, "rb"), creationflags=0x08000000)
            os.startfile(mp3)
        except Exception as e:
            log.warning(f"TTS failed: {e}")
    threading.Thread(target=_speak, daemon=True).start()
