---
type: Module
title: Skill layer
description: Atomic, stateless, permission-gated capabilities invoked by agents.
timestamp: 2026-09-24T18:48:53Z
sources:
  - synkage/skills/__init__.py
---

## Status
scaffolded — registry and first skills planned for [Phase 3](../../phases/phase-03-skills.md).

## Responsibilities
Stateless building blocks (summarize, classify intent, plan steps, draft message, format note). Permission-gated. Invoked only by [agents](agents.md). Make no decisions.

## Planned files
`base_skill.py`, a skill registry, subfolders `text/`, `analysis/`, `decision/`.

## Unknowns
Whether text skills call an LLM (and which) or are rule-based — spec says "no heavy model dependency required" but doesn't choose.
