#!/bin/bash
# Installation script for Ubuntu/Debian

set -e

echo "=== Telegram Obsidian Capture Bot Setup ==="

# Install system dependencies
sudo apt update
sudo apt install -y python3.11 python3.11-venv ffmpeg

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -e .

# Copy env template if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file - please edit with your credentials"
fi

# Install systemd service
sudo cp scripts/telegram-capture.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegram-capture

echo ""
echo "=== Setup complete ==="
echo "1. Edit .env with your credentials"
echo "2. Start with: sudo systemctl start telegram-capture"
echo "3. Check logs: journalctl -u telegram-capture -f"
