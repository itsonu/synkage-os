"""Skill registry: the only way agents reach skills.

    registry.for_agent("planner").call("plan_steps", verb="send", ...)

`invoke` checks the caller's permission (config/permissions.yaml `agent_skills`,
default deny), validates input against the skill's Input model, runs a fresh
skill instance, and validates the Output.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel, ValidationError

from synkage.config import SynkageConfig
from synkage.skills.analysis.classify_intent import ClassifyIntentSkill
from synkage.skills.base_skill import BaseSkill
from synkage.skills.decision.plan_steps import PlanStepsSkill
from synkage.skills.text.format_note import FormatNoteSkill

DEFAULT_SKILLS: tuple[type[BaseSkill], ...] = (PlanStepsSkill, ClassifyIntentSkill, FormatNoteSkill)


class SkillError(Exception):
    """Unknown skill, duplicate registration, or invalid input/output."""


class PermissionDenied(SkillError):
    """The calling agent is not allowed to use this skill."""


class SkillRegistry:
    def __init__(self, config: SynkageConfig, skills: Iterable[type[BaseSkill]] = DEFAULT_SKILLS):
        self.config = config
        self._skills: dict[str, type[BaseSkill]] = {}
        for skill in skills:
            self.register(skill)

    def register(self, skill: type[BaseSkill]) -> None:
        if skill.name in self._skills:
            raise SkillError(f"duplicate skill name: '{skill.name}'")
        self._skills[skill.name] = skill

    def names(self) -> list[str]:
        return sorted(self._skills)

    def get(self, name: str) -> type[BaseSkill]:
        try:
            return self._skills[name]
        except KeyError:
            raise SkillError(f"unknown skill: '{name}'") from None

    def allowed(self, caller: str) -> list[str]:
        return list(self.config.permissions.agent_skills.get(caller, []))

    def invoke(self, name: str, caller: str, data: BaseModel | dict[str, Any]) -> BaseModel:
        skill = self.get(name)
        if name not in self.allowed(caller):
            raise PermissionDenied(f"agent '{caller}' may not use skill '{name}'")
        try:
            payload = skill.Input.model_validate(data if isinstance(data, dict) else data.model_dump())
        except ValidationError as e:
            raise SkillError(f"{name}: invalid input: {e.errors()[0]['msg']}") from e
        result = skill(self.config).run(payload)
        if not isinstance(result, skill.Output):
            raise SkillError(f"{name}: returned {type(result).__name__}, expected {skill.Output.__name__}")
        return result

    def for_agent(self, caller: str) -> SkillClient:
        return SkillClient(self, caller)


class SkillClient:
    """A registry handle bound to one agent, so every call carries the caller's name."""

    def __init__(self, registry: SkillRegistry, caller: str):
        self._registry, self.caller = registry, caller

    def call(self, name: str, **data: Any) -> BaseModel:
        return self._registry.invoke(name, self.caller, data)
