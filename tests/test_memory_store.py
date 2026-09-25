"""ac-1: memory files are created on first run at the chosen location and survive restart."""

import stat

from typer.testing import CliRunner

from synkage.config import REPO_ROOT, load_config, resolve_audit_log, resolve_memory_dir
from synkage.interfaces.cli import app
from synkage.memory.store import MemoryStore

CFG = load_config()


def test_first_run_creates_dir_and_files(memory_dir):
    store = MemoryStore(CFG)
    created = store.ensure()
    assert created == [memory_dir, store.profile_path, store.relationship_path]
    assert stat.S_IMODE(memory_dir.stat().st_mode) == 0o700  # holds message text: owner only
    assert store.load_relationship().trust == CFG.memory.trust.neutral


def test_second_run_creates_nothing_and_never_overwrites(memory_dir):
    store = MemoryStore(CFG)
    store.ensure()
    rel = store.load_relationship()
    rel.trust = 0.8
    store.save_relationship(rel)
    assert store.ensure() == []
    assert store.load_relationship().trust == 0.8


def test_state_survives_restart():
    first = MemoryStore(CFG)
    profile = first.load_profile()
    profile.name = "Chandra"
    first.save_profile(profile)
    rel = first.load_relationship()
    rel.trust = 0.61
    first.save_relationship(rel)
    restarted = MemoryStore(load_config())  # fresh objects, same location
    assert restarted.load_profile().name == "Chandra"
    assert restarted.load_relationship().trust == 0.61


def test_cli_first_run_creates_memory(memory_dir):
    assert not memory_dir.exists()
    result = CliRunner().invoke(app, ["status"])
    assert result.exit_code == 0, result.output
    assert (memory_dir / "user_profile.json").is_file()
    assert (memory_dir / "relationship_state.json").is_file()
    assert f"Memory:   {memory_dir}" in result.output and "trust 0.50" in result.output


def test_default_location_is_outside_the_repo(monkeypatch):
    monkeypatch.delenv("SYNKAGE_MEMORY_DIR")
    monkeypatch.delenv("SYNKAGE_AUDIT_LOG")
    d = resolve_memory_dir()
    assert str(d).endswith(".synkage/memory")
    assert REPO_ROOT not in d.parents
    assert resolve_audit_log() == d / "logs.jsonl"  # the audit log is part of memory now


def test_history_is_bounded():
    store = MemoryStore(CFG)
    rel = store.load_relationship()
    from datetime import datetime, timezone

    from synkage.memory.store import HISTORY_KEEP, TrustPoint

    rel.history = [TrustPoint(at=datetime.now(timezone.utc), trust=0.5)] * (HISTORY_KEEP + 10)
    store.save_relationship(rel)
    assert len(store.load_relationship().history) == HISTORY_KEEP
