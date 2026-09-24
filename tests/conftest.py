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


@pytest.fixture(autouse=True)
def no_real_browser(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests must never reach live WhatsApp/Gmail. Mock-page tests pass their own session."""
    from synkage.adapters import local_exec_adapter

    def refuse():
        raise RuntimeError("real browser session requested in a test")

    monkeypatch.setattr(local_exec_adapter, "shared_session", refuse)


def _chromium_path() -> str | None:
    """Playwright's own browser if installed; else the container's fallback binary."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            if Path(p.chromium.executable_path).exists():
                return None
    except Exception:
        return None
    fallback = Path("/opt/pw-browsers/chromium")
    return str(fallback) if fallback.exists() else None


@pytest.fixture(scope="session")
def mock_server():
    from browser_helpers import start_server

    server, url = start_server()
    yield url
    server.shutdown()


@pytest.fixture(scope="session")
def browser_session():
    """One headless Chromium for all mock-page tests, with a throwaway profile."""
    from synkage.tools.browser.session import BrowserSession

    session = BrowserSession(profile_dir="", headless=True, executable_path=_chromium_path())
    try:
        session.page("probe")
    except Exception as e:  # no browser installed locally: run `playwright install chromium`
        pytest.skip(f"Chromium not available: {e}")
    yield session
    session.close()
