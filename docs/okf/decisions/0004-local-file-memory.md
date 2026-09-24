---
type: Decision
title: ADR-0004 Local file-based memory
description: Memory is plain local files, no database.
timestamp: 2026-09-24T18:48:53Z
tags: [adr, decision]
---

## Status
accepted (from spec)

## Context
README: "File-based memory", "CPU-friendly", "Lightweight & Modular".

## Decision
Store profile, relationship state, logs, and project notes as JSON/Markdown files ([memory store](../data-models/memory-store.md)).

## Alternatives considered
- SQLite / vector DB — rejected for MVP: extra dependency, not needed at this scale.

## Consequences
Easy to inspect and back up. Concurrent writes and large logs need care (night-cycle compression). Storage location is still open.

## Related
[memory](../modules/memory.md), [night cycle](../flows/night-cycle.md).
