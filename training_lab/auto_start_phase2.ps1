$logFile = "C:\Users\Asus\.gemini\antigravity-ide\brain\c754bc67-4c3f-4188-84a4-467b715b6355\.system_generated\tasks\task-924.log"
$targetString = "Master Orchestrator training complete. All 18 experts are trained!"
$found = $false

Write-Host "Waiting for Master Orchestrator to finish all 18 models..."

while (-not $found) {
    if (Test-Path $logFile) {
        $content = Get-Content -Path $logFile -Tail 50 -ErrorAction SilentlyContinue
        if ($content -match $targetString) {
            $found = $true
            Write-Host "Found completion signal!"
            break
        }
    }
    Start-Sleep -Seconds 30
}

Write-Host "Starting Phase 2: Advanced Defensive Cybersecurity Training..."
python phase2_defensive_trainer.py
