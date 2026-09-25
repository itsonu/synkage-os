---
type: Decision
title: ADR-0009 Situation policy — which states relax confirmation
description: Focused, urgent and emergency let low-risk actions skip confirmation; nothing else changes.
timestamp: 2026-09-25T13:30:46Z
tags: [adr, decision]
---

## Status
accepted (Phase 6; **inferred**, since the spec says situation "affects confirmation requirements" without saying how).

## Context
`docs/architecture.md`: situation (idle / normal / focused / urgent / emergency) affects autonomy thresholds, confirmation, execution speed and interruption policy. Detection is rule-based ([ADR-0003](0003-rule-based-situation-detection.md)). The hard rules ([ADR-0002](0002-bounded-autonomy.md)) must hold in every state.

## Decision
- Policy lives in `config/situation.yaml` → `states.<state>.auto_risk`: the risk classes that may run without confirmation **at the default level**.
- Defaults: idle `[]`, normal `[]`, focused `[low]` (don't interrupt deep work), urgent `[low]`, emergency `[low]`.
- Medium risk (sending messages) always confirms by default. The config loader **rejects** `auto_risk` entries for classes that require confirmation (high, critical).
- The guard applies the situation **before** the hard rules, so never-autonomous categories and high/critical still confirm. `ask before send` beats the situation. The situation never raises level 0/1 or affects preview or dry run.
- Urgency and emergency words count **only before the `:`**. Message text never changes the situation, so it can't loosen confirmation.
- The audit log records the situation, so an action that skipped confirmation stays explainable.

## Alternatives considered
- Focused → stricter (confirm everything, or queue) — rejected: it adds interruptions exactly when the user wants fewer.
- Emergency → auto-run medium risk (messages) — rejected: a wrong recipient in an emergency is costly. The user can opt in via config.

## Consequences
Behaviour differs by what's in front of the user. `--situation <state>` makes it reproducible. The execution-speed and interruption-policy parts of the spec are not implemented yet.

## Related
[situation detector](../modules/situation-detector.md), [autonomy guard](../modules/autonomy-guard.md), [situation config](../data-models/situation-config.md).
