import shutil
from pathlib import Path

import pytest

REPO_CONFIG = Path(__file__).resolve().parent.parent / "config"


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    """A writable copy of the repo config, for tests that break it on purpose."""
    dst = tmp_path / "config"
    shutil.copytree(REPO_CONFIG, dst)
    return dst


@pytest.fixture(autouse=True)
def runs_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Keep agent artifacts out of the repo's runs/ folder in every test."""
    d = tmp_path / "runs"
    monkeypatch.setenv("SYNKAGE_RUNS_DIR", str(d))
    return d


@pytest.fixture(autouse=True)
def audit_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Keep the audit log out of the repo's logs.jsonl in every test."""
    p = tmp_path / "audit.jsonl"
    monkeypatch.setenv("SYNKAGE_AUDIT_LOG", str(p))
    return p
