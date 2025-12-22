import os
import time
import json
import asyncio
from fastapi import FastAPI, Body, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from api.store import load_resources, load_stream, save_stream
from api.ui_home import render_home
from api.ui_ipad import render_ipad_home

from collector.obs_ws import obs_worker
from api.extensions import register_extensions

load_dotenv()

app = FastAPI(title="Stream Co-Pilot")

# ----------------------------
# Canonical in-memory state
# ----------------------------
STATE = {
    "stream": {"topic": "Untitled Stream", "mode": "default", "started": None},
    "scores": {"energy": 0.65, "clarity": 0.70, "engagement": 0.55, "pace": 0.60},
    "obs": {"scene": "OBS: not connected", "sources": [], "agent": {"status": "unknown", "last_seen": None, "agent_id": None}},
    "chat": {"last_20": []},
    "resources": [],
    "recommendations": {
        "talking_points": [
            "Explain what you’re doing in one sentence.",
            "Call out progress + what’s next.",
            "Ask chat a specific question.",
        ],
        "next_question": "Do you want the quick version or the deep dive?",
        "summary": "No chat yet.",
    },
    "updated": None,
}

# ----------------------------
# Persistence bootstrap
# ----------------------------
try:
    STATE["stream"] = load_stream() or STATE["stream"]
except Exception:
    pass

try:
    STATE["resources"] = load_resources() or []
except Exception:
    pass


# ----------------------------
# Models
# ----------------------------
class ChatMsg(BaseModel):
    user: str
    text: str
    ts: float | None = None


class StreamConfig(BaseModel):
    topic: str | None = None
    mode: str | None = None


class AgentObsPayload(BaseModel):
    agent_id: str | None = None
    scene: str | None = None
    sources: list[dict] | None = None
    status: str | None = None
    ts: float | None = None


# ----------------------------
# Scoring
# ----------------------------
def compute_scores(state: dict) -> None:
    """Rule-based scoring v0.1: 0..1 scores used by UI."""
    now = time.time()

    stream = state.get("stream", {}) or {}
    obs = state.get("obs", {}) or {}
    chat = (state.get("chat", {}) or {}).get("last_20", []) or []
    resources = state.get("resources", []) or []

    started_ok = 1.0 if stream.get("started") else 0.3

    recent = [
        m for m in chat
        if isinstance(m, dict) and m.get("ts") and (now - float(m["ts"])) < 120
    ]
    msg_rate = min(1.0, len(recent) / 8.0)

    scene = (obs.get("scene") or "Unknown").strip()
    obs_ok = 1.0 if (scene and "disconnected" not in scene.lower() and scene.lower() != "unknown") else 0.4

    # Agent staleness: if agent mode is on and we haven't seen it recently, penalize OBS score
    agent = (obs.get("agent") or {})
    last_seen = agent.get("last_seen")
    if (os.getenv("OBS_MODE", "") or "").strip().lower() == "agent":
        if not last_seen or (now - float(last_seen)) > 8:
            obs_ok = min(obs_ok, 0.35)

    res_ok = min(1.0, len(resources) / 10.0)

    def clamp(x: float) -> float:
        return max(0.0, min(1.0, float(x)))

    state["scores"] = {
        "energy": clamp(0.45 * msg_rate + 0.35 * started_ok + 0.20 * obs_ok),
        "engagement": clamp(0.60 * msg_rate + 0.25 * started_ok + 0.15 * res_ok),
        "clarity": clamp(0.55 * res_ok + 0.25 * started_ok + 0.20 * obs_ok),
        "pace": clamp(0.50 * msg_rate + 0.35 * started_ok + 0.15 * obs_ok),
    }


async def score_worker() -> None:
    while True:
        try:
            compute_scores(STATE)
            STATE["updated"] = time.time()
        except Exception:
            pass
        await asyncio.sleep(2.0)


# ----------------------------
# Startup
# ----------------------------
@app.on_event("startup")
async def startup_event():
    STATE["updated"] = time.time()
    asyncio.create_task(obs_worker(STATE))
    asyncio.create_task(score_worker())


# ----------------------------
# Core APIs
# ----------------------------
@app.get("/api/state")
def get_state():
    compute_scores(STATE)
    STATE["updated"] = time.time()
    return STATE


@app.post("/api/chat")
def post_chat(msg: ChatMsg):
    m = msg.model_dump()
    if not m.get("ts"):
        m["ts"] = time.time()

    STATE.setdefault("chat", {}).setdefault("last_20", [])
    STATE["chat"]["last_20"].append(m)
    STATE["chat"]["last_20"] = STATE["chat"]["last_20"][-20:]

    STATE.setdefault("recommendations", {})
    STATE["recommendations"]["summary"] = f"Latest: {m['user']}: {m['text'][:80]}"
    STATE["updated"] = time.time()
    compute_scores(STATE)
    return {"ok": True}


@app.post("/api/stream/config")
def set_stream_config(cfg: StreamConfig):
    if cfg.topic:
        STATE.setdefault("stream", {})["topic"] = cfg.topic
    if cfg.mode:
        STATE.setdefault("stream", {})["mode"] = cfg.mode

    # persist
    try:
        save_stream(STATE["stream"])
    except Exception:
        pass

    STATE["updated"] = time.time()
    compute_scores(STATE)
    return {"ok": True, "stream": STATE["stream"]}


# ----------------------------
# Agent mode: push OBS snapshot
# ----------------------------
@app.post("/api/agent/obs")
def agent_push_obs(payload: AgentObsPayload, request: Request):
    expected = (os.getenv("AGENT_TOKEN") or "").strip()
    got = (request.headers.get("x-agent-token") or "").strip()
    if expected and got != expected:
        raise HTTPException(status_code=401, detail="bad agent token")

    ts = payload.ts or time.time()
    agent_id = payload.agent_id or "unknown-agent"

    STATE.setdefault("obs", {}).setdefault("agent", {})
    STATE["obs"]["agent"].update({
        "status": payload.status or "ok",
        "last_seen": ts,
        "agent_id": agent_id,
    })

    if payload.scene is not None:
        STATE["obs"]["scene"] = payload.scene
    if payload.sources is not None:
        STATE["obs"]["sources"] = payload.sources

    STATE["updated"] = time.time()
    compute_scores(STATE)
    return {"ok": True, "obs": STATE["obs"]}


# ----------------------------
# Extensions (resources + stream controls, single registration)
# ----------------------------
register_extensions(app, STATE)


# ----------------------------
# UI
# ----------------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # ui_home.py should render safely on desktop
    return HTMLResponse(render_home())


@app.get("/ipad", response_class=HTMLResponse)
def ipad(request: Request):
    return HTMLResponse(render_ipad_home())
