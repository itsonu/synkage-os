"""ac-2 (automated part): WhatsApp draft flow on a mock page. Nothing is sent without 'yes'."""

import pytest
from routing_helpers import prepared

from synkage.adapters import local_exec_adapter
from synkage.adapters.local_exec_adapter import WhatsAppHandler
from synkage.adapters.tool_adapter_base import ExecutionStatus
from synkage.brain.prime import Prime
from synkage.config import load_config
from synkage.execution.audit import AuditLog
from synkage.execution.autonomy_router import AutonomyRouter
from synkage.execution.confirmation_loop import ConfirmationResult
from synkage.tools.browser import whatsapp as wa_module
from synkage.tools.browser.whatsapp import SELECTORS, WhatsAppWeb


@pytest.fixture
def wa(browser_session, mock_server, monkeypatch):
    monkeypatch.setattr(wa_module, "TIMEOUT_MS", 2000)
    browser_session.page("whatsapp").goto("about:blank")  # fresh mock state per test
    return WhatsAppWeb(browser_session, base_url=f"{mock_server}/whatsapp/")


def sent(wa):
    return wa.session.page("whatsapp").locator("#sent li").all_inner_texts()


def compose(wa):
    box = wa.session.page("whatsapp").locator(SELECTORS["compose"])
    return box.inner_text().strip() if box.count() else ""  # no chat open = nothing drafted


def test_draft_by_name_fills_but_does_not_send(wa):
    r = wa.draft("Raj", "running late")
    assert r.ok, r.message
    assert compose(wa) == "running late"
    assert sent(wa) == []


def test_draft_by_phone_uses_click_to_chat_link(wa):
    r = wa.draft("+91 98765 43210", "hello there")
    assert r.ok, r.message
    assert compose(wa) == "hello there"
    assert "send?phone=919876543210" in wa.session.page("whatsapp").url
    assert sent(wa) == []


def test_send_after_draft_sends_exactly_the_text(wa):
    wa.draft("Raj", "on my way")
    r = wa.send("Raj", "on my way")
    assert r.ok, r.message
    assert sent(wa) == ["Raj: on my way"]
    assert compose(wa) == ""


def test_send_refuses_if_compose_changed_after_draft(wa):
    wa.draft("Raj", "on my way")
    wa.session.page("whatsapp").locator(SELECTORS["compose"]).fill("something else")
    r = wa.send("Raj", "on my way")
    assert not r.ok and "changed since the draft" in r.message
    assert sent(wa) == []


def test_clear_empties_the_draft(wa):
    wa.draft("Raj", "never mind")
    wa.clear()
    assert compose(wa) == ""


def test_unknown_contact_fails_cleanly(wa):
    r = wa.draft("Nobody Known", "hi")
    assert not r.ok and "WhatsApp draft failed" in r.message


# --- through the real router ---------------------------------------------------------


@pytest.fixture
def pipeline(wa, tmp_path, monkeypatch):
    cfg = load_config()
    cfg.tools.get("whatsapp_web").enabled = True
    monkeypatch.setitem(local_exec_adapter.HANDLERS, "whatsapp_web", WhatsAppHandler(wa))
    router = AutonomyRouter(cfg, audit=AuditLog(tmp_path / "audit.jsonl"))
    return Prime(cfg, runs_dir=tmp_path / "runs"), router


def test_router_drafts_then_no_clears_draft_and_sends_nothing(pipeline, wa):
    prime, router = pipeline
    result, request, run_id = prepared(prime, "send message to Raj: see you at 6")
    staged = router.draft(request, result.intent, result.decision, run_id)
    assert staged.status == ExecutionStatus.drafted
    assert compose(wa) == "see you at 6"
    out = router.route(
        request,
        result.intent,
        result.decision,
        ConfirmationResult(confirmed=False, answer="no"),
        run_id,
        drafted=True,
    )
    assert out.status == ExecutionStatus.refused and "(draft cleared)" in out.message
    assert compose(wa) == "" and sent(wa) == []
    assert [r.result["status"] for r in router.audit.read()] == ["drafted", "refused"]


def test_router_sends_only_after_yes(pipeline, wa):
    prime, router = pipeline
    result, request, run_id = prepared(prime, "send message to Raj: see you at 6")
    router.draft(request, result.intent, result.decision, run_id)
    out = router.route(
        request,
        result.intent,
        result.decision,
        ConfirmationResult(confirmed=True, answer="yes"),
        run_id,
        drafted=True,
    )
    assert out.status == ExecutionStatus.success
    assert sent(wa) == ["Raj: see you at 6"]


def test_router_never_drafts_flagged_content(pipeline, wa):
    prime, router = pipeline
    result, request, run_id = prepared(prime, "send message to Raj: my password is hunter2")
    assert router.draft(request, result.intent, result.decision, run_id) is None
    assert compose(wa) == ""


def test_dry_run_touches_nothing(pipeline, wa):
    prime, router = pipeline
    result, request, run_id = prepared(prime, "send message to Raj dry run: hi")
    assert router.draft(request, result.intent, result.decision, run_id) is None
    out = router.route(request, result.intent, result.decision, None, run_id)
    assert out.status == ExecutionStatus.dry_run
    assert compose(wa) == "" and sent(wa) == []


# --- through the CLI (what a user sees) ------------------------------------------------


@pytest.fixture
def cli_with_mock_whatsapp(wa, config_dir, monkeypatch):
    import json

    reg = config_dir / "tool_registry.json"
    data = json.loads(reg.read_text())
    next(t for t in data["tools"] if t["id"] == "whatsapp_web")["enabled"] = True
    reg.write_text(json.dumps(data))
    monkeypatch.setitem(local_exec_adapter.HANDLERS, "whatsapp_web", WhatsAppHandler(wa))
    return config_dir


def test_cli_drafts_then_stops_at_prompt_and_no_sends_nothing(cli_with_mock_whatsapp, wa):
    from typer.testing import CliRunner

    from synkage.interfaces.cli import app

    out = (
        CliRunner()
        .invoke(
            app, ["--config-dir", str(cli_with_mock_whatsapp), "run", "send message to Raj: hi"], input="no\n"
        )
        .output
    )
    assert out.index("Execution: drafted") < out.index("Type 'yes'") < out.index("Execution: refused")
    assert "(draft cleared)" in out
    assert sent(wa) == []


def test_cli_yes_sends(cli_with_mock_whatsapp, wa):
    from typer.testing import CliRunner

    from synkage.interfaces.cli import app

    out = (
        CliRunner()
        .invoke(
            app,
            ["--config-dir", str(cli_with_mock_whatsapp), "run", "send message to Raj: hi"],
            input="yes\n",
        )
        .output
    )
    assert "Execution: success" in out
    assert sent(wa) == ["Raj: hi"]


def test_duplicate_contact_names_are_refused(wa):
    r = wa.draft("Priya", "hi")
    assert not r.ok and "2 chats named 'Priya'" in r.message
    assert compose(wa) == ""
