from __future__ import annotations

import abc
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ChatMessage:
    platform: str          # "youtube" | "twitch" | "tiktok"
    channel: str           # channel name / id
    user: str
    text: str
    ts: float = 0.0
    raw: Optional[Dict[str, Any]] = None

    def to_state(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "channel": self.channel,
            "user": self.user,
            "text": self.text,
            "ts": self.ts or time.time(),
        }


class ChatIngestor(abc.ABC):
    """
    A running task that connects to a chat source and emits normalized ChatMessage.
    """
    def __init__(self, *, emit_cb):
        self.emit_cb = emit_cb  # callable(ChatMessage) -> None

    @abc.abstractmethod
    async def start(self) -> None:
        ...

    @abc.abstractmethod
    async def stop(self) -> None:
        ...

    @abc.abstractmethod
    def is_running(self) -> bool:
        ...
