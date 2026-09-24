"""Autonomy guard: decides whether an intent may run, and whether it needs confirmation.

Inputs (docs/autonomy_safety.md): autonomy level, task risk class, tool sensitivity,
safety categories, situation. Phase 1 uses the configured default level and treats
the situation as 'normal'; situation-driven thresholds arrive in Phase 6.

Hard rules, applied last so nothing can override them:
  - any never_autonomous category  -> confirmation required
  - risk class with requires_confirmation (high, critical) -> confirmation required
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from synkage.brain.intent_resolver import Intent, Mode
from synkage.config import SynkageConfig

DEFAULT_RISK = "low"  # intents that touch no tool (e.g. summarize)


class AutonomyDecision(BaseModel):
    level: int
    risk_class: str
    categories: list[str] = Field(default_factory=list)
    may_execute: bool
    requires_confirmation: bool
    reasons: list[str] = Field(default_factory=list)


class AutonomyGuard:
    def __init__(self, config: SynkageConfig):
        self.cfg = config

    def categories_for(self, text: str) -> list[str]:
        """Safety categories whose keywords appear in the command (whole words)."""
        words = set(re.findall(r"[\w']+", text.lower()))
        kw = self.cfg.permissions.category_keywords
        return [
            c for c in self.cfg.permissions.never_autonomous if words & {k.lower() for k in kw.get(c, [])}
        ]

    def risk_for(self, intent: Intent) -> str:
        tool = self.cfg.tools.get(intent.tool) if intent.tool else None
        return tool.risk_class if tool else DEFAULT_RISK

    def decide(self, intent: Intent, level: int | None = None) -> AutonomyDecision:
        a = self.cfg.autonomy
        level = a.default_level if level is None else level
        reasons: list[str] = []

        if intent.modifier == "auto":
            level = 3
            reasons.append("'auto execute' requested level 3")
        elif intent.modifier == "confirm":
            level = min(level, 2)
            reasons.append("'ask before send' caps level at 2")

        if intent.mode == Mode.preview:
            level = min(level, 1)
            reasons.append("preview mode: " + ("; ".join(intent.unclear) or "requested"))

        risk = self.risk_for(intent)
        categories = self.categories_for(intent.raw)

        may_execute = level >= 2 and intent.mode == Mode.execute
        if intent.mode == Mode.dry_run:
            reasons.append("dry run: simulate only, no side effects")
        elif level <= 1:
            reasons.append(f"level {level} ({a.levels[level].name}) never executes")

        # Hard rules hold at every level, even when nothing runs, so callers can't
        # misread a level-0/1 decision as "safe to auto-run later".
        requires_confirmation = level == 2 and may_execute
        if requires_confirmation:
            reasons.append("level 2: execute with confirmation")
        if categories:
            requires_confirmation = True
            reasons.append(f"never autonomous: {', '.join(categories)}")
        if a.risk_classes[risk].requires_confirmation:
            requires_confirmation = True
            reasons.append(f"risk class '{risk}' always requires confirmation")

        return AutonomyDecision(
            level=level,
            risk_class=risk,
            categories=categories,
            may_execute=may_execute,
            requires_confirmation=requires_confirmation,
            reasons=reasons,
        )
