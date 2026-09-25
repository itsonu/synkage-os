"""ac-2 (Focused vs Idle changes confirmation) and ac-3 (hard rules hold in every state)."""

import pytest
from routing_helpers import FakeAdapter, prepared, setup

from synkage.adapters.tool_adapter_base import ExecutionStatus
from synkage.brain.autonomy_guard import AutonomyGuard
from synkage.brain.intent_resolver import IntentResolver
from synkage.brain.prime import Prime
from synkage.brain.situation_detector import Situation, SituationState
from synkage.config import SITUATION_STATES, ConfigError, load_config

CFG = load_config()
LOW = "save note meeting at 4pm"  # apple_notes, low risk
STATES = [SituationState(s) for s in SITUATION_STATES]


def decide(command, state, cfg=CFG, level=None):
    intent = IntentResolver(cfg).resolve(command)
    return AutonomyGuard(cfg).decide(intent, level=level, situation=Situation(state=state))


# --- ac-2 ---------------------------------------------------------------------------------


def test_same_intent_focused_vs_idle():
    focused, idle = decide(LOW, SituationState.focused), decide(LOW, SituationState.idle)
    assert (focused.risk_class, idle.risk_class) == ("low", "low")
    assert focused.requires_confirmation is False and focused.level == 3
    assert idle.requires_confirmation is True and idle.level == 2
    assert focused.situation == "focused" and idle.situation == "idle"


def test_focused_vs_idle_through_prime(tmp_path):
    focused = Prime(CFG, runs_dir=tmp_path, situation="focused").handle(LOW)
    idle = Prime(CFG, runs_dir=tmp_path, situation="idle").handle(LOW)
    assert (focused.decision.requires_confirmation, idle.decision.requires_confirmation) == (False, True)


def test_focused_vs_idle_through_router(tmp_path):
    cfg, _, router, _ = setup(tmp_path, enable=("apple_notes",))
    for state, expected in [("focused", ExecutionStatus.success), ("idle", ExecutionStatus.refused)]:
        prime = Prime(cfg, runs_dir=tmp_path / state, situation=state)
        result, request, _ = prepared(prime, LOW)
        assert router.route(request, result.intent, result.decision, None).status == expected, state


def test_medium_risk_still_confirms_when_focused():
    assert decide("send message to Raj: hi", SituationState.focused).requires_confirmation is True


def test_ask_before_send_beats_situation():
    d = decide("save note meeting at 4pm ask before send", SituationState.focused)
    assert (d.level, d.requires_confirmation) == (2, True)


def test_situation_never_raises_level_0_or_1():
    assert decide(LOW, SituationState.focused, level=1).may_execute is False


@pytest.mark.parametrize("state", STATES)
def test_preview_and_dry_run_never_execute_in_any_state(state):
    preview = decide("send message", state)  # no target -> preview
    dry = decide("save note dry run: meeting at 4pm", state)
    assert preview.may_execute is False and preview.level <= 1
    assert dry.may_execute is False


# --- ac-3 ---------------------------------------------------------------------------------

CATEGORY_CASES = [(c, kws[0]) for c, kws in CFG.permissions.category_keywords.items()]


@pytest.mark.parametrize("state", STATES)
@pytest.mark.parametrize("category, keyword", CATEGORY_CASES)
def test_never_autonomous_confirms_in_every_state(state, category, keyword):
    d = decide(f"save note {keyword} reminder", state)
    assert category in d.categories and d.requires_confirmation


@pytest.mark.parametrize("state", STATES)
@pytest.mark.parametrize("risk", ["high", "critical"])
def test_high_and_critical_confirm_in_every_state(state, risk):
    cfg = load_config()
    cfg.tools.get("apple_notes").risk_class = risk
    d = decide(LOW, state, cfg=cfg)
    assert d.risk_class == risk and d.requires_confirmation


@pytest.mark.parametrize("state", ["focused", "urgent", "emergency"])
def test_router_refuses_flagged_low_risk_even_when_situation_allows_auto(tmp_path, state):
    cfg, _, router, _ = setup(tmp_path, enable=("apple_notes",))
    prime = Prime(cfg, runs_dir=tmp_path / state, situation=state)
    result, request, _ = prepared(prime, "save note delete old backups")
    out = router.route(request, result.intent, result.decision, None)
    assert out.status == ExecutionStatus.refused and "destructive_file_ops" in out.message
    assert FakeAdapter.calls == []


# --- config can't loosen the hard rules ---------------------------------------------------------


@pytest.mark.parametrize("risk", ["high", "critical"])
def test_config_rejects_auto_for_high_or_critical(config_dir, risk):
    import yaml

    path = config_dir / "situation.yaml"
    data = yaml.safe_load(path.read_text())
    data["states"]["urgent"]["auto_risk"] = ["low", risk]
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ConfigError, match=f"'{risk}' always requires confirmation"):
        load_config(config_dir)


def test_config_requires_all_five_states(config_dir):
    import yaml

    path = config_dir / "situation.yaml"
    data = yaml.safe_load(path.read_text())
    del data["states"]["emergency"]
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ConfigError, match="states must be exactly"):
        load_config(config_dir)


def test_config_rejects_bad_quiet_hours(config_dir):
    import yaml

    path = config_dir / "situation.yaml"
    data = yaml.safe_load(path.read_text())
    data["quiet_hours"]["start"] = "25:00"
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ConfigError, match="situation.yaml"):
        load_config(config_dir)


def test_audit_records_the_situation(tmp_path):
    cfg, _, router, audit = setup(tmp_path, enable=("apple_notes",))
    prime = Prime(cfg, runs_dir=tmp_path / "runs", situation="focused")
    result, request, _ = prepared(prime, LOW)
    router.route(request, result.intent, result.decision, None)
    rec = audit.read()[-1]
    assert (rec.situation, rec.autonomy_level, rec.confirmation["required"]) == ("focused", 3, False)
