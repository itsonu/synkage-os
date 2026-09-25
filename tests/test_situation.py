"""ac-1: situation detector maps fixture signal sets to each of the 5 states (+ signal probes)."""

import subprocess
from datetime import datetime, time

import pytest

from synkage.brain.situation_detector import SituationDetector, SituationState
from synkage.config import load_config
from synkage.context.activity_monitor import ActivityMonitor, ActivitySignals
from synkage.context.signal_ingestion import SignalCollector, Signals
from synkage.context.time_context import TimeSignals, in_window, time_signals

CFG = load_config()
DETECT = SituationDetector(CFG.situation).classify
NOON = TimeSignals(now=datetime(2026, 1, 5, 12, 0), quiet_hours=False)
NIGHT = TimeSignals(now=datetime(2026, 1, 5, 23, 30), quiet_hours=True)


def signals(time=NOON, idle=None, app=None, urgent=(), emergency=(), override=None):
    return Signals(
        time=time,
        activity=ActivitySignals(idle_seconds=idle, frontmost_app=app),
        urgent_words=list(urgent),
        emergency_words=list(emergency),
        override=override,
    )


# --- ac-1: the five states ------------------------------------------------------------


@pytest.mark.parametrize(
    "fixture, state",
    [
        (signals(idle=600, app="Safari"), SituationState.idle),
        (signals(idle=4, app="Safari"), SituationState.normal),
        (signals(idle=4, app="Code"), SituationState.focused),
        (signals(idle=4, app="Safari", urgent=["urgent"]), SituationState.urgent),
        (signals(idle=4, app="Safari", emergency=["emergency"]), SituationState.emergency),
    ],
    ids=["idle", "normal", "focused", "urgent", "emergency"],
)
def test_fixture_signals_map_to_each_state(fixture, state):
    assert DETECT(fixture).state == state


@pytest.mark.parametrize(
    "fixture, state",
    [
        (signals(override="focused", emergency=["sos"]), SituationState.focused),  # override wins
        (signals(urgent=["asap"], emergency=["sos"]), SituationState.emergency),  # emergency beats urgent
        (signals(idle=900, app="Code"), SituationState.idle),  # away from the keyboard beats focus app
        (signals(idle=4, app="xcode"), SituationState.focused),  # case-insensitive app match
        (signals(), SituationState.normal),  # no data at all -> normal, never a guess
        (signals(time=NIGHT), SituationState.idle),  # quiet hours with no data
        (signals(time=NIGHT, idle=3, app="Safari"), SituationState.normal),  # quiet hours but active
        (signals(time=NIGHT, idle=3, app="Code"), SituationState.focused),
    ],
)
def test_rule_priority(fixture, state):
    assert DETECT(fixture).state == state


def test_reasons_explain_the_state():
    assert DETECT(signals(idle=4, app="Code")).reasons == ["working in Code"]
    assert DETECT(signals(idle=600)).reasons == ["no input for 600s"]


# --- time context -----------------------------------------------------------------------


@pytest.mark.parametrize(
    "t, inside",
    [
        (time(23, 30), True),
        (time(3, 0), True),
        (time(7, 0), False),
        (time(12, 0), False),
        (time(23, 0), True),
    ],
)
def test_quiet_window_wraps_midnight(t, inside):
    assert in_window(t, time(23, 0), time(7, 0)) is inside


def test_time_signals_uses_config_window():
    assert time_signals(CFG.situation.quiet_hours, datetime(2026, 1, 5, 23, 45)).quiet_hours is True
    assert time_signals(CFG.situation.quiet_hours, datetime(2026, 1, 5, 12, 0)).quiet_hours is False


# --- activity monitor (macOS probes, faked) ----------------------------------------------


class FakeRunner:
    def __init__(self, outputs):
        self.outputs, self.calls = outputs, []

    def __call__(self, cmd, **kwargs):
        self.calls.append(cmd[0])
        out = self.outputs.get(cmd[0])
        if isinstance(out, Exception):
            raise out
        return subprocess.CompletedProcess(cmd, 0 if out is not None else 1, stdout=out or "", stderr="")


def test_mac_probes_parse_idle_and_frontmost_app():
    runner = FakeRunner({"ioreg": '  | |   "HIDIdleTime" = 5000000000\n', "osascript": "Code\n"})
    a = ActivityMonitor(runner, platform="darwin").read()
    assert (a.idle_seconds, a.frontmost_app) == (5.0, "Code")


def test_probe_failures_are_unknown_not_guesses():
    runner = FakeRunner({"ioreg": subprocess.TimeoutExpired("ioreg", 3), "osascript": None})
    assert ActivityMonitor(runner, platform="darwin").read() == ActivitySignals()


def test_off_macos_runs_nothing():
    runner = FakeRunner({})
    assert ActivityMonitor(runner, platform="linux").read() == ActivitySignals()
    assert runner.calls == []


# --- keyword signals ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "command, urgent, emergency",
    [
        ("send urgent message to Raj: call me", ["urgent"], []),
        ("send message to Raj right now: call me", ["right now"], []),
        ("send urgently message to Raj", [], []),  # whole words only
        ("send SOS message to Raj: at the station", [], ["sos"]),
        ("send message to Raj: urgent, call me", [], []),  # message text never counts
        ("send message to Raj: emergency meeting at 5", [], []),
    ],
)
def test_keywords_in_command(command, urgent, emergency):
    class NoActivity:
        def read(self):
            return ActivitySignals()

    s = SignalCollector(CFG.situation, monitor=NoActivity()).collect(command, now=datetime(2026, 1, 5, 12, 0))
    assert (s.urgent_words, s.emergency_words) == (urgent, emergency)
