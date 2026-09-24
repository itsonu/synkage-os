from pathlib import Path

from synkage.agents.base_agent import AgentTask
from synkage.brain.autonomy_guard import AutonomyGuard
from synkage.brain.intent_resolver import IntentResolver
from synkage.config import load_config

CFG = load_config()


def make_task(agent: str, command: str, out: Path, inputs: list[Path] | None = None, cfg=CFG) -> AgentTask:
    intent = IntentResolver(cfg).resolve(command)
    return AgentTask(
        id=f"t/{agent}",
        agent=agent,
        intent=intent,
        decision=AutonomyGuard(cfg).decide(intent),
        inputs=inputs or [],
        output=out,
    )
