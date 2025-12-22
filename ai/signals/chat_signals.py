from __future__ import annotations
import re
from collections import Counter
from typing import Any, Dict, List
from ai.models import AIInputs, ChatSignals

STOP = {
    "the","and","that","this","with","you","your","for","are","was","but","not","have","just","like",
    "from","what","when","where","how","its","it's","im","i'm","we","our","they","them","then","than",
    "about","into","out","over","under","too","very","can","cant","don't","does","did","will","would",
    "stream","live","today","tonight","build","building","code","coding"
}

def _words(text: str) -> List[str]:
    w = re.findall(r"[a-z0-9']{3,}", (text or "").lower())
    return [x for x in w if x not in STOP and not x.isdigit()]

def analyze_chat(inputs: AIInputs) -> ChatSignals:
    chat = inputs.chat_last or []
    lines: List[str] = []
    ts: List[float] = []
    for m in chat:
        if not isinstance(m, dict):
            continue
        t = (m.get("text") or "").strip()
        if t:
            lines.append(t)
        if m.get("ts"):
            try:
                ts.append(float(m["ts"]))
            except Exception:
                pass

    msg_count = len(lines)
    question_lines = [t for t in lines if "?" in t]
    question_count = len(question_lines)

    # momentum over last 2 minutes, normalized
    now = inputs.now
    recent = 0
    for m in chat:
        if isinstance(m, dict) and m.get("ts"):
            try:
                if now - float(m["ts"]) < 120:
                    recent += 1
            except Exception:
                pass
    momentum = min(1.0, recent / 8.0)  # 8 msgs/2m => 1.0

    # themes
    all_words: List[str] = []
    for t in lines:
        all_words.extend(_words(t))
    themes = [w for w, _ in Counter(all_words).most_common(6)]

    # top questions (trim, de-dup)
    top_q = []
    seen = set()
    for q in question_lines[-12:][::-1]:
        q2 = re.sub(r"\s+", " ", q).strip()
        if q2 and q2.lower() not in seen:
            top_q.append(q2[:140])
            seen.add(q2.lower())
        if len(top_q) >= 4:
            break

    suggested_prompts = []
    if themes:
        suggested_prompts.append(f"Quick poll: are we focusing on {themes[0]} or {themes[1] if len(themes)>1 else 'the UI'}?")
    if top_q:
        suggested_prompts.append(f"Answer this next: “{top_q[0]}”")

    return ChatSignals(
        msg_count=msg_count,
        question_count=question_count,
        momentum_2m=momentum,
        themes=themes,
        top_questions=top_q,
        suggested_prompts=suggested_prompts
    )
