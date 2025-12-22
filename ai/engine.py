from __future__ import annotations

import time
from typing import Dict

from ai.types import AIInputs, AIOutput
from ai.providers.rulebased import RuleBasedProvider
from ai.providers.base import AIProvider


def _safe_str(x, default=""):
    try:
        s = str(x)
    except Exception:
        return default
    return s


class AIEngine:
    def __init__(self, state: dict):
        self.state = state
        self.provider: AIProvider = RuleBasedProvider()
        self.last_run_ts: float = 0.0

        self.state.setdefault("recommendations", {})
        self.state["recommendations"].setdefault("talking_points", [])
        self.state["recommendations"].setdefault("next_question", "")
        self.state["recommendations"].setdefault("summary", "No chat yet.")
        self.state["recommendations"].setdefault("alerts", [])
        self.state["recommendations"].setdefault("updated", time.time())
        self.state["recommendations"].setdefault("provider", self.provider.name)

    def set_provider(self, provider: AIProvider) -> None:
        self.provider = provider
        self.state["recommendations"]["provider"] = provider.name

    def build_inputs(self) -> AIInputs:
        st = self.state

        stream = st.get("stream") or {}
        obs = st.get("obs") or {}
        chat = st.get("chat") or {}
        scores = st.get("scores") or {}
        resources = st.get("resources") or []

        return AIInputs(
            topic=_safe_str(stream.get("topic") or "Untitled Stream"),
            mode=_safe_str(stream.get("mode") or "default"),
            started=stream.get("started"),
            scores=dict(scores) if isinstance(scores, dict) else {},
            obs_scene=_safe_str(obs.get("scene") or "Unknown"),
            chat_last_20=list(chat.get("last_20") or []),
            resources=list(resources),
        )

    def run_once(self) -> Dict:
        inputs = self.build_inputs()
        out: AIOutput = self.provider.generate(inputs)

        rec = self.state.setdefault("recommendations", {})
        rec["talking_points"] = out.talking_points
        rec["next_question"] = out.next_question
        rec["summary"] = out.summary
        rec["alerts"] = out.alerts
        rec["updated"] = time.time()
        rec["provider"] = self.provider.name
        rec["_debug"] = out.debug  # keep for now; we can hide later

        self.state["updated"] = time.time()
        self.last_run_ts = rec["updated"]
        return rec
