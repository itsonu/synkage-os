"""Autonomy router: the single place where a prepared action is allowed to run.

route(request, intent, decision, confirmation)
  1. plan it (tool, adapter, confirmation needed?)       -> action_planner
  2. dry run?          -> report what would happen, never call the adapter
  3. blocked / may not execute / unconfirmed -> refused
  4. nothing to do / tool unavailable        -> skipped / unavailable
  5. adapter.execute(request)
  6. audit every outcome (including refusals and dry runs)
"""

from __future__ import annotations

import json
from pathlib import Path

from synkage.adapters.registry import ADAPTERS
from synkage.adapters.tool_adapter_base import ActionRequest, ExecutionResult, ExecutionStatus, ToolAdapter
from synkage.brain.autonomy_guard import AutonomyDecision
from synkage.brain.intent_resolver import Intent, Mode
from synkage.config import SynkageConfig
from synkage.execution.action_planner import ActionPlanner, ExecutionPlan
from synkage.execution.audit import AuditLog, AuditRecord
from synkage.execution.confirmation_loop import ConfirmationResult


def load_request(draft_artifact: Path) -> ActionRequest:
    """Read the builder's action_draft artifact file into an ActionRequest."""
    data = json.loads(Path(draft_artifact).read_text(encoding="utf-8"))
    if data.get("kind") != "action_draft":
        raise ValueError(f"{draft_artifact} is a '{data.get('kind')}' artifact, not an action_draft")
    return ActionRequest.model_validate(data["body"])


class AutonomyRouter:
    def __init__(
        self,
        config: SynkageConfig,
        audit: AuditLog | None = None,
        adapters: dict[str, type[ToolAdapter]] | None = None,
    ):
        self.config = config
        self.audit = audit or AuditLog()
        self.adapters = ADAPTERS if adapters is None else adapters
        self.planner = ActionPlanner(config)

    def draft(
        self,
        request: ActionRequest,
        intent: Intent,
        decision: AutonomyDecision,
        run_id: str | None = None,
    ) -> ExecutionResult | None:
        """Stage the action before confirmation. None = no draft step for this action."""
        plan = self.planner.plan(request, intent, decision)
        if (
            intent.mode != Mode.execute
            or not decision.may_execute
            or plan.blocked
            or plan.unavailable
            or plan.nothing_to_do
            or plan.categories  # never put flagged content into a real app unconfirmed
            or self.config.autonomy.risk_classes[plan.risk_class].requires_confirmation
        ):
            return None
        adapter_cls = self.adapters.get(plan.adapter or "")
        if adapter_cls is None:
            return None
        adapter = adapter_cls(self.config)
        if not adapter.supports_draft(plan.tool):
            return None
        try:
            result = adapter.draft(request)
        except Exception as e:
            result = ExecutionResult(
                status=ExecutionStatus.failed,
                adapter=plan.adapter,
                tool=plan.tool,
                message=f"{type(e).__name__}: {e}",
            )
        self._audit(plan, intent, decision, None, result, run_id)
        return result

    def route(
        self,
        request: ActionRequest,
        intent: Intent,
        decision: AutonomyDecision,
        confirmation: ConfirmationResult | None = None,
        run_id: str | None = None,
        drafted: bool = False,
    ) -> ExecutionResult:
        plan = self.planner.plan(request, intent, decision)
        result = self._decide(request, intent, decision, confirmation, plan)
        if drafted and result.status == ExecutionStatus.refused:
            adapter_cls = self.adapters.get(plan.adapter or "")
            if adapter_cls is not None:
                adapter_cls(self.config).discard(request)
                result.message += " (draft cleared)"
        self._audit(plan, intent, decision, confirmation, result, run_id)
        return result

    def _audit(self, plan, intent, decision, confirmation, result, run_id) -> None:
        self.audit.append(
            AuditRecord(
                run_id=run_id,
                intent={
                    "raw": intent.raw,
                    "verb": intent.verb,
                    "object": intent.object,
                    "target": intent.target,
                    "mode": intent.mode.value,
                },
                tool=plan.tool,
                adapter=plan.adapter,
                autonomy_level=decision.level,
                risk_class=plan.risk_class,
                categories=plan.categories,
                confirmation={
                    "required": plan.requires_confirmation,
                    "confirmed": confirmation.confirmed if confirmation else None,
                },
                result={"status": result.status.value, "message": result.message},
            )
        )

    def _decide(
        self,
        request: ActionRequest,
        intent: Intent,
        decision: AutonomyDecision,
        confirmation: ConfirmationResult | None,
        plan: ExecutionPlan,
    ) -> ExecutionResult:
        def result(status: ExecutionStatus, message: str, **output) -> ExecutionResult:
            return ExecutionResult(
                status=status, adapter=plan.adapter, tool=plan.tool, message=message, output=output
            )

        if plan.blocked:
            return result(ExecutionStatus.refused, plan.blocked)

        if intent.mode == Mode.dry_run:
            if plan.nothing_to_do:
                would = "nothing to execute"
            elif plan.unavailable:
                would = f"route to {plan.adapter}, but {plan.unavailable}"
            else:
                would = f"run via {plan.adapter}"
            needs = "; needs confirmation" if plan.requires_confirmation else ""
            return result(
                ExecutionStatus.dry_run,
                f"dry run: would {would}{needs}",
                steps=request.steps,
                requires_confirmation=plan.requires_confirmation,
                reasons=plan.reasons,
            )

        if not decision.may_execute:
            return result(
                ExecutionStatus.refused, f"autonomy level {decision.level} does not allow execution"
            )
        if plan.requires_confirmation and not (confirmation and confirmation.confirmed):
            why = "; ".join(plan.reasons) or "confirmation required"
            return result(ExecutionStatus.refused, f"not confirmed ({why})")

        if plan.nothing_to_do:
            return result(ExecutionStatus.skipped, "nothing to execute; the report is the result")
        if plan.unavailable:
            return result(ExecutionStatus.unavailable, plan.unavailable)

        adapter_cls = self.adapters.get(plan.adapter or "")
        if adapter_cls is None:
            return result(ExecutionStatus.failed, f"unknown adapter '{plan.adapter}'")
        try:
            return adapter_cls(self.config).execute(request)
        except Exception as e:  # adapters shouldn't raise, but a bug must not skip the audit
            return result(ExecutionStatus.failed, f"{type(e).__name__}: {e}")
