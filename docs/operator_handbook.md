# 🧿 J.A.R.V.I.S. O.M.E.G.A. — OPERATOR HANDBOOK

## 1. Ignition Protocols (Startup)
*   **Automatic**: The system is moored to the Windows Startup registry. Simply powering on the machine and logging in will ignite the neural core.
*   **Manual Trigger**: If the watchdog fails, execute `c:\jarvis AI\jarvis\jarvis_guardian.bat`.
*   **HUD Launch**: Once the core is hot, access `http://localhost:5173` or use the voice command "Open HUD".

## 2. Decommissioning Protocols (Shutdown)
*   **Soft Shutdown**: Simply close the terminal windows. The Sentinel will attempt to restart them unless the process is explicitly killed via Task Manager.
*   **Hard Shutdown**: Execute `taskkill /f /im python.exe` in any terminal to silence both the Backend and Sentinel simultaneously.

## 3. Recovery Commands
*   **Port Reset**: `netstat -ano | findstr :5001` (Identify PID) -> `taskkill /f /pid <PID>` (Clear ghost port).
*   **Memory Purge**: `ollama stop llama3:8b` (Manual RAM recovery).
*   **Log Tail**: `Get-Content c:\jarvis AI\jarvis\omega_system.log -Wait` (Live telemetry).

## 4. Troubleshooting Guide

| **Symptom** | **Root Cause** | **Operator Response** |
| :--- | :--- | :--- |
| **"Backend Offline" on HUD** | Port 5001 Collision | Restart `api.py` manually. Check for ghost processes. |
| **Delayed Responses** | Memory Exhaustion | Check RAM usage. Unload Ollama manually if timer fails. |
| **Voice Recognition Failure** | Driver Conflict | Restart `jarvis_sentinel_v2.py`. Check Microphone permissions. |
| **Tunnel Timeout** | Localtunnel Jitter | Wait 10s for `ignite_tunnel.py` auto-reconnect logic. |

## 5. Security Protocols
*   **Access Token**: The HUD requires a valid JWT. If "Unauthorized", refresh the browser to trigger a re-handshake.
*   **Secrets Storage**: Do NOT store keys in `api.js`. All secrets must reside in the `.env` file on the backend.
