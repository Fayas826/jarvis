"""
JARVIS Android Background Service
===================================
Runs as an Android Foreground Service to keep
wake-word detection alive even when app is minimized.
"""

import time
import threading

from android.broadcast import BroadcastReceiver

# This file is loaded by Buildozer as a service
# It communicates with the main app via OSC

def start_service():
    """Entry point called by Android Service."""
    print("[JARVIS SERVICE] Background listener started")

    # Keep the service alive with a foreground notification
    _show_notification()

    # Start wake word loop
    _wake_loop()


def _show_notification():
    """Show persistent 'JARVIS Listening' notification."""
    try:
        from jnius import autoclass
        PythonService = autoclass('org.kivy.android.PythonService')
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationBuilder = autoclass('android.app.Notification$Builder')
        NotificationChannel = autoclass('android.app.NotificationChannel')
        Context = autoclass('android.content.Context')
        Color = autoclass('android.graphics.Color')

        service = PythonService.mService
        ctx = service

        CHANNEL_ID = "jarvis_listener"
        nm = service.getSystemService(Context.NOTIFICATION_SERVICE)

        channel = NotificationChannel(
            CHANNEL_ID,
            "JARVIS Listener",
            NotificationManager.IMPORTANCE_LOW
        )
        channel.setDescription("JARVIS is always listening for your command")
        nm.createNotificationChannel(channel)

        notification = (NotificationBuilder(ctx, CHANNEL_ID)
                        .setContentTitle("J.A.R.V.I.S  ACTIVE")
                        .setContentText("Say 'JARVIS' to activate")
                        .setSmallIcon(0x01080065)  # Android built-in mic icon
                        .setColor(Color.parseColor("#00F0FF"))
                        .setOngoing(True)
                        .build())

        service.startForeground(1, notification)
        print("[JARVIS SERVICE] Foreground notification shown")
    except Exception as e:
        print(f"[JARVIS SERVICE] Notification error: {e}")


def _wake_loop():
    """Continuously check for 'JARVIS' wake word."""
    from kivy.lib import osc

    while True:
        try:
            _listen_for_wake()
        except Exception as e:
            print(f"[JARVIS SERVICE] Wake loop error: {e}")
            time.sleep(1)


def _listen_for_wake():
    """Single listen cycle for wake word."""
    import threading

    result = [None]
    done = threading.Event()

    try:
        from jnius import autoclass
        PythonService  = autoclass('org.kivy.android.PythonService')
        SpeechRec      = autoclass('android.speech.SpeechRecognizer')
        RecogIntent    = autoclass('android.speech.RecognizerIntent')
        Intent         = autoclass('android.content.Intent')
        PythonJavaClass = autoclass('org.jnius.PythonJavaClass')

        ctx = PythonService.mService

        class WakeListener:
            def onReadyForSpeech(self, params): pass
            def onBeginningOfSpeech(self): pass
            def onRmsChanged(self, rmsdB): pass
            def onBufferReceived(self, buffer): pass
            def onEndOfSpeech(self): pass
            def onError(self, error):
                done.set()
            def onResults(self, bundle):
                matches = bundle.getStringArrayList(
                    RecogIntent.EXTRA_RESULTS
                )
                if matches and matches.size() > 0:
                    result[0] = matches.get(0)
                done.set()
            def onPartialResults(self, bundle): pass
            def onEvent(self, eventType, params): pass

        sr = SpeechRec.createSpeechRecognizer(ctx)
        sr.setRecognitionListener(WakeListener())

        intent = Intent(RecogIntent.ACTION_RECOGNIZE_SPEECH)
        intent.putExtra(
            RecogIntent.EXTRA_LANGUAGE_MODEL,
            RecogIntent.LANGUAGE_MODEL_FREE_FORM
        )
        intent.putExtra(RecogIntent.EXTRA_LANGUAGE, "en-US")
        intent.putExtra(RecogIntent.EXTRA_MAX_RESULTS, 1)
        sr.startListening(intent)

        done.wait(timeout=6)

        transcript = (result[0] or "").lower()
        if "jarvis" in transcript:
            _notify_main_app()

    except Exception as e:
        print(f"[JARVIS SERVICE] Listen error: {e}")
        time.sleep(0.5)


def _notify_main_app():
    """Send wake event to main app via broadcast intent."""
    try:
        from jnius import autoclass
        PythonService = autoclass('org.kivy.android.PythonService')
        Intent = autoclass('android.content.Intent')

        service = PythonService.mService
        intent = Intent("JARVIS_WAKE_WORD_DETECTED")
        service.sendBroadcast(intent)
        print("[JARVIS SERVICE] Wake word broadcast sent!")
    except Exception as e:
        print(f"[JARVIS SERVICE] Broadcast error: {e}")


# Start when loaded as service
if __name__ == '__main__':
    start_service()
