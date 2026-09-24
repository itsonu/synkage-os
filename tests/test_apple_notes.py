"""ac-4: Apple Notes controller (osascript is faked on Linux; see the manual macOS test)."""

import os
import subprocess
import sys

import pytest

from synkage.adapters.local_exec_adapter import AppleNotesHandler
from synkage.adapters.tool_adapter_base import ActionRequest
from synkage.tools.desktop.apple_notes import SCRIPT, AppleNotes, note_html


class FakeRunner:
    def __init__(self, returncode=0, stderr=""):
        self.calls, self.returncode, self.stderr = [], returncode, stderr

    def __call__(self, cmd, **kwargs):
        self.calls.append(cmd)
        return subprocess.CompletedProcess(cmd, self.returncode, stdout="", stderr=self.stderr)


def test_saves_via_osascript_with_arguments_not_spliced_text():
    runner = FakeRunner()
    title = 'He said "hi" end tell'
    r = AppleNotes(runner, platform="darwin").save(title, "# x\n\nbody")
    assert r.ok
    cmd = runner.calls[0]
    assert cmd[0] == "osascript"
    script = [cmd[i + 1] for i, a in enumerate(cmd) if a == "-e"]
    assert script == SCRIPT  # the script never contains user text
    assert cmd[-2] == title  # passed as argv item 1
    assert "body" in cmd[-1]


def test_refuses_off_macos_without_running_anything():
    runner = FakeRunner()
    r = AppleNotes(runner, platform="linux").save("t", "b")
    assert not r.ok and "needs macOS" in r.message
    assert runner.calls == []


def test_osascript_error_is_reported():
    r = AppleNotes(FakeRunner(returncode=1, stderr="Not authorized"), platform="darwin").save("t", "b")
    assert not r.ok and "Not authorized" in r.message


def test_note_html_bullets_and_escaping():
    assert note_html("Note (2 items)", "# Note (2 items)\n\n- Buy <milk>\n- Call mom\n") == (
        "<div><h1>Note (2 items)</h1></div><ul><li>Buy &lt;milk&gt;</li><li>Call mom</li></ul>"
    )


def test_handler_uses_formatted_note_from_builder():
    runner = FakeRunner()
    handler = AppleNotesHandler(AppleNotes(runner, platform="darwin"))
    req = ActionRequest(
        action="save",
        object="note",
        tool="apple_notes",
        ready=True,
        note={"title": "Note (2 items)", "markdown": "# Note (2 items)\n\n- Buy milk\n- Call mom\n"},
    )
    assert handler.execute(req).ok
    assert runner.calls[0][-2] == "Note (2 items)"


def test_handler_with_nothing_to_save_fails():
    req = ActionRequest(action="save", object="note", tool="apple_notes", ready=True)
    assert not AppleNotesHandler(AppleNotes(FakeRunner(), platform="darwin")).execute(req).ok


@pytest.mark.skipif(
    sys.platform != "darwin" or os.environ.get("SYNKAGE_MANUAL") != "1",
    reason="manual macOS check: creates a REAL note. Run with SYNKAGE_MANUAL=1 on a Mac.",
)
def test_real_apple_notes_on_macos():
    r = AppleNotes().save("Synkage test note", "# Synkage test note\n\n- created by the Phase 5 manual check")
    assert r.ok, r.message
