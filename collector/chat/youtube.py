from __future__ import annotations

import asyncio
import time
from typing import Optional

from googleapiclient.discovery import build

from collector.chat.base import ChatIngestor, ChatMessage


class YouTubeIngestor(ChatIngestor):
    def __init__(self, *, api_key: str, live_chat_id: str, channel_label: str = "youtube", emit_cb=None):
        super().__init__(emit_cb=emit_cb)
        self.api_key = api_key
        self.live_chat_id = live_chat_id
        self.channel_label = channel_label
        self._running = False
        self._stop_evt = asyncio.Event()
        self._seen = set()

    def is_running(self) -> bool:
        return self._running

    async def stop(self) -> None:
        self._stop_evt.set()
        self._running = False

    async def start(self) -> None:
        self._running = True
        self._stop_evt.clear()

        yt = build("youtube", "v3", developerKey=self.api_key, cache_discovery=False)
        page_token: Optional[str] = None

        while self._running and not self._stop_evt.is_set():
            req = yt.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="snippet,authorDetails",
                maxResults=200,
                pageToken=page_token
            )
            resp = req.execute()

            items = resp.get("items", []) or []
            for it in items:
                mid = it.get("id")
                if mid and mid in self._seen:
                    continue
                if mid:
                    self._seen.add(mid)

                author = (it.get("authorDetails") or {}).get("displayName") or "user"
                text = (it.get("snippet") or {}).get("displayMessage") or ""
                if text:
                    self.emit_cb(ChatMessage(
                        platform="youtube",
                        channel=self.channel_label,
                        user=author,
                        text=text,
                        ts=time.time(),
                        raw={"id": mid},
                    ))

            page_token = resp.get("nextPageToken")

            # YouTube recommends waiting pollingIntervalMillis
            wait_ms = int(resp.get("pollingIntervalMillis") or 1500)
            await asyncio.sleep(max(0.8, wait_ms / 1000.0))
