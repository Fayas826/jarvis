# 🛰️ J.A.R.V.I.S. O.M.E.G.A. — TECHNICAL ARCHITECTURE

## 1. System Overview
The JARVIS O.M.E.G.A. system is an **Advanced Agentic AI Monolith** designed for persistent, self-healing, and memory-abstracted operations. It utilizes a multi-process architecture to separate orchestration, reasoning, and observability.

---

## 2. Component Architecture

### A. Frontend (Zenith HUD)
*   **Tech Stack**: Vite + React + Vanilla CSS.
*   **Role**: Real-time 3D telemetry visualization, voice interaction interface, and system health monitoring.
*   **Auth**: Decoupled JWT-based handshake. Never exposes backend secrets.

### B. Backend (O.M.E.G.A. Core)
*   **Tech Stack**: FastAPI + Python 3.11.
*   **Orchestration**: `JarvisBrain` manages a 12-tier reasoning hierarchy (Groq -> Gemini -> Ollama).
*   **Middleware**: Custom latency metrics, structured JSON logging, and anomaly detection.
*   **Modules**:
    *   `neural_core.py`: Fast-path intent routing (1ms).
    *   `vision_loop.py`: Hybrid Pixtral/Gemini vision analysis with quota failover.
    *   `ignite_tunnel.py`: Persistent mobile bridge (Localtunnel).

### C. Watchdog System (The Sentinel)
*   **Module**: `jarvis_sentinel_v2.py`.
*   **Role**: OS-level persistence and mutual health monitoring.
*   **Mechanism**:
    *   **Backend Check**: Monitors Port 5001.
    *   **Self-Healing**: Automated re-ignition of failed nodes.
    *   **Acoustic Recon**: Faster-Whisper base-model for zero-latency wake-word detection.

---

## 3. Memory & Abstraction
*   **Architecture**: Semantic Vector Mesh (ChromaDB).
*   **Layers**:
    *   **Episodic**: Raw event stream (User/JARVIS interactions).
    *   **Semantic**: Abstracted knowledge and user preferences.
    *   **Procedural**: Workflow and agentic "recipes".
*   **The Abstraction Cycle**: A background "Consolidation Engine" that periodically (every 5m idle) summarizes raw experiences into conceptual facts.

---

## 4. Security & Authentication
*   **Auth Flow**:
    1.  Frontend sends **Handshake PIN** to `/auth/handshake`.
    2.  Backend verifies and signs a **JWT Token** (HS256).
    3.  Frontend stores token in session memory and includes it in all `Authorization: Bearer <token>` headers.
*   **Cryptographic Boundary**: The `JWT_SECRET` remains exclusively on the backend.

---

## 5. Persistence & Recovery
*   **Mutual Neural Resonance**: The Backend and Sentinel watch each other.
*   **Startup Anchor**: A Windows Startup shortcut (`Ignite_JARVIS.bat`) re-moors the system upon every reboot.
*   **Degraded Mode**: Safe fallbacks for Disk-Full, Memory-Lock, and Config-Corruption scenarios.
