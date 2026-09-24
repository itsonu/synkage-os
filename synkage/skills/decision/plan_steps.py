"""plan_steps: ordered steps for an action, from rule-based templates per verb."""

from __future__ import annotations

from pydantic import BaseModel, Field

from synkage.skills.base_skill import BaseSkill

MESSAGE_VERBS = {"send", "reply"}
SKILL_VERBS = {"summarize", "find", "plan", "generate"}


class PlanStepsInput(BaseModel):
    verb: str | None
    object: str | None = None
    target: str | None = None
    content: str | None = None
    details: str | None = None
    tool_name: str | None = None
    requires_confirmation: bool = False
    blocked: list[str] = Field(default_factory=list)  # non-empty -> no confirm/send/verify steps


class PlanStepsOutput(BaseModel):
    steps: list[str]


class PlanStepsSkill(BaseSkill):
    name = "plan_steps"
    description = "Ordered steps for an action (rule-based templates per verb)."
    Input = PlanStepsInput
    Output = PlanStepsOutput

    def run(self, data: PlanStepsInput) -> PlanStepsOutput:
        verb, tool = data.verb, data.tool_name
        steps: list[str] = []
        if verb in MESSAGE_VERBS:
            steps = [f"Open {tool or '(tool missing)'}", f"Find {data.target or '(recipient missing)'}"]
            draft = f": {data.content}" if data.content else " (content not given yet)"
            steps.append(f"Draft {data.object}{draft}")
        elif verb == "save":
            what = data.content or data.details or data.object
            steps = [f"Open {tool}", f"Create {data.object} with: {what}"]
        elif verb == "open":
            steps = [f"Open {tool}"] + ([data.details] if data.details else [])
        elif verb in {"create", "execute"}:
            steps = [f"Open {tool}", f"{verb.capitalize()} {data.object}"]
        elif verb in SKILL_VERBS:
            extra = f" ({data.details})" if data.details else ""
            steps = [f"{verb.capitalize()} {data.object or 'input'}{extra}"]

        if steps and not data.blocked:
            if data.requires_confirmation and verb != "plan":  # a plan is the answer, not an action
                steps.append("Ask the user to confirm")
            if verb in MESSAGE_VERBS:
                steps.append(f"Send via {tool}")
            if tool:
                steps.append("Verify the result")
        return PlanStepsOutput(steps=steps)
