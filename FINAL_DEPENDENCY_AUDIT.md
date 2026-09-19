# Final Dependency Audit — CognitiveOS

This document catalogs active, required, and optional framework dependencies.

---

## 1. Primary Python Libraries

| Library | Version Requirement | Category | Verification Path |
| :--- | :--- | :--- | :--- |
| **pyautogui** | `>=0.9.54` | Desktop Action | screenshot capture & click dispatch |
| **uiautomation** | `>=1.1.9` | Accessibility UIA | recursive active window traversal |
| **easyocr** | `>=1.7.1` | OCR Engine | dynamic text coordinate mapping |
| **opencv-python**| `>=4.8.0` | CV Perception | element shape contour segmenter |
| **playwright** | `>=1.40.0` | Browser Engine | page DOM accessibility fetch |

---

## 2. HUD Frontend Packages

* **React / Vite:** Serves the 3D HUD canvas overlay interface.
* **Framer Motion:** Telemetry stream transitions and alert overlays.
