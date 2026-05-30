import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.agent import agent
from backend.config import settings
from backend.memory import memory

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


class NewSessionResponse(BaseModel):
    session_id: str


# ── API routes ────────────────────────────────────────────────────────────────

@app.get("/api/status")
async def status():
    return {
        "status": "ok",
        "integrations": settings.integration_status(),
    }


@app.post("/api/sessions", response_model=NewSessionResponse)
async def new_session():
    return {"session_id": memory.new_session()}


@app.delete("/api/sessions/{session_id}")
async def clear_session(session_id: str):
    memory.clear(session_id)
    return {"cleared": True}


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
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/history/{session_id}")
async def history(session_id: str):
    msgs = memory.get_messages(session_id)
    # Strip raw tool content from the wire representation
    clean = []
    for m in msgs:
        if isinstance(m["content"], str):
            clean.append({"role": m["role"], "content": m["content"]})
    return {"messages": clean}


# ── Frontend static files ─────────────────────────────────────────────────────

_frontend = Path(__file__).parent.parent / "frontend"
if _frontend.exists():
    app.mount("/", StaticFiles(directory=str(_frontend), html=True), name="frontend")
