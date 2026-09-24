"""Agent task contract and base class.

Agents chain through files: each task names the artifact files it reads
(`inputs`) and the one file it must write (`output`). Nothing passes between
agents in memory. Agents never control tools; they only produce artifacts.

    AgentTask ──► BaseAgent.run() ──► writes Artifact JSON to task.output
                                  └─► returns AgentResult (status, output path)
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, Field, ValidationError

from synkage.brain.autonomy_guard import AutonomyDecision
from synkage.brain.intent_resolver import Intent
from synkage.config import SynkageConfig
from synkage.skills.registry import SkillRegistry


class TaskStatus(str, Enum):
    done = "done"
    failed = "failed"


class AgentTask(BaseModel):
    id: str
    agent: str
    intent: Intent
    decision: AutonomyDecision
    inputs: list[Path] = Field(default_factory=list)  # artifacts from earlier agents
    output: Path  # where this agent must write its artifact


class AgentResult(BaseModel):
    task_id: str
    agent: str
    status: TaskStatus
    output: Path | None = None
    error: str | None = None


class Artifact(BaseModel):
    """What every agent writes. `body` is agent-specific; `summary` is one line for humans."""

    agent: str
    kind: str
    task_id: str
    created: datetime
    inputs: list[str] = Field(default_factory=list)
    summary: str
    body: dict[str, Any] = Field(default_factory=dict)


def read_artifact(path: Path) -> Artifact:
    return Artifact.model_validate_json(Path(path).read_text(encoding="utf-8"))


def write_artifact(path: Path, artifact: Artifact) -> None:
    """Atomic write, so a crashed agent never leaves a half-written file for the next one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(artifact.model_dump_json(indent=2), encoding="utf-8")
    os.replace(tmp, path)


class BaseAgent(ABC):
    name: ClassVar[str]
    kind: ClassVar[str]  # artifact kind this agent produces, e.g. "plan"

    def __init__(self, config: SynkageConfig, skills: SkillRegistry | None = None):
        self.config = config
        # Skills are reached only through the registry, bound to this agent's name,
        # so every call is permission-checked.
        self.skills = (skills or SkillRegistry(config)).for_agent(self.name)

    def tool_name(self, tool_id: str | None) -> str | None:
        tool = self.config.tools.get(tool_id) if tool_id else None
        return tool.name if tool else None

    def run(self, task: AgentTask) -> AgentResult:
        if task.agent != self.name:
            return self._fail(task, f"task is for agent '{task.agent}', not '{self.name}'")
        try:
            inputs = [read_artifact(p) for p in task.inputs]
        except FileNotFoundError as e:
            return self._fail(task, f"missing input artifact: {e.filename}")
        except ValidationError as e:
            return self._fail(task, f"invalid input artifact: {e.errors()[0]['msg']}")
        try:
            summary, body = self.produce(task, inputs)
        except Exception as e:  # an agent bug must fail the task, not crash the chain runner
            return self._fail(task, f"{type(e).__name__}: {e}")
        artifact = Artifact(
            agent=self.name,
            kind=self.kind,
            task_id=task.id,
            created=datetime.now(timezone.utc),
            inputs=[str(p) for p in task.inputs],
            summary=summary,
            body=body,
        )
        write_artifact(task.output, artifact)
        return AgentResult(task_id=task.id, agent=self.name, status=TaskStatus.done, output=task.output)

    @abstractmethod
    def produce(self, task: AgentTask, inputs: list[Artifact]) -> tuple[str, dict[str, Any]]:
        """Return (one-line summary, body). Read earlier work only from `inputs`."""

    def _fail(self, task: AgentTask, error: str) -> AgentResult:
        return AgentResult(task_id=task.id, agent=self.name, status=TaskStatus.failed, error=error)
