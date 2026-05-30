# JARVIS — Project Intelligence System

AI assistant built on Claude with access to GitHub, Google Analytics, Notion, Linear, Trello, and local files.

## Quick Start

```bash
cp .env.example .env   # then fill in your API keys
./start.sh             # starts web server at http://localhost:8000
```

## Stack

- **Backend**: Python 3.11+, FastAPI, Anthropic SDK (Claude Opus)
- **Frontend**: Vanilla JS + CSS (no build step)
- **CLI**: Click + Rich

## Project Layout

```
backend/
  main.py    — FastAPI app, API routes, static file serving
  agent.py   — JarvisAgent: Claude tool-use loop + streaming
  tools.py   — Tool definitions and implementations (GitHub, GA4, Notion, Linear, Trello, Files)
  memory.py  — In-memory conversation storage
  config.py  — pydantic-settings config from .env

frontend/
  index.html — Chat UI
  style.css  — Dark JARVIS theme
  app.js     — SSE streaming client

cli/
  jarvis.py  — Click CLI (interactive REPL + one-shot mode)
```

## Running

```bash
# Server
uvicorn backend.main:app --reload

# CLI (one-shot)
python -m cli.jarvis "give me a status update"

# CLI (interactive)
python -m cli.jarvis
```

## Adding Integrations

Each integration is configured via `.env`. The `backend/tools.py` file contains one
function per tool that gracefully returns an error string if credentials are missing —
no crashes, just a clear message to the user.

To add a new tool:
1. Add the tool schema to `TOOL_DEFINITIONS` in `tools.py`
2. Implement the function
3. Add it to `_TOOL_MAP`
4. Add any new env vars to `config.py` and `.env.example`
