#!/usr/bin/env bash
# One-shot environment setup for rendering the ZeroDay explainer videos.
# Tested on Ubuntu 22.04 / 24.04. Run as root (or with sudo).
set -euo pipefail

echo "==> Installing system dependencies..."
apt-get update
apt-get install -y --no-install-recommends \
    ffmpeg sox libsox-fmt-base \
    libcairo2-dev libpango1.0-dev pkg-config \
    python3-dev python3-pip python3-venv \
    libttspico-utils \
    build-essential

echo "==> Creating Python virtualenv (.venv)..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo ""
echo "==> Setup complete. To render a video:"
echo ""
echo "  source .venv/bin/activate"
echo "  echo 'ELEVEN_API_KEY=your_key_here' > .env   # for studio-quality voice"
echo "  python generate_narration.py                 # generates audio/*.mp3"
echo "  manim -qh encryption_explainer.py MasterScene"
echo ""
echo "Output lands in: media/videos/encryption_explainer/1080p60/MasterScene.mp4"
