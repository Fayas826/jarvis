"""
JARVIS ANDROID NATIVE APP — MARK-L
====================================
Kivy-based Android APK with:
- Always-listening wake word ("JARVIS")
- Siri-style glowing orb animation
- Fingerprint unlock via power button sensor
- Universal app launcher (any installed app)
- TTS voice response
- Tailscale server connection
"""

import os
import threading
import time
import json
import urllib.request
import urllib.parse

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import (
    Color, Ellipse, Line, Rectangle, RoundedRectangle
)
from kivy.animation import Animation
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import (
    NumericProperty, StringProperty, BooleanProperty, ListProperty
)
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout

# Android-specific imports (only on device)
IS_ANDROID = platform == 'android'
if IS_ANDROID:
    from android.permissions import request_permissions, Permission, check_permission
    from android.runnable import run_on_ui_thread
    from jnius import autoclass, cast
    from android import activity
    from android.broadcast import BroadcastReceiver

    # Android Java classes
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent         = autoclass('android.content.Intent')
    PackageManager = autoclass('android.content.pm.PackageManager')
    BiometricPrompt = autoclass('androidx.biometric.BiometricPrompt')
    BiometricManager = autoclass('androidx.biometric.BiometricManager')
    SpeechRecognizer = autoclass('android.speech.SpeechRecognizer')
    RecognizerIntent = autoclass('android.speech.RecognizerIntent')
    TextToSpeech   = autoclass('android.speech.tts.TextToSpeech')
    Context        = autoclass('android.content.Context')
    Locale         = autoclass('java.util.Locale')
    TelephonyManager = autoclass('android.telephony.TelephonyManager')
    Uri            = autoclass('android.net.Uri')

# Tailscale JARVIS server URL
JARVIS_SERVER = "https://asus-a15.tail0eb81f.ts.net:8092"

# ─────────────────────────────────────────────
#  SIRI ORB WIDGET
# ─────────────────────────────────────────────

class SiriOrb(Widget):
    glow_radius = NumericProperty(80)
    glow_alpha  = NumericProperty(0.6)
    is_active   = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._pulse_anim = None
        self._angle = 0
        Clock.schedule_interval(self._rotate_tick, 1/30)
        self.bind(pos=self._redraw, size=self._redraw)
        self._redraw()

    def _redraw(self, *_):
        self.canvas.clear()
        cx = self.center_x
        cy = self.center_y
        r  = self.glow_radius

        with self.canvas:
            # Outer glow rings
            for i, (col, alpha) in enumerate([
                ((0, 0.94, 1, 0.12), r + 40),
                ((0.66, 0.33, 0.97, 0.18), r + 25),
                ((0.93, 0.28, 0.6, 0.1), r + 12),
            ]):
                Color(*col[:3], col[3] * self.glow_alpha)
                d = alpha * 2
                Ellipse(pos=(cx - alpha, cy - alpha), size=(d, d))

            # Core orb gradient simulation (3 layered ellipses)
            Color(0, 0.94, 1, 0.9 * self.glow_alpha)
            d = r * 2
            Ellipse(pos=(cx - r, cy - r), size=(d, d))

            Color(0.66, 0.33, 0.97, 0.7 * self.glow_alpha)
            r2 = r * 0.75
            Ellipse(pos=(cx - r2, cy - r2), size=(r2 * 2, r2 * 2))

            Color(0.93, 0.28, 0.6, 0.5 * self.glow_alpha)
            r3 = r * 0.45
            Ellipse(pos=(cx - r3, cy - r3), size=(r3 * 2, r3 * 2))

            # White core
            Color(1, 1, 1, 0.8 * self.glow_alpha)
            r4 = r * 0.18
            Ellipse(pos=(cx - r4, cy - r4), size=(r4 * 2, r4 * 2))

    def _rotate_tick(self, dt):
        self._angle = (self._angle + 2) % 360
        if self.is_active:
            self._redraw()

    def activate(self):
        self.is_active = True
        if self._pulse_anim:
            self._pulse_anim.cancel(self)
        self._pulse_anim = (
            Animation(glow_radius=100, glow_alpha=1.0, duration=0.4) +
            Animation(glow_radius=85, glow_alpha=0.85, duration=0.5)
        )
        self._pulse_anim.repeat = True
        self._pulse_anim.start(self)
        self._redraw()

    def deactivate(self):
        self.is_active = False
        if self._pulse_anim:
            self._pulse_anim.cancel(self)
            self._pulse_anim = None
        anim = Animation(glow_radius=80, glow_alpha=0.45, duration=0.6)
        anim.start(self)

    def on_glow_radius(self, *_): self._redraw()
    def on_glow_alpha(self, *_): self._redraw()


