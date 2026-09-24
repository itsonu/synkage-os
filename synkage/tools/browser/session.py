"""One Playwright Chromium session per process, opened on first use.

With a profile dir the context is persistent, so a login done once (by the user,
in the visible window) survives restarts. The profile holds session cookies:
it lives outside the repo (default ~/.synkage/browser-profile) and must never be
committed.

Env:
  SYNKAGE_BROWSER_PROFILE   profile dir ("" = throwaway context, used by tests)
  SYNKAGE_BROWSER_HEADLESS  "1" = no window (tests); default shows the window
  SYNKAGE_CHROMIUM_PATH     explicit Chromium binary (only when `playwright
                            install` can't provide the matching build)
"""

from __future__ import annotations

import atexit
import os
from pathlib import Path

from playwright.sync_api import BrowserContext, Page, Playwright, sync_playwright

DEFAULT_PROFILE = Path.home() / ".synkage" / "browser-profile"


class BrowserSession:
    def __init__(
        self,
        profile_dir: str | Path | None = None,
        headless: bool | None = None,
        executable_path: str | None = None,
    ):
        env_profile = os.environ.get("SYNKAGE_BROWSER_PROFILE")
        if profile_dir is None:
            profile_dir = DEFAULT_PROFILE if env_profile is None else (env_profile or None)
        self.profile_dir = Path(profile_dir).expanduser() if profile_dir else None
        self.headless = os.environ.get("SYNKAGE_BROWSER_HEADLESS") == "1" if headless is None else headless
        self.executable_path = executable_path or os.environ.get("SYNKAGE_CHROMIUM_PATH") or None
        self._pw: Playwright | None = None
        self._context: BrowserContext | None = None
        self._pages: dict[str, Page] = {}

    def page(self, key: str) -> Page:
        """A tab per controller (e.g. "whatsapp"), reused across calls."""
        if key not in self._pages or self._pages[key].is_closed():
            self._pages[key] = self._ensure_context().new_page()
        return self._pages[key]

    def open(self, url: str, key: str = "default", timeout_ms: int = 15000) -> Page:
        page = self.page(key)
        page.goto(url, timeout=timeout_ms)
        return page

    def close(self) -> None:
        if self._context is not None:
            self._context.close()
        if self._pw is not None:
            self._pw.stop()
        self._context, self._pw, self._pages = None, None, {}

    def _ensure_context(self) -> BrowserContext:
        if self._context is None:
            self._pw = sync_playwright().start()
            kwargs = {"headless": self.headless}
            if self.executable_path:
                kwargs["executable_path"] = self.executable_path
            if self.profile_dir:
                self.profile_dir.mkdir(parents=True, exist_ok=True)
                self._context = self._pw.chromium.launch_persistent_context(str(self.profile_dir), **kwargs)
            else:
                self._context = self._pw.chromium.launch(**kwargs).new_context()
            atexit.register(self.close)
        return self._context
