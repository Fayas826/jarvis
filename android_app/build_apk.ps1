# JARVIS Android APK Builder
# Run this script to build and install the APK on your Redmi phone
# Prerequisites: Docker Desktop running, ADB phone connected via USB

$ADB = "C:\AMD\platform-tools\adb.exe"
$APP_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$APK_OUT = "$APP_DIR\bin"

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  J.A.R.V.I.S  ANDROID APK BUILDER" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# ── STEP 1: Check Docker ──────────────────────────────────────────
Write-Host "[1/5] Checking Docker..." -ForegroundColor Yellow
$dockerCheck = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker Desktop is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}
Write-Host "     Docker is running ✓" -ForegroundColor Green

# ── STEP 2: Generate App Icon ─────────────────────────────────────
Write-Host "[2/5] Generating JARVIS app icon..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "$APP_DIR\assets" -Force | Out-Null

# Create a simple placeholder icon if not present
if (-not (Test-Path "$APP_DIR\assets\jarvis_icon.png")) {
    Write-Host "     (No icon found - build will use default icon)" -ForegroundColor DarkYellow
}
Write-Host "     Assets ready ✓" -ForegroundColor Green

# ── STEP 3: Build APK via Docker ─────────────────────────────────
Write-Host "[3/5] Building APK (this takes 20-30 min first time)..." -ForegroundColor Yellow
Write-Host "      Logs will stream below:" -ForegroundColor DarkGray
Write-Host ""

New-Item -ItemType Directory -Path $APK_OUT -Force | Out-Null

# Build inside Docker with Buildozer
docker run --rm `
    -v "${APP_DIR}:/app" `
    -v "jarvis_buildozer_cache:/root/.buildozer" `
    kivy/buildozer:latest `
    bash -c "cd /app && buildozer -v android debug 2>&1"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "BUILD FAILED!" -ForegroundColor Red
    Write-Host "Check the log above for errors." -ForegroundColor Red
    exit 1
}

# ── STEP 4: Find the APK ──────────────────────────────────────────
Write-Host ""
Write-Host "[4/5] Locating built APK..." -ForegroundColor Yellow

$apk = Get-ChildItem "$APP_DIR\bin\*.apk" -ErrorAction SilentlyContinue | 
       Sort-Object LastWriteTime -Descending | 
       Select-Object -First 1

if (-not $apk) {
    Write-Host "ERROR: APK file not found in bin/ directory!" -ForegroundColor Red
    exit 1
}

Write-Host "     Found: $($apk.Name) ($([math]::Round($apk.Length/1MB, 1)) MB)" -ForegroundColor Green

# ── STEP 5: Install on Phone ──────────────────────────────────────
Write-Host "[5/5] Installing on your Redmi phone via ADB..." -ForegroundColor Yellow

# Check ADB device
$devices = & $ADB devices
if ($devices -notmatch "uozd6pcuijqozhh6") {
    Write-Host "WARNING: Redmi phone not detected on USB!" -ForegroundColor DarkYellow
    Write-Host "Connect your phone via USB with USB Debugging enabled." -ForegroundColor DarkYellow
    
    $choice = Read-Host "Install anyway? (y/n)"
    if ($choice -ne "y") { exit 0 }
}

# Install APK
Write-Host "     Installing APK..." -ForegroundColor Yellow
& $ADB install -r $apk.FullName

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "  APK INSTALLED SUCCESSFULLY! " -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps on your Redmi phone:" -ForegroundColor Cyan
    Write-Host "  1. Find 'JARVIS' app in your app drawer" -ForegroundColor White
    Write-Host "  2. Open it and grant all permissions" -ForegroundColor White
    Write-Host "  3. Settings → Apps → Default Apps → Digital Assistant → JARVIS" -ForegroundColor White
    Write-Host "  4. Now long-press power button = JARVIS activates!" -ForegroundColor White
    Write-Host "  5. Say 'JARVIS' anytime → glowing orb appears" -ForegroundColor White
    Write-Host "  6. Say 'JARVIS unlock' → touch fingerprint sensor on power button" -ForegroundColor White
    Write-Host ""
    
    # Launch the app
    $launch = Read-Host "Launch JARVIS on phone now? (y/n)"
    if ($launch -eq "y") {
        & $ADB shell am start -n "com.fayas.jarvis/com.fayas.jarvis.MainActivity"
        Write-Host "JARVIS launched on your Redmi!" -ForegroundColor Green
    }
} else {
    Write-Host "INSTALL FAILED! Check USB connection and USB Debugging." -ForegroundColor Red
}
