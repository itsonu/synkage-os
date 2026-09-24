"""Gmail controller: create a draft. It never sends; sending is left to the user in Gmail.

Opens Gmail's compose link (to / subject / body prefilled) and waits until Gmail
reports the draft saved.

SELECTORS ARE UNVERIFIED against live Gmail. Tests use a mock page built to
them; check during the first manual run.
"""

from __future__ import annotations

import re
from urllib.parse import urlencode

from synkage.tools.base import ControllerResult
from synkage.tools.browser.session import BrowserSession

BASE_URL = "https://mail.google.com/mail/"
SELECTORS = {"saved": "text=/Draft saved/i"}
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TIMEOUT_MS = 20000


class Gmail:
    def __init__(self, session: BrowserSession, base_url: str = BASE_URL):
        self.session, self.base_url = session, base_url

    def draft(self, to: str, subject: str, body: str) -> ControllerResult:
        if not EMAIL.match(to):
            return ControllerResult(
                ok=False, message=f"Gmail needs an email address as the target, got '{to}'"
            )
        query = urlencode({"view": "cm", "fs": "1", "to": to, "su": subject, "body": body})
        try:
            page = self.session.open(f"{self.base_url}?{query}", key="gmail")
            page.locator(SELECTORS["saved"]).first.wait_for(timeout=TIMEOUT_MS)
        except Exception as e:
            return ControllerResult(ok=False, message=f"Gmail draft failed: {type(e).__name__}: {e}")
        return ControllerResult(
            ok=True, message=f"draft saved in Gmail to {to} (not sent; send it from Gmail)"
        )
