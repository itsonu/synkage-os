---
type: Phase
title: Tool control
description: Synkage drafts a message in a real app and saves a native note, with confirmation before send.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
todo

## Goal
Synkage drafts a message in a real app and saves a native note, with confirmation before send.

## Scope
**In:** Playwright browser controller, WhatsApp Web draft flow, Gmail draft flow, Sticky Notes save, confirm-before-send.
**Out:** Autonomous sending, other apps.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [ ] **ac-1** Browser controller launches Chromium via Playwright and opens a URL — test against a local page passes
- [ ] **ac-2** WhatsApp Web flow fills a draft and stops at the confirmation prompt; nothing is sent without 'yes' — test with a mock page passes, plus one manual run recorded
- [ ] **ac-3** Gmail flow creates a draft (not sent) — mock-page test passes, plus one manual run recorded
- [ ] **ac-4** 'save this as a note' writes a note via the desktop adapter — test passes on the target OS
- [ ] **ac-5** Matching tool entries set enabled: true in tool_registry.json and the status table shows them enabled

## Depends on
[phase-04-routing](phase-04-routing.md)

## OKF concepts touched
- [modules/tools.md](../okf/modules/tools.md)
- [modules/adapters.md](../okf/modules/adapters.md)
- [data-models/tool-registry.md](../okf/data-models/tool-registry.md)

## Notes
plan.md Phase 5 (Week 6). Real accounts are involved: logging in and sending need a human (CLAUDE.md guardrails). Sticky Notes is Windows-only — see Unknowns.
