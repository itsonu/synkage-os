"""Agent registry: name -> agent class. Prime looks agents up here."""

from __future__ import annotations

from synkage.agents.base_agent import BaseAgent
from synkage.agents.builder_agent import BuilderAgent
from synkage.agents.planner_agent import PlannerAgent
from synkage.agents.reporter_agent import ReporterAgent

AGENTS: dict[str, type[BaseAgent]] = {a.name: a for a in (PlannerAgent, BuilderAgent, ReporterAgent)}
