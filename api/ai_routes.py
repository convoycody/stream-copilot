from __future__ import annotations

import asyncio
import time
from fastapi import APIRouter, Body

from ai.engine import AIEngine


def make_ai_router(state: dict, engine: AIEngine) -> APIRouter:
    r = APIRouter()

    state.setdefault("_ai", {})
    state["_ai"].setdefault("enabled", True)
    state["_ai"].setdefault("interval_sec", 2.0)
    state["_ai"].setdefault("last_error", None)

    @r.get("/api/ai/state")
    def ai_state():
        return {
            "ok": True,
            "enabled": state["_ai"]["enabled"],
            "interval_sec": state["_ai"]["interval_sec"],
            "last_error": state["_ai"]["last_error"],
            "provider": (state.get("recommendations") or {}).get("provider"),
            "updated": (state.get("recommendations") or {}).get("updated"),
        }

    @r.post("/api/ai/enable")
    def ai_enable(payload: dict = Body(...)):
        state["_ai"]["enabled"] = bool(payload.get("enabled", True))
        state["updated"] = time.time()
        return {"ok": True, "enabled": state["_ai"]["enabled"]}

    @r.post("/api/ai/interval")
    def ai_interval(payload: dict = Body(...)):
        v = float(payload.get("interval_sec", 2.0))
        v = max(0.5, min(60.0, v))
        state["_ai"]["interval_sec"] = v
        state["updated"] = time.time()
        return {"ok": True, "interval_sec": v}

    @r.post("/api/ai/run_once")
    def ai_run_once():
        rec = engine.run_once()
        return {"ok": True, "recommendations": rec}

    return r


async def ai_loop(state: dict, engine: AIEngine) -> None:
    while True:
        try:
            if state.get("_ai", {}).get("enabled", True):
                engine.run_once()
            state["_ai"]["last_error"] = None
        except Exception as e:
            state["_ai"]["last_error"] = str(e)[:500]
        await asyncio.sleep(float(state.get("_ai", {}).get("interval_sec", 2.0)))
