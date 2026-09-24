"""ac-2: planner, builder, reporter each produce an artifact file from a sample task."""

import json

from agent_helpers import CFG, make_task

from synkage.agents.base_agent import TaskStatus, read_artifact
from synkage.agents.builder_agent import BuilderAgent
from synkage.agents.planner_agent import PlannerAgent
from synkage.agents.reporter_agent import NOT_EXECUTED, ReporterAgent

CMD = "send message to Rahul: running late"


def run(agent_cls, command, out, inputs=None):
    result = agent_cls(CFG).run(make_task(agent_cls.name, command, out, inputs))
    assert result.status == TaskStatus.done, result.error
    return read_artifact(out)


def test_planner_produces_plan(tmp_path):
    plan = run(PlannerAgent, CMD, tmp_path / "plan.json")
    assert plan.kind == "plan"
    steps = plan.body["steps"]
    assert steps[:3] == ["Open WhatsApp Web", "Find Rahul", "Draft message: running late"]
    assert "Ask the user to confirm" in steps
    assert plan.body["blocked"] == []


def test_planner_marks_preview_as_blocked(tmp_path):
    plan = run(PlannerAgent, "send message", tmp_path / "plan.json")
    assert any("needs a target" in b for b in plan.body["blocked"])
    assert "Ask the user to confirm" not in plan.body["steps"]


def test_builder_produces_action_draft(tmp_path):
    plan = tmp_path / "plan.json"
    run(PlannerAgent, CMD, plan)
    draft = run(BuilderAgent, CMD, tmp_path / "draft.json", [plan])
    assert draft.kind == "action_draft"
    b = draft.body
    assert (b["action"], b["target"], b["content"]) == ("send", "Rahul", "running late")
    assert (b["tool"], b["adapter"], b["ready"]) == ("whatsapp_web", "local_exec", True)
    assert b["requires_confirmation"] is True


def test_builder_uses_the_plan_file_not_its_own_plan(tmp_path):
    plan = tmp_path / "plan.json"
    run(PlannerAgent, CMD, plan)
    data = json.loads(plan.read_text())
    data["body"]["steps"] = ["hand-edited step"]
    plan.write_text(json.dumps(data))
    draft = run(BuilderAgent, CMD, tmp_path / "draft.json", [plan])
    assert draft.body["steps"] == ["hand-edited step"]


def test_builder_without_plan_fails(tmp_path):
    result = BuilderAgent(CFG).run(make_task("builder", CMD, tmp_path / "d.json"))
    assert result.status == TaskStatus.failed
    assert "exactly one plan" in result.error


def test_reporter_produces_report(tmp_path):
    plan, draft = tmp_path / "plan.json", tmp_path / "draft.json"
    run(PlannerAgent, CMD, plan)
    run(BuilderAgent, CMD, draft, [plan])
    report = run(ReporterAgent, CMD, tmp_path / "report.json", [plan, draft])
    assert report.kind == "report"
    text = report.body["text"]
    assert text.startswith("Ready: send message to Rahul via WhatsApp Web.")
    assert "Needs your confirmation." in text
    assert NOT_EXECUTED in text


def test_reporter_shows_safety_flags(tmp_path):
    cmd = "send message to Raj: my password is hunter2"
    plan = tmp_path / "plan.json"
    run(PlannerAgent, cmd, plan)
    report = run(ReporterAgent, cmd, tmp_path / "report.json", [plan])
    assert "password_handling" in report.body["text"]
