from __future__ import annotations

"""
Algorithm reference for Update/Merge/Append/Delete in medical memories.

This file consolidates the core decision logic scattered in the codebase
into a single, self‑contained module for easy reading and reuse. It mirrors
the behavior implemented in:

- src/core/medical_memory.py        (temporal + regimen rules)
- src/core/merge_confidence.py      (confidence scoring + safety gating)
- src/storage/sqlite_store.py       (SQLite delete helper)

Content
- Medication regimen: MedicationEntry helpers + decisions
- Symptom episodes: SymptomEpisode helpers + decisions
- Confidence scoring for both (with risk/approx flags)
- Delete helper (SQLite reference)
- Inline examples in __main__
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from math import exp
from typing import List, Optional, Tuple


# ------------------------------ Data model ------------------------------------

@dataclass
class MedicationEntry:
    """Minimal representation of a medication statement.

    Captures valid time (start/end), transaction time (last_updated) and a
    few essential fields to compare regimens.
    """

    rxnorm: str
    dose: str
    frequency: str
    route: str
    start: datetime
    end: Optional[datetime] = None
    status: str = "active"
    version_id: int = 1
    last_updated: datetime = field(default_factory=datetime.utcnow)
    provenance: Optional[str] = None


# ------------------------------ Symptom data model ----------------------------

@dataclass
class SymptomEpisode:
    """Minimal representation of a symptom episode.

    Captures the concept (code/name), context (body_site, characteristics),
    severity and temporal span. Designed to support UPDATE/APPEND/MERGE of
    symptom narratives independent of medication cycles.
    """

    code: str  # e.g., "头痛" or SNOMED code/name
    start: datetime
    end: Optional[datetime] = None
    severity: Optional[str] = None         # mild | moderate | severe
    progression: Optional[str] = None      # worsening | improving | stable
    body_site: Optional[str] = None        # e.g., 左侧头部, 胸部
    characteristics: Optional[str] = None  # e.g., 跳痛, 压榨样痛, 干咳/咳痰
    status: str = "active"                 # active | resolved
    approximate_time: bool = False
    version_id: int = 1
    last_updated: datetime = field(default_factory=datetime.utcnow)
    provenance: Optional[str] = None


# ------------------------------ Regimen helpers -------------------------------

def _norm(value: str) -> str:
    return value.replace(" ", "").lower()


def same_regimen(a: MedicationEntry, b: MedicationEntry) -> bool:
    """True if two entries describe exactly the same regimen.

    Based on normalized dose/frequency/route equality in addition to rxnorm.
    """

    return (
        a.rxnorm == b.rxnorm
        and _norm(a.dose) == _norm(b.dose)
        and _norm(a.frequency) == _norm(b.frequency)
        and _norm(a.route) == _norm(b.route)
    )


def _symptom_key(e: SymptomEpisode) -> Tuple[str, Optional[str], Optional[str]]:
    """Return a normalized key used to determine if two episodes are the same context.

    We consider the same episode only when symptom concept matches and there is
    no explicit conflict on body_site/characteristics (unknown is permissive).
    """
    code = _norm(e.code)
    site = _norm(e.body_site) if e.body_site else None
    ch = _norm(e.characteristics) if e.characteristics else None
    return code, site, ch


def overlap_or_adjacent(a: MedicationEntry, b: MedicationEntry) -> bool:
    """True if intervals overlap or directly touch (UPDATE candidate).

    For ongoing intervals, end defaults to now.
    """

    end_a = a.end or datetime.utcnow()
    end_b = b.end or datetime.utcnow()
    return not (a.start > end_b or b.start > end_a)


def overlap_or_adjacent_symptom(a: SymptomEpisode, b: SymptomEpisode, gap_days: int = 14) -> bool:
    """True if two symptom time spans overlap or are within ``gap_days``.

    More tolerant than medications by default because symptom reports are often
    vague; callers can tweak ``gap_days`` per use case.
    """
    end_a = a.end or datetime.utcnow()
    end_b = b.end or datetime.utcnow()
    # allow a small separation up to gap_days
    return not (a.start > end_b + timedelta(days=gap_days) or b.start > end_a + timedelta(days=gap_days))


def is_split_episode(a: MedicationEntry, b: MedicationEntry, gap_days: int = 7) -> bool:
    """True if ``b`` continues ``a`` with only a small positive gap (MERGE).

    Requires ``a`` to have an end; treats gaps within ``gap_days`` as a
    single course that was mistakenly split.
    """

    if a.end is None:
        return False
    gap = b.start - a.end
    return timedelta(0) < gap <= timedelta(days=gap_days)


def is_split_symptom(a: SymptomEpisode, b: SymptomEpisode, gap_days: int = 14) -> bool:
    """True if ``b`` continues ``a`` with a small positive gap (MERGE candidate)."""
    if a.end is None:
        return False
    gap = b.start - a.end
    return timedelta(0) < gap <= timedelta(days=gap_days)


# ------------------------------ Pure rule decision ----------------------------

def decide_update_merge_append(current: MedicationEntry, new: MedicationEntry) -> str:
    """Return one of: "update" | "merge" | "append" by pure rules.

    Rules (FHIR‑like simplification):
    - If regimen differs -> append
    - If same regimen and intervals overlap/adjacent -> update
    - If same regimen and short positive gap (<=7 days) -> merge
    - Otherwise -> append
    """

    if not same_regimen(current, new):
        return "append"

    if overlap_or_adjacent(current, new):
        return "update"

    if is_split_episode(current, new):
        return "merge"

    return "append"


def same_symptom_context(a: SymptomEpisode, b: SymptomEpisode) -> bool:
    """True if two episodes share the same symptom concept and context.

    Unknown body_site/characteristics do not block a match; explicit conflicts do.
    """
    ac, asite, ach = _symptom_key(a)
    bc, bsite, bch = _symptom_key(b)
    if ac != bc:
        return False
    if asite and bsite and asite != bsite:
        return False
    if ach and bch and ach != bch:
        return False
    return True


def decide_update_merge_append_symptom(current: SymptomEpisode, new: SymptomEpisode) -> str:
    """Return one of: "update" | "merge" | "append" for symptom episodes.

    Rules:
    - Different concept/context -> append
    - Same context and intervals overlap/adjacent (within 14d) -> update
    - Same context and short positive gap (<=14d) -> merge
    - Otherwise -> append
    """
    if not same_symptom_context(current, new):
        return "append"
    if overlap_or_adjacent_symptom(current, new):
        return "update"
    if is_split_symptom(current, new):
        return "merge"
    return "append"


# ------------------------------ Confidence scoring ---------------------------

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

HIGH_RISK_KEYWORDS = {
    # Anticoagulants, insulin, narrow TI, teratogens, chemo
    "warfarin",
    "heparin",
    "insulin",
    "clopidogrel",
    "digoxin",
    "lithium",
    "amiodarone",
    "theophylline",
    "carbamazepine",
    "valproate",
    "valproic",
    "phenytoin",
    "methotrexate",
    "cyclophosphamide",
    "isotretinoin",
}


def _provenance_score(p: Optional[str]) -> float:
    if not p:
        return 0.6
    return PROVENANCE_WEIGHTS.get(p.strip().lower(), 0.7)


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
    ref = a.end or a.start
    gap_days = abs((b.start - ref).days)
    return 0.2 * exp(-gap_days / 30.0)


def _is_high_risk(name_or_code: Optional[str], override: Optional[bool]) -> bool:
    if override is not None:
        return override
    if not name_or_code:
        return False
    key = str(name_or_code).lower()
    return any(kw in key for kw in HIGH_RISK_KEYWORDS)


def compute_merge_confidence(
    current: MedicationEntry,
    new: MedicationEntry,
    *,
    approximate_time: Optional[bool] = None,
    high_risk: Optional[bool] = None,
) -> Tuple[str, float]:
    """Return (action, confidence: 0..1) with safety gating.

    - If regimen differs -> APPEND (low score)
    - Same regimen + overlap/adjacent -> UPDATE (high score)
    - Same regimen + short gap -> MERGE (mid‑high)
    - Otherwise -> APPEND (derived by temporal/provenance)

    Safety:
    - approximate_time=True deducts score (−0.07)
    - high_risk raises thresholds (UPDATE≥0.80, MERGE≥0.75) and adds extra
      small deduction (−0.03) when approximate_time is also True
    """

    # Base: different drug → append
    if current.rxnorm != new.rxnorm:
        return "APPEND", 0.2

    conf = 0.2

    # Regimen similarity
    if same_regimen(current, new):
        conf += 0.4
    else:
        conf -= 0.4

    # Temporal contribution
    conf += _temporal_affinity(current, new)

    # Provenance + recency
    prov = (_provenance_score(current.provenance) + _provenance_score(new.provenance)) / 2.0
    conf += (prov - 0.6) * 0.3
    conf += _recency_bonus(current)

    # Approximate time discount
    if approximate_time is True:
        conf -= 0.07

    conf = max(0.0, min(1.0, conf))

    # Candidate by temporal relation
    if same_regimen(current, new):
        if overlap_or_adjacent(current, new):
            candidate = "UPDATE"
        elif is_split_episode(current, new):
            candidate = "MERGE"
        else:
            candidate = "APPEND"
    else:
        candidate = "APPEND"

    # Safety gating thresholds
    is_risk = _is_high_risk(new.rxnorm or current.rxnorm, high_risk)
    thresh_update = 0.80 if is_risk else 0.75
    thresh_merge = 0.75 if is_risk else 0.70

    if is_risk and approximate_time is True:
        conf -= 0.03
        conf = max(0.0, min(1.0, conf))

    # Apply thresholds
    if candidate == "UPDATE":
        if conf >= thresh_update:
            return "UPDATE", conf
        return "APPEND", min(conf, 0.6)
    if candidate == "MERGE":
        if conf >= thresh_merge:
            return "MERGE", conf
        return "APPEND", min(conf, 0.6)
    return "APPEND", min(conf, 0.6)


# ------------------------------ Symptom scoring -------------------------------

HIGH_RISK_SYMPTOMS = {
    # chest pain, dyspnea, neurological deficits, GI bleed, severe allergy
    "胸痛", "呼吸困难", "气促", "咯血", "黑便", "神志不清", "肢体无力", "抽搐", "严重过敏", "过敏性休克",
}


def _severity_trend_bonus(prev: Optional[str], now: Optional[str]) -> float:
    order = {"mild": 1, "轻度": 1, "moderate": 2, "中度": 2, "severe": 3, "重度": 3}
    if not prev or not now:
        return 0.0
    a, b = order.get(prev.lower(), 0), order.get(now.lower(), 0)
    if a == b:
        return 0.03
    # coherent progression mild→moderate/severe or reverse
    if abs(b - a) == 1:
        return 0.02
    return -0.02


def compute_symptom_merge_confidence(
    current: SymptomEpisode,
    new: SymptomEpisode,
    *,
    approximate_time: Optional[bool] = None,
    high_risk: Optional[bool] = None,
    gap_days: int = 14,
) -> Tuple[str, float]:
    """Return (action, confidence) for symptom episodes with safety gating.

    Heuristics mirror medication scoring but tuned for symptoms:
    - Different concept/context: APPEND with low-moderate confidence
    - Same context + overlap/adjacent (<=gap): UPDATE with higher confidence
    - Same context + short positive gap: MERGE with mid-high confidence
    - Approximate time deducts score; high-risk symptoms raise thresholds
    """

    if not same_symptom_context(current, new):
        return "APPEND", 0.35

    conf = 0.35
    conf += 0.25 if overlap_or_adjacent_symptom(current, new, gap_days) else 0.10
    if is_split_symptom(current, new, gap_days):
        conf += 0.10

    # Provenance and recency reuse med helpers
    prov = (_provenance_score(current.provenance) + _provenance_score(new.provenance)) / 2.0
    conf += (prov - 0.6) * 0.25
    conf += _recency_bonus(current)

    # Severity trend small influence
    conf += _severity_trend_bonus(current.severity, new.severity)

    # Approximate time discount
    approx = approximate_time if approximate_time is not None else (current.approximate_time or new.approximate_time)
    if approx:
        conf -= 0.05

    conf = max(0.0, min(1.0, conf))

    # Candidate action
    if overlap_or_adjacent_symptom(current, new, gap_days):
        candidate = "UPDATE"
    elif is_split_symptom(current, new, gap_days):
        candidate = "MERGE"
    else:
        candidate = "APPEND"

    # Safety thresholds
    name = (new.code or current.code or "").lower()
    is_risk = high_risk if high_risk is not None else any(k in name for k in HIGH_RISK_SYMPTOMS)
    thresh_update = 0.78 if is_risk else 0.72
    thresh_merge = 0.74 if is_risk else 0.68
    if is_risk and approx:
        conf -= 0.03
        conf = max(0.0, min(1.0, conf))

    if candidate == "UPDATE":
        if conf >= thresh_update:
            return "UPDATE", conf
        return "APPEND", min(conf, 0.55)
    if candidate == "MERGE":
        if conf >= thresh_merge:
            return "MERGE", conf
        return "APPEND", min(conf, 0.55)
    return "APPEND", min(conf, 0.55)


# ------------------------------ Delete helper (SQLite) ------------------------

def delete_by_pattern_sqlite(db_path: str, user_id: str, pattern: str) -> int:
    """Delete rows in SQLite memories table by LIKE pattern.

    This mirrors the behavior used by the demo API and is provided here for
    reference. Returns number of deleted rows.
    """

    import sqlite3

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM memories WHERE user_id = ? AND content LIKE ?",
        (user_id, pattern),
    )
    deleted = cursor.rowcount or 0
    conn.commit()
    conn.close()
    return deleted


# ------------------------------ Examples --------------------------------------

if __name__ == "__main__":
    # Minimal, in-memory examples (no DB), showing pure decisions and scoring.
    cur = MedicationEntry(
        rxnorm="阿莫西林",
        dose="500 毫克",
        frequency="每日三次",
        route="口服",
        start=datetime.fromisoformat("2025-08-01T00:00:00"),
        end=datetime.fromisoformat("2025-08-10T00:00:00"),
        provenance="医生",
    )

    new_merge = MedicationEntry(
        rxnorm="阿莫西林",
        dose="500 毫克",
        frequency="每日三次",
        route="口服",
        start=datetime.fromisoformat("2025-08-12T00:00:00"),
        end=datetime.fromisoformat("2025-08-20T00:00:00"),
        provenance="医生",
    )

    new_update = MedicationEntry(
        rxnorm="阿莫西林",
        dose="500 毫克",
        frequency="每日三次",
        route="口服",
        start=datetime.fromisoformat("2025-08-09T00:00:00"),
        end=None,
        provenance="医生",
    )

    new_append = MedicationEntry(
        rxnorm="阿司匹林",
        dose="81 毫克",
        frequency="每日一次",
        route="口服",
        start=datetime.fromisoformat("2025-08-28T00:00:00"),
        end=None,
        provenance="医生",
    )

    print("Pure rules →")
    print("  decide(cur, new_update) =", decide_update_merge_append(cur, new_update))
    print("  decide(cur, new_merge)  =", decide_update_merge_append(cur, new_merge))
    print("  decide(cur, new_append) =", decide_update_merge_append(cur, new_append))

    print("\nScoring + thresholds →")
    for label, entry in [("UPDATE", new_update), ("MERGE", new_merge), ("APPEND", new_append)]:
        action, conf = compute_merge_confidence(cur, entry, approximate_time=False, high_risk=False)
        print(f"  candidate={label:6s} → action={action}, confidence={conf:.2f}")

    # --- Symptom examples ---
    from datetime import timedelta as _td
    s1 = SymptomEpisode(
        code="头痛",
        start=datetime.utcnow() - _td(days=3),
        end=None,
        severity="轻度",
        body_site="头部",
        provenance="自述",
    )
    s_update = SymptomEpisode(
        code="头痛",
        start=datetime.utcnow() - _td(days=1),
        end=None,
        severity="中度",
        body_site="头部",
        provenance="自述",
    )
    s_merge = SymptomEpisode(
        code="头痛",
        start=(s1.start + _td(days=1)),
        end=s1.start + _td(days=2),
        severity="轻度",
        body_site="头部",
        provenance="医生",
    )
    s_append = SymptomEpisode(
        code="胸痛",
        start=datetime.utcnow(),
        severity="中度",
        body_site="胸部",
        provenance="自述",
    )

    print("\nSymptom rules →")
    print("  decide_symptom(s1, s_update) =", decide_update_merge_append_symptom(s1, s_update))
    print("  decide_symptom(s1, s_merge)  =", decide_update_merge_append_symptom(s1, s_merge))
    print("  decide_symptom(s1, s_append) =", decide_update_merge_append_symptom(s1, s_append))

    print("\nSymptom scoring + thresholds →")
    for label, entry in [("UPDATE", s_update), ("MERGE", s_merge), ("APPEND", s_append)]:
        action, conf = compute_symptom_merge_confidence(s1, entry, approximate_time=False)
        print(f"  candidate={label:6s} → action={action}, confidence={conf:.2f}")
