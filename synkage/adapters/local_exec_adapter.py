"""Local execution adapter: runs actions through per-tool controllers in synkage/tools/.

Phase 4 ships no controllers (real browser/desktop control is Phase 5), so every
request comes back `unavailable`. Phase 5 registers controllers in CONTROLLERS.
"""

from __future__ import annotations

from collections.abc import Callable

from synkage.adapters.tool_adapter_base import ActionRequest, ExecutionResult, ExecutionStatus, ToolAdapter

# tool id -> controller(request) -> ExecutionResult
Controller = Callable[[ActionRequest], ExecutionResult]
CONTROLLERS: dict[str, Controller] = {}


class LocalExecAdapter(ToolAdapter):
    name = "local_exec"

    def execute(self, request: ActionRequest) -> ExecutionResult:
        controller = CONTROLLERS.get(request.tool or "")
        if controller is None:
            return ExecutionResult(
                status=ExecutionStatus.unavailable,
                adapter=self.name,
                tool=request.tool,
                message=f"no local controller for '{request.tool}' yet (tool control arrives in Phase 5)",
            )
        try:
            return controller(request)
        except Exception as e:  # a controller bug is a failed execution, not a crash
            return ExecutionResult(
                status=ExecutionStatus.failed,
                adapter=self.name,
                tool=request.tool,
                message=f"{type(e).__name__}: {e}",
            )
