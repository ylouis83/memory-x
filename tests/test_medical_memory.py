from datetime import datetime, timedelta

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.medical_memory import (
    MedicationEntry,
    upsert_medication_entry,
)


def test_append_update_merge():
    now = datetime.utcnow()
    entries = []
    first = MedicationEntry(
        rxnorm="12345",
        dose="5 mg",
        frequency="qd",
        route="oral",
        start=now - timedelta(days=30),
    )
    action = upsert_medication_entry(entries, first)
    assert action == "append"
    assert len(entries) == 1

    # Update within the same regimen
    follow_up = MedicationEntry(
        rxnorm="12345",
        dose="5 mg",
        frequency="qd",
        route="oral",
        start=now - timedelta(days=21),
        end=now - timedelta(days=11),
    )
    action = upsert_medication_entry(entries, follow_up)
    assert action == "update"
    assert len(entries) == 1
    assert entries[0].version_id == 2
    assert entries[0].end == follow_up.end
    assert entries[0].status == "completed"

    # Merge split episode with short gap
    new_course = MedicationEntry(
        rxnorm="12345",
        dose="5 mg",
        frequency="qd",
        route="oral",
        start=follow_up.end + timedelta(days=1),
    )
    action = upsert_medication_entry(entries, new_course)
    assert action == "merge"
    assert len(entries) == 1
    assert entries[0].start == first.start
    assert entries[0].end is None
    assert entries[0].status == "active"
    assert entries[0].version_id == 3


def test_merge_produces_single_active_entry():
    """Merging two adjacent segments results in one active course."""
    now = datetime.utcnow()

    # First segment already stored as completed therapy
    first = MedicationEntry(
        rxnorm="777",
        dose="10 mg",
        frequency="qd",
        route="oral",
        start=now - timedelta(days=20),
        end=now - timedelta(days=10),
        status="completed",
    )
    entries = [first]

    # Follow-up continuation within allowed merge gap
    second = MedicationEntry(
        rxnorm="777",
        dose="10 mg",
        frequency="qd",
        route="oral",
        start=first.end + timedelta(days=1),
        provenance="clinic",
    )

    action = upsert_medication_entry(entries, second)
    assert action == "merge"
    assert len(entries) == 1

    merged = entries[0]
    assert merged.start == first.start
    assert merged.end is None
    assert merged.status == "active"
    assert merged.version_id == first.version_id + 1
    # provenance of the newest information should be kept
    assert merged.provenance == "clinic"

