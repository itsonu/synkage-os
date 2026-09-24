"""ac-2 (adapter from registry), ac-3 (refusals), ac-4 (audit), ac-5 (dry run)."""

import pytest
from routing_helpers import FakeAdapter, prepared, setup

from synkage.adapters.tool_adapter_base import ExecutionStatus
from synkage.execution.confirmation_loop import ConfirmationResult

YES = ConfirmationResult(confirmed=True, answer="yes")
NO = ConfirmationResult(confirmed=False, answer="no")


# --- ac-2: adapter comes from the tool's registry entry ------------------------------


def test_router_uses_registry_adapter(tmp_path):
    cfg, prime, router, _ = setup(tmp_path)
    result, request, _ = prepared(prime, "send message to Raj: hi")
    out = router.route(request, result.intent, result.decision, YES)
    assert out.status == ExecutionStatus.success
    assert [r.target for r in FakeAdapter.calls] == ["Raj"]


def test_registry_beats_adapter_named_in_draft(tmp_path):
    cfg, prime, router, _ = setup(tmp_path)
    result, request, _ = prepared(prime, "send message to Raj: hi")
    request.adapter = "openclaw"  # stale or tampered draft
    router.route(request, result.intent, result.decision, YES)
    assert len(FakeAdapter.calls) == 1
    plan = router.planner.plan(request, result.intent, result.decision)
    assert any("registry says 'fake'" in r for r in plan.reasons)


def test_unknown_adapter_fails(tmp_path):
    cfg, prime, router, _ = setup(tmp_path, adapter="nowhere")
    result, request, _ = prepared(prime, "send message to Raj: hi")
    out = router.route(request, result.intent, result.decision, YES)
    assert (out.status, out.message) == (ExecutionStatus.failed, "unknown adapter 'nowhere'")


def test_disabled_tool_is_unavailable_and_adapter_not_called(tmp_path):
    cfg, prime, router, _ = setup(tmp_path, enable=())
    result, request, _ = prepared(prime, "send message to Raj: hi")
    out = router.route(request, result.intent, result.decision, YES)
    assert out.status == ExecutionStatus.unavailable
    assert "disabled" in out.message and FakeAdapter.calls == []


# --- ac-3: refusals ----------------------------------------------------------------


@pytest.mark.parametrize("risk", ["high", "critical"])
@pytest.mark.parametrize("confirmation", [None, NO])
def test_unconfirmed_high_or_critical_is_refused(tmp_path, risk, confirmation):
    cfg, prime, router, _ = setup(tmp_path, risk=risk)
    result, request, _ = prepared(prime, "send message to Raj: hi")
    out = router.route(request, result.intent, result.decision, confirmation)
    assert out.status == ExecutionStatus.refused
    assert f"risk class '{risk}'" in out.message
    assert FakeAdapter.calls == []


@pytest.mark.parametrize("risk", ["high", "critical"])
def test_confirmed_high_or_critical_runs(tmp_path, risk):
    cfg, prime, router, _ = setup(tmp_path, risk=risk)
    result, request, _ = prepared(prime, "send message to Raj: hi")
    assert router.route(request, result.intent, result.decision, YES).status == ExecutionStatus.success


def test_never_autonomous_refused_even_with_tampered_decision(tmp_path):
    cfg, prime, router, _ = setup(tmp_path)
    result, request, _ = prepared(prime, "send message to Raj: my password is hunter2 auto execute")
    d = result.decision
    # pretend an upstream bug cleared the safety flags
    d.level, d.may_execute, d.requires_confirmation, d.categories = 3, True, False, []
    request.requires_confirmation = False
    out = router.route(request, result.intent, d, None)
    assert out.status == ExecutionStatus.refused
    assert "password_handling" in out.message
    assert FakeAdapter.calls == []


def test_level_3_low_risk_runs_without_confirmation(tmp_path):
    cfg, prime, router, _ = setup(tmp_path)
    result, request, _ = prepared(prime, "send message to Raj auto execute: hi")
    assert result.decision.requires_confirmation is False
    assert router.route(request, result.intent, result.decision, None).status == ExecutionStatus.success


def test_default_level_2_needs_confirmation(tmp_path):
    cfg, prime, router, _ = setup(tmp_path)
    result, request, _ = prepared(prime, "send message to Raj: hi")
    assert router.route(request, result.intent, result.decision, None).status == ExecutionStatus.refused


