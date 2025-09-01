import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.medical_memory import MedicationEntry
from src.core.merge_confidence import compute_merge_confidence, decide_with_confidence


def entry(rx="123", start_days=-14, end_days=None, dose="5 mg", freq="qd", route="po", prov="doctor"):
    start = datetime.utcnow() + timedelta(days=start_days)
    end = (datetime.utcnow() + timedelta(days=end_days)) if end_days is not None else None
    return MedicationEntry(
        rxnorm=rx,
        dose=dose,
        frequency=freq,
        route=route,
        start=start,
        end=end,
        provenance=prov,
    )


def test_update_high_confidence_for_overlap_same_regimen():
    cur = entry(start_days=-10, end_days=None)
    new = entry(start_days=-5, end_days=None)
    action, conf = compute_merge_confidence(cur, new)
    assert action == "UPDATE"
    assert conf >= 0.75


def test_merge_medium_confidence_for_short_gap():
    cur = entry(start_days=-20, end_days=-10)
    new = entry(start_days=-8, end_days=-3)
    action, conf = compute_merge_confidence(cur, new)
    assert action == "MERGE"
    assert conf >= 0.7


def test_append_low_confidence_for_different_regimen():
    cur = entry(dose="5 mg")
    new = entry(dose="10 mg")
    action, conf = compute_merge_confidence(cur, new)
    assert action == "APPEND"
    assert conf <= 0.5


def test_decide_with_confidence_picks_best_candidate():
    history = [
        entry(start_days=-120, end_days=-90),  # old
        entry(start_days=-20, end_days=-10),   # recent
    ]
    new = entry(start_days=-8, end_days=None)
    decision = decide_with_confidence(history, new)
    assert decision.action in ("UPDATE", "MERGE")
    assert 0.6 <= decision.confidence <= 1.0
    assert decision.candidate is not None

