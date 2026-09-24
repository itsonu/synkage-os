from pathlib import Path

from synkage.adapters.tool_adapter_base import ActionRequest, ExecutionResult, ExecutionStatus, ToolAdapter
from synkage.brain.prime import Prime
from synkage.config import load_config
from synkage.execution.audit import AuditLog
from synkage.execution.autonomy_router import AutonomyRouter, load_request


class FakeAdapter(ToolAdapter):
    """Records every request it receives; always succeeds."""

    name = "fake"
    calls: list[ActionRequest] = []

    def execute(self, request):
        FakeAdapter.calls.append(request)
        return ExecutionResult(
            status=ExecutionStatus.success, adapter=self.name, tool=request.tool, message="done"
        )


def setup(tmp_path: Path, enable=("whatsapp_web", "gmail"), adapter="fake", risk=None):
    """Config with some tools enabled and pointed at FakeAdapter; router with a temp audit log."""
    FakeAdapter.calls = []
    cfg = load_config()
    for tool_id in enable:
        tool = cfg.tools.get(tool_id)
        tool.enabled = True
        tool.adapter = adapter
        if risk:
            tool.risk_class = risk
    audit = AuditLog(tmp_path / "audit.jsonl")
    router = AutonomyRouter(cfg, audit=audit, adapters={"fake": FakeAdapter})
    return cfg, Prime(cfg, runs_dir=tmp_path / "runs"), router, audit


def prepared(prime: Prime, command: str):
    """handle + delegate; returns (PrimeResult, ActionRequest, run_id)."""
    result = prime.handle(command)
    delegation = prime.delegate(result)
    return result, load_request(delegation.output_of("builder")), delegation.run_id
