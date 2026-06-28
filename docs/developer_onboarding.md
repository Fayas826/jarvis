# 🧬 J.A.R.V.I.S. O.M.E.G.A. — DEVELOPER ONBOARDING

## 1. Project Structure

```text
/jarvis
├── backend/
│   ├── src/ai/
│   │   ├── brain.py       # Tiered Reasoning Orchestrator
│   │   └── neural_core.py  # Intent Routing Logic
│   ├── long_term_memory.py # ChromaDB Vector Mesh
│   ├── api.py              # FastAPI Entry Point
│   ├── system_logger.py    # Async Telemetry Node
│   └── ignite_tunnel.py    # Mobile Resilience Bridge
├── frontend/               # Zenith HUD (React)
├── jarvis_sentinel_v2.py   # Watchdog / Persistence
└── api_starter.py          # Ignition Entry Point
```

---

## 2. Core Responsibilities

### `brain.py` (The Soul)
If you want to change how JARVIS "thinks" or add a new LLM provider, modify the `get_ai_response` method. It handles the fallover logic from cloud to local.

### `long_term_memory.py` (The Memory)
This is where embeddings are generated and stored. To change the "Abstraction" logic (how memories are compressed), modify the `consolidate_memory` function.

### `jarvis_sentinel_v2.py` (The Body)
This is the system watchdog. It handles audio input (claps/wake-words) and process monitoring. To add a new hardware sensor (e.g., motion), add a new thread to this module.

---

## 3. Safe Extension Points

### Adding a New Command
1.  Navigate to `backend/src/ai/neural_core.py`.
2.  Add a new regex pattern to the `NEURAL_MAP`.
3.  Add the corresponding function in the backend to handle the action.

### Adding a New Memory Register
1.  Navigate to `backend/long_term_memory.py`.
2.  In `__init__`, create a new collection (e.g., `self.preferences`).
3.  Add a search/add method for that register.

---

## 4. Development Best Practices
*   **Always Async**: The system is designed for high concurrency. Never block the event loop in `api.py`.
*   **Telemetry First**: Every new feature should log success/failure via `system_logger.log`.
*   **Memory Safety**: Ensure all local model interactions are wrapped in the `_inference_lock` found in `brain.py`.
