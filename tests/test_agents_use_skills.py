"""ac-4: agents invoke skills only via the registry (and the registry checks permission)."""

from agent_helpers import make_task
from pydantic import BaseModel

from synkage.agents.base_agent import TaskStatus, read_artifact
from synkage.agents.builder_agent import BuilderAgent
from synkage.agents.planner_agent import PlannerAgent
from synkage.config import load_config
from synkage.skills.registry import SkillRegistry


class RecordingRegistry(SkillRegistry):
    def __init__(self, config):
        super().__init__(config)
        self.calls = []

    def invoke(self, name, caller, data):
        self.calls.append((caller, name))
        return super().invoke(name, caller, data)


def test_planner_calls_plan_steps_and_classify_via_registry(tmp_path):
    cfg = load_config()
    reg = RecordingRegistry(cfg)
    result = PlannerAgent(cfg, reg).run(make_task("planner", "send message to Rahul", tmp_path / "p.json"))
    assert result.status == TaskStatus.done
    assert reg.calls == [("planner", "plan_steps"), ("planner", "classify_intent")]
    assert read_artifact(tmp_path / "p.json").body["task_type"] == "messaging"


def test_planner_output_comes_from_the_registered_skill(tmp_path):
    class FakeOut(BaseModel):
        steps: list[str]

    class FakeRegistry(SkillRegistry):
        def invoke(self, name, caller, data):
            if name == "plan_steps":
                return FakeOut(steps=["from the registry"])
            return super().invoke(name, caller, data)

    cfg = load_config()
    PlannerAgent(cfg, FakeRegistry(cfg)).run(
        make_task("planner", "send message to Rahul", tmp_path / "p.json")
    )
    assert read_artifact(tmp_path / "p.json").body["steps"] == ["from the registry"]


def test_planner_fails_without_permission(tmp_path):
    cfg = load_config()
    cfg.permissions.agent_skills["planner"] = []
    result = PlannerAgent(cfg).run(make_task("planner", "send message to Rahul", tmp_path / "p.json"))
    assert result.status == TaskStatus.failed
    assert result.error.startswith("PermissionDenied: agent 'planner' may not use skill 'plan_steps'")


def test_builder_formats_notes_via_registry(tmp_path):
    cfg = load_config()
    reg = RecordingRegistry(cfg)
    cmd = "save note buy milk; call mom"
    plan = tmp_path / "p.json"
    PlannerAgent(cfg, reg).run(make_task("planner", cmd, plan, cfg=cfg))
    BuilderAgent(cfg, reg).run(make_task("builder", cmd, tmp_path / "b.json", [plan], cfg=cfg))
    assert ("builder", "format_note") in reg.calls
    note = read_artifact(tmp_path / "b.json").body["note"]
    assert note["markdown"] == "# Note (2 items)\n\n- Buy milk\n- Call mom\n"


def test_prime_shares_one_registry(tmp_path):
    from synkage.brain.prime import Prime

    prime = Prime(load_config(), runs_dir=tmp_path)
    assert prime.delegate(prime.handle("send message to Rahul")).ok
    assert isinstance(prime.skills, SkillRegistry)
