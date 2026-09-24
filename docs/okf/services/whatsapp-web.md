---
type: Integration
title: WhatsApp Web
description: Message drafting and sending through the WhatsApp Web site.
timestamp: 2026-09-24T19:40:06Z
sources:
  - synkage/tools/browser/whatsapp.py
---

## Status
built against a mock page (Phase 5). **Live site not verified**: the manual run is pending.

## Flow
- **Phone target** (`+91 98765 43210`): opens `web.whatsapp.com/send?phone=<digits>&text=<text>` (WhatsApp's click-to-chat link), which prefills the draft.
- **Name target** (`Raj`): types the name into chat search and opens the chat whose title matches **exactly**. Two matching chats → refused.
- `draft` fills the compose box; nothing is sent. `send` re-checks the box holds exactly the drafted text, clicks Send, and waits for the box to empty. `clear` empties it (used when the user says `no`).

## Selectors (unverified)
`SELECTORS` in the file: search `[contenteditable][aria-label*="Search"]`, chat `span[title="<name>"]`, compose `[contenteditable][aria-label*="Type a message"]`, send `button[aria-label="Send"]`. The mock (`tests/mock_pages/whatsapp.html`) is built to these, so tests prove the flow, not live compatibility.

## Connections
Driven by `WhatsAppHandler` in the [adapters](../modules/adapters.md). Registry id `whatsapp_web` ([tool registry](../data-models/tool-registry.md)).
