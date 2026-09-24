---
type: Decision
title: ADR-0007 Playwright for browser automation
description: Use Playwright; Selenium is the documented fallback.
timestamp: 2026-09-24T18:48:53Z
tags: [adr, decision]
---

## Status
accepted (from spec)

## Context
`requirements.txt`: "Browser automation (pick one — Playwright recommended)"; Selenium commented out.

## Decision
Playwright drives all browser tools (WhatsApp Web, Gmail, generic browser).

## Alternatives considered
- Selenium — kept as a commented optional alternative.

## Consequences
Requires `playwright install` for browser binaries. Async API fits anyio.

## Related
[tools](../modules/tools.md), [Phase 5](../../phases/phase-05-tool-control.md).
