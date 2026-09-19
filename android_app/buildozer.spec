[app]
# ─── Basic Info ───────────────────────────────────────
title = JARVIS
package.name = jarvis
package.domain = com.fayas.jarvis
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav,json
version = 1.0

# ─── Requirements ─────────────────────────────────────
# Core Kivy + Android bridge + networking
requirements = python3,kivy==2.3.0,pyjnius,android,certifi,urllib3,requests

# ─── Android Build Settings ───────────────────────────
android.sdk_path = ~/.buildozer/android/platform/android-sdk
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25c
android.ndk = 25c
android.api = 33
android.minapi = 26
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a

# ─── Permissions ──────────────────────────────────────
android.permissions =
    RECORD_AUDIO,
    CALL_PHONE,
    SEND_SMS,
    READ_CONTACTS,
    INTERNET,
    FOREGROUND_SERVICE,
    FOREGROUND_SERVICE_MICROPHONE,
    USE_BIOMETRIC,
    USE_FINGERPRINT,
    RECEIVE_BOOT_COMPLETED,
    SYSTEM_ALERT_WINDOW,
    WAKE_LOCK,
    READ_PHONE_STATE,
    MODIFY_AUDIO_SETTINGS,
    VIBRATE

# ─── Fullscreen & Orientation ─────────────────────────
fullscreen = 0
orientation = portrait

# ─── Features ─────────────────────────────────────────
android.features =
    android.hardware.microphone,
    android.hardware.fingerprint

# ─── App Icon ─────────────────────────────────────────
icon.filename = assets/jarvis_icon.png
presplash.filename = assets/jarvis_splash.png

# ─── Background Service ───────────────────────────────
android.services = Jarvislistener:jarvis_service.py:foreground

# ─── Extra Gradle Deps (for BiometricPrompt) ──────────
android.gradle_dependencies =
    androidx.biometric:biometric:1.2.0-alpha05,
    androidx.appcompat:appcompat:1.6.1

# ─── Manifest extras ──────────────────────────────────
android.manifest.intent_filters =
    <intent-filter>
        <action android:name="android.intent.action.ASSIST" />
        <category android:name="android.intent.category.DEFAULT" />
    </intent-filter>

# Sets JARVIS as a valid Digital Assistant app
android.meta_data =
    android.app.voice_interaction_service=.VoiceInteractionService

# ─── Build Type ───────────────────────────────────────
[buildozer]
log_level = 2
warn_on_root = 1
