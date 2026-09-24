---
type: Phase
title: Tool control
description: Synkage drafts a message in a real app and saves a native note, with confirmation before send.
timestamp: 2026-09-24T18:48:00Z
tags: [phase]
---

## Status
in_progress — automated parts done; manual runs on the user's Mac pending

## Goal
Synkage drafts a message in a real app and saves a native note, with confirmation before send.

## Scope
**In:** Playwright browser controller, WhatsApp Web draft flow, Gmail draft flow, Sticky Notes save, confirm-before-send.
**Out:** Autonomous sending, other apps.

## Acceptance criteria
Tick in `phases.json` with evidence when met.
- [x] **ac-1** Browser controller launches Chromium via Playwright and opens a URL — test against a local page passes  
  _Evidence:_ tests/test_browser_session.py (6 tests): ::test_opens_local_page_over_http, ::test_opens_file_url
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
**Progress (not yet ticked — each needs the user's manual run, see `docs/okf/runbooks/phase5-manual-checks.md`):**
- ac-2 automated part done: tests/test_whatsapp_flow.py (13 tests) — draft by name/phone, nothing sent before `yes`, `no` clears the draft, send refuses changed text, duplicate names refused, CLI draft → prompt → refused. **Pending:** one manual run on live WhatsApp Web.
- ac-3 automated part done: tests/test_gmail_flow.py (5 tests) — draft saved, never sent. **Pending:** manual run on live Gmail.
- ac-4: user's OS is macOS, so the notes target is Apple Notes (ADR-0008). tests/test_apple_notes.py (6 tests with faked osascript + 1 opt-in real-Mac test). **Pending:** `SYNKAGE_MANUAL=1` test on the Mac.
- ac-5: tools deliberately still `enabled: false`; flip once the manual checks pass.

plan.md Phase 5 (Week 6). Real accounts are involved: logging in and sending need a human (CLAUDE.md guardrails). Sticky Notes is Windows-only — see Unknowns.
