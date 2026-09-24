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
