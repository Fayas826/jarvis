# JARVIS Android APK — README

## Quick Start

### Build & Install in 3 Steps:

1. **Start Docker Desktop** (make sure it's running)
2. **Run the build script:**
   ```powershell
   cd "c:\jarvis AI\jarvis\android_app"
   powershell -ExecutionPolicy Bypass -File build_apk.ps1
   ```
3. **Follow on-screen instructions** to set JARVIS as default assistant

---

## What You Get

| Feature | How to Use |
|---|---|
| **Wake word** | Say "JARVIS" anytime → orb activates |
| **Fingerprint unlock** | Say "JARVIS unlock" → touch power button sensor |
| **Open apps** | "JARVIS open YouTube" → YouTube opens |
| **Make calls** | "JARVIS call Mum" → dials from contacts |
| **Set as assistant** | Settings → Apps → Default Apps → Digital Assistant → JARVIS |
| **Power button** | Hold power button → JARVIS opens (after setting as default) |

---

## Files

| File | Purpose |
|---|---|
| `main.py` | Main Kivy UI — orb, voice, fingerprint |
| `jarvis_service.py` | Background wake word service |
| `buildozer.spec` | Android build config + permissions |
| `Dockerfile.build` | Docker build environment |
| `build_apk.ps1` | One-click build + install script |

---

## Fingerprint on Power Button

Your **Redmi Note 12 Pro 5G** has a side-mounted fingerprint sensor IN the power button. Here's how JARVIS uses it:

1. Phone is locked / screen is off
2. You say **"JARVIS"** (wake word detected by background service)
3. JARVIS orb glows and says "How can I help?"
4. You say **"unlock"** or just touch the power button fingerprint sensor
5. `BiometricPrompt` fires → sensor lights up → touch it → **UNLOCKED** ✅

> The sensor is hardware-controlled by Android OS. JARVIS triggers the BiometricPrompt dialog which activates the sensor — you just touch it.
