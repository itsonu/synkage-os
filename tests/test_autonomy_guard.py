import pytest

from synkage.brain.autonomy_guard import AutonomyGuard
from synkage.brain.intent_resolver import IntentResolver
from synkage.config import load_config

LEVELS = [0, 1, 2, 3]


def decide(command, level=None, cfg=None):
    cfg = cfg or load_config()
    return AutonomyGuard(cfg).decide(IntentResolver(cfg).resolve(command), level=level)


CFG = load_config()
CATEGORY_CASES = [(c, kws[0]) for c, kws in CFG.permissions.category_keywords.items()]


# --- ac-4: hard rules hold at every level ---------------------------------------


@pytest.mark.parametrize("level", LEVELS)
@pytest.mark.parametrize("category, keyword", CATEGORY_CASES)
def test_never_autonomous_requires_confirmation_at_every_level(category, keyword, level):
    d = decide(f"send message to Raj about {keyword} auto execute", level=level)
    assert category in d.categories
    assert d.requires_confirmation


@pytest.mark.parametrize("level", LEVELS)
@pytest.mark.parametrize("risk", ["high", "critical"])
def test_high_and_critical_risk_require_confirmation_at_every_level(risk, level):
    cfg = load_config()
    cfg.tools.get("gmail").risk_class = risk
    d = decide("send message to Raj use gmail auto execute", level=level, cfg=cfg)
    assert d.risk_class == risk
    assert d.requires_confirmation


# --- level behaviour -------------------------------------------------------------


def test_default_level_2_executes_with_confirmation():
    d = decide("send message to Rahul")
    assert (d.level, d.may_execute, d.requires_confirmation) == (2, True, True)


@pytest.mark.parametrize("level", [0, 1])
def test_levels_0_and_1_never_execute(level):
    assert decide("send message to Rahul", level=level).may_execute is False


def test_auto_execute_low_risk_runs_without_confirmation():
    d = decide("send message to Rahul auto execute")
    assert (d.level, d.risk_class, d.may_execute, d.requires_confirmation) == (3, "medium", True, False)


def test_ask_before_send_caps_level_3_at_2():
    d = decide("send message to Rahul ask before send", level=3)
    assert (d.level, d.requires_confirmation) == (2, True)


def test_preview_never_executes():
    d = decide("send message")
    assert (d.level, d.may_execute) == (1, False)


def test_dry_run_never_executes():
    assert decide("send message to Rahul dry run").may_execute is False


def test_keywords_match_whole_words_only():
    # "repay" / "posted" must not trigger payments / public_posting
    assert decide("summarize repayment plan").categories == []
