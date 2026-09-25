"""Time signals: local time and whether it falls inside the configured quiet hours."""

from __future__ import annotations

from datetime import datetime, time

from pydantic import BaseModel

from synkage.config import QuietHours


class TimeSignals(BaseModel):
    now: datetime
    quiet_hours: bool


def _hhmm(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


def in_window(t: time, start: time, end: time) -> bool:
    """Inclusive start, exclusive end; windows may wrap midnight (23:00-07:00)."""
    return start <= t < end if start <= end else t >= start or t < end


def time_signals(quiet: QuietHours, now: datetime | None = None) -> TimeSignals:
    now = now or datetime.now().astimezone()
    return TimeSignals(now=now, quiet_hours=in_window(now.time(), _hhmm(quiet.start), _hhmm(quiet.end)))
