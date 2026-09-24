import json

import pytest
import yaml

from synkage.config import (
    HARD_NEVER_AUTONOMOUS,
    REPO_ROOT,
    ConfigError,
    load_config,
    tool_registry_json_schema,
)


def edit_yaml(path, fn):
    data = yaml.safe_load(path.read_text())
    fn(data)
    path.write_text(yaml.safe_dump(data))


def test_repo_config_loads():
    cfg = load_config(REPO_ROOT / "config")
    assert cfg.autonomy.default_level == 2
    assert set(cfg.autonomy.levels) == {0, 1, 2, 3}
    assert HARD_NEVER_AUTONOMOUS <= set(cfg.permissions.never_autonomous)
    assert cfg.tools.get("whatsapp_web") is not None


def test_env_var_selects_config_dir(config_dir, monkeypatch):
    monkeypatch.setenv("SYNKAGE_CONFIG_DIR", str(config_dir))
    assert load_config().config_dir == config_dir


def test_missing_dir(tmp_path):
    with pytest.raises(ConfigError, match="config directory not found"):
        load_config(tmp_path / "nope")


def test_missing_file(config_dir):
    (config_dir / "permissions.yaml").unlink()
    with pytest.raises(ConfigError, match="missing config file"):
        load_config(config_dir)


def test_unparseable_yaml(config_dir):
    (config_dir / "autonomy_levels.yaml").write_text("levels: [unclosed")
    with pytest.raises(ConfigError, match="cannot parse autonomy_levels.yaml"):
        load_config(config_dir)


def test_default_level_must_exist(config_dir):
    edit_yaml(config_dir / "autonomy_levels.yaml", lambda d: d.update(default_level=7))
    with pytest.raises(ConfigError, match="default_level 7"):
        load_config(config_dir)


def test_high_risk_must_require_confirmation(config_dir):
    def relax(d):
        d["risk_classes"]["high"]["requires_confirmation"] = False

    edit_yaml(config_dir / "autonomy_levels.yaml", relax)
    with pytest.raises(ConfigError, match="'high' must exist and require confirmation"):
        load_config(config_dir)


def test_cannot_drop_hard_safety_rule(config_dir):
    edit_yaml(config_dir / "permissions.yaml", lambda d: d["never_autonomous"].remove("payments"))
    with pytest.raises(ConfigError, match="cannot drop hard safety rules"):
        load_config(config_dir)


def test_can_add_safety_rule(config_dir):
    def add(d):
        d["never_autonomous"].append("calendar_invites")
        d["category_keywords"]["calendar_invites"] = ["invite"]

    edit_yaml(config_dir / "permissions.yaml", add)
    assert "calendar_invites" in load_config(config_dir).permissions.never_autonomous


def test_every_category_needs_keywords(config_dir):
    edit_yaml(config_dir / "permissions.yaml", lambda d: d["category_keywords"].pop("payments"))
    with pytest.raises(ConfigError, match="category_keywords missing for: \\['payments'\\]"):
        load_config(config_dir)


def test_verb_rules_loaded():
    verbs = load_config(REPO_ROOT / "config").commands.verbs
    assert verbs["send"].needs_target and verbs["send"].needs_tool
    assert not verbs["summarize"].needs_tool


def test_unknown_key_rejected(config_dir):
    edit_yaml(config_dir / "app_preferences.yaml", lambda d: d.update(typo_key=1))
    with pytest.raises(ConfigError, match="app_preferences.yaml"):
        load_config(config_dir)


def test_preference_must_reference_registered_tool(config_dir):
    edit_yaml(config_dir / "app_preferences.yaml", lambda d: d["preferred_tools"].update(notes="evernote"))
    with pytest.raises(ConfigError, match="unknown tool 'evernote'"):
        load_config(config_dir)


def test_duplicate_tool_ids_rejected(config_dir):
    path = config_dir / "tool_registry.json"
    data = json.loads(path.read_text())
    data["tools"].append(dict(data["tools"][0]))
    path.write_text(json.dumps(data))
    with pytest.raises(ConfigError, match="duplicate tool ids"):
        load_config(config_dir)


def test_committed_schema_matches_model():
    committed = json.loads((REPO_ROOT / "config/schema/tool_registry.schema.json").read_text())
    assert committed == tool_registry_json_schema(), "run: python scripts/gen_schema.py"
