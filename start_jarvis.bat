@echo off
title JARVIS Master Boot Sequence
color 0A

echo ===================================================
echo             JARVIS SYSTEM INITIALIZATION
echo ===================================================
echo.
echo [1/3] Waking up Meta-Architect (Self-Healing Daemon)...
start "JARVIS Meta-Architect" cmd /c "title JARVIS Meta-Architect & python core\orchestration\meta_architect_agent.py --watch --interval 60"
timeout /t 2 >nul

echo [2/3] Initializing FastAPI Brain (Backend AI Core)...
start "JARVIS Backend Core" cmd /c "title JARVIS Backend API & cd backend & uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 >nul

echo [3/3] Booting Next.js HUD Interface (Frontend)...
start "JARVIS UI" cmd /c "title JARVIS Frontend & cd frontend & npm run dev"
timeout /t 3 >nul

echo.
echo ===================================================
echo ALL SYSTEMS ONLINE.
echo The JARVIS Swarm is now awake and monitoring.
echo ===================================================
echo.
pause
