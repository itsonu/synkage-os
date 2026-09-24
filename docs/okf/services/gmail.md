---
type: Integration
title: Gmail
description: Email drafts through Gmail's compose link. Never sends.
timestamp: 2026-09-24T19:40:06Z
sources:
  - synkage/tools/browser/gmail.py
---

## Status
built against a mock page (Phase 5). **Live site not verified.**

## Flow
Opens `mail.google.com/mail/?view=cm&fs=1&to=&su=&body=` and waits for "Draft saved". The target must be an email address. The subject comes from `details` (usually empty); the body is the message content. `reply` isn't supported yet. **Nothing is ever sent**: both the draft and execute steps only save a draft ([ADR-0008](../decisions/0008-macos-tool-control.md)).

## Connections
Driven by `GmailHandler` in the [adapters](../modules/adapters.md). Registry id `gmail`.
