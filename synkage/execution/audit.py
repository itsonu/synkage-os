"""Audit log (docs/autonomy_safety.md): every routed action — executed, refused, or
dry-run — appends one JSON line with intent, tool, autonomy level, confirmation
state and result. Append-only here. The only rewriter is the night cycle (synkage/memory/night_cycle.py),
which moves old records into summaries + a gzip archive. Both sides hold an
exclusive flock on the file, so a record appended mid-cycle is never lost.
"""

from __future__ import annotations

import fcntl
import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from synkage.config import resolve_audit_log


class AuditRecord(BaseModel):
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    run_id: str | None = None
    intent: dict  # raw command + verb/object/target/mode
    tool: str | None
    adapter: str | None
    autonomy_level: int
    situation: str = "normal"  # explains why a low-risk action may have skipped confirmation
    risk_class: str
    categories: list[str] = Field(default_factory=list)
    confirmation: dict  # {"required": bool, "confirmed": bool | None}
    result: dict  # {"status": ..., "message": ...}


class AuditLog:
    def __init__(self, path: str | Path | None = None):
        self.path = resolve_audit_log(path)

    def append(self, record: AuditRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)  # released on close
            f.write(record.model_dump_json() + "\n")

    def read(self) -> list[AuditRecord]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        return [AuditRecord.model_validate(json.loads(line)) for line in lines if line.strip()]
