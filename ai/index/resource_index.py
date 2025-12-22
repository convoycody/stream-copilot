from __future__ import annotations
import re
from collections import Counter
from typing import Any, Dict, List, Tuple

STOP = {
    "the","and","that","this","with","you","your","for","are","was","but","not","have","just","like",
    "from","what","when","where","how","its","it's","im","i'm","we","our","they","them","then","than",
    "about","into","out","over","under","too","very","can","cant","don't","does","did","will","would",
    "stream","live","today","tonight"
}

def _tokens(s: str) -> List[str]:
    w = re.findall(r"[a-z0-9']{3,}", (s or "").lower())
    return [x for x in w if x not in STOP and not x.isdigit()]

def build_resource_terms(resources: List[Dict[str, Any]]) -> Tuple[List[str], Dict[str, List[int]]]:
    # returns top_terms and inverted index term->resource indices
    inv: Dict[str, List[int]] = {}
    all_words: List[str] = []
    for i, r in enumerate(resources or []):
        if not isinstance(r, dict):
            continue
        text = " ".join([
            str(r.get("title") or ""),
            str(r.get("text") or ""),
            str(r.get("url") or ""),
            " ".join([str(x) for x in (r.get("tags") or [])]),
        ])
        toks = _tokens(text)
        all_words.extend(toks)
        for t in set(toks):
            inv.setdefault(t, []).append(i)

    top_terms = [w for w, _ in Counter(all_words).most_common(12)]
    return top_terms, inv

def rank_resources(resources: List[Dict[str, Any]], query_terms: List[str], top_k: int = 6) -> List[Dict[str, Any]]:
    # simple scoring: count of query terms appearing in resource fields
    qt = set([t.lower() for t in query_terms if t])
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for r in (resources or []):
        if not isinstance(r, dict):
            continue
        blob = " ".join([str(r.get("title") or ""), str(r.get("text") or ""), str(r.get("url") or "")]).lower()
        score = 0.0
        for t in qt:
            if t and t in blob:
                score += 1.0
        # slight boost if tagged
        tags = [str(x).lower() for x in (r.get("tags") or [])]
        score += 0.25 * sum(1 for t in qt if t in tags)
        if score > 0:
            scored.append((score, r))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:top_k]]
