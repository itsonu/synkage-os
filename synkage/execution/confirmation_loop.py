"""Confirmation loop (docs/autonomy_safety.md): show plan -> show tool target ->
require explicit confirm -> execute -> log.

This module owns the rule (only an explicit "yes" counts). The interface layer
supplies `show` and `ask`, so prompts render however the UI likes. Executing and
logging the result belong to the router (Phase 4); callers act on the return value.
"""

from __future__ import annotations

from collections.abc import Callable

from pydantic import BaseModel

CONFIRM_WORD = "yes"


class ConfirmationResult(BaseModel):
    confirmed: bool
    answer: str | None  # what the user typed; None on EOF / Ctrl-C


def confirm(
    plan: str,
    tool_target: str,
    ask: Callable[[str], str],
    show: Callable[[str], None],
) -> ConfirmationResult:
    show(f"Plan: {plan}")
    show(f"Tool: {tool_target}")
    try:
        answer = ask(f"Type '{CONFIRM_WORD}' to confirm, anything else cancels: ")
    except (EOFError, KeyboardInterrupt):
        return ConfirmationResult(confirmed=False, answer=None)
    return ConfirmationResult(confirmed=answer.strip().lower() == CONFIRM_WORD, answer=answer)
