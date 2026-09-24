---
type: Decision
title: ADR-0006 Code in a synkage/ package; config data in config/
description: Layer code lives under synkage/<layer>/; runtime config files live in root config/.
timestamp: 2026-09-24T18:48:53Z
tags: [adr, decision]
---

## Status
accepted (Phase 0, inferred — deviates from the flat layout in README / docs/proj.md)

## Context
The spec lists top-level folders `brain/`, `tools/`, `config/`, `memory/`… Top-level Python packages named `tools`, `config`, `context` collide with common third-party names, and `config/` must also hold YAML data. The spec also disagrees on where `tool_registry.json` lives (`config/` in README vs `tools/` in proj.md).

## Decision
- All code under one importable package: `synkage/{brain,agents,skills,execution,adapters,tools,context,memory,avatar,interfaces}`.
- All runtime config under root `config/`, **including `tool_registry.json`** (README wins; it's the user-facing install doc).
- Entry: `scripts/run_synkage.py` or `python -m synkage`.

## Alternatives considered
- Flat top-level packages exactly as in proj.md — rejected: import-name collisions, code and data mixed in `config/`.

## Consequences
Imports read `from synkage.brain import …`. `docs/proj.md` updated to match.

## Related
[config loader](../modules/config-loader.md), [tool registry](../data-models/tool-registry.md).
