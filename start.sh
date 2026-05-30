#!/usr/bin/env bash
set -e

# Jarvis quick-start script

if [ ! -f .env ]; then
  echo "No .env found. Copying .env.example → .env"
  cp .env.example .env
  echo "Edit .env with your API keys, then re-run this script."
  exit 1
fi

if ! python -c "import anthropic" 2>/dev/null; then
  echo "Installing dependencies..."
  pip install -r requirements.txt
fi

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║          JARVIS  v1.0.0              ║"
echo "  ║   Just A Rather Very Intelligent     ║"
echo "  ║             System                   ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  Web UI → http://localhost:8000"
echo "  CLI    → python -m cli.jarvis"
echo ""

uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
