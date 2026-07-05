#!/usr/bin/env bash
#
# Simple foreground runner for Linux/macOS (no systemd).
# Creates the virtualenv on first run, then starts the bot.
#
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${PROJECT_DIR}"

if [ ! -d "venv" ]; then
    echo "==> Creating virtualenv"
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
fi

if [ ! -f ".env" ]; then
    echo "ERROR: .env not found. Copy .env.example to .env and fill it in first."
    exit 1
fi

exec ./venv/bin/python bot.py
