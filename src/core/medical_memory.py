from __future__ import annotations

"""Utilities for medication memory management with FHIR-like semantics."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional


@dataclass
class MedicationEntry:
    """Minimal representation of a medication statement.

    It captures both the valid time (``start``/``end``) and transaction time
    (``last_updated``) to allow bi-temporal queries.  ``version_id`` is incremented
    every time the record is updated or merged.
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


def _norm(value: str) -> str:
    return value.replace(" ", "").lower()


def same_regimen(a: MedicationEntry, b: MedicationEntry) -> bool:
    """Return ``True`` if two entries describe the same medication regimen."""

    return (
        a.rxnorm == b.rxnorm
        and _norm(a.dose) == _norm(b.dose)
        and _norm(a.frequency) == _norm(b.frequency)
        and _norm(a.route) == _norm(b.route)
    )


def overlap_or_adjacent(a: MedicationEntry, b: MedicationEntry) -> bool:
    """Return True if two intervals overlap or directly touch.

    This corresponds to ``UPDATE`` semantics where the incoming information
    belongs to the same medication course without any gap.
    """

    end_a = a.end or datetime.utcnow()
    end_b = b.end or datetime.utcnow()
    return not (a.start > end_b or b.start > end_a)


def is_split_episode(a: MedicationEntry, b: MedicationEntry, gap_days: int = 7) -> bool:
    """Return ``True`` if ``b`` continues ``a`` with only a small gap."""

    if a.end is None:
        return False
    gap = b.start - a.end
    return timedelta(0) < gap <= timedelta(days=gap_days)


def upsert_medication_entry(entries: List[MedicationEntry], new: MedicationEntry, months: int = 12) -> str:
    """Insert ``new`` into ``entries`` following Append/Update/Merge rules.

    The function returns the action performed: ``"append"``, ``"update`` or
    ``"merge"``.
    """

    cutoff = datetime.utcnow() - timedelta(days=30 * months)
    candidates = [e for e in entries if e.rxnorm == new.rxnorm and e.start >= cutoff]
    if not candidates:
        entries.append(new)
        return "append"

    best = max(candidates, key=lambda e: e.start)
    if same_regimen(best, new):
        if overlap_or_adjacent(best, new):
            # Update: patch fields and bump version.
            best.dose = new.dose or best.dose
            best.frequency = new.frequency or best.frequency
            best.route = new.route or best.route
            if new.start and new.start < best.start:
                best.start = new.start
            if new.end:
                best.end = new.end
                best.status = "completed"
            best.version_id += 1
            best.last_updated = datetime.utcnow()
            best.provenance = new.provenance or best.provenance
            return "update"
        if is_split_episode(best, new):
            merged = MedicationEntry(
                rxnorm=best.rxnorm,
                dose=best.dose,
                frequency=best.frequency,
                route=best.route,
                start=min(best.start, new.start),
                end=new.end,
                status="active" if new.end is None else "completed",
                version_id=best.version_id + 1,
                provenance=new.provenance or best.provenance,
            )
            entries.remove(best)
            entries.append(merged)
            return "merge"

    entries.append(new)
    return "append"
