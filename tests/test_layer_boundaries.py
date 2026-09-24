"""Architecture invariants from CLAUDE.md, checked on imports."""

import ast
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parent.parent / "synkage"

FORBIDDEN = {
    # agents never control tools or run execution
    "agents": ("synkage.tools", "synkage.adapters", "synkage.execution"),
    # the brain never executes tools directly
    "brain": ("synkage.tools", "synkage.adapters"),
    # skills make no decisions and touch no tools
    "skills": ("synkage.brain", "synkage.tools", "synkage.adapters", "synkage.execution"),
    # adapters run what the router hands them; they can't reach the decision layers
    "adapters": ("synkage.brain", "synkage.agents", "synkage.execution"),
    # tool controllers take plain arguments; they know nothing above them
    "tools": ("synkage.brain", "synkage.agents", "synkage.skills", "synkage.execution", "synkage.adapters"),
    # the avatar is presentation only
    "avatar": ("synkage.brain", "synkage.execution", "synkage.adapters", "synkage.tools"),
}


def imports(path: Path) -> set[str]:
    names = set()
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            names |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_agents_reach_skills_only_through_the_registry():
    allowed = {"synkage.skills.registry"}
    for py in (PKG / "agents").rglob("*.py"):
        direct = {m for m in imports(py) if m.startswith("synkage.skills") and m not in allowed}
        assert not direct, f"{py.relative_to(PKG.parent)} imports skills directly: {sorted(direct)}"


@pytest.mark.parametrize("layer", sorted(FORBIDDEN))
def test_layer_does_not_import_forbidden_layers(layer):
    for py in (PKG / layer).rglob("*.py"):
        bad = {m for m in imports(py) for f in FORBIDDEN[layer] if m == f or m.startswith(f + ".")}
        assert not bad, f"{py.relative_to(PKG.parent)} imports {sorted(bad)}"
