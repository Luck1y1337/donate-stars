#!/usr/bin/env bash
#
# One-shot deploy helper for a Linux VPS (Debian/Ubuntu).
# Creates a virtualenv, installs dependencies and registers a systemd
# service so the bot starts on boot and restarts on failure.
#
# Usage:
#   cd /path/to/Stars-Donate
#   chmod +x deploy/deploy.sh
#   ./deploy/deploy.sh
#
set -euo pipefail

SERVICE_NAME="luck1y-donate-bot"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_USER="$(whoami)"

echo "Project dir: ${PROJECT_DIR}"
echo "Service user: ${RUN_USER}"

if [ ! -f "${PROJECT_DIR}/.env" ]; then
    echo "ERROR: .env not found. Copy .env.example to .env and fill it in first."
    exit 1
fi

echo "==> Creating virtualenv and installing dependencies"
python3 -m venv "${PROJECT_DIR}/venv"
"${PROJECT_DIR}/venv/bin/pip" install --upgrade pip
"${PROJECT_DIR}/venv/bin/pip" install -r "${PROJECT_DIR}/requirements.txt"

echo "==> Building systemd unit"
UNIT_TMP="$(mktemp)"
sed \
    -e "s#REPLACE_USER#${RUN_USER}#g" \
    -e "s#REPLACE_DIR#${PROJECT_DIR}#g" \
    "${PROJECT_DIR}/deploy/${SERVICE_NAME}.service" > "${UNIT_TMP}"

echo "==> Installing service (requires sudo)"
sudo cp "${UNIT_TMP}" "/etc/systemd/system/${SERVICE_NAME}.service"
rm -f "${UNIT_TMP}"

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}"
sudo systemctl restart "${SERVICE_NAME}"

echo
echo "Done. Useful commands:"
echo "  sudo systemctl status ${SERVICE_NAME}"
echo "  sudo journalctl -u ${SERVICE_NAME} -f"
