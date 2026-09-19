# Final Computer Use Engine Report — CognitiveOS

This report documents E2E execution loop parameters.

---

## 1. Unified Execution Loop
The loop executes:
$$\text{Observe} \rightarrow \text{Understand} \rightarrow \text{Ground} \rightarrow \text{Safety Check} \rightarrow \text{Execute} \rightarrow \text{Verify} \rightarrow \text{Reflect}$$

---

## 2. Dynamic Grounding & DPI mapping
* **DPI Normalizer:** Maps coordinates from 100% to 200% DPI factors dynamically using Windows `shcore` scaling APIs.
* **Coordinate independent execution:** Bypasses hardcoded coordinate paths; all actions are mapped to real-time UIA/DOM bounding box centers.
