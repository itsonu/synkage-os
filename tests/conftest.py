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
