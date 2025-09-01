from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional, Tuple, Dict, Any
import re
from enum import IntEnum


class Precision(IntEnum):
    exact_date = 5
    day_range = 4
    week_range = 3
    month_range = 2
    vague_recent = 1
    vague_nearterm = 0


@dataclass
class ValidationResult:
    is_valid: bool
    reason: str
    confidence: float
    time_range: Optional[Tuple[date, Optional[date]]] = None
    approximate_time: bool = False
    precision: Optional[Precision] = None
    phrase: Optional[str] = None


VAGUE_TIME_KEYWORDS = {
    "最近": (7, 14),   # within last 1–2 weeks; choose 14d for conservative start
    "近期": (14, 30),  # within last 2–4 weeks; choose 30d for conservative start
}


OBVIOUSLY_FAKE_MARKERS = [
    "乱说", "编的", "骗你的", "假的", "不是真的", "瞎说", "开玩笑", "胡说", "扯淡",
]


CONTRADICTION_PATTERNS = [
    ("男", "怀孕"),  # male + pregnant
    ("昨天得了很多年", None),  # impossible duration phrasing
]


CN_NUM = {
    "零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "俩": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
}


def _cn_text_to_int(text: str) -> Optional[int]:
    text = text.strip()
    if text.isdigit():
        return int(text)
    if text in ("几", "些"):
        return 3  # heuristic
    if text == "半":
        return 1  # handled via unit scaling later for months/weeks as 0.5; fallback 1 day if unknown
    # handle up to 99 in simple Chinese numerals
    # e.g., 十=10, 十一=11, 二十=20, 二十一=21
    if len(text) == 1:
        return CN_NUM.get(text)
    # patterns like 十X, X十, X十Y
    if text.startswith("十"):
        ones = CN_NUM.get(text[1:]) if len(text) > 1 else 0
        return 10 + (ones or 0)
    if text.endswith("十"):
        tens = CN_NUM.get(text[:-1])
        return (tens or 0) * 10
    # X十Y
    if "十" in text:
        parts = text.split("十")
        tens = CN_NUM.get(parts[0], 0)
        ones = CN_NUM.get(parts[1], 0) if len(parts) > 1 else 0
        return tens * 10 + ones
    return None


@dataclass
class TimeParseResult:
    start: date
    end: Optional[date]
    precision: Precision
    approximate: bool
    confidence: float
    phrase: str


def parse_time_phrase(text: str) -> Optional[TimeParseResult]:
    """Parse Chinese vague/relative time phrases.

    Supported patterns:
    - 最近/近/过去 + 数字/中文数字/几/些 + 天/周/星期/月
    - 最近几天/这几天/近些天/近一个月/最近一个月
    - 单独的 最近 / 近期
    """
    today = date.today()
    t = text.strip()

    # 1) 数字 + 单位
    pattern = re.compile(r"(最近|近|过去|这)(?P<num>\d+|[一二两俩三四五六七八九十几些半])(?P<unit>天|日|周|星期|月)")
    m = pattern.search(t)
    if m:
        raw_num = m.group("num")
        unit = m.group("unit")
        n = _cn_text_to_int(raw_num)
        # handle half month/week explicitly if '半'
        approx = True
        if raw_num == "半":
            if unit in ("月",):
                days = 15
            elif unit in ("周", "星期"):
                days = 3
            else:
                days = 1
        else:
            if n is None:
                n = 3  # fallback
            if unit in ("天", "日"):
                days = n
            elif unit in ("周", "星期"):
                days = n * 7
            else:
                days = n * 30
        start = today - timedelta(days=days)
        precision = Precision.week_range if unit in ("周", "星期") else (
            Precision.day_range if unit in ("天", "日") else Precision.month_range
        )
        conf = 0.85 if n is not None else 0.7
        return TimeParseResult(start=start, end=None, precision=precision, approximate=approx, confidence=conf, phrase=m.group(0))

    # 2) 几/些 + 单位
    pattern2 = re.compile(r"(最近|这|近)(几|些)(?P<unit>天|日|周|星期|月)")
    m2 = pattern2.search(t)
    if m2:
        unit = m2.group("unit")
        if unit in ("天", "日"):
            days = 5
            precision = Precision.day_range
        elif unit in ("周", "星期"):
            days = 14
            precision = Precision.week_range
        else:
            days = 30
            precision = Precision.month_range
        start = today - timedelta(days=days)
        return TimeParseResult(start=start, end=None, precision=precision, approximate=True, confidence=0.75, phrase=m2.group(0))

    # 3) 单词 最近 / 近期
    for kw, (_min_d, max_d) in VAGUE_TIME_KEYWORDS.items():
        if kw in t:
            start = today - timedelta(days=max_d)
            precision = Precision.vague_recent if kw == "最近" else Precision.vague_nearterm
            return TimeParseResult(start=start, end=None, precision=precision, approximate=True, confidence=0.65, phrase=kw)

    return None


