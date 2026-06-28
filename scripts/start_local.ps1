# Start CS-OS locally (Windows)
# Usage: .\scripts\start_local.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Port = 8003
$EnvPath = Join-Path $Root ".env"
$venvPython = Join-Path $Root ".venv\Scripts\python.exe"

function Set-EnvValue {
    param([string]$Key, [string]$Value)
    if (-not (Test-Path $EnvPath)) { return }
    $lines = Get-Content $EnvPath
    $found = $false
    $newLines = foreach ($line in $lines) {
        if ($line -match "^$Key=") {
            $found = $true
            "$Key=$Value"
        } else {
            $line
        }
    }
    if (-not $found) { $newLines += "$Key=$Value" }
    $newLines | Set-Content $EnvPath -Encoding utf8NoBOM
}

function Get-EnvValue {
    param([string]$Key)
    if (-not (Test-Path $EnvPath)) { return "" }
    foreach ($line in Get-Content $EnvPath) {
        if ($line -match "^$Key=(.*)$") { return $matches[1].Trim() }
    }
    return ""
}

if (-not (Test-Path $venvPython)) {
    Write-Host "Creating venv..."
    python -m venv .venv
    & $venvPython -m pip install -q -r requirements.txt
}

if (-not (Test-Path $EnvPath)) {
    Copy-Item (Join-Path $Root ".env.example") $EnvPath
    Write-Host "Created .env from .env.example."
}

# Free the port — kill listeners and orphaned uvicorn --reload workers (Windows keeps
# multiprocessing.spawn children alive after the reloader parent dies).
$listenerPids = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object { $_.OwningProcess } | Sort-Object -Unique)
foreach ($procId in $listenerPids) {
    if ($procId -and $procId -ne 0) {
        Write-Host "Stopping listener on port $Port (PID $procId)"
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
}
Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'multiprocessing\.spawn.*spawn_main' } |
    ForEach-Object {
        Write-Host "Stopping orphaned uvicorn worker (PID $($_.ProcessId))"
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'uvicorn app\.main:app.*--port\s+$Port' } |
    ForEach-Object {
        Write-Host "Stopping stale uvicorn shell (PID $($_.ProcessId))"
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
Start-Sleep -Seconds 1

$stripeKey = Get-EnvValue "STRIPE_SECRET_KEY"
$webhookSecret = Get-EnvValue "STRIPE_WEBHOOK_SECRET"

if ((Get-Command stripe -ErrorAction SilentlyContinue) -and $stripeKey -and -not $webhookSecret) {
    Write-Host "Fetching Stripe webhook secret into .env ..."
    $printed = stripe listen --print-secret --api-key $stripeKey 2>&1 | Out-String
    if ($printed -match '(whsec_[a-zA-Z0-9]+)') {
        Set-EnvValue "STRIPE_WEBHOOK_SECRET" $matches[1]
        Write-Host "STRIPE_WEBHOOK_SECRET saved to .env"
    } else {
        Write-Host "Could not auto-fetch webhook secret. Run: stripe login"
    }
}

Write-Host ""
Write-Host "=== CS-OS local stack ==="
Write-Host "App:      http://127.0.0.1:$Port"
Write-Host "Login:    http://127.0.0.1:$Port/login  (password in .env OPS_PASSWORD)"
Write-Host "Checkout: http://127.0.0.1:$Port/checkout"
Write-Host ""

Write-Host "Starting app server..."
Start-Process powershell -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location '$Root'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 127.0.0.1 --port $Port"
)

if ((Get-Command stripe -ErrorAction SilentlyContinue) -and $stripeKey) {
    Write-Host "Starting Stripe webhook forwarder..."
    Start-Process powershell -ArgumentList @(
        "-NoExit", "-Command",
        "Set-Location '$Root'; stripe listen --forward-to localhost:$Port/webhooks/stripe --api-key '$stripeKey'"
    )
} elseif (-not $stripeKey) {
    Write-Host "STRIPE_SECRET_KEY missing in .env — checkout will not work."
} else {
    Write-Host "Stripe CLI not installed — https://stripe.com/docs/stripe-cli"
}

Write-Host ""
Write-Host "Done. Two extra PowerShell windows should be open."
Write-Host "Liaison guide: docs/LIAISON.md"
