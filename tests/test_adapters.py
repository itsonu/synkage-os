"""ac-1: tool_adapter_base defines execute() -> ExecutionResult; local_exec and openclaw implement it."""

import pytest

from synkage.adapters import local_exec_adapter
from synkage.adapters.local_exec_adapter import LocalExecAdapter
from synkage.adapters.openclaw_adapter import OpenClawAdapter
from synkage.adapters.registry import ADAPTERS
from synkage.adapters.tool_adapter_base import ActionRequest, ExecutionResult, ExecutionStatus, ToolAdapter
from synkage.brain.prime import Prime
from synkage.config import load_config
from synkage.execution.autonomy_router import load_request
from synkage.tools.base import ControllerResult

CFG = load_config()
REQ = ActionRequest(
    action="send", object="message", target="Raj", tool="whatsapp_web", adapter="local_exec", ready=True
)


def test_registry_maps_config_adapter_names():
    assert ADAPTERS == {"local_exec": LocalExecAdapter, "openclaw": OpenClawAdapter}
    assert {t.adapter for t in CFG.tools.tools} <= set(ADAPTERS)


@pytest.mark.parametrize("cls", [LocalExecAdapter, OpenClawAdapter])
def test_adapters_implement_contract(cls):
    assert issubclass(cls, ToolAdapter)
    result = cls(CFG).execute(REQ)
    assert isinstance(result, ExecutionResult)
    assert result.adapter == cls.name and result.tool == "whatsapp_web"


def test_tool_adapter_is_abstract():
    with pytest.raises(TypeError):
        ToolAdapter(CFG)


def test_local_exec_without_controller_is_unavailable():
    req = REQ.model_copy(update={"tool": "vscode"})
    result = LocalExecAdapter(CFG).execute(req)
    assert result.status == ExecutionStatus.unavailable
    assert "no local controller for 'vscode'" in result.message


class FakeHandler(local_exec_adapter.ToolHandler):
    has_draft = True

    def __init__(self, fail=None):
        self.fail, self.calls = fail, []

    def draft(self, request):
        self.calls.append("draft")
        return ControllerResult(ok=True, message="drafted")

    def execute(self, request):
        self.calls.append("execute")
        if self.fail:
            raise self.fail
        return ControllerResult(ok=True, message=f"sent to {request.target}")

    def discard(self, request):
        self.calls.append("discard")


def test_local_exec_dispatches_to_handler(monkeypatch):
    handler = FakeHandler()
    monkeypatch.setitem(local_exec_adapter.HANDLERS, "whatsapp_web", handler)
    adapter = LocalExecAdapter(CFG)
    assert adapter.supports_draft("whatsapp_web") and not adapter.supports_draft("apple_notes")
    assert adapter.draft(REQ).status == ExecutionStatus.drafted
    result = adapter.execute(REQ)
    assert (result.status, result.message) == (ExecutionStatus.success, "sent to Raj")
    adapter.discard(REQ)
    assert handler.calls == ["draft", "execute", "discard"]


def test_local_exec_handler_crash_is_failed(monkeypatch):
    monkeypatch.setitem(
        local_exec_adapter.HANDLERS, "whatsapp_web", FakeHandler(fail=RuntimeError("browser died"))
    )
    result = LocalExecAdapter(CFG).execute(REQ)
    assert (result.status, result.message) == (ExecutionStatus.failed, "RuntimeError: browser died")


def test_whatsapp_handler_needs_text_before_touching_the_browser():
    result = LocalExecAdapter(CFG).execute(REQ)  # REQ has no content; shared_session would raise
    assert result.status == ExecutionStatus.failed
    assert "no message text" in result.message


def test_openclaw_stub_never_runs():
    result = OpenClawAdapter(CFG).execute(REQ)
    assert result.status == ExecutionStatus.unavailable
    assert "stub" in result.message


@pytest.mark.parametrize(
    "command", ["send message to Raj: hi", "save note buy milk; call mom", "summarize thread"]
)
def test_builder_draft_is_a_valid_action_request(tmp_path, command):
    prime = Prime(CFG, runs_dir=tmp_path)
    delegation = prime.delegate(prime.handle(command))
    request = load_request(delegation.output_of("builder"))  # extra="forbid" catches drift
    assert request.action == command.split()[0]


def test_load_request_rejects_non_draft_artifacts(tmp_path):
    prime = Prime(CFG, runs_dir=tmp_path)
    delegation = prime.delegate(prime.handle("send message to Raj"))
    with pytest.raises(ValueError, match="not an action_draft"):
        load_request(delegation.output_of("planner"))
