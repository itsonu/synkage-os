"""Adapter registry: adapter name (as used in tool_registry.json) -> adapter class."""

from __future__ import annotations

from synkage.adapters.local_exec_adapter import LocalExecAdapter
from synkage.adapters.openclaw_adapter import OpenClawAdapter
from synkage.adapters.tool_adapter_base import ToolAdapter

ADAPTERS: dict[str, type[ToolAdapter]] = {a.name: a for a in (LocalExecAdapter, OpenClawAdapter)}
