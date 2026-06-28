# Run Playwright E2E smoke tests against local CS-OS.
# Prereq: npm install (once). App on :8003 or let Playwright start it.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path "node_modules\@playwright\test")) {
    Write-Host "Installing Playwright..."
    npm install
    npx playwright install chromium
}

$env:BASE_URL = if ($env:BASE_URL) { $env:BASE_URL } else { "http://127.0.0.1:8003" }
$env:E2E_NO_SERVER = "1"
Write-Host "E2E target: $env:BASE_URL"
npx playwright test
