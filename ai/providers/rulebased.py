from __future__ import annotations

import re
from collections import Counter
from typing import List

from ai.types import AIInputs, AIOutput
from ai.providers.base import AIProvider


def _clamp01(x: float) -> float:
    try:
        x = float(x)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, x))


def _pick_keywords(lines: List[str]) -> List[str]:
    # lightweight keyword extraction for on-the-fly prompts
    text = " ".join(lines).lower()
    words = re.findall(r"[a-z0-9']{3,}", text)
    stop = {
        "the","and","that","this","with","you","your","for","are","was","but","not","have","just","like",
        "from","what","when","where","how","its","it's","im","i'm","we","our","they","them","then","than",
        "about","into","out","over","under","too","very","can","cant","don't","does","did","will","would",
        "stream","live","today","tonight"
    }
    words = [w for w in words if w not in stop and not w.isdigit()]
    common = [w for w, _ in Counter(words).most_common(6)]
    return common


class RuleBasedProvider(AIProvider):
    name = "rulebased"

    def generate(self, inputs: AIInputs) -> AIOutput:
        topic = (inputs.topic or "Untitled Stream").strip()
        mode = (inputs.mode or "default").strip()
        scene = (inputs.obs_scene or "Unknown").strip()

        scores = inputs.scores or {}
        energy = _clamp01(scores.get("energy", 0.5))
        clarity = _clamp01(scores.get("clarity", 0.5))
        engagement = _clamp01(scores.get("engagement", 0.5))
        pace = _clamp01(scores.get("pace", 0.5))

        chat = inputs.chat_last_20 or []
        chat_lines = [(m.get("text") or "") for m in chat if isinstance(m, dict)]
        chat_lines = [t.strip() for t in chat_lines if t.strip()]
        kws = _pick_keywords(chat_lines[:20])

        resources = inputs.resources or []
        res_titles = []
        for r in resources[:25]:
            if isinstance(r, dict):
                t = (r.get("title") or r.get("text") or "").strip()
                if t:
                    res_titles.append(t[:80])

        # ---- summary ----
        if not chat_lines:
            summary = "No chat yet."
        else:
            # quick “vibe” summary: questions + top keywords
            q_count = sum(1 for t in chat_lines if "?" in t)
            if kws:
                summary = f"Chat is active ({len(chat_lines)} msgs, {q_count} questions). Hot words: {', '.join(kws[:4])}."
            else:
                summary = f"Chat is active ({len(chat_lines)} msgs, {q_count} questions)."

        # ---- alerts ----
        alerts = []
        if clarity < 0.45:
            alerts.append("Clarity low: tighten the ‘one sentence’ explanation of what’s happening.")
        if engagement < 0.45:
            alerts.append("Engagement low: ask chat a single-choice question (A/B).")
        if pace < 0.40:
            alerts.append("Pace slow: narrate your next 2 steps out loud.")
        if energy < 0.40:
            alerts.append("Energy low: do a quick reset (sit/stand, sip water, smile, re-intro).")

        # ---- talking points (adaptive) ----
        tps = []

        # always useful anchors
        tps.append(f"Open loop: ‘Today we’re building {topic} — and I’ll show it working live.’")
        tps.append("Narrate: say what you just did, what you’re doing next, and why it matters.")
        tps.append("Micro check-in: ‘If you just joined, here’s the 10-second recap.’")

        if res_titles:
            tps.append(f"Reference a resource: ‘We’re using: {res_titles[0]}’")
        else:
            tps.append("Ask for context: ‘What are you hoping this stream helps you with?’")

        if kws:
            tps.append(f"Thread pull: ‘I saw chat mention {kws[0]} — want the quick version or deep dive?’")
        else:
            tps.append("Invite input: ‘Drop one thing you want me to cover before we wrap.’")

        # ---- next question ----
        if kws:
            next_q = f"On {kws[0]} — do you want the quick version or the deep dive?"
        else:
            next_q = "Do you want the quick version or the deep dive?"

        # mode/scene seasoning
        if mode != "default":
            tps.insert(1, f"Mode callout: ‘We’re in {mode} mode — expect faster decisions and fewer tangents.’")
        if scene and scene.lower() != "unknown":
            tps.insert(2, f"Scene check: ‘We’re on {scene} — tell me if the layout is readable.’")

        # cap and return
        out = AIOutput(
            talking_points=tps[:8],
            next_question=next_q,
            summary=summary,
            alerts=alerts[:5],
            debug={
                "kws": kws,
                "scores": {"energy": energy, "clarity": clarity, "engagement": engagement, "pace": pace},
                "topic": topic,
            }
        )
        return out
