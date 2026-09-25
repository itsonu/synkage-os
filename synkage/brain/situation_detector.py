"""Situation detector: rule-based classification of signals into one of five
states (ADR-0003). First matching rule wins:

  1. explicit override (--situation)                  -> that state
  2. emergency keyword in the command                 -> emergency
  3. urgent keyword in the command                    -> urgent
  4. idle for >= idle_after_seconds                   -> idle
  5. frontmost app is a focus app                     -> focused
  6. quiet hours and no activity data at all          -> idle
  7. otherwise                                        -> normal

Unknown signals (None) never trigger a rule, so missing data falls through to normal.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from synkage.config import SituationConfig
from synkage.context.signal_ingestion import Signals


class SituationState(str, Enum):
    idle = "idle"
    normal = "normal"
    focused = "focused"
    urgent = "urgent"
    emergency = "emergency"


class Situation(BaseModel):
    state: SituationState
    reasons: list[str] = Field(default_factory=list)


class SituationDetector:
    def __init__(self, config: SituationConfig):
        self.config = config

    def classify(self, s: Signals) -> Situation:
        a = s.activity
        if s.override:
            return Situation(state=SituationState(s.override), reasons=["set explicitly"])
        if s.emergency_words:
            return Situation(
                state=SituationState.emergency, reasons=[f"command says: {', '.join(s.emergency_words)}"]
            )
        if s.urgent_words:
            return Situation(
                state=SituationState.urgent, reasons=[f"command says: {', '.join(s.urgent_words)}"]
            )
        if a.idle_seconds is not None and a.idle_seconds >= self.config.idle_after_seconds:
            return Situation(state=SituationState.idle, reasons=[f"no input for {int(a.idle_seconds)}s"])
        focus = {name.lower() for name in self.config.focus_apps}
        if a.frontmost_app and a.frontmost_app.lower() in focus:
            return Situation(state=SituationState.focused, reasons=[f"working in {a.frontmost_app}"])
        if s.time.quiet_hours and a.idle_seconds is None and a.frontmost_app is None:
            return Situation(state=SituationState.idle, reasons=["quiet hours, no activity data"])
        return Situation(state=SituationState.normal, reasons=["no rule matched"])
