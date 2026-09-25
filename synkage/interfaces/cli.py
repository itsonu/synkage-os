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
from synkage.adapters.tool_adapter_base import ExecutionResult, ExecutionStatus
from synkage.agents.base_agent import read_artifact
from synkage.brain.intent_resolver import Mode
from synkage.brain.prime import DelegationResult, Prime, PrimeResult
from synkage.config import SITUATION_STATES, ConfigError, SynkageConfig, load_config
from synkage.execution.autonomy_router import AutonomyRouter, load_request
from synkage.execution.confirmation_loop import confirm
from synkage.logging_setup import setup_logging
from synkage.skills.registry import SkillRegistry

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
    situation: Annotated[
        str | None,
        typer.Option("--situation", help="Force a situation: idle, normal, focused, urgent, emergency."),
    ] = None,
) -> None:
    log = setup_logging(log_level)
    try:
        cfg = load_config(config_dir)
    except ConfigError as e:
        log.error("Config error: %s", e)
        raise typer.Exit(code=1) from e
    log.debug("Loaded config from %s", cfg.config_dir)
    if situation is not None and situation not in SITUATION_STATES:
        log.error("Unknown situation '%s' (use: %s)", situation, ", ".join(SITUATION_STATES))
        raise typer.Exit(code=1)
    ctx.meta["situation"] = situation
    ctx.obj = cfg
    if ctx.invoked_subcommand is None:
        render_status(cfg, situation)


@app.command()
def status(ctx: typer.Context) -> None:
    """Print system state: config, situation, autonomy, safety rules, tools."""
    render_status(ctx.obj, ctx.meta.get("situation"))


@app.command()
def parse(
    ctx: typer.Context,
    command: Annotated[str, typer.Argument(help='e.g. "send message to Rahul"')],
    as_json: Annotated[bool, typer.Option("--json", help="Print the result as JSON.")] = False,
) -> None:
    """Parse one command and show the intent and autonomy decision. Executes nothing."""
    result = Prime(ctx.obj, situation=ctx.meta.get("situation")).handle(command)
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
    prime = Prime(ctx.obj, situation=ctx.meta.get("situation"))
    result = prime.handle(command)
    render_result(result)
    delegation = prime.delegate(result)
    render_delegation(delegation)
    if not delegation.ok and delegation.chain:
        raise typer.Exit(code=1)


@app.command()
def run(
    ctx: typer.Context,
    command: Annotated[str, typer.Argument(help='e.g. "send message to Raj: running late dry run"')],
) -> None:
    """Run one command: parse, prepare, confirm if needed, route to an adapter."""
    ok = _process(
        ctx.obj,
        Prime(ctx.obj, situation=ctx.meta.get("situation")),
        AutonomyRouter(ctx.obj),
        command,
        _make_ask(),
    )
    if not ok:
        raise typer.Exit(code=1)


@app.command()
def shell(ctx: typer.Context) -> None:
    """Interactive loop: parse, prepare via agents, confirm, route to an adapter."""
    prime, router, ask = (
        Prime(ctx.obj, situation=ctx.meta.get("situation")),
        AutonomyRouter(ctx.obj),
        _make_ask(),
    )
    console.print("Synkage shell — type a command, 'exit' to quit.")
    while True:
        try:
            line = ask("synkage> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            continue
        if line.lower() in {"exit", "quit"}:
            break
        _process(ctx.obj, prime, router, line, ask)


def _process(cfg: SynkageConfig, prime: Prime, router: AutonomyRouter, line: str, ask) -> bool:
    """parse -> prepare -> (confirm) -> route. Returns False if preparing failed."""
    result = prime.handle(line)
    render_result(result)
    delegation = prime.delegate(result)
    render_delegation(delegation)
    if not delegation.ok:
        return not delegation.chain  # level 0 runs no agents; that's not a failure
    draft = delegation.output_of("builder")
    if draft is None:  # preview / plan-only chains have nothing to route
        return True
    request = load_request(draft)
    d = result.decision
    confirmation, drafted = None, False
    if result.intent.mode == Mode.execute and d.may_execute and request.ready:
        staged = router.draft(request, result.intent, d, run_id=delegation.run_id)
        if staged is not None:
            render_execution(staged)
            if staged.status != ExecutionStatus.drafted:
                return True  # the draft failed; sending would fail the same way
            drafted = True
        plan = router.planner.plan(request, result.intent, d)
        if plan.requires_confirmation:
            confirmation = confirm(result.plan_text(), _tool_label(cfg, result), ask, _show)
    execution = router.route(
        request, result.intent, d, confirmation, run_id=delegation.run_id, drafted=drafted
    )
    render_execution(execution)
    return True


@app.command()
def skills(ctx: typer.Context) -> None:
    """List registered skills and which agents may call them."""
    cfg: SynkageConfig = ctx.obj
    registry = SkillRegistry(cfg)
    table = Table(title="Skills", title_justify="left")
    for col in ("Skill", "Allowed agents", "Description"):
        table.add_column(col)
    for name in registry.names():
        agents = [a for a, allowed in cfg.permissions.agent_skills.items() if name in allowed]
        table.add_row(name, ", ".join(agents) or "none", registry.get(name).description)
    console.print(table)


@app.command()
def login(
    services: Annotated[list[str] | None, typer.Argument(help="whatsapp, gmail (default: both)")] = None,
) -> None:
    """Open Synkage's browser window at WhatsApp Web / Gmail so you can sign in once.

    The login is kept in the browser profile (~/.synkage/browser-profile, outside the
    repo). Nothing is sent or typed for you.
    """
    from synkage.adapters.local_exec_adapter import LOGIN_PAGES, open_login_pages

    which = services or list(LOGIN_PAGES)
    unknown = [s for s in which if s not in LOGIN_PAGES]
    if unknown:
        console.print(f"[red]Unknown service(s):[/] {', '.join(unknown)} (use: {', '.join(LOGIN_PAGES)})")
        raise typer.Exit(code=1)
    session = open_login_pages(which)
    try:
        input("Sign in in the browser window, then press Enter here to close it... ")
    except (EOFError, KeyboardInterrupt):
        pass
    session.close()
    console.print(f"Saved login in {session.profile_dir}")


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
    console.print(
        f"Situation: {result.situation.state.value} ({escape('; '.join(result.situation.reasons))})"
    )
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


STATUS_STYLE = {
    ExecutionStatus.success: "green",
    ExecutionStatus.drafted: "cyan",
    ExecutionStatus.failed: "red",
    ExecutionStatus.refused: "red",
    ExecutionStatus.unavailable: "yellow",
    ExecutionStatus.dry_run: "cyan",
    ExecutionStatus.skipped: "dim",
}


def render_execution(execution: ExecutionResult) -> None:
    style = STATUS_STYLE[execution.status]
    console.print(f"[{style}]Execution: {execution.status.value}[/] — {escape(execution.message)}")


def render_status(cfg: SynkageConfig, situation_override: str | None = None) -> None:
    a = cfg.autonomy
    default = a.levels[a.default_level]
    situation = Prime(cfg, situation=situation_override).situation()
    auto = cfg.situation.states[situation.state.value].auto_risk
    console.print(f"[bold]Synkage Core[/] v{__version__}")
    console.print(f"Config:   {cfg.config_dir}")
    console.print(
        f"Situation: [bold]{situation.state.value}[/] ({escape('; '.join(situation.reasons))})"
        + (f" — {', '.join(auto)}-risk actions run without confirmation" if auto else "")
    )
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
