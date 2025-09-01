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
