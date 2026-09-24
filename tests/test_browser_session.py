"""ac-1: the browser controller launches Chromium via Playwright and opens a URL (local page)."""

from synkage.tools.browser.session import BrowserSession


def test_opens_local_page_over_http(browser_session, mock_server):
    page = browser_session.open(f"{mock_server}/whatsapp/", key="t-http")
    assert page.title() == "WhatsApp (mock)"


def test_opens_file_url(browser_session, tmp_path):
    f = tmp_path / "hello.html"
    f.write_text("<title>hello file</title><p>ok</p>")
    assert browser_session.open(f.as_uri(), key="t-file").title() == "hello file"


def test_pages_are_reused_per_key(browser_session, mock_server):
    a = browser_session.page("t-reuse")
    assert browser_session.page("t-reuse") is a
    assert browser_session.page("t-other") is not a


def test_defaults_come_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("SYNKAGE_BROWSER_PROFILE", str(tmp_path / "profile"))
    monkeypatch.setenv("SYNKAGE_BROWSER_HEADLESS", "1")
    monkeypatch.setenv("SYNKAGE_CHROMIUM_PATH", "/x/chromium")
    s = BrowserSession()
    assert (s.profile_dir, s.headless, s.executable_path) == (tmp_path / "profile", True, "/x/chromium")


def test_default_profile_is_outside_the_repo(monkeypatch):
    monkeypatch.delenv("SYNKAGE_BROWSER_PROFILE", raising=False)
    s = BrowserSession()
    assert str(s.profile_dir).endswith(".synkage/browser-profile")
    assert "synkage-os" not in str(s.profile_dir)


def test_nothing_launches_until_first_page():
    s = BrowserSession(profile_dir="", headless=True)
    assert s._context is None
