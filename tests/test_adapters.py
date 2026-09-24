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
    result = LocalExecAdapter(CFG).execute(REQ)
    assert result.status == ExecutionStatus.unavailable
    assert "Phase 5" in result.message


def test_local_exec_dispatches_to_controller(monkeypatch):
    def controller(req):
        return ExecutionResult(status=ExecutionStatus.success, tool=req.tool, message=f"sent to {req.target}")

    monkeypatch.setitem(local_exec_adapter.CONTROLLERS, "whatsapp_web", controller)
    result = LocalExecAdapter(CFG).execute(REQ)
    assert (result.status, result.message) == (ExecutionStatus.success, "sent to Raj")


def test_local_exec_controller_crash_is_failed(monkeypatch):
    def controller(req):
        raise RuntimeError("browser died")

    monkeypatch.setitem(local_exec_adapter.CONTROLLERS, "whatsapp_web", controller)
    result = LocalExecAdapter(CFG).execute(REQ)
    assert (result.status, result.message) == (ExecutionStatus.failed, "RuntimeError: browser died")


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
