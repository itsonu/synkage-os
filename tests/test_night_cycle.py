"""ac-2 (compression), ac-3 (trust from logged outcomes), ac-4 (script + scheduler)."""

import gzip
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import pytest

from synkage.config import REPO_ROOT, load_config
from synkage.memory import night_cycle as nc_module
from synkage.memory.night_cycle import NightCycle, outcome_of
from synkage.memory.store import MemoryStore

NOW = datetime(2026, 9, 25, 3, 17, tzinfo=timezone.utc)
CFG = load_config()


def record(days_ago=0.1, status="success", confirmed=True, required=True, tool="whatsapp_web", verb="send"):
    return {
        "ts": (NOW - timedelta(days=days_ago)).isoformat(),
        "intent": {"raw": "x", "verb": verb},
        "tool": tool,
        "confirmation": {"required": required, "confirmed": confirmed},
        "result": {"status": status, "message": "m"},
    }


def write_log(store, records, extra_lines=()):
    store.audit_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(r) for r in records] + list(extra_lines)
    store.audit_path.write_text("".join(ln + "\n" for ln in lines))


@pytest.fixture
def store():
    s = MemoryStore(load_config())
    s.ensure()
    return s


# --- ac-2: compression ---------------------------------------------------------------------


def test_old_records_become_daily_summaries_and_are_archived(store):
    old = [
        record(days_ago=40),
        record(days_ago=40, status="refused", confirmed=False, tool="gmail"),
        record(days_ago=35, verb="save", tool="apple_notes"),
    ]
    recent = [record(days_ago=1)]
    write_log(store, old + recent, extra_lines=["not json"])
    report = NightCycle(store).run(now=NOW)

    assert report.compressed_records == 3
    assert report.compressed_days == [
        (NOW - timedelta(days=40)).date().isoformat(),
        (NOW - timedelta(days=35)).date().isoformat(),
    ]
    summaries = json.loads(store.summaries_path.read_text())
    day40 = summaries[(NOW - timedelta(days=40)).date().isoformat()]
    assert day40 == {
        "total": 2,
        "by_status": {"success": 1, "refused": 1},
        "by_tool": {"whatsapp_web": 1, "gmail": 1},
        "by_verb": {"send": 2},
    }

    kept = store.audit_path.read_text().splitlines()
    assert kept == [json.dumps(recent[0]), "not json"]  # unparseable lines are never dropped
    assert report.kept_records == 2

    archived = []
    for gz in sorted(store.archive_dir.glob("logs-*.jsonl.gz")):
        archived += gzip.open(gz, "rt").read().splitlines()
    assert sorted(archived) == sorted(json.dumps(r) for r in old)  # nothing lost


def test_second_run_compresses_nothing_more(store):
    write_log(store, [record(days_ago=40), record(days_ago=1)])
    NightCycle(store).run(now=NOW)
    assert NightCycle(store).run(now=NOW + timedelta(hours=1)).compressed_records == 0


def test_summaries_merge_across_runs(store):
    day = (NOW - timedelta(days=40)).date().isoformat()
    write_log(store, [record(days_ago=40)])
    NightCycle(store).run(now=NOW)
    with store.audit_path.open("a") as f:  # a late record for the same old day
        f.write(json.dumps(record(days_ago=40)) + "\n")
    NightCycle(store).run(now=NOW + timedelta(hours=1))
    assert json.loads(store.summaries_path.read_text())[day]["total"] == 2


def test_nothing_old_means_file_untouched(store):
    write_log(store, [record(days_ago=1)])
    before = store.audit_path.read_text()
    NightCycle(store).run(now=NOW)
    assert store.audit_path.read_text() == before
    assert not store.summaries_path.exists()


def test_cycle_holds_the_audit_lock(store, monkeypatch):
    calls = []
    monkeypatch.setattr(nc_module.fcntl, "flock", lambda f, op: calls.append(op))
    NightCycle(store).run(now=NOW)
    assert calls == [nc_module.fcntl.LOCK_EX]


# --- ac-3: trust ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rec, outcome",
    [
        (record(status="success", confirmed=True), "confirmed_success"),
        (record(status="refused", confirmed=False), "declined"),
        (record(status="failed", confirmed=True), "failed"),
        (record(status="failed", confirmed=None, required=False), "failed"),
        (record(status="success", confirmed=None, required=False), None),  # auto-run: no trust signal
        (record(status="dry_run", confirmed=None), None),
        (record(status="unavailable", confirmed=True), None),
    ],
)
def test_outcome_mapping(rec, outcome):
    assert outcome_of(rec) == outcome


