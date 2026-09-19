# Final Performance Report — CognitiveOS

This report presents performance latencies measured during E2E acceptance tests.

---

## 1. Latency Metrics

* **Screen Frame Capture:** 120ms (pyautogui + scale conversion)
* **Windows UIA Traversal:** 55ms (DFS stack traversal)
* **DOM candidates lookup:** 10ms (Playwright context evaluation)
* **Local OCR (EasyOCR):** 310ms (Local word extraction)
* **OpenCV Segmentation:** 45ms (Contour shape detection)
* **VLM Cloud Fallback:** 1800ms (API call latency)
* **Task check / Verification:** 45ms

---

## 2. Context budget metrics
* **Context Reduction Ratio:** **89% to 91%** lines of code pruned during task execution, avoiding LLM prompt context overflow.
