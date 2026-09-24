---
type: Decision
title: ADR-0002 Bounded autonomy with non-removable hard rules
description: Default level 2; high/critical risk and six hard categories always need confirmation.
timestamp: 2026-09-24T18:48:53Z
tags: [adr, decision]
---

## Status
accepted (from spec; enforcement detail inferred)

## Context
`docs/autonomy_safety.md` defines levels 0–3 (default 2), four risk classes, and six never-autonomous categories.

## Decision
- Policy lives in config ([autonomy policy](../data-models/autonomy-policy.md)).
- The [config loader](../modules/config-loader.md) **rejects** config that drops a built-in never-autonomous category or lets high/critical run without confirmation. Users can tighten, not loosen. *(Inferred — the spec states the rules but not how config may change them.)*

## Alternatives considered
- Fully user-editable policy — rejected: a config typo could silently enable autonomous payments.

## Consequences
Safety rules are hard-coded in `HARD_NEVER_AUTONOMOUS`; changing them needs a code change and review.

## Related
[confirmation loop](../flows/confirmation-loop.md), [brain](../modules/brain.md).
