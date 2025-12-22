from __future__ import annotations

import os
import time
from fastapi import APIRouter, Body, HTTPException

from collector.chat.manager import ChatManager
from collector.chat.twitch import TwitchIngestor
from collector.chat.youtube import YouTubeIngestor
from collector.chat.base import ChatMessage


def make_chat_router(state: dict, manager: ChatManager) -> APIRouter:
    r = APIRouter()

    @r.get("/api/chat/status")
    def status():
        return {"ok": True, "status": manager.status(), "count": len(state.get("chat", {}).get("last_20", []))}

    @r.post("/api/chat/start")
    async def start_chat(payload: dict = Body(default={})):
        # payload can optionally override env (useful later)
        which = payload.get("which")  # "twitch"|"youtube"|"all"|None
        which = (which or "all").lower()

        emit_cb = manager.make_emit_cb()

        if which in ("twitch", "all"):
            ch = (payload.get("twitch_channel") or os.getenv("TWITCH_CHANNEL") or "").strip()
            tok = (payload.get("twitch_oauth_token") or os.getenv("TWITCH_OAUTH_TOKEN") or "").strip()
            nick = (payload.get("twitch_nick") or os.getenv("TWITCH_NICK") or "").strip()

            if ch and tok and nick:
                await manager.start("twitch", TwitchIngestor(channel=ch, oauth_token=tok, nick=nick, emit_cb=emit_cb))
            elif which == "twitch":
                raise HTTPException(status_code=400, detail="Missing TWITCH_CHANNEL / TWITCH_OAUTH_TOKEN / TWITCH_NICK")

        if which in ("youtube", "all"):
            key = (payload.get("youtube_api_key") or os.getenv("YOUTUBE_API_KEY") or "").strip()
            live_chat_id = (payload.get("youtube_live_chat_id") or os.getenv("YOUTUBE_LIVE_CHAT_ID") or "").strip()
            if key and live_chat_id:
                await manager.start("youtube", YouTubeIngestor(api_key=key, live_chat_id=live_chat_id, emit_cb=emit_cb))
            elif which == "youtube":
                raise HTTPException(status_code=400, detail="Missing YOUTUBE_API_KEY / YOUTUBE_LIVE_CHAT_ID")

        state["updated"] = time.time()
        return {"ok": True, "status": manager.status()}

    @r.post("/api/chat/stop")
    async def stop_chat(payload: dict = Body(default={})):
        which = (payload.get("which") or "all").lower()
        if which == "all":
            await manager.stop_all()
        else:
            await manager.stop(which)
        state["updated"] = time.time()
        return {"ok": True, "status": manager.status()}

    # Generic ingest endpoint (TikTok relay, or any other chat)
    @r.post("/api/chat/ingest")
    def ingest(payload: dict = Body(...)):
        platform = (payload.get("platform") or "unknown").strip()
        channel = (payload.get("channel") or "").strip() or platform
        user = (payload.get("user") or "user").strip()
        text = (payload.get("text") or "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="text required")

        msg = ChatMessage(platform=platform, channel=channel, user=user, text=text, ts=time.time())
        manager.make_emit_cb()(msg)
        return {"ok": True}

    return r
