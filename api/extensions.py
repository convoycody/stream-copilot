from __future__ import annotations

import time
from typing import Any, Dict, List

from fastapi import Body, HTTPException
from api.store import load_resources, save_resources, load_stream, save_stream, new_id

def _clamp01(x: float) -> float:
    try:
        x = float(x)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, x))

def compute_scores(state: Dict[str, Any]) -> None:
    """Rule-based scoring v0.1 (0..1)."""
    now = time.time()

    stream = state.get("stream") or {}
    obs = state.get("obs") or {}
    chat = (state.get("chat") or {}).get("last_20") or []
    resources = state.get("resources") or []

    started_ok = 1.0 if stream.get("started") else 0.3

    recent = [
        m for m in chat
        if isinstance(m, dict) and m.get("ts") and (now - float(m["ts"])) < 120
    ]
    msg_rate = min(1.0, len(recent) / 8.0)

    scene = (obs.get("scene") or "Unknown").strip()
    obs_ok = 1.0 if (scene and "disconnected" not in scene.lower() and scene.lower() != "unknown") else 0.4

    res_ok = min(1.0, len(resources) / 10.0)

    energy = 0.45 * msg_rate + 0.35 * started_ok + 0.20 * obs_ok
    engagement = 0.60 * msg_rate + 0.25 * started_ok + 0.15 * res_ok
    clarity = 0.55 * res_ok + 0.25 * started_ok + 0.20 * obs_ok
    pace = 0.50 * msg_rate + 0.35 * started_ok + 0.15 * obs_ok

    state["scores"] = {
        "energy": _clamp01(energy),
        "clarity": _clamp01(clarity),
        "engagement": _clamp01(engagement),
        "pace": _clamp01(pace),
    }

def register_extensions(app, STATE: Dict[str, Any]) -> None:
    # ---- bootstrap persisted state (idempotent) ----
    if "stream" not in STATE:
        try:
            STATE["stream"] = load_stream()
        except Exception:
            STATE["stream"] = {"topic": "Untitled Stream", "mode": "default", "started": None}

    if "resources" not in STATE:
        try:
            STATE["resources"] = load_resources()
        except Exception:
            STATE["resources"] = []

    STATE.setdefault("chat", {"last_20": []})
    STATE.setdefault("obs", {"scene": "Unknown", "sources": []})
    STATE.setdefault("scores", {})
    STATE.setdefault("updated", time.time())

    # ---- APIs ----
    @app.get("/api/resources")
    def api_get_resources():
        return {"resources": STATE.get("resources", [])}

    @app.post("/api/resources")
    def api_add_resource(payload: dict = Body(...)):
        text = (payload.get("text") or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="text is required")

        item = {
            "id": new_id(),
            "text": text,
            "title": (payload.get("title") or "").strip() or None,
            "url": (payload.get("url") or "").strip() or None,
            "tags": payload.get("tags") or [],
            "ts": time.time(),
        }

        items = list(STATE.get("resources", []))
        items.insert(0, item)
        items = items[:200]
        STATE["resources"] = items
        save_resources(items)

        STATE["updated"] = time.time()
        return {"ok": True, "resource": item, "count": len(items)}

    @app.delete("/api/resources/{rid}")
    def api_delete_resource(rid: str):
        items = list(STATE.get("resources", []))
        new_items = [x for x in items if str(x.get("id")) != str(rid)]
        if len(new_items) == len(items):
            raise HTTPException(status_code=404, detail="not found")
        STATE["resources"] = new_items
        save_resources(new_items)
        STATE["updated"] = time.time()
        return {"ok": True, "count": len(new_items)}

    @app.post("/api/stream/topic")
    def api_set_topic(payload: dict = Body(...)):
        topic = (payload.get("topic") or "").strip()
        if not topic:
            raise HTTPException(status_code=400, detail="topic is required")
        STATE.setdefault("stream", {})
        STATE["stream"]["topic"] = topic
        save_stream(STATE["stream"])
        STATE["updated"] = time.time()
        return {"ok": True, "stream": STATE["stream"]}

    @app.post("/api/stream/mode")
    def api_set_mode(payload: dict = Body(...)):
        mode = (payload.get("mode") or "").strip() or "default"
        STATE.setdefault("stream", {})
        STATE["stream"]["mode"] = mode
        save_stream(STATE["stream"])
        STATE["updated"] = time.time()
        return {"ok": True, "stream": STATE["stream"]}

    @app.post("/api/stream/start")
    def api_stream_start():
        STATE.setdefault("stream", {})
        STATE["stream"]["started"] = time.time()
        save_stream(STATE["stream"])
        STATE["updated"] = time.time()
        return {"ok": True, "stream": STATE["stream"]}

    @app.post("/api/stream/stop")
    def api_stream_stop():
        STATE.setdefault("stream", {})
        STATE["stream"]["started"] = None
        save_stream(STATE["stream"])
        STATE["updated"] = time.time()
        return {"ok": True, "stream": STATE["stream"]}

    # ---- scoring hook: if app already has a loop, it can call compute_scores ----
    # We won't start extra loops here to avoid duplication.
