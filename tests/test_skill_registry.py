"""ac-1 (registry) and ac-2 (permission gating)."""

import pytest
from pydantic import BaseModel

from synkage.agents.registry import AGENTS
from synkage.config import load_config
from synkage.skills.base_skill import BaseSkill
from synkage.skills.registry import DEFAULT_SKILLS, PermissionDenied, SkillError, SkillRegistry

CFG = load_config()


class In(BaseModel):
    x: int


class Out(BaseModel):
    y: int


class DoubleSkill(BaseSkill):
    name = "double"
    description = "test"
    Input, Output = In, Out

    def run(self, data):
        return Out(y=data.x * 2)


class WrongOutputSkill(DoubleSkill):
    name = "wrong_output"

    def run(self, data):
        return In(x=1)


def registry_with(*skills, agent_skills=None):
    cfg = load_config()
    cfg.permissions.agent_skills = agent_skills or {"tester": [s.name for s in skills]}
    return SkillRegistry(cfg, skills)


# --- ac-1 ------------------------------------------------------------------------


def test_lists_registered_skills():
    assert SkillRegistry(CFG).names() == ["classify_intent", "format_note", "plan_steps"]


def test_rejects_duplicate_names():
    with pytest.raises(SkillError, match="duplicate skill name: 'double'"):
        SkillRegistry(CFG, [DoubleSkill, DoubleSkill])


def test_register_after_init_rejects_duplicate():
    r = registry_with(DoubleSkill)
    with pytest.raises(SkillError, match="duplicate"):
        r.register(DoubleSkill)


def test_unknown_skill():
    with pytest.raises(SkillError, match="unknown skill: 'nope'"):
        SkillRegistry(CFG).invoke("nope", "planner", {})


def test_invoke_validates_input_and_output():
    r = registry_with(DoubleSkill, WrongOutputSkill)
    assert r.invoke("double", "tester", {"x": 2}) == Out(y=4)
    with pytest.raises(SkillError, match="invalid input"):
        r.invoke("double", "tester", {"x": "not a number"})
    with pytest.raises(SkillError, match="expected Out"):
        r.invoke("wrong_output", "tester", {"x": 1})


def test_client_binds_caller():
    r = registry_with(DoubleSkill)
    assert r.for_agent("tester").call("double", x=5).y == 10


# --- ac-2 ------------------------------------------------------------------------


def test_permission_denied_for_unlisted_skill():
    with pytest.raises(PermissionDenied, match="agent 'reporter' may not use skill 'format_note'"):
        SkillRegistry(CFG).invoke("format_note", "reporter", {"text": "hi"})


def test_unlisted_agent_is_denied_everything():
    r = SkillRegistry(CFG)
    for name in r.names():
        with pytest.raises(PermissionDenied):
            r.for_agent("stranger").call(name)


def test_permission_checked_before_input_validation():
    # a denied caller learns nothing about the skill's input shape
    with pytest.raises(PermissionDenied):
        SkillRegistry(CFG).invoke("format_note", "reporter", {"bad": "input"})


def test_permission_config_names_real_agents_and_skills():
    known = {s.name for s in DEFAULT_SKILLS}
    for agent, skills in CFG.permissions.agent_skills.items():
        assert agent in AGENTS, f"unknown agent '{agent}' in agent_skills"
        assert set(skills) <= known, f"unknown skills for {agent}: {set(skills) - known}"
