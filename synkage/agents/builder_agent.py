"""Builder agent: turns a plan artifact into an action draft the router can execute
(Phase 4). Builds the payload only; never touches a tool.
"""

from __future__ import annotations

from typing import Any

from synkage.agents.base_agent import AgentTask, Artifact, BaseAgent


class BuilderAgent(BaseAgent):
    name = "builder"
    kind = "action_draft"

    def produce(self, task: AgentTask, inputs: list[Artifact]) -> tuple[str, dict[str, Any]]:
        plans = [a for a in inputs if a.kind == "plan"]
        if len(plans) != 1:
            raise ValueError(f"builder needs exactly one plan input, got {len(plans)}")
        plan = plans[0].body
        i, d = task.intent, task.decision
        tool = self.config.tools.get(plan.get("tool")) if plan.get("tool") else None

        missing = list(plan.get("blocked", []))
        if tool is None and self.config.commands.verbs[i.verb].needs_tool:
            missing.append("no tool")
        draft = {
            "action": i.verb,
            "object": i.object,
            "target": i.target,
            "content": i.content,
            "details": i.details,
            "tool": tool.id if tool else None,
            "adapter": tool.adapter if tool else None,
            "steps": plan.get("steps", []),
            "requires_confirmation": d.requires_confirmation,
            "ready": not missing,
            "missing": missing,
        }
        if draft["ready"] and plan.get("task_type") == "notes":
            text = i.content or i.details or ""
            if text.strip():
                note = self.skills.call("format_note", text=text)
                draft["note"] = {"title": note.title, "markdown": note.markdown}
        where = f" via {tool.name}" if tool else ""
        state = "ready" if draft["ready"] else "not ready: " + "; ".join(missing)
        return f"{i.verb} {i.object or ''}{where} — {state}".replace("  ", " "), draft
