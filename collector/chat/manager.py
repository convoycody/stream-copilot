from __future__ import annotations

import asyncio
import time
from typing import Dict, Optional

from collector.chat.base import ChatMessage, ChatIngestor


class ChatManager:
    def __init__(self, state: dict):
        self.state = state
        self._tasks: Dict[str, asyncio.Task] = {}
        self._ingestors: Dict[str, ChatIngestor] = {}

        self.state.setdefault("chat", {})
        self.state["chat"].setdefault("last_20", [])

    def _emit(self, msg: ChatMessage) -> None:
        # Normalize into your STATE shape
        item = msg.to_state()

        buf = list(self.state.get("chat", {}).get("last_20", []))
        buf.append(item)
        buf = buf[-20:]  # keep last 20
        self.state["chat"]["last_20"] = buf
        self.state["updated"] = time.time()

    def status(self) -> dict:
        out = {}
        for key, ing in self._ingestors.items():
            out[key] = {"running": ing.is_running()}
        return out

    async def start(self, key: str, ingestor: ChatIngestor) -> None:
        # key examples: "youtube", "twitch", "tiktok"
        await self.stop(key)

        self._ingestors[key] = ingestor

        async def runner():
            await ingestor.start()

        self._tasks[key] = asyncio.create_task(runner())

    async def stop(self, key: str) -> None:
        ing = self._ingestors.get(key)
        if ing:
            try:
                await ing.stop()
            except Exception:
                pass

        t = self._tasks.get(key)
        if t:
            t.cancel()
            try:
                await t
            except Exception:
                pass

        self._tasks.pop(key, None)
        self._ingestors.pop(key, None)

    async def stop_all(self) -> None:
        for key in list(self._tasks.keys()):
            await self.stop(key)

    def make_emit_cb(self):
        return self._emit
