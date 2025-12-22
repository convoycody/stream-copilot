from __future__ import annotations
import time
from typing import Dict, List
from ai.models import AIInputs, AIOutput, StreamState, HealthSignals, TopicPlan, RecItem
from ai.signals.chat_signals import analyze_chat
from ai.signals.resource_signals import analyze_resources
from ai.planners.topic_plan import build_topic_plan

def _clamp01(x) -> float:
    try:
        x = float(x)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, x))

def _has_chat(inputs: AIInputs) -> bool:
    return bool(inputs.chat_last)

def _has_resources(inputs: AIInputs) -> bool:
    return bool(inputs.resources)

def _obs_ok(inputs: AIInputs) -> bool:
    scene = (inputs.obs_scene or "Unknown").strip().lower()
    return (scene != "unknown") and ("disconnected" not in scene)

def _coverage(inputs: AIInputs) -> Dict[str, float]:
    # 0..1 “data availability” per channel
    cov = {
        "topic": 1.0 if (inputs.topic and inputs.topic.strip()) else 0.2,
        "obs": 1.0 if _obs_ok(inputs) else 0.3,
        "chat": 1.0 if _has_chat(inputs) else 0.2,
        "resources": 1.0 if _has_resources(inputs) else 0.2,
        "scores": 1.0 if bool(inputs.scores) else 0.5,
        "started": 1.0 if inputs.started else 0.4,
    }
    return cov

def _overall_confidence(cov: Dict[str, float]) -> float:
    # weighted coverage = “how grounded can we be”
    w = {"topic":0.15,"obs":0.15,"chat":0.25,"resources":0.20,"scores":0.10,"started":0.15}
    return _clamp01(sum(cov[k]*w[k] for k in w))

def _usefulness(scores: Dict[str, float], cov: Dict[str, float]) -> float:
    # “is the model likely to help right now”
    e = _clamp01(scores.get("engagement", 0.5))
    c = _clamp01(scores.get("clarity", 0.5))
    # if chat/resources missing, usefulness drops (because we’d be guessing)
    base = 0.45*e + 0.35*c + 0.20*_overall_confidence(cov)
    return _clamp01(base)

def _rec(id_: str, kind: str, text: str, confidence: float, why: str, based_on: List[str]) -> RecItem:
    return RecItem(
        id=id_,
        kind=kind, text=text,
        confidence=_clamp01(confidence),
        why=(why or "")[:180],
        based_on=based_on[:6],
    )

def _phase_transition(state: StreamState, inputs: AIInputs, chat_momentum: float, q_count: int) -> StreamState:
    now = inputs.now
    started = bool(inputs.started)

    if not started:
        state.phase = "PRELIVE" if inputs.mode != "offline" else "OFFLINE"
        state.entered_ts = state.entered_ts or now
        return state

    if state.phase in ("OFFLINE","PRELIVE"):
        state.phase = "LIVE"
        state.entered_ts = now
        return state

    if q_count >= 3 and chat_momentum > 0.4 and state.phase not in ("QNA","WRAP"):
        state.phase = "QNA"
        state.entered_ts = now
        return state

    if state.phase == "LIVE" and chat_momentum > 0.55 and q_count == 0:
        state.phase = "DEEP_DIVE"
        state.entered_ts = now
        return state

    live_for = now - float(inputs.started or now)
    if live_for > 60*55:
        state.phase = "WRAP"
        state.entered_ts = now
        return state

    return state

def _health(inputs: AIInputs, chat_count: int, res_count: int) -> HealthSignals:
    obs_ok = _obs_ok(inputs)
    stream_started = bool(inputs.started)
    chat_ok = chat_count > 0
    resources_ok = res_count > 0

    alerts: List[str] = []
    if not obs_ok:
        alerts.append("OBS not detected: confirm obs-websocket is connected.")
    if stream_started and not chat_ok:
        alerts.append("No chat yet: ask a direct question to pull people in.")
    if not resources_ok:
        alerts.append("No resources loaded: add links/notes so AI can cite specifics.")
    return HealthSignals(
        obs_ok=obs_ok,
        chat_ok=chat_ok,
        resources_ok=resources_ok,
        stream_started=stream_started,
        alerts=alerts
    )

