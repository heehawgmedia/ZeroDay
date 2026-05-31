import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.agent import agent
from backend.cache import cache
from backend.config import settings
from backend.memory import memory
from backend.sites import site_registry

app = FastAPI(title="Jarvis", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str
    message: str


class AddSiteRequest(BaseModel):
    url: str
    name: str | None = None
    sentry_project: str | None = None
    search_console_url: str | None = None


class RemoveSiteRequest(BaseModel):
    url: str


# ── Status ────────────────────────────────────────────────────────────────────

@app.get("/api/status")
async def status():
    return {
        "status": "ok",
        "integrations": settings.integration_status(),
    }


# ── Sessions ──────────────────────────────────────────────────────────────────

@app.post("/api/sessions")
async def new_session():
    return {"session_id": memory.new_session()}


@app.delete("/api/sessions/{session_id}")
async def clear_session(session_id: str):
    memory.clear(session_id)
    return {"cleared": True}


# ── Chat ──────────────────────────────────────────────────────────────────────

@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(400, "message cannot be empty")

    async def generate():
        async for event in agent.chat(req.session_id, req.message):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/history/{session_id}")
async def history(session_id: str):
    msgs = memory.get_messages(session_id)
    clean = [m for m in msgs if isinstance(m["content"], str)]
    return {"messages": clean}


# ── Site management ───────────────────────────────────────────────────────────

@app.get("/api/sites")
async def list_sites():
    return {"sites": site_registry.list_sites()}


@app.post("/api/sites")
async def add_site(req: AddSiteRequest):
    result = site_registry.add_site(
        req.url,
        name=req.name,
        sentry_project=req.sentry_project,
        search_console_url=req.search_console_url,
    )
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result


@app.delete("/api/sites")
async def remove_site(req: RemoveSiteRequest):
    removed = site_registry.remove_site(req.url)
    if not removed:
        raise HTTPException(404, f"{req.url} not found")
    cache.remove_site(req.url.rstrip("/"))
    return {"removed": req.url}


@app.patch("/api/sites/{url:path}/toggle")
async def toggle_site(url: str):
    site = site_registry.get_site(url)
    if not site:
        raise HTTPException(404, f"{url} not found")
    updated = site_registry.update_site(url, enabled=not site.get("enabled", True))
    return updated


# ── Dashboard (cached poll results) ──────────────────────────────────────────

@app.get("/api/dashboard")
async def dashboard():
    sites = site_registry.list_sites()
    all_cache = cache.read()
    rows = []
    for site in sites:
        url = site["url"]
        site_cache = all_cache.get(url, {})
        rows.append({
            "url": url,
            "name": site["name"],
            "enabled": site.get("enabled", True),
            "sentry_project": site.get("sentry_project"),
            "health": site_cache.get("health"),
            "pagespeed": site_cache.get("pagespeed"),
            "sentry": site_cache.get("sentry"),
        })
    return {
        "sites": rows,
        "poll_interval_seconds": settings.poll_interval_seconds,
    }


# ── Frontend static files ─────────────────────────────────────────────────────

_frontend = Path(__file__).parent.parent / "frontend"
if _frontend.exists():
    app.mount("/", StaticFiles(directory=str(_frontend), html=True), name="frontend")
