"""Apple Notes controller (macOS): create a note via osascript.

Title and body are passed as osascript *arguments* (`on run argv`), never spliced
into the script text, so quotes or AppleScript in a note can't inject code.
"""

from __future__ import annotations

import html
import subprocess
import sys
from collections.abc import Callable

from synkage.tools.base import ControllerResult

SCRIPT = [
    "on run argv",
    'tell application "Notes"',
    "make new note with properties {name:(item 1 of argv), body:(item 2 of argv)}",
    "end tell",
    "end run",
]
Runner = Callable[..., subprocess.CompletedProcess]


def note_html(title: str, markdown: str) -> str:
    """Notes stores HTML; the first line is the title. Markdown bullets become a list."""
    lines = [ln for ln in markdown.splitlines() if ln.strip() and ln.strip() != f"# {title}"]
    parts = [f"<div><h1>{html.escape(title)}</h1></div>"]
    items = [ln.strip()[2:] for ln in lines if ln.strip().startswith("- ")]
    if items and len(items) == len(lines):
        parts.append("<ul>" + "".join(f"<li>{html.escape(i)}</li>" for i in items) + "</ul>")
    else:
        parts += [f"<div>{html.escape(ln.strip())}</div>" for ln in lines]
    return "".join(parts)


class AppleNotes:
    def __init__(self, runner: Runner = subprocess.run, platform: str = sys.platform):
        self.runner, self.platform = runner, platform

    def save(self, title: str, markdown: str) -> ControllerResult:
        if self.platform != "darwin":
            return ControllerResult(ok=False, message=f"Apple Notes needs macOS (this is {self.platform})")
        cmd = ["osascript"]
        for line in SCRIPT:
            cmd += ["-e", line]
        cmd += [title, note_html(title, markdown)]
        try:
            proc = self.runner(cmd, capture_output=True, text=True, timeout=30)
        except (OSError, subprocess.SubprocessError) as e:
            return ControllerResult(ok=False, message=f"osascript failed: {type(e).__name__}: {e}")
        if proc.returncode != 0:
            return ControllerResult(
                ok=False, message=f"osascript error: {proc.stderr.strip() or proc.returncode}"
            )
        return ControllerResult(ok=True, message=f"note '{title}' saved in Apple Notes")
