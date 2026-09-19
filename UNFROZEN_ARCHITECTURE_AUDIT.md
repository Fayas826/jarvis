# JARVIS Unfrozen Architecture Audit

This report presents a thorough audit of the JARVIS repository architecture, mapping obsolete systems, duplicates, and key performance/VRAM bottlenecks in preparation for v1.1.

---

## 1. Outdated & Duplicate Modules

- **Precog Engine Duplication:**
  - `core/cognition/reasoning/precog_engine.py` (process watcher & latent loader) collides with `backend/src/ai/precog_engine.py` (log analyzer & AST redundancy check).
  - *Recommendation:* Consolidate into a unified `PrecogEngine` in `core/cognition/reasoning/precog_engine.py` and remove the duplicate `backend/src/ai/precog_engine.py` path.

- **Consciousness Node Collision:**
  - `backend/singularity.py` (recursive gc self-healer) and `backend/singularity_node.py` (sovereign synthetic consciousness metadata) have name overlap.
  - *Recommendation:* Refactor `singularity.py` into a unified `core/reliability/evolution_engine.py` extension, keeping backend routing isolated.

- **Test Suite Mocks:**
  - `tests/benchmark_runner.py` mocks ScreenSpot, OSWorld, and Mind2Web.
  - *Recommendation:* Maintain the mock structures for quick regression checks but expand to support hybrid real-world execution paths.

---

## 2. Structural & Performance Gaps

- **Cold Start Latency:**
  - Ollama phi3 loading times out on cold starts if the hardcoded client timeout is less than 15.0 seconds.
  - *Solution implemented:* Keep dynamic timeout scaling active in `brain.py`.

- **Trust Boundaries:**
  - Trust checks are currently static regex arrays in `conversational_interpreter.py`.
  - *Recommendation:* Expand the prompt-injection classifier with semantic vector distance screening.

---

## 3. Next-Generation Priorities
- Consolidate name collisions (Precog / Singularity).
- Enforce strict separation between backend routing controllers and core reasoning libraries.
