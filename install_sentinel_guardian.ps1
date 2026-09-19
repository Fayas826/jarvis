# 🛡️ J.A.R.V.I.S. O.M.E.G.A. — SENTINEL_GUARDIAN_INSTALLER
# Configures a Windows Scheduled Task for persistent background resonance.

$TaskName = "JarvisSentinelGuardian"
$PythonPath = "python"
$ScriptPath = "c:\jarvis AI\jarvis\jarvis_sentinel_v2.py"
$WorkingDir = "c:\jarvis AI\jarvis"

# 1. Create the Action
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath -WorkingDirectory $WorkingDir

# 2. Create the Trigger (At Startup)
$Trigger = New-ScheduledTaskTrigger -AtStartup

# 3. Create Settings (Restart on failure)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

# 4. Register the Task
# We use -User "SYSTEM" for maximum authority and background execution without window.
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -User "SYSTEM" -Force
    Write-Host "[SUCCESS] O.M.E.G.A. Sentinel Guardian registered."
    Write-Host "[INFO] The Sentinel will now auto-start on boot and recover within 60s of failure."
} catch {
    Write-Host "[FAIL] Registration failed: $_"
}
