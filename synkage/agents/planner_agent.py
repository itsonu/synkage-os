"""Planner agent: turns an intent into ordered steps. Rule-based templates per verb."""

from __future__ import annotations

from typing import Any

from synkage.agents.base_agent import AgentTask, Artifact, BaseAgent
from synkage.brain.intent_resolver import Mode

MESSAGE_VERBS = {"send", "reply"}
SKILL_VERBS = {"summarize", "find", "plan", "generate"}  # handled by skills from Phase 3


class PlannerAgent(BaseAgent):
    name = "planner"
    kind = "plan"

    def produce(self, task: AgentTask, inputs: list[Artifact]) -> tuple[str, dict[str, Any]]:
        i, d = task.intent, task.decision
        tool = self.tool_name(i.tool) or i.tool
        steps: list[str] = []

        if i.verb in MESSAGE_VERBS:
            steps = [f"Open {tool or '(tool missing)'}", f"Find {i.target or '(recipient missing)'}"]
            draft = f": {i.content}" if i.content else " (content not given yet)"
            steps.append(f"Draft {i.object}{draft}")
        elif i.verb == "save":
            what = i.content or i.details or i.object
            steps = [f"Open {tool}", f"Create {i.object} with: {what}"]
        elif i.verb == "open":
            steps = [f"Open {tool}"] + ([i.details] if i.details else [])
        elif i.verb in {"create", "execute"}:
            steps = [f"Open {tool}", f"{i.verb.capitalize()} {i.object}"]
        elif i.verb in SKILL_VERBS:
            extra = f" ({i.details})" if i.details else ""
            steps = [f"{i.verb.capitalize()} {i.object or 'input'}{extra}"]

        blocked = list(i.unclear) if i.mode == Mode.preview else []
        if steps and not blocked:
            if d.requires_confirmation and i.verb != "plan":  # a plan is the answer, not an action
                steps.append("Ask the user to confirm")
            if i.verb in MESSAGE_VERBS:
                steps.append(f"Send via {tool}")
            if i.tool:
                steps.append("Verify the result")

        summary = f"{len(steps)} step plan" + (f", blocked: {'; '.join(blocked)}" if blocked else "")
        return summary, {"steps": steps, "blocked": blocked, "tool": i.tool}