def test_not_ready_draft_is_refused(tmp_path):
    cfg, prime, router, _ = setup(tmp_path)
    result, request, _ = prepared(prime, "send message to Raj: hi")
    request.ready, request.missing = False, ["no tool"]
    out = router.route(request, result.intent, result.decision, YES)
    assert (out.status, out.message) == (ExecutionStatus.refused, "not ready: no tool")


def test_level_below_2_is_refused(tmp_path):
    cfg, prime, router, _ = setup(tmp_path)
    result, request, _ = prepared(prime, "send message to Raj: hi")
    result.decision.level, result.decision.may_execute = 1, False
    out = router.route(request, result.intent, result.decision, YES)
    assert out.status == ExecutionStatus.refused and FakeAdapter.calls == []


def test_skill_only_verb_is_skipped(tmp_path):
    cfg, prime, router, _ = setup(tmp_path)
    result, request, _ = prepared(prime, "summarize this thread")
    out = router.route(request, result.intent, result.decision, YES)
    assert out.status == ExecutionStatus.skipped


def test_adapter_exception_is_failed_and_audited(tmp_path, monkeypatch):
    cfg, prime, router, audit = setup(tmp_path)

    def boom(self, request):
        raise RuntimeError("adapter bug")

    monkeypatch.setattr(FakeAdapter, "execute", boom)
    result, request, _ = prepared(prime, "send message to Raj: hi")
    out = router.route(request, result.intent, result.decision, YES)
    assert (out.status, out.message) == (ExecutionStatus.failed, "RuntimeError: adapter bug")
    assert audit.read()[-1].result["status"] == "failed"


# --- ac-4: audit ---------------------------------------------------------------------


def test_every_routed_action_is_audited(tmp_path):
    cfg, prime, router, audit = setup(tmp_path)
    cmds = [
        ("send message to Raj: hi", YES),
        ("send message to Raj: hi", NO),
        ("send message to Raj dry run", None),
    ]
    for cmd, confirmation in cmds:
        result, request, run_id = prepared(prime, cmd)
        router.route(request, result.intent, result.decision, confirmation, run_id=run_id)
    records = audit.read()
    assert [r.result["status"] for r in records] == ["success", "refused", "dry_run"]
    first = records[0]
    assert first.intent["raw"] == "send message to Raj: hi" and first.intent["target"] == "Raj"
    assert (first.tool, first.adapter, first.autonomy_level, first.risk_class) == (
        "whatsapp_web",
        "fake",
        2,
        "medium",
    )
    assert first.confirmation == {"required": True, "confirmed": True}
    assert first.run_id
    assert records[1].confirmation == {"required": True, "confirmed": False}
    assert records[2].confirmation["confirmed"] is None


def test_audit_records_router_derived_categories(tmp_path):
    cfg, prime, router, audit = setup(tmp_path)
    result, request, _ = prepared(prime, "send message to Raj: my password is x")
    result.decision.categories = []  # the router re-derives them
    router.route(request, result.intent, result.decision, NO)
    assert audit.read()[-1].categories == ["password_handling"]


def test_audit_is_append_only_jsonl(tmp_path):
    cfg, prime, router, audit = setup(tmp_path)
    for _ in range(3):
        result, request, _ = prepared(prime, "send message to Raj: hi")
        router.route(request, result.intent, result.decision, YES)
    assert len(audit.path.read_text().splitlines()) == 3


# --- ac-5: dry run -------------------------------------------------------------------


def test_dry_run_never_calls_adapter(tmp_path):
    cfg, prime, router, _ = setup(tmp_path)
    result, request, _ = prepared(prime, "send message to Raj dry run: hi")
    out = router.route(request, result.intent, result.decision, YES)
    assert out.status == ExecutionStatus.dry_run
    assert FakeAdapter.calls == []
    assert out.message == "dry run: would run via fake; needs confirmation"
    assert out.output["steps"][:2] == ["Open WhatsApp Web", "Find Raj"]


def test_dry_run_reports_unavailable_tool(tmp_path):
    cfg, prime, router, _ = setup(tmp_path, enable=())
    result, request, _ = prepared(prime, "send message to Raj dry run")
    out = router.route(request, result.intent, result.decision)
    assert out.status == ExecutionStatus.dry_run and "disabled" in out.message
