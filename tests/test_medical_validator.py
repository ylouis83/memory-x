import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import timedelta, date
from src.modules.medical_validator import (
    assess_statement,
    parse_time_phrase,
    TimeWindow,
    update_time_window,
    Precision,
)


def test_reject_obvious_fabrication():
    text = "其实我是在乱说病情，刚才都是编的，骗你的。"
    result = assess_statement(text)
    assert result.is_valid is False
    assert result.confidence >= 0.8
    assert "marker" in result.reason or "编的" in result.reason


def test_vague_time_recent_normalisation():
    text = "我最近一直头痛，晚上更严重。"
    result = assess_statement(text)
    assert result.is_valid is True
    assert result.approximate_time is True
    assert result.time_range is not None
    start, end = result.time_range
    assert end is None  # ongoing
    # start should fall within last ~30 days (conservative bound)
    assert start <= date.today() and start >= date.today() - timedelta(days=30)


def test_parse_recent_one_week():
    text = "最近1周头疼"
    r = parse_time_phrase(text)
    assert r is not None
    assert r.precision == Precision.week_range
    assert r.start >= date.today() - timedelta(days=8)
    assert r.start <= date.today() - timedelta(days=6)


def test_update_keep_when_new_is_more_vague():
    today = date.today()
    prev = TimeWindow(start=today - timedelta(days=7), end=None, precision=Precision.week_range, approximate=True)
    new = TimeWindow(start=today - timedelta(days=30), end=None, precision=Precision.vague_nearterm, approximate=True)
    action, updated = update_time_window(prev, new)
    # Should not downgrade precision or push start back just because of vaguer statement
    assert action in ("keep", "widen", "merge")
    assert updated.start <= prev.start  # may keep or widen conservatively
    # Core expectation for your scenario: don't worsen precision
    assert updated.precision >= prev.precision


def test_update_refine_when_new_is_more_precise():
    today = date.today()
    prev = TimeWindow(start=today - timedelta(days=30), end=None, precision=Precision.vague_nearterm, approximate=True)
    new = TimeWindow(start=today - timedelta(days=7), end=None, precision=Precision.week_range, approximate=True)
    action, updated = update_time_window(prev, new)
    assert action in ("refine", "merge")
    assert updated.start >= today - timedelta(days=8)
    assert updated.precision >= new.precision