def assess_statement(text: str) -> ValidationResult:
    t = text.strip()
    # 1) Explicitly fake markers
    for m in OBVIOUSLY_FAKE_MARKERS:
        if m in t:
            parsed = parse_time_phrase(t)
            return ValidationResult(
                is_valid=False,
                reason=f"Detected disclaimer marker: {m}",
                confidence=0.95,
                time_range=(parsed.start, parsed.end) if parsed else None,
                approximate_time=parsed.approximate if parsed else False,
                precision=parsed.precision if parsed else None,
                phrase=parsed.phrase if parsed else None,
            )

    # 2) Quick contradiction checks (very lightweight heuristics)
    for a, b in CONTRADICTION_PATTERNS:
        if a in t and (b is None or b in t):
            parsed = parse_time_phrase(t)
            return ValidationResult(
                is_valid=False,
                reason=f"Contradictory medical claim around: {a}{'+'+b if b else ''}",
                confidence=0.8,
                time_range=(parsed.start, parsed.end) if parsed else None,
                approximate_time=parsed.approximate if parsed else False,
                precision=parsed.precision if parsed else None,
                phrase=parsed.phrase if parsed else None,
            )

    # 3) Parse time phrase if present
    parsed = parse_time_phrase(t)
    if parsed:
        return ValidationResult(
            is_valid=True,
            reason="Time phrase parsed",
            confidence=parsed.confidence,
            time_range=(parsed.start, parsed.end),
            approximate_time=parsed.approximate,
            precision=parsed.precision,
            phrase=parsed.phrase,
        )

    # Default accept (no clear red flags found)
    return ValidationResult(
        is_valid=True,
        reason="No red flags",
        confidence=0.6,
        time_range=None,
        approximate_time=False,
        precision=None,
        phrase=None,
    )


@dataclass
class TimeWindow:
    start: date
    end: Optional[date]
    precision: Precision
    approximate: bool = True


def update_time_window(prev: TimeWindow, new: TimeWindow, gap_days: int = 7) -> Tuple[str, TimeWindow]:
    """Update previous window using new info.

    Rules:
    - Never downgrade precision. If new.precision < prev.precision and new.start <= prev.start: keep prev ("keep").
    - If new is more precise and overlaps/contained: refine to new.start ("refine").
    - If new widens earlier start (more vague but earlier) and overlaps/adjacent: widen start to min ("widen").
    - If windows are disjoint with gap > gap_days: append (caller should create new record).
    """

    def overlap_or_adjacent(a: TimeWindow, b: TimeWindow) -> bool:
        end_a = a.end or date.today()
        end_b = b.end or date.today()
        return not (a.start > end_b + timedelta(days=gap_days) or b.start > end_a + timedelta(days=gap_days))

    if not overlap_or_adjacent(prev, new):
        return "append", prev

    # New is more precise → refine
    if new.precision > prev.precision:
        refined = TimeWindow(
            start=max(prev.start, new.start),  # contained start preferred
            end=new.end if new.end else prev.end,
            precision=new.precision,
            approximate=new.approximate,
        )
        return "refine", refined

    # New is less precise but earlier → widen (do not downgrade precision)
    if new.precision < prev.precision and new.start < prev.start:
        widened = TimeWindow(
            start=new.start,
            end=prev.end,
            precision=prev.precision,
            approximate=prev.approximate,
        )
        return "widen", widened

    # Same precision → unify conservatively
    if new.precision == prev.precision:
        merged = TimeWindow(
            start=min(prev.start, new.start),
            end=prev.end if prev.end is not None else new.end,
            precision=prev.precision,
            approximate=prev.approximate and new.approximate,
        )
        return "merge", merged

    # Default keep
    return "keep", prev
