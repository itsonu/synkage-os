"""WhatsApp Web controller: fill a draft, and send only what was drafted.

Two ways to open a chat:
  - target is a phone number -> https://web.whatsapp.com/send?phone=<n>&text=<t>
    (WhatsApp's documented click-to-chat link; prefills the draft)
  - target is a name -> type it into the chat search and open the matching chat

SELECTORS ARE UNVERIFIED against live WhatsApp Web, which changes its DOM often.
Tests run against a mock page built to these selectors, so they prove the flow,
not live compatibility. Check them during the first manual run.
"""

from __future__ import annotations

import re
from urllib.parse import quote

from synkage.tools.base import ControllerResult
from synkage.tools.browser.session import BrowserSession

BASE_URL = "https://web.whatsapp.com/"
SELECTORS = {
    "search": '[contenteditable="true"][aria-label*="Search" i]',
    "chat": 'span[title="{name}"]',
    "compose": '[contenteditable="true"][aria-label*="Type a message" i]',
    "send": 'button[aria-label="Send"]',
}
PHONE = re.compile(r"^\+?\d[\d\s\-]{6,}$")
TIMEOUT_MS = 20000  # first load includes the QR/login screen on a fresh profile


class WhatsAppWeb:
    def __init__(self, session: BrowserSession, base_url: str = BASE_URL):
        self.session, self.base_url = session, base_url
        self._drafted: tuple[str, str] | None = None  # (target, text) currently in the compose box

    def draft(self, target: str, text: str) -> ControllerResult:
        try:
            page = self._open_chat(target, text)
            compose = page.locator(SELECTORS["compose"])
            if _text(compose) != text:  # name path, or the link didn't prefill
                compose.fill(text)
            if _text(compose) != text:
                return ControllerResult(
                    ok=False, message="could not put the text into the WhatsApp compose box"
                )
        except Exception as e:
            return ControllerResult(ok=False, message=f"WhatsApp draft failed: {type(e).__name__}: {e}")
        self._drafted = (target, text)
        return ControllerResult(ok=True, message=f"draft ready in WhatsApp for {target} (not sent)")

    def send(self, target: str, text: str) -> ControllerResult:
        """Send exactly `text` to `target`. Drafts first if needed; refuses if the box holds anything else."""
        if self._drafted != (target, text):
            drafted = self.draft(target, text)
            if not drafted.ok:
                return drafted
        page = self.session.page("whatsapp")
        compose = page.locator(SELECTORS["compose"])
        current = _text(compose)
        if current != text:
            return ControllerResult(
                ok=False,
                message="compose box changed since the draft; not sending",
                output={"found": current},
            )
        try:
            page.locator(SELECTORS["send"]).click(timeout=TIMEOUT_MS)
            page.wait_for_function(
                "sel => (document.querySelector(sel)?.innerText || '').trim() === ''",
                arg=SELECTORS["compose"],
                timeout=TIMEOUT_MS,
            )
        except Exception as e:
            return ControllerResult(ok=False, message=f"WhatsApp send failed: {type(e).__name__}: {e}")
        self._drafted = None
        return ControllerResult(ok=True, message=f"sent to {target} on WhatsApp")

    def clear(self) -> None:
        """Empty the compose box (used when the user declines a draft)."""
        page = self.session.page("whatsapp")
        page.locator(SELECTORS["compose"]).fill("", timeout=5000)
        self._drafted = None

    def _open_chat(self, target: str, text: str):
        if PHONE.match(target):
            digits = re.sub(r"\D", "", target)
            page = self.session.open(f"{self.base_url}send?phone={digits}&text={quote(text)}", key="whatsapp")
            page.locator(SELECTORS["compose"]).wait_for(timeout=TIMEOUT_MS)
            return page
        page = self.session.page("whatsapp")
        if not page.url.startswith(self.base_url):
            page.goto(self.base_url, timeout=TIMEOUT_MS)
        search = page.locator(SELECTORS["search"])
        search.wait_for(timeout=TIMEOUT_MS)
        search.fill(target)
        chat = page.locator(SELECTORS["chat"].format(name=target.replace('"', '\\"')))
        chat.first.wait_for(timeout=TIMEOUT_MS)
        if chat.count() > 1:  # two contacts with the same name: never guess the recipient
            raise LookupError(f"{chat.count()} chats named '{target}'; use a phone number")
        chat.click(timeout=TIMEOUT_MS)
        page.locator(SELECTORS["compose"]).wait_for(timeout=TIMEOUT_MS)
        return page


def _text(locator) -> str:
    return locator.inner_text().strip()
