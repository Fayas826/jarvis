# Final Limitations Report — CognitiveOS

This report outlines known performance and hardware boundaries of the current system.

---

## 1. Hardware Constraints (RTX 3050 4GB Laptop GPU)
* **OmniParser/Heavy segmenters:** Infeasible due to long delays and VRAM crash risks.
* **Perception Strategy:** Prioritizes local coordinates resolution (UIA Accessibility trees, Playwright DOM selectors, EasyOCR text blocks) and leverages lightweight VLM API prompts only as a fallback.

---

## 2. Browser Limits
* **Captcha/Anti-bot:** JARVIS does not support automated CAPTCHA bypass. Tasks requiring user verification require operator input.
