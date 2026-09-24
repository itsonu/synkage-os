"""CLI entry point. Renders state only; no decision logic lives here."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.markup import escape
from rich.table import Table

from synkage import __version__
from synkage.agents.base_agent import read_artifact
from synkage.brain.prime import DelegationResult, Prime, PrimeResult
from synkage.config import ConfigError, SynkageConfig, load_config
from synkage.execution.confirmation_loop import confirm
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
def parse(
    ctx: typer.Context,
    command: Annotated[str, typer.Argument(help='e.g. "send message to Rahul"')],
    as_json: Annotated[bool, typer.Option("--json", help="Print the result as JSON.")] = False,
) -> None:
    """Parse one command and show the intent and autonomy decision. Executes nothing."""
    result = Prime(ctx.obj).handle(command)
    if as_json:
        print(result.model_dump_json(indent=2))
    else:
        render_result(result)


@app.command()
def prepare(
    ctx: typer.Context,
    command: Annotated[str, typer.Argument(help='e.g. "send message to Rahul: running late"')],
) -> None:
    """Parse a command and run the agent chain (plan -> draft -> report). Executes nothing."""
    prime = Prime(ctx.obj)
    result = prime.handle(command)
    render_result(result)
    delegation = prime.delegate(result)
    render_delegation(delegation)
    if not delegation.ok and delegation.chain:
        raise typer.Exit(code=1)


@app.command()
def shell(ctx: typer.Context) -> None:
    """Interactive loop: parse, prepare via agents, confirm. Executes nothing yet."""
    prime = Prime(ctx.obj)
    ask = _make_ask()
    console.print("Synkage shell — type a command, 'exit' to quit. Nothing is executed until Phase 4.")
    while True:
        try:
            line = ask("synkage> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            break
        result = prime.handle(line)
        render_result(result)
        delegation = prime.delegate(result)
        render_delegation(delegation)
        d = result.decision
        if not delegation.ok:
            continue
        if d.may_execute and d.requires_confirmation:
            outcome = confirm(result.plan_text(), _tool_label(ctx.obj, result), ask, _show)
            console.print("Confirmed — execution arrives in Phase 4." if outcome.confirmed else "Cancelled.")
        elif d.may_execute:
            console.print("Would run without confirmation — execution arrives in Phase 4.")


@app.command()
def version() -> None:
    """Print the Synkage version."""
    console.print(__version__)


def _make_ask() -> Callable[[str], str]:
    if sys.stdin.isatty():
        from prompt_toolkit import PromptSession

        return PromptSession().prompt
    return input


def _show(text: str) -> None:
    console.print(text, markup=False, highlight=False)


def _tool_label(cfg: SynkageConfig, result: PrimeResult) -> str:
    tool = cfg.tools.get(result.intent.tool) if result.intent.tool else None
    return f"{tool.name} ({tool.id})" if tool else "none"


def render_result(result: PrimeResult) -> None:
    i, d = result.intent, result.decision
    table = Table(title="Intent", title_justify="left", show_header=False)
    table.add_column("Field")
    table.add_column("Value")
    fields = {
        "verb": i.verb,
        "object": i.object,
        "target": i.target,
        "details": i.details,
        "content": i.content,
        "tool": f"{i.tool} (from {i.tool_source.value})" if i.tool and i.tool_source else i.tool,
        "modifier": i.modifier,
        "agent directive": i.agent_directive,
        "mode": i.mode.value,
    }
    for name, value in fields.items():
        if value is not None:
            table.add_row(name, escape(str(value)))
    console.print(table)
    for reason in i.unclear:
        console.print(f"[yellow]unclear:[/] {escape(reason)}")
    confirmation = "required" if d.requires_confirmation else "not required"
    console.print(
        f"Autonomy: level [bold]{d.level}[/] · risk {d.risk_class} · "
        f"may execute: {'yes' if d.may_execute else 'no'} · confirmation: {confirmation}"
    )
    if d.categories:
        console.print(f"[red]Never autonomous:[/] {', '.join(d.categories)}")
    for reason in d.reasons:
        console.print(f"  - {escape(reason)}")


def render_delegation(delegation: DelegationResult) -> None:
    for note in delegation.notes:
        console.print(f"[dim]agents: {escape(note)}[/]")
    for r in delegation.results:
        if r.error:
            console.print(f"[red]{r.agent} failed:[/] {escape(r.error)}")
    if delegation.artifact:
        console.rule("Report")
        _show(read_artifact(delegation.artifact).body.get("text", ""))
        console.print(f"[dim]Artifacts: {escape(str(delegation.run_dir))}[/]")


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
