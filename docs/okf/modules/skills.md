---
type: Module
title: Skill layer
description: Atomic, stateless, permission-gated capabilities invoked by agents through a registry.
timestamp: 2026-09-24T19:17:25Z
sources:
  - synkage/skills/__init__.py
  - synkage/skills/base_skill.py
  - synkage/skills/registry.py
  - synkage/skills/decision/plan_steps.py
  - synkage/skills/analysis/classify_intent.py
  - synkage/skills/text/format_note.py
---

## Status
in-progress — base class, registry, permission gating and 3 rule-based skills built in [Phase 3](../../phases/phase-03-skills.md). **summarize** and **draft message** are not built: they wait on the LLM-or-not decision (see `docs/context/state.md`).

## Contract (`base_skill.py`)
A subclass sets `name`, `description`, `Input` and `Output` (pydantic models) and implements `run(data) -> Output`. Skills get the config as read-only reference data. They make no decisions and touch no tools.

## Registry (`registry.py`)
- `SkillRegistry(config, skills=DEFAULT_SKILLS)`: `register()` rejects duplicate names; `names()`, `get()`.
- `invoke(name, caller, data)`: unknown skill → `SkillError`; **permission check first** → `PermissionDenied`; then input validation, a **fresh skill instance per call** (so a skill can't keep state), and output type check.
- `for_agent(name) -> SkillClient` binds the caller, so `client.call("plan_steps", ...)` is always permission-checked.
- Permissions: `agent_skills` in [autonomy policy](../data-models/autonomy-policy.md) (`config/permissions.yaml`). **Default deny**: an agent that isn't listed gets no skills.

## Skills
| Skill | Folder | Used by | Does |
|---|---|---|---|
| `plan_steps` | decision/ | planner | Ordered steps per verb (moved out of the planner in Phase 3). No confirm/send/verify steps when blocked; no confirm step for `plan` |
| `classify_intent` | analysis/ | planner | Task type (messaging/email/notes/code/web) + verb. A tool phrase beats an object noun; message content is ignored; `confidence` = share of {verb, task type} found |
| `format_note` | text/ | builder | Tidies text into Markdown: items split on `;` or newlines, bullets for 2+ items; title = explicit, else the first 6 words (1 item) or "Note (N items)" |

## Rules
- Skills never import `synkage.brain`, `synkage.tools`, `synkage.adapters` or `synkage.execution`.
- [Agents](agents.md) import only `synkage.skills.registry`, never a skill module directly. Both rules are enforced by `tests/test_layer_boundaries.py`.

## Connections
Called by [agents](agents.md). The [CLI](cli.md) `skills` command lists skills and the agents allowed to call them.
