from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AIInputs:
    topic: str = "Untitled Stream"
    mode: str = "default"
    started: Optional[float] = None

    scores: Dict[str, float] = field(default_factory=dict)
    obs_scene: str = "Unknown"

    chat_last_20: List[Dict[str, Any]] = field(default_factory=list)
    resources: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AIOutput:
    talking_points: List[str] = field(default_factory=list)
    next_question: str = ""
    summary: str = ""
    alerts: List[str] = field(default_factory=list)
    debug: Dict[str, Any] = field(default_factory=dict)
