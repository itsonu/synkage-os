---
type: Decision
title: ADR-0008 Tool control on macOS — draft first, Apple Notes, Gmail drafts only
description: How Phase 5 drives real apps safely on the user's primary OS (macOS).
timestamp: 2026-09-24T19:40:06Z
tags: [adr, decision]
---

## Status
accepted (Phase 5). The user confirmed **macOS** as the primary OS. Apple Notes as the notes target is inferred.

## Context
`docs/plan.md` Phase 5 names a WhatsApp Web draft flow, a Gmail draft flow, Sticky Notes, and "confirmation before send". Sticky Notes is Windows-only, and macOS Stickies isn't scriptable. Real accounts are involved, so the flows must never act without the user's explicit consent.

## Decision
1. **Draft, then confirm, then commit.** `AutonomyRouter.draft()` stages the action (fills the WhatsApp message) before the confirmation prompt, so the user sees exactly what will be sent. On `no`, the draft is cleared. On `yes`, the controller sends **only if the compose box still holds exactly the drafted text**. There is no pre-confirmation draft for never-autonomous categories or high/critical risk.
2. **Gmail only drafts.** Both `draft` and `execute` save a Gmail draft; Synkage never sends email. The user sends from Gmail.
3. **Notes on macOS go to Apple Notes** via `osascript`, with user text passed as `argv` (no script injection). `sticky_notes` stays registered but has no controller.
4. **One persistent browser profile outside the repo** (`~/.synkage/browser-profile`). The user signs in once (`synkage login`). The profile holds session cookies and is never committed.
5. **Ambiguous recipients are refused:** two chats with the same name → error; use a phone number.

## Alternatives considered
- Confirm first, then draft and send in one go — rejected: the user would confirm without seeing the real draft.
- Gmail send after confirmation — rejected for now: an email can't be recalled, and the phase only asks for drafts.
- macOS Stickies — rejected: no AppleScript support.

## Consequences
- Controllers keep state between draft and send (same process, same browser tab).
- WhatsApp/Gmail selectors are **unverified** against the live sites, so the first manual run may need selector fixes ([manual checks](../runbooks/phase5-manual-checks.md)).

## Related
[tools](../modules/tools.md), [adapters](../modules/adapters.md), [execution routing](../flows/execution-routing.md), [WhatsApp Web](../services/whatsapp-web.md), [Gmail](../services/gmail.md), [Apple Notes](../services/apple-notes.md).