def test_trust_moves_with_logged_outcomes(store):
    t = CFG.memory.trust
    write_log(store, [record()] * 3 + [record(status="refused", confirmed=False)] + [record(status="failed")])
    report = NightCycle(store).run(now=NOW)
    expected = round(t.neutral + 3 * t.success + t.declined + t.failed, 4)
    assert report.trust_after == expected == store.load_relationship().trust
    assert report.outcomes == {"confirmed_success": 3, "declined": 1, "failed": 1}
    rel = store.load_relationship()
    assert (rel.outcomes.confirmed_success, rel.outcomes.declined, rel.outcomes.failed) == (3, 1, 1)
    assert rel.last_night_cycle == NOW and rel.history[-1].trust == expected


def test_outcomes_are_counted_once(store):
    write_log(store, [record()] * 2)
    NightCycle(store).run(now=NOW)
    second = NightCycle(store).run(now=NOW + timedelta(hours=1))
    assert second.outcomes == {}


@pytest.mark.parametrize("days, factor", [(1, 0.9), (2, 0.81), (0.0417, 0.9**0.0417)])
def test_trust_decays_toward_neutral_per_day_elapsed(store, days, factor):
    rel = store.load_relationship()
    rel.trust, rel.last_night_cycle = 0.8, NOW - timedelta(days=days)
    store.save_relationship(rel)
    report = NightCycle(store).run(now=NOW)
    assert report.trust_after == pytest.approx(0.5 + 0.3 * factor, abs=1e-3)


def test_trust_is_clamped(store):
    write_log(store, [record(status="failed")] * 30)
    assert NightCycle(store).run(now=NOW).trust_after == 0.0


def test_future_records_are_ignored(store):
    write_log(store, [record(days_ago=-1)])  # clock skew
    assert NightCycle(store).run(now=NOW).outcomes == {}


# --- ac-4: script + scheduler -------------------------------------------------------------------


def test_nightly_script_runs_once_and_exits_0(memory_dir):
    proc = subprocess.run(
        [sys.executable, "scripts/nightly_update.py"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.startswith("night cycle: trust 0.500 -> 0.500")
    assert json.loads((memory_dir / "relationship_state.json").read_text())["last_night_cycle"]


def test_nightly_script_bad_config_exits_1(tmp_path):
    proc = subprocess.run(
        [sys.executable, "scripts/nightly_update.py", "--config-dir", str(tmp_path / "nope")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 1 and "config error" in proc.stderr


def test_scheduler_registers_daily_job():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import nightly_update
    from apscheduler.schedulers.background import BackgroundScheduler

    sched = nightly_update.build_scheduler(CFG, BackgroundScheduler())
    job = sched.get_job(nightly_update.JOB_ID)
    assert job is not None and job.func is nightly_update.run_once
    fields = {f.name: str(f) for f in job.trigger.fields}
    assert (fields["hour"], fields["minute"]) == (
        str(CFG.memory.schedule.hour),
        str(CFG.memory.schedule.minute),
    )
    assert not sched.running


def test_no_record_lost_when_appends_race_the_cycle(store):
    """Real flock between an appender thread and repeated night cycles on the same file."""
    import threading

    from synkage.execution.audit import AuditLog, AuditRecord

    write_log(store, [record(days_ago=40)] * 50)  # old records the cycles will compress
    audit = AuditLog(store.audit_path)
    n = 300

    def append_many():
        for i in range(n):
            audit.append(
                AuditRecord(
                    run_id=f"r{i}",
                    intent={"raw": "x"},
                    tool=None,
                    adapter=None,
                    autonomy_level=2,
                    risk_class="low",
                    confirmation={},
                    result={"status": "success"},
                )
            )

    t = threading.Thread(target=append_many)
    t.start()
    for i in range(20):
        NightCycle(store).run(now=datetime.now(timezone.utc) + timedelta(seconds=i))
    t.join()

    kept = [json.loads(ln) for ln in store.audit_path.read_text().splitlines()]
    assert sorted(r["run_id"] for r in kept) == sorted(f"r{i}" for i in range(n))
    assert (
        json.loads(store.summaries_path.read_text())[(NOW - timedelta(days=40)).date().isoformat()]["total"]
        == 50
    )
