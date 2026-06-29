# Run Playwright E2E against CS-OS (starts isolated server on :8012 unless E2E_NO_SERVER=1).
# Prereq: npm install (once).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path "node_modules\@playwright\test")) {
    Write-Host "Installing Playwright..."
    npm install
    npx playwright install chromium
}

if (-not $env:BASE_URL) { $env:BASE_URL = "http://127.0.0.1:8012" }
if (-not $env:OPS_PASSWORD) { $env:OPS_PASSWORD = "csos-local" }
Write-Host "E2E target: $env:BASE_URL (auto-start unless E2E_NO_SERVER=1)"
npx playwright test
