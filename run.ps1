# Simple launcher for Windows PowerShell.
# Usage:  powershell -ExecutionPolicy Bypass -File run.ps1
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

if (-not (Test-Path "venv")) {
    Write-Host "==> Creating virtualenv"
    python -m venv venv
    .\venv\Scripts\python.exe -m pip install --upgrade pip
    .\venv\Scripts\pip.exe install -r requirements.txt
}

if (-not (Test-Path ".env")) {
    Write-Host "ERROR: .env not found. Copy .env.example to .env and fill it in first."
    exit 1
}

Write-Host "==> Starting bot. Press Ctrl+C to stop."
.\venv\Scripts\python.exe bot.py
