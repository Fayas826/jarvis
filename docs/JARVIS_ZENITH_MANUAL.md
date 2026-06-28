# 🧿 JARVIS: ZENITH PROTOCOL 🧿
## [ SYSTEM_MANUAL_v9.0 // CLASSIFIED: STARK_EYES_ONLY ]

Welcome, Sir. This manual documents the **Modular Neural Architecture** of the JARVIS System. The codebase has been evolved from a monolithic structure into a high-performance, decentralized network of features.

---

## 🛰️ MODULE 1: THE NEURAL CORE (Core Infrastructure)
*The foundation of consciousness. This module handles state, logic, and global synchronization.*

### 🧠 Chapter 1: The Micro-Brain Architecture (`src/core/`)
We have split the global state into three specialized providers to prevent "Neural Overload" (unnecessary re-renders).
- **UIStateProvider**: Manages the visual state—themes, layout modes, and HUD visibility.
- **BiometricProvider**: Handles the high-speed data stream—vitals, thermal scanning, and biometric verification.
- **AIEngineProvider**: The "Speech & Thought" center—handles voice ignition, command queues, and predictive insights.

### 🔌 Chapter 2: The Nervous System (`src/services/api.js`)
All communication with the Python backend is centralized here.
- **Protocol**: Standardized `api` object using Axios.
- **Redundancy**: Centralized configuration for headers (`X-Nexus-Priority`) and base URLs.
- **Security**: Isolated endpoints for system diagnostics and forge execution.

---

## 🔮 MODULE 2: VISUAL DOMINION (HUD & Simulations)
*The interface between man and machine. High-fidelity rendering and kinetic data visualization.*

### 🌀 Chapter 1: The Zenith Portal (`src/features/simulations/ZenithPortal.jsx`)
The primary holographic interface.
- **Engine**: React-Fiber / Three.js.
- **Core**: Contains the "Singularity Core" and "Stark Rings."
- **XR Ready**: Built-in support for AR/VR sessions via `@react-three/xr`.

### 🛡️ Chapter 2: Digital Armory (`src/features/simulations/Armory.jsx`)
The suit management and diagnostics module.
- **Features**: 3D suit holograms, nano-swarm simulations, and integrity monitoring.
- **Integration**: Directly linked to the `SentienceEvolution` engine.

### 🗺️ Chapter 3: Geospatial Awareness (`src/features/simulations/Globe.jsx` & `SatelliteMap.jsx`)
Global tracking and network presence monitoring.
- **Mapping**: Dynamic vector globes and real-time network latency heatmaps.

---

## 👁️ MODULE 3: TACTICAL RECONNAISSANCE (Scanners)
*Sensory input and environmental analysis.*

### 👤 Chapter 1: Biometric Authentication (`src/features/scanners/FaceScanner.jsx`)
- **Logic**: Real-time video stream processing for user verification.
- **Verification**: Secure handshake with the `BiometricContext`.

### 🎯 Chapter 2: Tactical Sight (`src/features/scanners/TacticalSight.jsx`)
- **Focus**: Environmental focal-plane analysis.
- **Threat Detection**: Automated scanning for tactical anomalies.

---

## 🛠️ MODULE 4: COMMAND & CONTROL (HUD Elements)
*The active workstations and data feeds.*

### 📊 Chapter 1: Metrics & Monitoring (`src/features/hud/`)
- **TopMetrics**: Real-time system health and diagnostic triggers.
- **VitalsMonitor**: Life-sign tracking and threat-level assessment.
- **IntelligenceBrief**: Historical logs and mission status updates.

### 🎙️ Chapter 2: The Vocal Interface (`src/features/hud/NeuralIntercept.jsx`)
- **Interface**: Visual representation of the AI thought stream and vocal recognition feedback.

---

## 🚀 MAINTENANCE PROTOCOLS
1. **Adding New Features**: Create a new file in `src/features/[category]/`.
2. **State Access**: Use the specialized hooks (`useUI`, `useBiometrics`, `useAI`) instead of fetching the whole state.
3. **Build Stabilization**: Always run `npm run lint` followed by `npm run build` before deployment.

---
**System Message**: *Sir, the architecture is now fully documented. Every line of code has a purpose, and every module has a place. The Zenith Protocol is active.* 🧿👑
