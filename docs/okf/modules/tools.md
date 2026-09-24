---
type: Module
title: Tool layer
description: Browser and desktop controllers that perform real actions.
timestamp: 2026-09-24T19:40:06Z
sources:
  - synkage/tools/__init__.py
  - synkage/tools/base.py
  - synkage/tools/browser/session.py
  - synkage/tools/browser/whatsapp.py
  - synkage/tools/browser/gmail.py
  - synkage/tools/desktop/apple_notes.py
---

## Status
in-progress — controllers built and tested against mock pages and a faked `osascript` in [Phase 5](../../phases/phase-05-tool-control.md). **Not yet verified against live WhatsApp/Gmail or on a real Mac** ([manual checks](../runbooks/phase5-manual-checks.md)).

## Contract
Controllers take plain arguments (`draft(target, text)`, `save(title, markdown)`) and return `ControllerResult(ok, message, output)` (`base.py`). They know nothing about intents, autonomy or adapters. The [local exec adapter](adapters.md) translates `ActionRequest`s into these calls. No decision logic lives here.

## Controllers
| File | Class | Does |
|---|---|---|
| `browser/session.py` | `BrowserSession` | One Playwright Chromium per process, opened on first use. Persistent profile (`SYNKAGE_BROWSER_PROFILE`, default `~/.synkage/browser-profile`); `SYNKAGE_BROWSER_HEADLESS`; `SYNKAGE_CHROMIUM_PATH`. One tab per controller key |
| `browser/whatsapp.py` | `WhatsAppWeb` | `draft`, `send` (only the exact drafted text), `clear`. See [WhatsApp Web](../services/whatsapp-web.md) |
| `browser/gmail.py` | `Gmail` | `draft` only. See [Gmail](../services/gmail.md) |
| `desktop/apple_notes.py` | `AppleNotes` | `save` via osascript (argv, no injection). See [Apple Notes](../services/apple-notes.md) |

## Rules
Tools import nothing above them (brain, agents, skills, execution, adapters); `tests/test_layer_boundaries.py` enforces it. Tests never touch live sites: an autouse fixture makes the shared session raise, and mock-page tests pass their own headless session. Browser automation uses Playwright ([ADR-0007](../decisions/0007-playwright-browser-automation.md)). Design choices: [ADR-0008](../decisions/0008-macos-tool-control.md).
