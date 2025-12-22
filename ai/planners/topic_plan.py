from __future__ import annotations
from ai.models import AIInputs, TopicPlan

def build_topic_plan(inputs: AIInputs) -> TopicPlan:
    topic = (inputs.topic or "Untitled Stream").strip()

    # v0.2: deterministic segments. Later: dynamic (resource-based outlines).
    segments = [
        {"name":"Set the goal", "goal":"Say the goal in one sentence + what ‘done’ looks like.", "done": False},
        {"name":"Show current state", "goal":"What’s working now? What’s broken? (1 minute)", "done": False},
        {"name":"Build next piece", "goal":"Implement one concrete step on-screen.", "done": False},
        {"name":"Test live", "goal":"Prove it works (demo) + narrate.", "done": False},
        {"name":"Q&A", "goal":"Answer top chat questions, pick 1 deep dive.", "done": False},
        {"name":"Wrap", "goal":"Recap + next stream plan + CTA.", "done": False},
    ]

    return TopicPlan(
        headline=topic,
        segments=segments,
        default_cta="Ask a question or vote A/B in chat."
    )
