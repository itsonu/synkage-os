---
type: Data Model
title: Memory store
description: Planned local files: user profile, relationship state, interaction logs, project notes.
timestamp: 2026-09-24T18:48:53Z
---

## Status
planned — [Phase 7](../../phases/phase-07-memory.md).

## Planned files
`user_profile.json`, `relationship_state.json`, `logs.json`, `project.md` (per `docs/proj.md`). Written by the [memory layer](../modules/memory.md); rationale in [ADR-0004](../decisions/0004-local-file-memory.md).

## Unknowns
- Location: the spec puts them in the repo's `memory/` folder, but personal data should not be committed. A user data dir (e.g. `~/.synkage/`) is likely better — decide in Phase 7.
- How the user trust score is computed and stored.
