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


@pytest.mark.parametrize("layer", sorted(FORBIDDEN))
def test_layer_does_not_import_forbidden_layers(layer):
    for py in (PKG / layer).rglob("*.py"):
        bad = {m for m in imports(py) for f in FORBIDDEN[layer] if m == f or m.startswith(f + ".")}
        assert not bad, f"{py.relative_to(PKG.parent)} imports {sorted(bad)}"
