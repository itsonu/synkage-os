"""OpenClaw adapter stub. The real integration is optional Phase 8; the spec gives
no API contract yet, so this adapter never calls anything.
"""

from __future__ import annotations

from synkage.adapters.tool_adapter_base import ActionRequest, ExecutionResult, ExecutionStatus, ToolAdapter


class OpenClawAdapter(ToolAdapter):
    name = "openclaw"

    def execute(self, request: ActionRequest) -> ExecutionResult:
        return ExecutionResult(
            status=ExecutionStatus.unavailable,
            adapter=self.name,
            tool=request.tool,
            message="OpenClaw adapter is a stub (integration planned for Phase 8)",
        )
