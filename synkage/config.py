"""Config loader: reads and validates everything under the config directory.

Files (all required):
    autonomy_levels.yaml   levels 0-3, default level, risk classes
    permissions.yaml       hard "never autonomous" categories
    command_aliases.yaml   command vocabulary (docs/command_grammar.md)
    app_preferences.yaml   preferred tool per task type
    tool_registry.json     registered tools and their execution adapter

Every problem surfaces as ConfigError with the offending file named, so the CLI
can report it and exit non-zero instead of crashing later.
"""

from __future__ import annotations

import json
import os
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_DIR = REPO_ROOT / "config"

# From docs/autonomy_safety.md. Config may extend this list but never shrink it.
HARD_NEVER_AUTONOMOUS = frozenset(
    {
        "payments",
        "account_changes",
        "password_handling",
        "public_posting",
        "destructive_file_ops",
        "system_config_changes",
    }
)


class ConfigError(Exception):
    """Config is missing or invalid."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --- autonomy_levels.yaml ---------------------------------------------------


class AutonomyLevel(_Strict):
    name: str
    description: str


class RiskClass(_Strict):
    examples: list[str] = Field(default_factory=list)
    requires_confirmation: bool


class AutonomyConfig(_Strict):
    default_level: int
    levels: dict[int, AutonomyLevel]
    risk_classes: dict[str, RiskClass]

    @model_validator(mode="after")
    def _check(self) -> AutonomyConfig:
        if sorted(self.levels) != [0, 1, 2, 3]:
            raise ValueError(f"levels must be exactly 0-3, got {sorted(self.levels)}")
        if self.default_level not in self.levels:
            raise ValueError(f"default_level {self.default_level} is not a defined level")
        for name in ("high", "critical"):
            rc = self.risk_classes.get(name)
            if rc is None or not rc.requires_confirmation:
                raise ValueError(f"risk class '{name}' must exist and require confirmation")
        return self


# --- permissions.yaml -------------------------------------------------------


class PermissionsConfig(_Strict):
    never_autonomous: list[str]
    category_keywords: dict[str, list[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _check(self) -> PermissionsConfig:
        missing = HARD_NEVER_AUTONOMOUS - set(self.never_autonomous)
        if missing:
            raise ValueError(f"never_autonomous cannot drop hard safety rules: {sorted(missing)}")
        no_keywords = sorted(c for c in self.never_autonomous if not self.category_keywords.get(c))
        if no_keywords:
            raise ValueError(f"category_keywords missing for: {no_keywords}")
        unknown = sorted(set(self.category_keywords) - set(self.never_autonomous))
        if unknown:
            raise ValueError(f"category_keywords for unknown categories: {unknown}")
        return self


# --- command_aliases.yaml ---------------------------------------------------


class VerbRule(_Strict):
    needs_target: bool = False
    needs_tool: bool = False


class CommandAliases(_Strict):
    verbs: dict[str, VerbRule]
    object_types: dict[str, str] = Field(default_factory=dict)
    tool_directives: dict[str, str]
    autonomy_modifiers: dict[str, str]
    agent_directives: list[str] = Field(default_factory=list)


# --- app_preferences.yaml ---------------------------------------------------


class AppPreferences(_Strict):
    preferred_tools: dict[str, str] = Field(default_factory=dict)


# --- tool_registry.json -----------------------------------------------------


class ToolKind(str, Enum):
    browser = "browser"
    desktop = "desktop"
    runtime = "runtime"


class Tool(_Strict):
    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    name: str
    kind: ToolKind
    adapter: str = Field(description="Execution adapter that drives this tool, e.g. local_exec, openclaw.")
    risk_class: str
    enabled: bool = False
    notes: str = ""


class ToolRegistry(_Strict):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_ref: str | None = Field(default=None, alias="$schema")
    version: int = 1
    tools: list[Tool]

    @model_validator(mode="after")
    def _unique_ids(self) -> ToolRegistry:
        ids = [t.id for t in self.tools]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise ValueError(f"duplicate tool ids: {dupes}")
        return self

    def get(self, tool_id: str) -> Tool | None:
        return next((t for t in self.tools if t.id == tool_id), None)


def tool_registry_json_schema() -> dict[str, Any]:
    """JSON Schema for tool_registry.json (committed at config/schema/)."""
    return ToolRegistry.model_json_schema(by_alias=True)


# --- aggregate --------------------------------------------------------------


class SynkageConfig(BaseModel):
    config_dir: Path
    autonomy: AutonomyConfig
    permissions: PermissionsConfig
    commands: CommandAliases
    preferences: AppPreferences
    tools: ToolRegistry

    @model_validator(mode="after")
    def _cross_refs(self) -> SynkageConfig:
        problems = []
        for tool in self.tools.tools:
            if tool.risk_class not in self.autonomy.risk_classes:
                problems.append(f"tool '{tool.id}' has unknown risk_class '{tool.risk_class}'")
        for task, tool_id in self.preferences.preferred_tools.items():
            if self.tools.get(tool_id) is None:
                problems.append(f"preferred_tools.{task} -> unknown tool '{tool_id}'")
        for phrase, tool_id in self.commands.tool_directives.items():
            if self.tools.get(tool_id) is None:
                problems.append(f"tool_directives '{phrase}' -> unknown tool '{tool_id}'")
        if problems:
            raise ValueError("; ".join(problems))
        return self


def resolve_config_dir(config_dir: str | Path | None = None) -> Path:
    """Explicit arg > SYNKAGE_CONFIG_DIR (env or .env) > <repo>/config."""
    if config_dir is None:
        load_dotenv(REPO_ROOT / ".env")
        config_dir = os.environ.get("SYNKAGE_CONFIG_DIR") or DEFAULT_CONFIG_DIR
    path = Path(config_dir)
    if not path.is_absolute():
        path = (REPO_ROOT / path) if not path.exists() else path.resolve()
    return path


def _read(path: Path) -> Any:
    if not path.is_file():
        raise ConfigError(f"missing config file: {path}")
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        raise ConfigError(f"cannot parse {path.name}: {e}") from e


def _build(model: type[BaseModel], path: Path) -> Any:
    data = _read(path)
    if not isinstance(data, dict):
        raise ConfigError(f"{path.name}: expected a mapping at top level")
    try:
        return model.model_validate(data)
    except ValidationError as e:
        raise ConfigError(f"{path.name}: {e}") from e


def load_config(config_dir: str | Path | None = None) -> SynkageConfig:
    d = resolve_config_dir(config_dir)
    if not d.is_dir():
        raise ConfigError(f"config directory not found: {d}")
    parts = {
        "autonomy": _build(AutonomyConfig, d / "autonomy_levels.yaml"),
        "permissions": _build(PermissionsConfig, d / "permissions.yaml"),
        "commands": _build(CommandAliases, d / "command_aliases.yaml"),
        "preferences": _build(AppPreferences, d / "app_preferences.yaml"),
        "tools": _build(ToolRegistry, d / "tool_registry.json"),
    }
    try:
        return SynkageConfig(config_dir=d, **parts)
    except ValidationError as e:
        raise ConfigError(f"cross-file check failed: {e}") from e
