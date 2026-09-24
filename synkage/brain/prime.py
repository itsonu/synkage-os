"""Prime agent: the brain's entry point. Resolves intent, asks the autonomy guard,
and delegates to specialist agents. Never executes tools itself.

Delegation writes one run folder per command:

    runs/<run-id>/01-planner.json  ->  02-builder.json  ->  03-reporter.json

Each agent reads only the files before it (see synkage/agents/base_agent.py).
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from synkage.agents.base_agent import AgentResult, AgentTask, TaskStatus
from synkage.agents.registry import AGENTS
from synkage.brain.autonomy_guard import AutonomyDecision, AutonomyGuard
from synkage.brain.intent_resolver import Intent, IntentResolver, Mode
from synkage.config import SynkageConfig, resolve_runs_dir

FULL_CHAIN = ["planner", "builder", "reporter"]
PLAN_CHAIN = ["planner", "reporter"]


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


class DelegationResult(BaseModel):
    run_id: str
    run_dir: Path | None
    chain: list[str]
    results: list[AgentResult] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return bool(self.results) and all(r.status == TaskStatus.done for r in self.results)

    @property
    def artifact(self) -> Path | None:
        """The last agent's artifact — the one to show the user."""
        return self.results[-1].output if self.ok else None


def select_chain(intent: Intent, decision: AutonomyDecision) -> tuple[list[str], list[str]]:
    """Which agents run, in order, plus notes explaining the choice."""
    if decision.level == 0:
        return [], ["level 0 (observe): no agents run"]
    if intent.verb is None:
        return ["planner", "reporter"], ["unknown action: plan only"]
    if intent.mode == Mode.preview or decision.level == 1:
        return PLAN_CHAIN, ["preview / plan only: no action draft"]
    if intent.verb == "plan":
        return PLAN_CHAIN, ["'plan' asks for a plan, not an action"]
    notes = []
    if intent.agent_directive == "research then write":
        notes.append("researcher agent not built yet: planning without research")
    return FULL_CHAIN, notes


def _run_id(intent: Intent) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = re.sub(r"[^a-z0-9]+", "-", f"{intent.verb or 'unknown'} {intent.object or ''}".lower()).strip("-")
    return f"{stamp}-{slug[:40]}-{uuid.uuid4().hex[:6]}"


class Prime:
    def __init__(self, config: SynkageConfig, runs_dir: str | Path | None = None):
        self.config = config
        self.runs_dir = resolve_runs_dir(runs_dir)
        self.resolver = IntentResolver(config)
        self.guard = AutonomyGuard(config)

    def handle(self, text: str) -> PrimeResult:
        intent = self.resolver.resolve(text)
        return PrimeResult(intent=intent, decision=self.guard.decide(intent))

    def delegate(self, result: PrimeResult) -> DelegationResult:
        """Run the agent chain for this intent. Stops at the first failed agent."""
        chain, notes = select_chain(result.intent, result.decision)
        run_id = _run_id(result.intent)
        if not chain:
            return DelegationResult(run_id=run_id, run_dir=None, chain=[], notes=notes)

        run_dir = self.runs_dir / run_id
        out = DelegationResult(run_id=run_id, run_dir=run_dir, chain=chain, notes=notes)
        inputs: list[Path] = []
        for n, name in enumerate(chain, start=1):
            task = AgentTask(
                id=f"{run_id}/{n:02d}-{name}",
                agent=name,
                intent=result.intent,
                decision=result.decision,
                inputs=list(inputs),
                output=run_dir / f"{n:02d}-{name}.json",
            )
            agent_result = AGENTS[name](self.config).run(task)
            out.results.append(agent_result)
            if agent_result.status != TaskStatus.done:
                break
            inputs.append(agent_result.output)
        return out
