import os
import sys
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.fhir_memory_policy import (
    EffectivePeriod,
    MedicationRecord,
    decide_action,
)


def build(rx, start, end=None):
    return MedicationRecord(
        rxnorm=rx,
        dose="5 mg",
        frequency="once daily",
        route="oral",
        period=EffectivePeriod(date.fromisoformat(start), date.fromisoformat(end) if end else None),
    )


def test_append_for_new_drug():
    history = [build("123", "2024-01-01", "2024-02-01")]
    new = build("999", "2024-03-01")
    assert decide_action(history, new) == "APPEND"


def test_update_for_same_ongoing_regimen():
    history = [build("123", "2024-01-01")]
    new = build("123", "2024-02-01")
    assert decide_action(history, new) == "UPDATE"


def test_merge_for_split_episode():
    history = [build("123", "2024-01-01", "2024-01-10")]
    new = build("123", "2024-01-12", "2024-01-20")
    assert decide_action(history, new) == "MERGE"
