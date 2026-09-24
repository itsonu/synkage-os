---
type: Data Model
title: Autonomy policy
description: Autonomy levels, risk classes, and hard never-autonomous categories.
timestamp: 2026-09-24T18:58:38Z
sources:
  - config/autonomy_levels.yaml
  - config/permissions.yaml
---

## Status
built — enforced by the [autonomy guard](../modules/autonomy-guard.md) (Phase 1).

## Contents
- **Levels:** 0 observe · 1 plan · 2 confirm (**default**) · 3 limited auto.
- **Risk classes:** low · medium · high · critical. High and critical always require confirmation.
- **Never autonomous** (`permissions.yaml`): payments, account_changes, password_handling, public_posting, destructive_file_ops, system_config_changes.
- **Category keywords** (`permissions.yaml`): whole-word triggers per category. Every category must have at least one. Deliberately broad — a false match only adds a confirmation. *(Keyword approach inferred; spec names categories only.)*

Source doc: `docs/autonomy_safety.md`. Rationale: [ADR-0002](../decisions/0002-bounded-autonomy.md). Enforced by the [brain](../modules/brain.md) and [execution](../modules/execution.md) layers.
