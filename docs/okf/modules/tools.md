---
type: Module
title: Tool layer
description: Browser and desktop controllers that perform real actions.
timestamp: 2026-09-24T18:48:53Z
sources:
  - synkage/tools/__init__.py
---

## Status
scaffolded — controllers planned for [Phase 5](../../phases/phase-05-tool-control.md).

## Responsibilities
Perform real-world actions and return results. No decision logic. Browser automation uses Playwright ([ADR-0007](../decisions/0007-playwright-browser-automation.md)).

## Planned folders
`browser/`, `desktop/`, `fallback/`. The registry itself lives in `config/` ([ADR-0006](../decisions/0006-package-layout.md)), described by [tool registry](../data-models/tool-registry.md).
