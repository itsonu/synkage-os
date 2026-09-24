"""ac-3 (automated part): Gmail creates a draft on a mock page and never sends."""

import pytest

from synkage.adapters.local_exec_adapter import GmailHandler
from synkage.adapters.tool_adapter_base import ActionRequest
from synkage.tools.browser import gmail as gmail_module
from synkage.tools.browser.gmail import Gmail


@pytest.fixture
def gmail(browser_session, mock_server, monkeypatch):
    monkeypatch.setattr(gmail_module, "TIMEOUT_MS", 2000)
    return Gmail(browser_session, base_url=f"{mock_server}/mail/")


def test_draft_prefills_and_waits_for_saved(gmail):
    r = gmail.draft("raj@example.com", "Downtime", "Back online at 6.")
    assert r.ok, r.message
    assert "not sent" in r.message
    page = gmail.session.page("gmail")
    assert page.input_value("#to") == "raj@example.com"
    assert page.input_value("#subject") == "Downtime"
    assert page.locator("#body").inner_text() == "Back online at 6."


def test_non_email_target_fails_before_opening_browser(browser_session):
    r = Gmail(browser_session, base_url="http://127.0.0.1:9/never/").draft("Raj", "s", "b")
    assert not r.ok and "needs an email address" in r.message


def test_no_saved_indicator_is_a_failure(browser_session, mock_server, monkeypatch):
    monkeypatch.setattr(gmail_module, "TIMEOUT_MS", 1000)
    r = Gmail(browser_session, base_url=f"{mock_server}/mail-broken/").draft("raj@example.com", "s", "b")
    assert not r.ok and "Gmail draft failed" in r.message


def test_handler_execute_also_only_drafts(gmail):
    handler = GmailHandler(gmail)
    req = ActionRequest(
        action="send", object="email", target="raj@example.com", content="hi", tool="gmail", ready=True
    )
    assert handler.execute(req).message.endswith("(not sent; send it from Gmail)")


def test_handler_rejects_reply_for_now(gmail):
    req = ActionRequest(action="reply", object="email", target="last thread", tool="gmail", ready=True)
    r = GmailHandler(gmail).draft(req)
    assert not r.ok and "isn't supported yet" in r.message
