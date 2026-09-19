# JARVIS AI - Training Monitor Dashboard
# Usage in PowerShell: .\monitor_training.ps1

$host.UI.RawUI.WindowTitle = "JARVIS AI - Neural Network Training Monitor"

$logFile = "C:\Users\Asus\.gemini\antigravity-ide\brain\7b743d62-ee01-421f-9811-857d037f759c\.system_generated\tasks\task-2171.log"

if (-not (Test-Path $logFile)) {
    Write-Host "Log file not found: $logFile" -ForegroundColor Red
    exit
}

Clear-Host

function Show-Header {
    Write-Host "==========================================================================" -ForegroundColor Cyan
    Write-Host "                🤖 JARVIS AI - BRAIN TRAINING DASHBOARD                    " -ForegroundColor Yellow -BackgroundColor Black
    Write-Host "==========================================================================" -ForegroundColor Cyan
    Write-Host " Active Target: Qwen2.5-Coder-3B-Instruct (LoRA / QLoRA 4-bit)" -ForegroundColor Gray
    Write-Host " Hardware: NVIDIA RTX 3050 | Fan Mode: Turbo (G-Helper)" -ForegroundColor Gray
    Write-Host "--------------------------------------------------------------------------" -ForegroundColor DarkGray
}

Show-Header

Get-Content -Path $logFile -Wait -Tail 20 | ForEach-Object {
    $line = $_
    if ($line -match "(\d+)%/.*?(\d+)/(\d+)\s+\[(.*?)<(.*?),.*?([\d\.]+)s/it\]") {
        $pct = [int]$matches[1]
        $currStep = $matches[2]
        $totalStep = $matches[3]
        $elapsed = $matches[4]
        $eta = $matches[5]
        $secPerIt = $matches[6]

        # Draw ASCII Progress Bar
        $barLength = 30
        $filled = [int](($pct / 100) * $barLength)
        $unfilled = $barLength - $filled
        $progressBar = ("█" * $filled) + ("░" * $unfilled)

        Write-Host "`r[$progressBar] $pct% | Step: $currStep/$totalStep | Speed: ${secPerIt}s/it | Elapsed: $elapsed | ETA: $eta " -ForegroundColor Green -NoNewline
    }
    elseif ($line -match "'loss': '([\d\.]+)'") {
        Write-Host ""
        Write-Host "  >> [TRAINING LOG] $line" -ForegroundColor Yellow
    }
    else {
        if ($line.Trim().Length -gt 0) {
            Write-Host "  $line" -ForegroundColor DarkGray
        }
    }
}
