"""Planner agent: turns an intent into ordered steps via the plan_steps skill,
and tags the task type via classify_intent.
"""

from __future__ import annotations

from typing import Any

from synkage.agents.base_agent import AgentTask, Artifact, BaseAgent
from synkage.brain.intent_resolver import Mode


class PlannerAgent(BaseAgent):
    name = "planner"
    kind = "plan"

    def produce(self, task: AgentTask, inputs: list[Artifact]) -> tuple[str, dict[str, Any]]:
        i, d = task.intent, task.decision
        blocked = list(i.unclear) if i.mode == Mode.preview else []
        plan = self.skills.call(
            "plan_steps",
            verb=i.verb,
            object=i.object,
            target=i.target,
            content=i.content,
            details=i.details,
            tool_name=self.tool_name(i.tool) or i.tool,
            requires_confirmation=d.requires_confirmation,
            blocked=blocked,
        )
        task_type = self.skills.call("classify_intent", text=i.raw).task_type

        summary = f"{len(plan.steps)} step plan" + (f", blocked: {'; '.join(blocked)}" if blocked else "")
        return summary, {"steps": plan.steps, "blocked": blocked, "tool": i.tool, "task_type": task_type}
