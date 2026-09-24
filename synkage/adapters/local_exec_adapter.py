"""Local execution adapter: translates an ActionRequest into calls on the tool
controllers in synkage/tools/ and normalizes their results.

    HANDLERS[tool_id].draft(request)    stage it (fill the message); nothing sent
    HANDLERS[tool_id].execute(request)  commit it (send / save)
    HANDLERS[tool_id].discard(request)  clear a declined draft

One browser session is shared by all browser tools and opened on first use, so
importing this module never launches anything.
"""

from __future__ import annotations

from synkage.adapters.tool_adapter_base import ActionRequest, ExecutionResult, ExecutionStatus, ToolAdapter
from synkage.tools.base import ControllerResult
from synkage.tools.browser.gmail import Gmail
from synkage.tools.browser.session import BrowserSession
from synkage.tools.browser.whatsapp import WhatsAppWeb
from synkage.tools.desktop.apple_notes import AppleNotes

_session: BrowserSession | None = None


def shared_session() -> BrowserSession:
    global _session
    if _session is None:
        _session = BrowserSession()
    return _session


LOGIN_PAGES = {"whatsapp": "https://web.whatsapp.com/", "gmail": "https://mail.google.com/"}


def open_login_pages(which: list[str]) -> BrowserSession:
    """Open the Synkage browser profile at the given services so the user can sign in.
    Setup only: nothing is typed or clicked on the user's behalf."""
    session = shared_session()
    for name in which:
        session.open(LOGIN_PAGES[name], key=name, timeout_ms=60000)
    return session


class ToolHandler:
    has_draft = False

    def draft(self, request: ActionRequest) -> ControllerResult:
        raise NotImplementedError

    def execute(self, request: ActionRequest) -> ControllerResult:
        raise NotImplementedError

    def discard(self, request: ActionRequest) -> None:
        pass


class WhatsAppHandler(ToolHandler):
    has_draft = True

    def __init__(self, controller: WhatsAppWeb | None = None):
        self._controller = controller

    @property
    def controller(self) -> WhatsAppWeb:
        if self._controller is None:
            self._controller = WhatsAppWeb(shared_session())
        return self._controller

    def _check(self, request: ActionRequest) -> ControllerResult | None:
        if not request.target:
            return ControllerResult(ok=False, message="no recipient")
        if not request.content:
            return ControllerResult(ok=False, message="no message text (add ': <text>' to the command)")
        return None

    def draft(self, request):
        return self._check(request) or self.controller.draft(request.target, request.content)

    def execute(self, request):
        return self._check(request) or self.controller.send(request.target, request.content)

    def discard(self, request):
        self.controller.clear()


class GmailHandler(ToolHandler):
    """Drafts only. `execute` also just saves a draft: Synkage never sends email."""

    has_draft = True

    def __init__(self, controller: Gmail | None = None):
        self._controller = controller

    @property
    def controller(self) -> Gmail:
        if self._controller is None:
            self._controller = Gmail(shared_session())
        return self._controller

    def draft(self, request):
        if request.action != "send":
            return ControllerResult(
                ok=False, message=f"Gmail '{request.action}' isn't supported yet (only new drafts)"
            )
        if not request.target:
            return ControllerResult(ok=False, message="no recipient")
        return self.controller.draft(
            request.target, subject=request.details or "", body=request.content or ""
        )

    execute = draft


class AppleNotesHandler(ToolHandler):
    def __init__(self, controller: AppleNotes | None = None):
        self.controller = controller or AppleNotes()

    def execute(self, request):
        if request.note:
            title, markdown = request.note["title"], request.note["markdown"]
        else:
            text = request.content or request.details or ""
            if not text.strip():
                return ControllerResult(ok=False, message="nothing to put in the note")
            title, markdown = text.strip().split("\n")[0][:60], text
        return self.controller.save(title, markdown)


HANDLERS: dict[str, ToolHandler] = {
    "whatsapp_web": WhatsAppHandler(),
    "gmail": GmailHandler(),
    "apple_notes": AppleNotesHandler(),
}


class LocalExecAdapter(ToolAdapter):
    name = "local_exec"

    def supports_draft(self, tool: str | None) -> bool:
        handler = HANDLERS.get(tool or "")
        return bool(handler and handler.has_draft)

    def draft(self, request: ActionRequest) -> ExecutionResult:
        return self._call(request, "draft", ExecutionStatus.drafted)

    def execute(self, request: ActionRequest) -> ExecutionResult:
        return self._call(request, "execute", ExecutionStatus.success)

    def discard(self, request: ActionRequest) -> None:
        handler = HANDLERS.get(request.tool or "")
        if handler is not None:
            try:
                handler.discard(request)
            except Exception:  # best effort; the refusal is already decided and audited
                pass

    def _call(self, request: ActionRequest, step: str, ok_status: ExecutionStatus) -> ExecutionResult:
        handler = HANDLERS.get(request.tool or "")
        if handler is None:
            return self._result(
                ExecutionStatus.unavailable, request, f"no local controller for '{request.tool}'"
            )
        try:
            outcome = getattr(handler, step)(request)
        except Exception as e:  # a controller bug is a failed execution, not a crash
            return self._result(ExecutionStatus.failed, request, f"{type(e).__name__}: {e}")
        status = ok_status if outcome.ok else ExecutionStatus.failed
        return self._result(status, request, outcome.message, outcome.output)

    def _result(self, status, request, message, output=None) -> ExecutionResult:
        return ExecutionResult(
            status=status, adapter=self.name, tool=request.tool, message=message, output=output or {}
        )
