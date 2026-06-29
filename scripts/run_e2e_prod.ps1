# Production launch-gate Playwright suite (read-only + checkout redirect; no mutating ops).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Test-Path "node_modules\@playwright\test")) {
    npm install
    npx playwright install chromium
}

$env:BASE_URL = if ($env:BASE_URL) { $env:BASE_URL } else { "https://doggybagg.cc" }
$env:E2E_PROD = "1"
$env:E2E_NO_SERVER = "1"

Write-Host "E2E prod gates against $env:BASE_URL"
npx playwright test e2e/prod-launch.spec.js
