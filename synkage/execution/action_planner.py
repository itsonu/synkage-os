"""Action planner: decides *how* a prepared action would run — which tool and adapter,
whether confirmation is required — and whether it is blocked before any adapter
is involved. Pure: reads config, never executes.

Safety is re-derived here rather than trusted from the brain's decision: the tool's
risk class comes from the registry, and never-autonomous categories are re-matched
on the raw command. A stale or tampered decision cannot skip confirmation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from synkage.adapters.tool_adapter_base import ActionRequest
from synkage.brain.autonomy_guard import AutonomyDecision, AutonomyGuard
from synkage.brain.intent_resolver import Intent, Mode
from synkage.config import SynkageConfig


class ExecutionPlan(BaseModel):
    tool: str | None
    adapter: str | None
    risk_class: str
    categories: list[str] = Field(default_factory=list)
    requires_confirmation: bool
    reasons: list[str] = Field(default_factory=list)
    blocked: str | None = None  # refusal reason; None = may proceed
    unavailable: str | None = None  # can't run yet (disabled tool, unknown adapter)
    nothing_to_do: bool = False  # no tool involved (skill-only verbs)


class ActionPlanner:
    def __init__(self, config: SynkageConfig):
        self.config = config
        self.guard = AutonomyGuard(config)

    def plan(self, request: ActionRequest, intent: Intent, decision: AutonomyDecision) -> ExecutionPlan:
        reasons: list[str] = []
        categories = sorted(set(decision.categories) | set(self.guard.categories_for(intent.raw)))
        tool = self.config.tools.get(request.tool) if request.tool else None

        risk = tool.risk_class if tool else "low"
        requires = decision.requires_confirmation or request.requires_confirmation
        if intent.mode == Mode.dry_run and decision.level == 2:
            requires = True  # report what a real run would need, not the dry run itself
        if categories:
            requires = True
            reasons.append(f"never autonomous: {', '.join(categories)}")
        if self.config.autonomy.risk_classes[risk].requires_confirmation:
            requires = True
            reasons.append(f"risk class '{risk}' always requires confirmation")

        adapter = tool.adapter if tool else None
        if tool and request.adapter and request.adapter != tool.adapter:
            reasons.append(f"draft named adapter '{request.adapter}'; registry says '{tool.adapter}'")
        plan = ExecutionPlan(
            tool=tool.id if tool else request.tool,
            adapter=adapter,
            risk_class=risk,
            categories=categories,
            requires_confirmation=requires,
            reasons=reasons,
        )

        if not request.ready:
            plan.blocked = "not ready: " + ("; ".join(request.missing) or "unknown")
        elif request.tool and tool is None:
            plan.blocked = f"unknown tool '{request.tool}'"
        elif tool is None:
            plan.nothing_to_do = True
        elif not tool.enabled:
            plan.unavailable = f"tool '{tool.id}' is disabled in tool_registry.json"
        return plan
