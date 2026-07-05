@echo off
REM Simple launcher for Windows. Double-click or run from cmd.
cd /d "%~dp0"

if not exist "venv\" (
    echo ==^> Creating virtualenv
    python -m venv venv
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\pip.exe install -r requirements.txt
)

if not exist ".env" (
    echo ERROR: .env not found. Copy .env.example to .env and fill it in first.
    pause
    exit /b 1
)

echo ==^> Starting bot. Press Ctrl+C to stop.
venv\Scripts\python.exe bot.py
pause
