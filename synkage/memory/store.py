"""Memory store: the personal files, created on first run and kept across restarts.

    <memory dir>/                     default ~/.synkage/memory (SYNKAGE_MEMORY_DIR)
      user_profile.json               who the user is (grows in later phases)
      relationship_state.json         trust score, outcome counts, trust history
      logs.jsonl                      audit log (written by execution/audit.py)
      log_summaries.json              per-day summaries made by the night cycle
      archive/logs-YYYY-MM.jsonl.gz   raw audit lines the night cycle compressed

The directory is created owner-only (0700): it holds message text.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from synkage.config import SynkageConfig, resolve_audit_log, resolve_memory_dir


def _now() -> datetime:
    return datetime.now(timezone.utc)


class UserProfile(BaseModel):
    created: datetime = Field(default_factory=_now)
    name: str | None = None
    preferences: dict[str, str] = Field(default_factory=dict)


class OutcomeCounts(BaseModel):
    confirmed_success: int = 0
    declined: int = 0
    failed: int = 0


class TrustPoint(BaseModel):
    at: datetime
    trust: float


class RelationshipState(BaseModel):
    created: datetime = Field(default_factory=_now)
    trust: float
    outcomes: OutcomeCounts = Field(default_factory=OutcomeCounts)
    last_night_cycle: datetime | None = None
    history: list[TrustPoint] = Field(default_factory=list)  # last HISTORY_KEEP points


HISTORY_KEEP = 90


def write_json_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


class MemoryStore:
    def __init__(self, config: SynkageConfig, memory_dir: str | Path | None = None):
        self.config = config
        self.dir = resolve_memory_dir(memory_dir)

    @property
    def profile_path(self) -> Path:
        return self.dir / "user_profile.json"

    @property
    def relationship_path(self) -> Path:
        return self.dir / "relationship_state.json"

    @property
    def summaries_path(self) -> Path:
        return self.dir / "log_summaries.json"

    @property
    def archive_dir(self) -> Path:
        return self.dir / "archive"

    @property
    def audit_path(self) -> Path:
        return resolve_audit_log()

    def ensure(self) -> list[Path]:
        """Create the directory and any missing files. Never overwrites. Returns what it created."""
        created = []
        if not self.dir.exists():
            self.dir.mkdir(parents=True, mode=0o700)
            created.append(self.dir)
        if not self.profile_path.exists():
            self.save_profile(UserProfile())
            created.append(self.profile_path)
        if not self.relationship_path.exists():
            self.save_relationship(RelationshipState(trust=self.config.memory.trust.neutral))
            created.append(self.relationship_path)
        return created

    def load_profile(self) -> UserProfile:
        self.ensure()
        return UserProfile.model_validate_json(self.profile_path.read_text(encoding="utf-8"))

    def save_profile(self, profile: UserProfile) -> None:
        write_json_atomic(self.profile_path, profile.model_dump_json(indent=2))

    def load_relationship(self) -> RelationshipState:
        self.ensure()
        return RelationshipState.model_validate_json(self.relationship_path.read_text(encoding="utf-8"))

    def save_relationship(self, state: RelationshipState) -> None:
        state.history = state.history[-HISTORY_KEEP:]
        write_json_atomic(self.relationship_path, state.model_dump_json(indent=2))
