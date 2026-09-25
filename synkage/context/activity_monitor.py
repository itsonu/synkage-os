"""Activity signals on macOS: seconds since the last keyboard/mouse input, and the
frontmost app. Each probe returns None when it can't tell (not macOS, permission
denied, timeout); the detector treats None as "unknown", never as a guess.

  idle time      `ioreg -c IOHIDSystem` -> HIDIdleTime (nanoseconds)
  frontmost app  osascript / System Events (asks for Automation permission once)
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Callable

from pydantic import BaseModel

Runner = Callable[..., subprocess.CompletedProcess]
IDLE_RE = re.compile(r'"HIDIdleTime"\s*=\s*(\d+)')
FRONTMOST = (
    'tell application "System Events" to get name of first application process whose frontmost is true'
)


class ActivitySignals(BaseModel):
    idle_seconds: float | None = None
    frontmost_app: str | None = None


class ActivityMonitor:
    def __init__(self, runner: Runner = subprocess.run, platform: str = sys.platform):
        self.runner, self.platform = runner, platform

    def read(self) -> ActivitySignals:
        if self.platform != "darwin":
            return ActivitySignals()
        return ActivitySignals(idle_seconds=self._idle_seconds(), frontmost_app=self._frontmost_app())

    def _run(self, cmd: list[str]) -> str | None:
        try:
            proc = self.runner(cmd, capture_output=True, text=True, timeout=3)
        except (OSError, subprocess.SubprocessError):
            return None
        return proc.stdout if proc.returncode == 0 else None

    def _idle_seconds(self) -> float | None:
        out = self._run(["ioreg", "-c", "IOHIDSystem"])
        m = IDLE_RE.search(out or "")
        return int(m.group(1)) / 1e9 if m else None

    def _frontmost_app(self) -> str | None:
        out = self._run(["osascript", "-e", FRONTMOST])
        return out.strip() or None if out is not None else None
