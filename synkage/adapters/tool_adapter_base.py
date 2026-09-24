"""Adapter contract: the router hands an adapter one ActionRequest, and the adapter
returns one ExecutionResult. Adapters translate requests into backend calls and
normalize results. They never decide autonomy: by the time execute() is called,
the router has already checked confirmation and safety rules.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from synkage.config import SynkageConfig


class ActionRequest(BaseModel):
    """The builder's action_draft body. `extra="forbid"` catches builder/adapter drift."""

    model_config = ConfigDict(extra="forbid")

    action: str | None
    object: str | None = None
    target: str | None = None
    content: str | None = None
    details: str | None = None
    tool: str | None = None
    adapter: str | None = None
    steps: list[str] = Field(default_factory=list)
    requires_confirmation: bool = True
    ready: bool = False
    missing: list[str] = Field(default_factory=list)
    note: dict[str, str] | None = None


class ExecutionStatus(str, Enum):
    success = "success"  # the adapter did it
    drafted = "drafted"  # a draft is ready in the tool; nothing was sent
    failed = "failed"  # the adapter tried and hit an error
    unavailable = "unavailable"  # no way to run it yet (disabled tool, no controller, stub)
    refused = "refused"  # the router blocked it (safety, confirmation, not ready)
    dry_run = "dry_run"  # simulated; no adapter was called
    skipped = "skipped"  # nothing to execute (e.g. skill-only verbs like summarize)


class ExecutionResult(BaseModel):
    status: ExecutionStatus
    adapter: str | None = None
    tool: str | None = None
    message: str
    output: dict[str, Any] = Field(default_factory=dict)


class ToolAdapter(ABC):
    name: ClassVar[str]

    def __init__(self, config: SynkageConfig):
        self.config = config

    @abstractmethod
    def execute(self, request: ActionRequest) -> ExecutionResult:
        """Run the request against the backend. Must not raise for expected failures."""

    def supports_draft(self, tool: str | None) -> bool:
        """True if this adapter can stage the action (e.g. fill a message) without committing it."""
        return False

    def draft(self, request: ActionRequest) -> ExecutionResult:
        """Stage the action without committing it. Only called when supports_draft() is True."""
        raise NotImplementedError

    def discard(self, request: ActionRequest) -> None:
        """Undo a draft the user declined. Best effort; default does nothing."""
        return None
