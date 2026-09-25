"""Night cycle: runs once a day (scripts/nightly_update.py).

  1. trust   — outcomes logged since the last cycle move the trust score
               (confirmed success +, declined -, failed -), after decaying it toward
               neutral by decay_per_day for each day elapsed (so an extra run the
               same night barely decays).
  2. compress — audit records older than retention_days become per-day summaries
               (log_summaries.json); their raw lines go to archive/logs-YYYY-MM.jsonl.gz.
               Nothing is lost; logs.jsonl just stays small.

Reads raw JSON lines rather than execution's models, so memory stays independent
of the execution layer. Unparseable lines are kept as they are.
"""

from __future__ import annotations

import fcntl
import gzip
import json
from collections import Counter
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field

from synkage.memory.store import MemoryStore, TrustPoint, write_json_atomic


class NightReport(BaseModel):
    ran_at: datetime
    trust_before: float
    trust_after: float
    outcomes: dict[str, int] = Field(default_factory=dict)  # counted this run
    compressed_records: int = 0
    compressed_days: list[str] = Field(default_factory=list)
    kept_records: int = 0


def _ts(record: dict) -> datetime | None:
    try:
        ts = datetime.fromisoformat(str(record["ts"]).replace("Z", "+00:00"))
    except (KeyError, ValueError):
        return None
    return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)


def outcome_of(record: dict) -> str | None:
    """Which trust outcome an audit record counts as, if any."""
    status = (record.get("result") or {}).get("status")
    confirmed = (record.get("confirmation") or {}).get("confirmed")
    if status == "failed":
        return "failed"
    if confirmed is False:
        return "declined"
    if confirmed is True and status == "success":
        return "confirmed_success"
    return None


class NightCycle:
    def __init__(self, store: MemoryStore):
        self.store = store
        self.cfg = store.config.memory

    def run(self, now: datetime | None = None) -> NightReport:
        now = now or datetime.now(timezone.utc)
        self.store.ensure()
        state = self.store.load_relationship()
        report = NightReport(ran_at=now, trust_before=state.trust, trust_after=state.trust)

        path = self.store.audit_path
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a+", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)  # same lock AuditLog.append takes
            f.seek(0)
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
            parsed = [(ln, self._parse(ln)) for ln in lines]

            self._update_trust(state, parsed, now, report)
            keep = self._compress(parsed, now, report)
            if report.compressed_records:
                f.seek(0)
                f.truncate()
                f.write("".join(ln + "\n" for ln in keep))
                f.flush()
        report.kept_records = len(keep)

        state.last_night_cycle = now
        state.history.append(TrustPoint(at=now, trust=state.trust))
        self.store.save_relationship(state)
        report.trust_after = state.trust
        return report

    @staticmethod
    def _parse(line: str) -> dict | None:
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            return None
        return data if isinstance(data, dict) else None

    def _update_trust(self, state, parsed, now: datetime, report: NightReport) -> None:
        t = self.cfg.trust
        last = state.last_night_cycle
        days = 1.0 if last is None else max((now - last).total_seconds() / 86400, 0.0)
        trust = t.neutral + (state.trust - t.neutral) * (1 - t.decay_per_day) ** days

        counts: Counter[str] = Counter()
        for _, rec in parsed:
            ts = _ts(rec) if rec else None
            if ts is None or (last is not None and ts <= last) or ts > now:
                continue
            outcome = outcome_of(rec)
            if outcome:
                counts[outcome] += 1
        delta = {"confirmed_success": t.success, "declined": t.declined, "failed": t.failed}
        trust += sum(delta[k] * n for k, n in counts.items())
        state.trust = round(min(1.0, max(0.0, trust)), 4)
        for k, n in counts.items():
            setattr(state.outcomes, k, getattr(state.outcomes, k) + n)
        report.outcomes = dict(counts)

    def _compress(self, parsed, now: datetime, report: NightReport) -> list[str]:
        cutoff = now - timedelta(days=self.cfg.retention_days)
        keep, old = [], []
        for line, rec in parsed:
            ts = _ts(rec) if rec else None
            (old if ts is not None and ts < cutoff else keep).append((line, rec, ts))
        if not old:
            return [line for line, *_ in keep]

        summaries = self._load_summaries()
        archives: dict[str, list[str]] = {}
        for line, rec, ts in old:
            day = ts.date().isoformat()
            s = summaries.setdefault(day, {"total": 0, "by_status": {}, "by_tool": {}, "by_verb": {}})
            s["total"] += 1
            for key, value in (
                ("by_status", (rec.get("result") or {}).get("status")),
                ("by_tool", rec.get("tool")),
                ("by_verb", (rec.get("intent") or {}).get("verb")),
            ):
                name = str(value) if value is not None else "none"
                s[key][name] = s[key].get(name, 0) + 1
            archives.setdefault(ts.strftime("%Y-%m"), []).append(line)

        self.store.archive_dir.mkdir(parents=True, exist_ok=True)
        for month, raw in archives.items():  # append mode: a gzip file may hold several members
            with gzip.open(self.store.archive_dir / f"logs-{month}.jsonl.gz", "at", encoding="utf-8") as gz:
                gz.write("".join(ln + "\n" for ln in raw))
        write_json_atomic(self.store.summaries_path, json.dumps(dict(sorted(summaries.items())), indent=2))

        report.compressed_records = len(old)
        report.compressed_days = sorted({ts.date().isoformat() for *_, ts in old})
        return [line for line, *_ in keep]

    def _load_summaries(self) -> dict:
        p = self.store.summaries_path
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
