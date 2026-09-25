"""Collects one snapshot of every signal the situation detector reads.
Context only reports; the brain's situation detector decides.
"""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, Field

from synkage.config import SituationConfig
from synkage.context.activity_monitor import ActivityMonitor, ActivitySignals
from synkage.context.time_context import TimeSignals, time_signals


class Signals(BaseModel):
    time: TimeSignals
    activity: ActivitySignals
    urgent_words: list[str] = Field(default_factory=list)
    emergency_words: list[str] = Field(default_factory=list)
    override: str | None = None  # state the user set explicitly (--situation)


def _matches(text: str, words: list[str]) -> list[str]:
    return [w for w in words if re.search(rf"(?<!\w){re.escape(w)}(?!\w)", text, re.IGNORECASE)]


class SignalCollector:
    def __init__(self, config: SituationConfig, monitor: ActivityMonitor | None = None):
        self.config = config
        self.monitor = monitor or ActivityMonitor()

    def collect(self, command: str = "", override: str | None = None, now: datetime | None = None) -> Signals:
        # Only the command itself counts, not message text after ':'. Text inside a
        # message must never loosen confirmation (same rule as autonomy modifiers).
        head = command.split(":", 1)[0]
        return Signals(
            time=time_signals(self.config.quiet_hours, now),
            activity=self.monitor.read(),
            urgent_words=_matches(head, self.config.urgent_keywords),
            emergency_words=_matches(head, self.config.emergency_keywords),
            override=override,
        )
