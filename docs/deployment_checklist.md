# 🚀 J.A.R.V.I.S. O.M.E.G.A. — DEPLOYMENT CHECKLIST

## 1. Core Dependencies (Python)
Ensure the following are installed in the global or venv environment:
*   `fastapi`, `uvicorn`, `httpx` (API Surface)
*   `chromadb`, `onnxruntime` (Neural Memory)
*   `faster-whisper`, `speech_recognition` (Acoustic Recon)
*   `psutil` (Watchdog Observability)
*   `python-dotenv` (Config Management)

## 2. External Neural Nodes
*   **Groq**: Valid API Key (Tier 1 Reasoning).
*   **Gemini**: Valid API Key (Tier 2 Reasoning / Vision).
*   **Ollama**: Installed and running locally (Tier 3 Reasoning).
    *   Models: `llama3:8b`, `phi3`.

## 3. Environment Variables (.env)
```env
GROQ_API_KEY=gsk_***
GEMINI_API_KEY=AIza***
JWT_SECRET=omega_zenith_***
SENTINEL_PIN=4422
PERSIST_DIRECTORY=neural_memory
```

## 4. Required Ports
*   **5001**: Backend (FastAPI).
*   **5173**: Frontend (Vite).
*   **11434**: Ollama API.

## 5. Persistence Configuration
*   **Startup Shortcut**: `C:\Users\Asus\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Ignite_JARVIS.bat`.
*   **Persistence Script**: `c:\jarvis AI\jarvis\api_starter.py`.

## 6. Backup Strategy
*   **Memory Backup**: Weekly compression of the `neural_memory/` directory.
*   **Config Backup**: Encrypted storage of `.env` file.
*   **Log Rotation**: Handled automatically by `system_logger.py` (Daily gzip).
