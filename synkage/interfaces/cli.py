"""CLI entry point. Renders state only; no decision logic lives here."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from synkage import __version__
from synkage.config import ConfigError, SynkageConfig, load_config
from synkage.logging_setup import setup_logging

app = typer.Typer(add_completion=False, help="Synkage — situation-aware execution copilot.")
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    config_dir: Annotated[
        Path | None, typer.Option("--config-dir", help="Config directory (default: ./config).")
    ] = None,
    log_level: Annotated[
        str | None, typer.Option("--log-level", help="DEBUG, INFO, WARNING or ERROR.")
    ] = None,
) -> None:
    log = setup_logging(log_level)
    try:
        cfg = load_config(config_dir)
    except ConfigError as e:
        log.error("Config error: %s", e)
        raise typer.Exit(code=1) from e
    log.debug("Loaded config from %s", cfg.config_dir)
    ctx.obj = cfg
    if ctx.invoked_subcommand is None:
        render_status(cfg)


@app.command()
def status(ctx: typer.Context) -> None:
    """Print system state: config, autonomy, safety rules, tools."""
    render_status(ctx.obj)


@app.command()
def version() -> None:
    """Print the Synkage version."""
    console.print(__version__)


def render_status(cfg: SynkageConfig) -> None:
    a = cfg.autonomy
    default = a.levels[a.default_level]
    console.print(f"[bold]Synkage Core[/] v{__version__}")
    console.print(f"Config:   {cfg.config_dir}")
    console.print(
        f"Autonomy: default level [bold]{a.default_level}[/] ({default.name} — {default.description})"
    )

    risk = Table(title="Risk classes", title_justify="left")
    risk.add_column("Class")
    risk.add_column("Confirmation")
    risk.add_column("Examples")
    for name, rc in a.risk_classes.items():
        risk.add_row(name, "required" if rc.requires_confirmation else "by level", ", ".join(rc.examples))
    console.print(risk)

    console.print("Never autonomous: " + ", ".join(cfg.permissions.never_autonomous))

    tools = Table(title="Tools", title_justify="left")
    for col in ("ID", "Kind", "Adapter", "Risk", "Enabled"):
        tools.add_column(col)
    for t in cfg.tools.tools:
        tools.add_row(t.id, t.kind.value, t.adapter, t.risk_class, "yes" if t.enabled else "no")
    console.print(tools)

    enabled = sum(t.enabled for t in cfg.tools.tools)
    console.print(
        f"{len(cfg.tools.tools)} tools registered, {enabled} enabled. "
        f"{len(cfg.commands.verbs)} command verbs loaded."
    )
