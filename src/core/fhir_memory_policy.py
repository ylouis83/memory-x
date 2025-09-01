"""Rules for deciding memory update actions (append/update/merge).

This module implements simplified logic inspired by FHIR guidelines for
handling long‑term medication statements.  It inspects existing records and a
newly extracted record to decide whether the information represents a new
therapy, a correction to an ongoing therapy, or two segments that should be
merged into one course.

The rules are intentionally lightweight – they do not attempt full semantic
normalisation of doses or routes – but they capture the core temporal
reasoning required for agents that model medical memories.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Optional


@dataclass
class EffectivePeriod:
    start: date
    end: Optional[date] = None


@dataclass
class MedicationRecord:
    """Minimal representation of a medication statement."""

    rxnorm: str
    dose: str
    frequency: str
    route: str
    period: EffectivePeriod


def _normalise(text: str) -> str:
    """Very small normaliser used for comparisons.

    Real systems would map units and frequency keywords; for unit tests we
    lower‑case and strip whitespace so that ``"5mg"`` equals ``"5 mg"``.
    """

    return "".join(text.lower().split())


def same_regimen(a: MedicationRecord, b: MedicationRecord) -> bool:
    """Return True if the two records describe the same regimen."""

    return (
        a.rxnorm == b.rxnorm
        and _normalise(a.dose) == _normalise(b.dose)
        and _normalise(a.frequency) == _normalise(b.frequency)
        and _normalise(a.route) == _normalise(b.route)
    )


def overlap_or_adjacent(a: EffectivePeriod, b: EffectivePeriod, gap_days: int = 0) -> bool:
    """Return True if periods overlap or touch."""

    end_a = a.end or date.today()
    end_b = b.end or date.today()
    return not (a.start > end_b + timedelta(days=gap_days) or b.start > end_a + timedelta(days=gap_days))


def decide_action(existing: Iterable[MedicationRecord], new: MedicationRecord) -> str:
    """Decide whether to APPEND, UPDATE or MERGE based on existing records.

    The function implements the decision tree described in the repository's
    documentation.  ``existing`` should contain candidate records for the same
    patient and medication within a recent time window.
    """

    candidates = [r for r in existing if r.rxnorm == new.rxnorm]
    if not candidates:
        return "APPEND"

    current = candidates[0]  # placeholder for more advanced ranking
    if not same_regimen(current, new):
        return "APPEND"

    if overlap_or_adjacent(current.period, new.period):
        return "UPDATE"

    # Treat short gaps as splits of the same therapy
    if current.period.end and new.period.start <= current.period.end + timedelta(days=7):
        return "MERGE"

    return "APPEND"
