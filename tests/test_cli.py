import subprocess
import sys

from typer.testing import CliRunner

from synkage import __version__
from synkage.config import REPO_ROOT
from synkage.interfaces.cli import app

runner = CliRunner()


def test_no_args_prints_status():
    result = runner.invoke(app, [])
    assert result.exit_code == 0, result.output
    assert "default level 2" in result.output
    assert "whatsapp_web" in result.output
    assert "payments" in result.output


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_bad_config_dir_exits_1(tmp_path):
    result = runner.invoke(app, ["--config-dir", str(tmp_path / "missing"), "status"])
    assert result.exit_code == 1


def test_entry_script_boots():
    proc = subprocess.run(
        [sys.executable, "scripts/run_synkage.py"], cwd=REPO_ROOT, capture_output=True, text=True, timeout=60
    )
    assert proc.returncode == 0, proc.stderr
    assert "Synkage Core" in proc.stdout


def test_parse_json():
    import json

    result = runner.invoke(app, ["parse", "--json", "send message to Rahul"])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["intent"]["target"] == "Rahul"
    assert data["decision"]["requires_confirmation"] is True


def test_parse_escapes_markup_in_user_text():
    result = runner.invoke(app, ["parse", "send message to Raj: [red]hi[/red]"])
    assert result.exit_code == 0
    assert "[red]hi[/red]" in result.output


# --- ac-6: interactive loop -------------------------------------------------------


def test_shell_prints_intent_and_autonomy():
    result = runner.invoke(app, ["shell"], input="send message to Rahul\nno\nexit\n")
    assert result.exit_code == 0, result.output
    assert "Rahul" in result.output
    assert "level 2" in result.output
    assert "confirmation: required" in result.output


def test_shell_confirm_yes_and_no():
    result = runner.invoke(app, ["shell"], input="send message to Rahul\nyes\nsend message to Rahul\nno\n")
    assert result.exit_code == 0
    assert "Plan: send message to Rahul" in result.output
    assert "Tool: WhatsApp Web (whatsapp_web)" in result.output
    assert "Confirmed" in result.output
    assert "Cancelled." in result.output


def test_shell_preview_does_not_ask_for_confirmation():
    result = runner.invoke(app, ["shell"], input="send message\n")
    assert result.exit_code == 0
    assert "needs a target" in result.output
    assert "Type 'yes'" not in result.output


def test_shell_exits_on_eof():
    assert runner.invoke(app, ["shell"], input="").exit_code == 0


def test_prepare_runs_agent_chain(runs_dir):
    result = runner.invoke(app, ["prepare", "send message to Rahul: running late"])
    assert result.exit_code == 0, result.output
    assert "Ready: send message to Rahul via WhatsApp Web." in result.output
    assert "Nothing was executed" in result.output
    assert len(list(runs_dir.glob("*/03-reporter.json"))) == 1


def test_shell_shows_report_before_confirmation():
    result = runner.invoke(app, ["shell"], input="send message to Rahul\nno\n")
    assert result.exit_code == 0
    out = result.output
    assert out.index("Ready: send message to Rahul") < out.index("Type 'yes'")


def test_skills_command_lists_skills_and_permissions():
    result = runner.invoke(app, ["skills"])
    assert result.exit_code == 0, result.output
    for name in ("plan_steps", "classify_intent", "format_note"):
        assert name in result.output
    assert "builder" in result.output
