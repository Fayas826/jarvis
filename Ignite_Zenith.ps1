# JARVIS O.M.E.G.A. - Ignite_Zenith.ps1
# Master PowerShell Launcher - Zero CMD Window Edition

$BASE_DIR    = "c:\jarvis AI\jarvis"
$BACKEND_DIR = "$BASE_DIR\backend"
$PYTHON      = "C:\Users\Asus\AppData\Local\Programs\Python\Python311\python.exe"
$PYTHONW     = "C:\Users\Asus\AppData\Local\Programs\Python\Python311\pythonw.exe"

# Remove stale shutdown lock
if (Test-Path "$BASE_DIR\shutdown.lock") { Remove-Item "$BASE_DIR\shutdown.lock" -Force }

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  JARVIS O.M.E.G.A. - IGNITION SEQUENCE" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan

# Step 1: Purge stale JARVIS processes
Write-Host "[1/4] Purging stale processes..." -ForegroundColor Yellow
Get-CimInstance Win32_Process -Filter "name='python.exe' OR name='pythonw.exe'" | ForEach-Object {
    $cmd = $_.CommandLine
    if ($cmd -and ($cmd -match "api\.py" -or $cmd -match "jarvis_sentinel_v2\.py")) {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        Write-Host "  Killed PID $($_.ProcessId)" -ForegroundColor DarkYellow
    }
}
Start-Sleep -Seconds 2

# Step 2: Launch Backend - fully hidden, logs via file
Write-Host "[2/4] Igniting Backend (hidden)..." -ForegroundColor Yellow
$backendProc = Start-Process `
    -FilePath    $PYTHONW `
    -ArgumentList "`"$BACKEND_DIR\api.py`"" `
    -WorkingDirectory $BACKEND_DIR `
    -PassThru `
    -WindowStyle Hidden `
    -RedirectStandardOutput "$BACKEND_DIR\api_stdout.log" `
    -RedirectStandardError "$BACKEND_DIR\api_stderr.log"
Write-Host "  Backend PID: $($backendProc.Id)" -ForegroundColor Green

# Step 3: Launch Sentinel - hidden, logs via file
Write-Host "[3/4] Igniting Sentinel (hidden)..." -ForegroundColor Yellow
$sentinelProc = Start-Process `
    -FilePath    $PYTHONW `
    -ArgumentList "`"$BASE_DIR\jarvis_sentinel_v2.py`"" `
    -WorkingDirectory $BASE_DIR `
    -PassThru `
    -WindowStyle Hidden `
    -RedirectStandardOutput "$BASE_DIR\sentinel_stdout.log" `
    -RedirectStandardError "$BASE_DIR\sentinel_stderr.log"
Write-Host "  Sentinel PID: $($sentinelProc.Id)" -ForegroundColor Green

# Step 4: Wait for port 5001
Write-Host "[4/4] Waiting for backend on port 5001..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $tcp.Connect("127.0.0.1", 5001)
        $tcp.Close()
        $ready = $true
        break
    } catch {}
    Start-Sleep -Seconds 1
}

if ($ready) {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  JARVIS O.M.E.G.A. ONLINE - Port 5001 LIVE" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Backend did not respond in 30s. Check api_stderr.log" -ForegroundColor Red
}

Write-Host ""
Write-Host "  Backend log  : $BACKEND_DIR\api_stdout.log" -ForegroundColor Cyan
Write-Host "  Sentinel log : $BASE_DIR\sentinel_stdout.log" -ForegroundColor Cyan
Write-Host "  [Ctrl+C] to stop" -ForegroundColor DarkGray
Write-Host ""

# Step 5: Tail backend log live in this console
Write-Host "--- LIVE BACKEND LOG ---" -ForegroundColor DarkCyan
$logPath = "$BACKEND_DIR\api_stdout.log"

# Wait for log file to appear
$waited = 0
while (-not (Test-Path $logPath) -and $waited -lt 15) {
    Start-Sleep -Seconds 1
    $waited++
}

if (Test-Path $logPath) {
    try {
        Get-Content -Path $logPath -Wait -Tail 0 | ForEach-Object {
            Write-Host "[API] $_" -ForegroundColor Gray
        }
    } catch {
        Write-Host "Log stream ended." -ForegroundColor DarkGray
    }
} else {
    Write-Host "  No log file yet. Sentinel will route backend logs on recovery." -ForegroundColor DarkGray
    Write-Host "  Keeping console alive..." -ForegroundColor DarkGray
    while ($true) { Start-Sleep -Seconds 10 }
}
