from __future__ import annotations
from typing import Any, Dict, List
from ai.models import AIInputs, ResourceSignals, ChatSignals
from ai.index.resource_index import build_resource_terms, rank_resources

def analyze_resources(inputs: AIInputs, chat: ChatSignals) -> ResourceSignals:
    resources: List[Dict[str, Any]] = [r for r in (inputs.resources or []) if isinstance(r, dict)]
    top_terms, _inv = build_resource_terms(resources)

    query_terms: List[str] = []
    query_terms.extend((inputs.topic or "").split()[:10])
    query_terms.extend(chat.themes[:6])
    for q in chat.top_questions[:3]:
        query_terms.extend(q.split()[:8])

    relevant = rank_resources(resources, query_terms, top_k=6)
    return ResourceSignals(
        count=len(resources),
        top_terms=top_terms,
        relevant_now=relevant
    )
