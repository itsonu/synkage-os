# Synkage Core — knowledge graph

OKF bundle: one concept per file, links are the graph. Each concept has a `## Status` line (`planned` / `scaffolded` / `in-progress` / `built`).

| Folder | What's in it |
|---|---|
| [modules/](modules/index.md) | The ten layers plus built Phase 0 modules (CLI, config loader, logging) |
| [data-models/](data-models/index.md) | Config files and planned memory store |
| [apis/](apis/index.md) | Command grammar |
| [services/](services/index.md) | External integrations (OpenClaw) |
| [flows/](flows/index.md) | Startup, command pipeline, confirmation loop, night cycle |
| [runbooks/](runbooks/index.md) | Local setup, schema changes |
| [decisions/](decisions/index.md) | ADRs |

Start with the [command pipeline](flows/command-pipeline.md) for the big picture. History: [log](log.md). Roadmap: [phases](../phases/index.md).

Tooling (vendored in `.tools/`): `python docs/okf/.tools/okf_lint.py --repo . --bundle docs/okf`, `okf_sync.py`, `okf_graph.py --html`.
