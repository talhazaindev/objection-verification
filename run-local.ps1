# Run Objection prototype locally (no Docker required)
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "=== Objection Local Dev ===" -ForegroundColor Cyan

# Backend
Write-Host "`nStarting backend on http://127.0.0.1:8000 ..."
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:root\backend
    & .\.venv\Scripts\Activate.ps1
    uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
}

Start-Sleep -Seconds 3
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 5
    Write-Host "Backend: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "Backend failed to start. Is port 8000 in use?" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

# Frontend
Write-Host "`nStarting frontend on http://127.0.0.1:3000 ..."
$env:WATCHPACK_POLLING = "true"
$env:CHOKIDAR_USEPOLLING = "true"
Push-Location "$root\frontend"
if (-not (Test-Path .env.local)) {
    Copy-Item .env.local.example .env.local
    (Get-Content .env.local) -replace '.*', 'NEXT_PUBLIC_API_URL=http://localhost:8000' | Set-Content .env.local
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; `$env:WATCHPACK_POLLING='true'; npm run dev"
Pop-Location

Write-Host "`nOpen in browser:" -ForegroundColor Cyan
Write-Host "  App:     http://localhost:3000"
Write-Host "  API:     http://localhost:8000/docs"
Write-Host "  Health:  http://localhost:8000/health"
Write-Host "`nPress Ctrl+C to stop backend job, close frontend window separately."

Wait-Job $backendJob