# ─────────────────────────────────────────────
#  WAVE BAR WIDGET
# ─────────────────────────────────────────────

class WaveBars(Widget):
    heights = ListProperty([0.2, 0.4, 0.7, 0.5, 0.9, 0.6, 0.3])
    active  = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._t = 0
        Clock.schedule_interval(self._tick, 1/20)
        self.bind(pos=self._draw, size=self._draw)

    def _tick(self, dt):
        if self.active:
            import math
            self._t += dt
            self.heights = [
                0.3 + 0.65 * abs(math.sin(self._t * 3.2 + i * 0.7))
                for i in range(7)
            ]
        else:
            self.heights = [0.15] * 7
        self._draw()

    def _draw(self, *_):
        self.canvas.clear()
        n = len(self.heights)
        total_w = self.width
        bar_w = max(4, total_w / (n * 1.8))
        gap   = (total_w - bar_w * n) / (n + 1)

        with self.canvas:
            for i, h in enumerate(self.heights):
                bh = self.height * h
                x  = self.x + gap * (i + 1) + bar_w * i
                y  = self.center_y - bh / 2
                # Gradient: cyan → purple
                t = i / max(n - 1, 1)
                Color(0 + t * 0.66, 0.94 - t * 0.61, 1 - t * 0.03, 0.9)
                RoundedRectangle(pos=(x, y), size=(bar_w, bh), radius=[bar_w / 2])


# ─────────────────────────────────────────────
#  MAIN JARVIS SCREEN
# ─────────────────────────────────────────────