def compile_output(inputs: AIInputs, state: StreamState) -> AIOutput:
    chat = analyze_chat(inputs)
    res = analyze_resources(inputs, chat)
    plan: TopicPlan = build_topic_plan(inputs)
    health = _health(inputs, chat.msg_count, res.count)

    cov = _coverage(inputs)
    overall = _overall_confidence(cov)
    useful = _usefulness(inputs.scores or {}, cov)

    state = _phase_transition(state, inputs, chat.momentum_2m, chat.question_count)

    scores = inputs.scores or {}
    energy = _clamp01(scores.get("energy", 0.5))
    clarity = _clamp01(scores.get("clarity", 0.5))
    engagement = _clamp01(scores.get("engagement", 0.5))
    pace = _clamp01(scores.get("pace", 0.5))

    # ---- Alerts as items ----
    alert_items: List[RecItem] = []
    for i, a in enumerate(health.alerts):
        # higher confidence because these are direct checks
        based = []
        if "OBS" in a: based = ["obs"]
        elif "chat" in a.lower(): based = ["chat"]
        elif "resources" in a.lower(): based = ["resources"]
        alert_items.append(_rec(f"alert_health_{i}", "alert", a, 0.85*overall + 0.10, "Direct health rule.", based))

    if clarity < 0.45:
        alert_items.append(_rec("alert_clarity", "alert",
            "Clarity low: say the goal in ONE sentence, then do the next step.",
            0.70*overall + 0.10, f"Clarity score is {int(clarity*100)}%.", ["scores","topic"]))
    if engagement < 0.45:
        alert_items.append(_rec("alert_engage", "alert",
            "Engagement low: ask chat A/B + wait 10 seconds before continuing.",
            0.70*overall + 0.10, f"Engagement score is {int(engagement*100)}%.", ["scores","chat"]))
    if pace < 0.40:
        alert_items.append(_rec("alert_pace", "alert",
            "Pace slow: narrate actions; keep each step under 30 seconds.",
            0.65*overall + 0.10, f"Pace score is {int(pace*100)}%.", ["scores"]))
    if energy < 0.40:
        alert_items.append(_rec("alert_energy", "alert",
            "Energy low: quick reset - sip, smile, re-intro in 8 seconds.",
            0.60*overall + 0.10, f"Energy score is {int(energy*100)}%.", ["scores"]))

    # ---- Summary (still string) ----
    if chat.msg_count == 0:
        summary = "No chat yet."
    else:
        th = ", ".join(chat.themes[:4]) if chat.themes else "—"
        summary = f"{chat.msg_count} msgs • {chat.question_count} questions • Momentum {int(chat.momentum_2m*100)}% • Themes: {th}"

    # ---- Next question as item ----
    if chat.top_questions:
        nq_text = chat.top_questions[0]
        nq = _rec("q_top", "question", nq_text, 0.75*overall + 0.15, "Directly asked by chat.", ["chat"])
    elif chat.themes:
        nq_text = f"Do you want the quick version or deep dive on {chat.themes[0]}?"
        nq = _rec("q_theme", "question", nq_text, 0.55*overall + 0.10, "Theme inferred from recent chat.", ["chat"])
    else:
        nq_text = "Do you want the quick version or the deep dive?"
        nq = _rec("q_default", "question", nq_text, 0.40*overall, "Fallback prompt when chat is quiet.", ["topic"])

    # ---- Talking points as items ----
    tps: List[RecItem] = []
    tps.append(_rec(
        "tp_goal", "talking_point",
        f"Goal: “We’re building {inputs.topic} and getting it working live.”",
        0.65*overall + 0.10,
        "Anchors the stream objective for clarity.",
        ["topic","scores"]
    ))

    if res.relevant_now:
        r0 = res.relevant_now[0]
        label = (r0.get("title") or r0.get("text") or "Top resource").strip()
        tps.append(_rec(
            "tp_resource_0", "talking_point",
            f"Pull resource: “Let’s reference: {label[:70]}”",
            0.70*overall + 0.10,
            "Resource is ranked relevant to topic + chat themes.",
            ["resources","topic","chat"]
        ))

    if chat.top_questions:
        tps.append(_rec(
            "tp_answer_next", "talking_point",
            f"Answer next: “{chat.top_questions[0][:110]}”",
            0.75*overall + 0.15,
            "High relevance: direct question from viewers.",
            ["chat"]
        ))
    else:
        tps.append(_rec(
            "tp_pull_chat", "talking_point",
            "Ask: “Do you want quick version or deep dive?”",
            0.45*overall + 0.10,
            "Chat is quiet; this invites interaction.",
            ["chat","topic"]
        ))

    # Phase-specific talking points
    if state.phase == "PRELIVE":
        tps.append(_rec("tp_prelive_1","talking_point","Prelive: confirm preview + audio + scene layout is readable.",
                        0.60*overall+0.10,"Prelive checklist to avoid avoidable pain.",["obs","started"]))
        tps.append(_rec("tp_prelive_2","talking_point","Prompt: “Say hi + where you’re watching from.”",
                        0.55*overall+0.10,"Simple opener tends to increase chat flow.",["chat"]))
    elif state.phase == "LIVE":
        tps.append(_rec("tp_live_1","talking_point","Narrate: what changed in the last 60 seconds and what changes next.",
                        0.65*overall+0.10,"Keeps viewers oriented while coding.",["scores","topic"]))
        tps.append(_rec("tp_live_2","talking_point","Ask A/B: “Should we focus on UI polish or backend wiring?”",
                        0.55*overall+0.10,"Binary choice is easy for chat to answer.",["chat","topic"]))
    elif state.phase == "DEEP_DIVE":
        tps.append(_rec("tp_deep_1","talking_point","Deep dive: explain the architecture in 3 bullets, then implement 1 change.",
                        0.60*overall+0.10,"Combines explanation + visible progress.",["topic","scores"]))
        tps.append(_rec("tp_deep_2","talking_point","Checkpoint: “Pause me if you want examples.”",
                        0.50*overall+0.10,"Invites interruption and prevents rambling.",["chat"]))
    elif state.phase == "QNA":
        tps.append(_rec("tp_qna_1","talking_point","Q&A: answer 2 quick, 1 deep. Then back to build.",
                        0.60*overall+0.10,"Keeps Q&A bounded and productive.",["chat"]))
        tps.append(_rec("tp_qna_2","talking_point","Confirm: “Did that answer it?”",
                        0.65*overall+0.10,"Closes loops and boosts engagement.",["chat"]))
    elif state.phase == "WRAP":
        tps.append(_rec("tp_wrap_1","talking_point","Wrap: recap what shipped + what’s next stream.",
                        0.60*overall+0.10,"Ends with clarity and momentum.",["topic"]))
        tps.append(_rec("tp_wrap_2","talking_point","CTA: follow/subscribe + drop feature requests.",
                        0.55*overall+0.10,"Captures intent while viewers are warm.",["chat"]))

    # ---- Cues (actionable next 15–30s) ----
    cues: List[RecItem] = []
    if not inputs.started:
        cues.append(_rec("cue_start","cue","Click Start in the dashboard (or start streaming) so phase flips to LIVE.",
                         0.80*overall+0.10,"Stream not started in state.",["started"]))
    cues.append(_rec("cue_say_first","cue","Say the next sentence out loud BEFORE you code it.",
                     0.55*overall+0.10,"Narration improves retention and perceived pace.",["scores"]))
    if chat.msg_count == 0:
        cues.append(_rec("cue_wait","cue","Ask one direct question, then wait 8 seconds in silence.",
                         0.60*overall+0.10,"Quiet gap often triggers chat responses.",["chat"]))
    if res.relevant_now:
        cues.append(_rec("cue_resource","cue","Open the top resource and quote 1 line / requirement, then implement it.",
                         0.70*overall+0.10,"Grounds build in something concrete.",["resources","topic"]))

    # ---- Segments ----
    segments = plan.segments
    active_name = {
        "PRELIVE": "Set the goal",
        "LIVE": "Build next piece",
        "DEEP_DIVE": "Build next piece",
        "QNA": "Q&A",
        "WRAP": "Wrap",
        "OFFLINE": "Set the goal",
    }.get(state.phase, "Build next piece")

    for seg in segments:
        seg["active"] = (seg["name"] == active_name)

    return AIOutput(
        phase=state.phase,
        summary=summary,
        talking_points=tps[:10],
        next_question=nq,
        alerts=alert_items[:10],
        segments=segments,
        cues=cues[:10],
        resource_refs=res.relevant_now[:6],
        updated=inputs.now,
        overall_confidence=overall,
        usefulness=useful,
        coverage=cov,
        provider="logic_v1",
        debug={
            "scores": {"energy":energy,"clarity":clarity,"engagement":engagement,"pace":pace},
            "chat": {"themes":chat.themes,"momentum_2m":chat.momentum_2m,"top_q":chat.top_questions},
            "resources": {"top_terms":res.top_terms[:8], "relevant_count":len(res.relevant_now)},
            "obs_scene": inputs.obs_scene,
        }
    )
