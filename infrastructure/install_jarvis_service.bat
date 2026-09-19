@echo off
echo ====================================================
echo JARVIS AUTOMATIC STARTUP INJECTOR
echo ====================================================

set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "VBS_SOURCE=C:\jarvis AI\jarvis\infrastructure\stealth_boot.vbs"
set "VBS_DEST=%STARTUP_DIR%\jarvis_stealth_boot.vbs"

echo Injecting Sentinel Watchdog into Windows Startup...
copy "%VBS_SOURCE%" "%VBS_DEST%" /Y

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] JARVIS will now boot automatically in stealth mode on laptop startup.
) else (
    echo [ERROR] Failed to inject JARVIS into the Startup folder. Run as Administrator.
)

pause