class JarvisScreen(FloatLayout):

    def __init__(self, **kw):
        super().__init__(**kw)
        Window.clearcolor = (0.02, 0.027, 0.055, 1)

        # Background subtle grid
        with self.canvas.before:
            Color(0, 0.94, 1, 0.04)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)

        # Siri orb (center)
        self.orb = SiriOrb(size_hint=(None, None), size=(200, 200))
        self.add_widget(self.orb)

        # Wave bars (below orb)
        self.waves = WaveBars(size_hint=(None, None), size=(220, 50))
        self.add_widget(self.waves)

        # Status label
        self.status_lbl = Label(
            text="Say  [ JARVIS ]  to activate",
            font_size="15sp",
            color=(0, 0.94, 1, 0.8),
            bold=True,
            halign="center"
        )
        self.add_widget(self.status_lbl)

        # Transcript label
        self.transcript_lbl = Label(
            text="",
            font_size="13sp",
            color=(1, 1, 1, 0.85),
            halign="center",
            text_size=(Window.width * 0.85, None)
        )
        self.add_widget(self.transcript_lbl)

        # Response label
        self.response_lbl = Label(
            text="",
            font_size="12sp",
            color=(0, 1, 0.53, 0.9),
            halign="center",
            text_size=(Window.width * 0.85, None)
        )
        self.add_widget(self.response_lbl)

        # Tap mic button
        self.mic_btn = Button(
            text="🎙️  TAP TO SPEAK",
            size_hint=(None, None),
            size=(220, 48),
            background_color=(0, 0, 0, 0),
            color=(0, 0.94, 1, 1),
            font_size="13sp",
            bold=True
        )
        self.mic_btn.bind(on_press=self._on_mic_tap)
        with self.mic_btn.canvas.before:
            Color(0, 0.94, 1, 0.15)
            self._mic_bg = RoundedRectangle(
                pos=self.mic_btn.pos,
                size=self.mic_btn.size,
                radius=[24]
            )
        self.mic_btn.bind(
            pos=lambda *_: setattr(self._mic_bg, 'pos', self.mic_btn.pos),
            size=lambda *_: setattr(self._mic_bg, 'size', self.mic_btn.size)
        )
        self.add_widget(self.mic_btn)

        # JARVIS title
        self.title_lbl = Label(
            text="J.A.R.V.I.S  MARK-L",
            font_size="11sp",
            color=(0, 0.94, 1, 0.5),
            bold=True,
            letter_spacing=3
        )
        self.add_widget(self.title_lbl)

        self.bind(size=self._layout, pos=self._layout)
        self._layout()

        # Internal state
        self._listening = False
        self._always_listen = True
        self._tts = None

        # Request permissions then start
        if IS_ANDROID:
            self._request_permissions()
        else:
            Clock.schedule_once(lambda dt: self._start_wake_loop(), 1)

    def _update_bg(self, *_):
        self._bg_rect.pos  = self.pos
        self._bg_rect.size = self.size

    def _layout(self, *_):
        W, H = self.width, self.height
        cx = W / 2

        # Orb — center-upper area
        orb_size = min(W * 0.45, 200)
        self.orb.size = (orb_size, orb_size)
        self.orb.center = (cx, H * 0.58)

        # Wave bars — just below orb
        self.waves.size = (W * 0.6, 50)
        self.waves.center = (cx, H * 0.38)

        # Status label
        self.status_lbl.center = (cx, H * 0.30)
        self.status_lbl.text_size = (W * 0.85, None)

        # Transcript
        self.transcript_lbl.center = (cx, H * 0.23)

        # Response
        self.response_lbl.center = (cx, H * 0.17)

        # Mic button
        self.mic_btn.center = (cx, H * 0.10)

        # Title
        self.title_lbl.center = (cx, H * 0.96)

    # ── PERMISSIONS ──

    def _request_permissions(self):
        perms = [
            Permission.RECORD_AUDIO,
            Permission.CALL_PHONE,
            Permission.SEND_SMS,
            Permission.READ_CONTACTS,
            Permission.USE_BIOMETRIC,
            Permission.INTERNET,
            Permission.FOREGROUND_SERVICE,
            Permission.SYSTEM_ALERT_WINDOW,
        ]
        request_permissions(perms, self._on_permissions)

    def _on_permissions(self, permissions, results):
        Clock.schedule_once(lambda dt: self._start_wake_loop(), 0.5)
        if IS_ANDROID:
            self._init_tts()

    # ── TTS ──

    def _init_tts(self):
        """Initialize Android TTS engine."""
        if not IS_ANDROID:
            return
        try:
            ctx = PythonActivity.mActivity
            self._tts = TextToSpeech(ctx, None)
            time.sleep(0.5)
            self._tts.setLanguage(Locale.US)
        except Exception as e:
            print(f"TTS init error: {e}")

    def speak(self, text):
        """Say text aloud."""
        # Try server TTS first (AndrewNeural voice)
        try:
            url = f"{JARVIS_SERVER}/api/v1/tts?text={urllib.parse.quote(text)}"
            req = urllib.request.Request(url, headers={"User-Agent": "JARVIS-APK/1.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                audio_data = resp.read()
            self._play_audio_bytes(audio_data)
            return
        except Exception as e:
            from core.reliability.system_logger import system_logger
            system_logger.log('ERROR', 'main', f'Unhandled exception: {e}')
            pass
        # Fallback to Android TTS
        if IS_ANDROID and self._tts:
            try:
                self._tts.speak(text, TextToSpeech.QUEUE_FLUSH, None, "jarvis_utt")
            except Exception as e:
                print(f"TTS speak error: {e}")

    def _play_audio_bytes(self, audio_bytes):
        """Save mp3 to temp file and play."""
        if not IS_ANDROID:
            return
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
            print(f"Audio play error: {e}")

    # ── WAKE WORD / VOICE ──

    def _start_wake_loop(self):
        """Start background wake-word listening thread."""
        self._wake_thread = threading.Thread(
            target=self._wake_word_loop, daemon=True
        )
        self._wake_thread.start()

    def _wake_word_loop(self):
        """Continuously listen for 'JARVIS' wake word."""
        while True:
            try:
                if IS_ANDROID:
                    self._android_listen_once(wake_mode=True)
                else:
                    time.sleep(2)  # Desktop: no mic, simulate
            except Exception as e:
                print(f"Wake loop error: {e}")
                time.sleep(1)

    def _android_listen_once(self, wake_mode=False):
        """Use Android SpeechRecognizer for one utterance."""
        from kivy.clock import Clock as KClock

        result_holder = [None]
        done_event = threading.Event()

        @run_on_ui_thread
        def _start():
            ctx = PythonActivity.mActivity
            sr = SpeechRecognizer.createSpeechRecognizer(ctx)

            class Listener(autoclass('android.speech.RecognitionListener')):
                def onReadyForSpeech(self, params): pass
                def onBeginningOfSpeech(self): pass
                def onRmsChanged(self, rmsdB): pass
                def onBufferReceived(self, buffer): pass
                def onEndOfSpeech(self): pass
                def onError(self, error): done_event.set()
                def onResults(self, results):
                    matches = results.getStringArrayList(
                        RecognizerIntent.EXTRA_RESULTS
                    )
                    if matches and matches.size() > 0:
                        result_holder[0] = matches.get(0)
                    done_event.set()
                def onPartialResults(self, partialResults):
                    matches = partialResults.getStringArrayList(
                        RecognizerIntent.EXTRA_PARTIAL_RESULTS
                    )
                    if matches and matches.size() > 0:
                        partial = matches.get(0)
                        Clock.schedule_once(
                            lambda dt: self._show_transcript(partial), 0
                        )
                def onEvent(self, eventType, params): pass

            sr.setRecognitionListener(Listener())
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "en-US")
            intent.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, True)
            intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            sr.startListening(intent)

        _start()
        done_event.wait(timeout=8)
        transcript = result_holder[0] or ""

        if wake_mode:
            if "jarvis" in transcript.lower():
                Clock.schedule_once(lambda dt: self._on_wake_detected(), 0)
        else:
            Clock.schedule_once(
                lambda dt: self._process_command(transcript), 0
            )

    def _on_mic_tap(self, *_):
        """User manually tapped mic button."""
        self._enter_command_mode()

    @mainthread
    def _on_wake_detected(self):
        """JARVIS wake word heard — activate."""
        self._enter_command_mode()

    @mainthread
    def _enter_command_mode(self):
        """Activate orb and start listening for command."""
        self.orb.activate()
        self.waves.active = True
        self._set_status("🔴  LISTENING...", (0.93, 0.28, 0.6, 1))
        self._set_transcript("")
        self._set_response("")
        self._listening = True

        t = threading.Thread(
            target=lambda: self._android_listen_once(wake_mode=False),
            daemon=True
        )
        t.start()

    @mainthread
    def _show_transcript(self, text):
        self._set_transcript(text)

    # ── COMMAND PROCESSING ──

    def _process_command(self, command):
        """Send command to JARVIS server or handle locally."""
        if not command.strip():
            self._deactivate()
            return

        self._set_transcript(f'"{command}"')

        # Check for fingerprint unlock command
        lower = command.lower()
        if any(w in lower for w in ["unlock", "fingerprint", "open lock", "unblock"]):
            self._trigger_fingerprint_unlock()
            return

        # Send to JARVIS server
        def _send():
            try:
                url = f"{JARVIS_SERVER}/api/command"
                data = json.dumps({"command": command}).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data,
                    headers={"Content-Type": "application/json",
                             "User-Agent": "JARVIS-APK/1.0"}
                )
                with urllib.request.urlopen(req, timeout=8) as resp:
                    result = json.loads(resp.read().decode("utf-8"))
                reply = result.get("response", "Done, sir.")
                Clock.schedule_once(
                    lambda dt: self._handle_response(reply), 0
                )
            except Exception as e:
                # Handle locally if server unreachable
                reply = self._local_command(command)
                Clock.schedule_once(
                    lambda dt: self._handle_response(reply), 0
                )

        threading.Thread(target=_send, daemon=True).start()

    def _local_command(self, command):
        """Handle commands locally on Android without server."""
        lower = command.lower()

        if IS_ANDROID:
            ctx = PythonActivity.mActivity

            # Open any app
            if any(w in lower for w in ["open", "launch", "start"]):
                app_map = {
                    "youtube":   "com.google.android.youtube",
                    "whatsapp":  "com.whatsapp",
                    "spotify":   "com.spotify.music",
                    "instagram": "com.instagram.android",
                    "maps":      "com.google.android.apps.maps",
                    "chrome":    "com.android.chrome",
                    "gmail":     "com.google.android.gm",
                    "telegram":  "org.telegram.messenger",
                    "netflix":   "com.netflix.mediaclient",
                    "settings":  "com.android.settings",
                    "camera":    "android.media.action.IMAGE_CAPTURE",
                    "phone":     "com.google.android.dialer",
                    "calculator":"com.google.android.calculator",
                    "clock":     "com.google.android.deskclock",
                    "gpay":      "com.google.android.apps.nbu.paisa.user",
                }
                for name, pkg in app_map.items():
                    if name in lower:
                        try:
                            pm = ctx.getPackageManager()
                            intent = pm.getLaunchIntentForPackage(pkg)
                            if intent:
                                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                                ctx.startActivity(intent)
                                return f"Opening {name.title()} on your phone, sir."
                        except Exception as e:
                            from core.reliability.system_logger import system_logger
                            system_logger.log('ERROR', 'main', f'Unhandled exception: {e}')
                            pass

            # Make a call
            if any(w in lower for w in ["call", "dial", "ring"]):
                try:
                    phone_intent = Intent(Intent.ACTION_CALL)
                    phone_intent.setData(Uri.parse("tel:"))
                    phone_intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    ctx.startActivity(phone_intent)
                    return "Opening dialer, sir."
                except Exception as e:
                    return f"Call error: {e}"

        return f"Command received: {command}"

    @mainthread
    def _handle_response(self, reply):
        """Show response and speak it."""
        self._set_response(f"JARVIS: {reply}")
        self._deactivate()
        threading.Thread(
            target=lambda: self.speak(reply), daemon=True
        ).start()

    @mainthread
    def _deactivate(self):
        self.orb.deactivate()
        self.waves.active = False
        self._set_status("Say  [ JARVIS ]  to activate", (0, 0.94, 1, 0.8))
        self._listening = False

    # ── FINGERPRINT UNLOCK ──

    def _trigger_fingerprint_unlock(self):
        """Show Android BiometricPrompt — power button fingerprint sensor."""
        self._set_status("👆  Touch fingerprint sensor...", (1, 0.67, 0, 1))

        if not IS_ANDROID:
            Clock.schedule_once(
                lambda dt: self._handle_response(
                    "Fingerprint unlock simulated, sir."
                ), 1
            )
            return

        @run_on_ui_thread
        def _show_biometric():
            try:
                from jnius import PythonJavaClass, java_method

                class AuthCallback(PythonJavaClass):
                    __javainterfaces__ = [
                        'androidx/biometric/BiometricPrompt$AuthenticationCallback'
                    ]
                    __javacontext__ = 'app'

                    @java_method('(Landroidx/biometric/BiometricPrompt$AuthenticationResult;)V')
                    def onAuthenticationSucceeded(self, result):
                        Clock.schedule_once(
                            lambda dt: self._on_fingerprint_success(), 0
                        )

                    @java_method('(ILjava/lang/CharSequence;)V')
                    def onAuthenticationFailed(self):
                        Clock.schedule_once(
                            lambda dt: self._on_fingerprint_fail(), 0
                        )

                    @java_method('(ILjava/lang/CharSequence;)V')
                    def onAuthenticationError(self, errorCode, errString):
                        Clock.schedule_once(
                            lambda dt: self._on_fingerprint_fail(), 0
                        )

                Executor = autoclass('java.util.concurrent.Executors')
                executor = Executor.newSingleThreadExecutor()
                ctx = PythonActivity.mActivity
                callback = AuthCallback()
                prompt = BiometricPrompt(ctx, executor, callback)

                PromptInfo = autoclass(
                    'androidx.biometric.BiometricPrompt$PromptInfo'
                )
                Builder = autoclass(
                    'androidx.biometric.BiometricPrompt$PromptInfo$Builder'
                )
                info = (Builder()
                        .setTitle("JARVIS Security")
                        .setSubtitle("Touch the fingerprint sensor")
                        .setNegativeButtonText("Cancel")
                        .build())
                prompt.authenticate(info)

            except Exception as e:
                print(f"Biometric error: {e}")
                Clock.schedule_once(
                    lambda dt: self._on_fingerprint_fail(), 0
                )

        _show_biometric()

    @mainthread
    def _on_fingerprint_success(self):
        self.orb.activate()
        self._set_status("✅  Unlocked! Welcome back, sir.", (0, 1, 0.53, 1))
        self.speak("Phone unlocked. Welcome back, sir.")
        Clock.schedule_once(lambda dt: self._deactivate(), 2)

    @mainthread
    def _on_fingerprint_fail(self):
        self._set_status("❌  Fingerprint failed. Try again.", (1, 0.27, 0.27, 1))
        Clock.schedule_once(lambda dt: self._deactivate(), 2)

    # ── UI HELPERS ──

    @mainthread
    def _set_status(self, text, color=(0, 0.94, 1, 0.8)):
        self.status_lbl.text  = text
        self.status_lbl.color = color

    @mainthread
    def _set_transcript(self, text):
        self.transcript_lbl.text = text

    @mainthread
    def _set_response(self, text):
        self.response_lbl.text = text


# ─────────────────────────────────────────────
#  KIVY APP
# ─────────────────────────────────────────────

class JarvisApp(App):
    title = "JARVIS"

    def build(self):
        Window.clearcolor = (0.02, 0.027, 0.055, 1)
        return JarvisScreen()

    def on_start(self):
        # Start background service for always-listening
        if IS_ANDROID:
            from android import mActivity
            from jnius import autoclass as jclass
            Service = jclass(
                'org.test.jarvis.ServiceJarvislistener'
            )
            mActivity.startService(
                Service.getIntent(mActivity)
            )


if __name__ == "__main__":
    JarvisApp().run()
