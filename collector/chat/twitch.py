from __future__ import annotations

import asyncio
import os
import time
from typing import Optional

import websockets

from collector.chat.base import ChatIngestor, ChatMessage


class TwitchIngestor(ChatIngestor):
    def __init__(self, *, channel: str, oauth_token: str, nick: str, emit_cb):
        super().__init__(emit_cb=emit_cb)
        self.channel = channel.lstrip("#")
        self.oauth_token = oauth_token
        self.nick = nick
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._running = False
        self._stop_evt = asyncio.Event()

    def is_running(self) -> bool:
        return self._running

    async def stop(self) -> None:
        self._stop_evt.set()
        self._running = False
        if self._ws:
            try:
                await self._ws.close()
            except Exception:
                pass
        self._ws = None

    async def start(self) -> None:
        self._running = True
        self._stop_evt.clear()

        uri = "wss://irc-ws.chat.twitch.tv:443"
        async with websockets.connect(uri) as ws:
            self._ws = ws

            # CAP for tags (optional but nice)
            await ws.send("CAP REQ :twitch.tv/tags twitch.tv/commands twitch.tv/membership")

            # Auth
            tok = self.oauth_token
            if not tok.startswith("oauth:"):
                tok = "oauth:" + tok
            await ws.send(f"PASS {tok}")
            await ws.send(f"NICK {self.nick}")

            await ws.send(f"JOIN #{self.channel}")

            while self._running and not self._stop_evt.is_set():
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=25)
                except asyncio.TimeoutError:
                    await ws.send("PING :keepalive")
                    continue

                if raw.startswith("PING"):
                    await ws.send("PONG :tmi.twitch.tv")
                    continue

                # Basic PRIVMSG parse
                # Example: ... PRIVMSG #channel :hello
                if "PRIVMSG" in raw:
                    try:
                        # username usually before '!'
                        user = raw.split("!", 1)[0].split()[-1].lstrip(":")
                        # message after ' :'
                        text = raw.split(" :", 1)[1].strip()
                        self.emit_cb(ChatMessage(
                            platform="twitch",
                            channel=self.channel,
                            user=user or "user",
                            text=text,
                            ts=time.time(),
                            raw={"line": raw},
                        ))
                    except Exception:
                        pass
