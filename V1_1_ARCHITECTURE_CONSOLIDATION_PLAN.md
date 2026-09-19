# JARVIS v1.1 Architecture Consolidation Plan

This document maps out the system-wide consolidation plan for the un-locked JARVIS v1.1 architecture, defining how legacy, duplicate, and obsolete subsystems will be cleaned up, refactored, or integrated.

---

## 1. System Duplicate Analysis & Consolidation Actions

### A. Precognition System Name Collision
- **Duplicate Components:**
  - `core/cognition/reasoning/precog_engine.py` (Proactive process-monitoring watcher)
  - `backend/src/ai/precog_engine.py` (Static AST log & performance auditor)
- **Consolidation Action:**
  - Keep proactive process watcher in `core/cognition/reasoning/precog_engine.py` as the canonical `PrecogEngine`.
  - Refactor `backend/src/ai/precog_engine.py` log auditing and AST analysis logic into the unified `core/reliability/experience_engine.py`.
  - Delete `backend/src/ai/precog_engine.py` once migrated.

### B. Singularity Self-Healing / Consciousness Clashes
- **Duplicate Components:**
  - `backend/singularity.py` (Self-evolution memory purging thread loop)
  - `backend/singularity_node.py` (Consciousness integrity status endpoint structure)
- **Consolidation Action:**
  - Merge self-evolution gc collection and self-healing analysis loops into `core/reliability/evolution_engine.py`.
  - Move consciousness integrity checker classes into `core/cognition/reasoning/asi_core.py`.
  - Delete `backend/singularity.py` and `backend/singularity_node.py`.
  - Redirect backend API endpoint checks directly to the unified `asi_core.py` and `evolution_engine.py` instances.

---

## 2. Canonical Orchestration & Core Architecture Mooring

All requests will flow through a unified core:

```text
USER INPUT -> Conversational Interpreter -> Intent Engine -> Orchestrator (DAG Planning)
  -> Safety Watchdog -> Computer Use Agent -> Action Executor -> Progress Verifier
```

- **Unified Planner:** `core/orchestration/task_planner.py` will remain the sovereign DAG planner.
- **Unified Safety Gate:** `infrastructure/watchdog/safety_layer.py` is the single authority for commands validation.
- **Unified Memory:** `core/cognition/memory/memory.py` remains the active user memory controller, with ChromaDB RAG handling episodic memory lookup.

---

## 3. Migration Safe Execution Strategy
1. Backup target files.
2. Port logic to target destinations.
3. Update FastAPI import routing in `backend/api.py`.
4. Run full unit and integration tests.
5. Deprecate and remove redundant files.
