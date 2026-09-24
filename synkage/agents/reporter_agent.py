"""Reporter agent: one brief, human-readable report from the earlier artifacts."""

from __future__ import annotations

from typing import Any

from synkage.agents.base_agent import AgentTask, Artifact, BaseAgent

NOT_EXECUTED = "Nothing was executed (execution arrives in Phase 4)."


class ReporterAgent(BaseAgent):
    name = "reporter"
    kind = "report"

    def produce(self, task: AgentTask, inputs: list[Artifact]) -> tuple[str, dict[str, Any]]:
        by_kind = {a.kind: a for a in inputs}
        plan, draft = by_kind.get("plan"), by_kind.get("action_draft")
        d = task.decision
        lines: list[str] = []

        if plan and plan.body.get("blocked"):
            lines.append("Preview only — " + "; ".join(plan.body["blocked"]) + ".")
        elif draft:
            b = draft.body
            action = " ".join(
                x for x in (b["action"], b["object"], f"to {b['target']}" if b["target"] else "") if x
            )
            via = f" via {self.tool_name(b['tool'])}" if b["tool"] else ""
            lines.append(f"Ready: {action}{via}." if b["ready"] else f"Not ready: {'; '.join(b['missing'])}.")
            if draft.body["ready"] and d.may_execute:
                needs = d.requires_confirmation
                lines.append("Needs your confirmation." if needs else "Can run without confirmation.")
        elif plan:
            lines.append(f"Plan: {plan.summary}.")
        if d.categories:
            lines.append(f"Safety flags: {', '.join(d.categories)} (always needs confirmation).")
        if plan and plan.body.get("steps"):
            lines.append("Steps: " + " → ".join(plan.body["steps"]))
        lines.append(NOT_EXECUTED)

        text = "\n".join(lines)
        return lines[0], {"text": text, "sources": [a.kind for a in inputs]}
