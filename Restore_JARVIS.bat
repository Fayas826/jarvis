@echo off
color 0A
title JARVIS 1-Click System Restore
echo ===================================================
echo        JARVIS 1-CLICK SYSTEM RESTORE (O.M.E.G.A)
echo ===================================================
echo.
echo WARNING: This will overwrite your current JARVIS files with the latest backup!
echo Make sure JARVIS is fully closed before proceeding.
echo.
pause

echo.
echo [1/3] Locating newest Restore Point in C:\JARVIS_RESTORE_POINTS...

powershell -Command "$latest = Get-ChildItem -Path 'C:\JARVIS_RESTORE_POINTS' -Filter '*.zip' | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if ($latest) { Write-Host 'Found: ' $latest.FullName; Expand-Archive -Path $latest.FullName -DestinationPath 'C:\jarvis AI\jarvis' -Force; Write-Host '[SUCCESS] JARVIS System Restored!' -ForegroundColor Green } else { Write-Host '[ERROR] No restore points found!' -ForegroundColor Red }"

echo.
echo ===================================================
echo Restore Complete! You can now restart JARVIS.
echo ===================================================
pause
