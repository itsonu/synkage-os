"""Prime agent: the brain's entry point. Resolves intent, asks the autonomy guard,
and (from Phase 2) delegates to specialist agents. Never executes tools itself.
"""

from __future__ import annotations

from pydantic import BaseModel

from synkage.brain.autonomy_guard import AutonomyDecision, AutonomyGuard
from synkage.brain.intent_resolver import Intent, IntentResolver
from synkage.config import SynkageConfig


class PrimeResult(BaseModel):
    intent: Intent
    decision: AutonomyDecision

    def plan_text(self) -> str:
        i = self.intent
        parts = [i.verb or "?", i.object or ""]
        if i.target:
            parts.append(f"to {i.target}")
        if i.details:
            parts.append(f"({i.details})")
        text = " ".join(p for p in parts if p)
        return f"{text}: {i.content}" if i.content else text


class Prime:
    def __init__(self, config: SynkageConfig):
        self.config = config
        self.resolver = IntentResolver(config)
        self.guard = AutonomyGuard(config)

    def handle(self, text: str) -> PrimeResult:
        intent = self.resolver.resolve(text)
        return PrimeResult(intent=intent, decision=self.guard.decide(intent))

    def delegate(self, result: PrimeResult):
        raise NotImplementedError("agent delegation arrives in Phase 2")
