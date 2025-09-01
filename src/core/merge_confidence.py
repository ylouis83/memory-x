from __future__ import annotations

"""Merge confidence scoring for medical memories.

Inspired by agent memory designs, this module computes a confidence score
for choosing between APPEND / UPDATE / MERGE. It reuses the semantics and
helpers defined in ``medical_memory`` to reason about regimen equality and
temporal relations.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import exp
from typing import Iterable, Optional, Tuple

from .medical_memory import MedicationEntry, same_regimen, overlap_or_adjacent, is_split_episode


@dataclass
class Decision:
    action: str  # one of: APPEND, UPDATE, MERGE
    confidence: float  # 0..1
    candidate: Optional[MedicationEntry] = None


PROVENANCE_WEIGHTS = {
    # stronger sources
    "ehr": 1.0,
    "hospital": 0.95,
    "doctor": 0.95,
    "clinic": 0.9,
    # medium reliability
    "insurance": 0.85,
    "pharmacy": 0.85,
    # self report / chat
    "self-report": 0.65,
    "self": 0.65,
    "chat": 0.6,
}


def _provenance_score(p: Optional[str]) -> float:
    if not p:
        return 0.6
    key = p.strip().lower()
    return PROVENANCE_WEIGHTS.get(key, 0.7)


def _recency_bonus(entry: MedicationEntry, days: int = 90) -> float:
    try:
        delta = datetime.utcnow() - (entry.last_updated or datetime.utcnow())
    except Exception:
        return 0.0
    return 0.05 if delta <= timedelta(days=days) else 0.0


def _temporal_affinity(a: MedicationEntry, b: MedicationEntry) -> float:
    if overlap_or_adjacent(a, b):
        return 0.3
    if is_split_episode(a, b):
        return 0.2
    # distance-based small affinity (decays with gap)
    ref = a.end or a.start
    gap_days = abs((b.start - ref).days)
    return 0.2 * exp(-gap_days / 30.0)


def compute_merge_confidence(current: MedicationEntry, new: MedicationEntry) -> Tuple[str, float]:
    """Return (proposed_action, confidence in 0..1) for merging ``new`` with ``current``.

    Heuristics:
    - Different drug (rxnorm): APPEND with low confidence.
    - Same regimen + overlap/adjacent → UPDATE with high confidence.
    - Same regimen + short gap → MERGE with medium-high confidence.
    - Otherwise → APPEND with score derived from temporal affinity and provenance.
    """

    if current.rxnorm != new.rxnorm:
        return "APPEND", 0.2

    base = 0.2
    conf = base

    # Regimen similarity
    if same_regimen(current, new):
        conf += 0.4
    else:
        conf -= 0.4

    # Temporal
    conf += _temporal_affinity(current, new)

    # Provenance: average of sources
    prov = (_provenance_score(current.provenance) + _provenance_score(new.provenance)) / 2.0
    conf += (prov - 0.6) * 0.3  # scale contribution

    # Recency bonus
    conf += _recency_bonus(current)

    # Clamp
    conf = max(0.0, min(1.0, conf))

    # Choose action according to temporal relation
    if same_regimen(current, new):
        if overlap_or_adjacent(current, new):
            action = "UPDATE"
            conf = max(conf, 0.75)
        elif is_split_episode(current, new):
            action = "MERGE"
            conf = max(conf, 0.7)
        else:
            action = "APPEND"
            conf = min(conf, 0.6)
    else:
        action = "APPEND"
        conf = min(conf, 0.5)

    return action, conf


def decide_with_confidence(existing: Iterable[MedicationEntry], new: MedicationEntry) -> Decision:
    candidates = [e for e in existing if e.rxnorm == new.rxnorm]
    if not candidates:
        return Decision(action="APPEND", confidence=0.8, candidate=None)
    # pick best by confidence
    best_decision: Optional[Decision] = None
    for c in candidates:
        action, score = compute_merge_confidence(c, new)
        d = Decision(action=action, confidence=score, candidate=c)
        if not best_decision or d.confidence > best_decision.confidence:
            best_decision = d
    return best_decision or Decision(action="APPEND", confidence=0.5, candidate=None)

