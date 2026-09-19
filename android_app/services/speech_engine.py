import threading
import time
import urllib.request
import urllib.parse
from kivy.utils import platform

IS_ANDROID = platform == 'android'

if IS_ANDROID:
    from jnius import autoclass
    from android.runnable import run_on_ui_thread
    from kivy.clock import Clock
    
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
    RecognizerIntent = autoclass('android.speech.RecognizerIntent')
    TextToSpeech   = autoclass('android.speech.tts.TextToSpeech')
    Locale         = autoclass('java.util.Locale')

class SpeechEngine:
    def __init__(self, server_url):
        self.server_url = server_url
        self._tts = None
        if IS_ANDROID:
            self._init_tts()

    def _init_tts(self):
        try:
            ctx = PythonActivity.mActivity
            self._tts = TextToSpeech(ctx, None)
            time.sleep(0.5)
            self._tts.setLanguage(Locale.US)
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'speech_engine', f'TTS init error: {e}')

    def speak(self, text):
        def _speak():
            try:
                url = f"{self.server_url}/api/v1/tts?text={urllib.parse.quote(text)}"
                req = urllib.request.Request(url, headers={"User-Agent": "JARVIS-APK/1.0"})
                with urllib.request.urlopen(req, timeout=6) as resp:
                    audio_data = resp.read()
                self._play_audio_bytes(audio_data)
                return
            except Exception:
                if IS_ANDROID and self._tts:
                    try:
                        self._tts.speak(text, TextToSpeech.QUEUE_FLUSH, None, "jarvis_utt")
                    except Exception as e:
                        from core.reliability.system_logger import system_logger
                        system_logger.log('ERROR', 'speech_engine', f'TTS speak error: {e}')
        threading.Thread(target=_speak, daemon=True).start()

    def _play_audio_bytes(self, audio_bytes):
        if not IS_ANDROID: return
        try:
            import tempfile
            MediaPlayer = autoclass('android.media.MediaPlayer')
            tmp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            tmp.write(audio_bytes)
            tmp.close()
            mp = MediaPlayer()
            mp.setDataSource(tmp.name)
            mp.prepare()
            mp.start()
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'speech_engine', f'Audio play error: {e}')
