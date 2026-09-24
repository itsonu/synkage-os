---
type: Data Model
title: App preferences
description: Preferred tool per task type.
timestamp: 2026-09-24T19:40:06Z
sources:
  - config/app_preferences.yaml
---

## Status
built (Phase 0)

## Contents
`preferred_tools`: task type → tool id (messaging → whatsapp_web, email → gmail, notes → apple_notes on macOS, code → vscode, web → browser). Every value must exist in the [tool registry](tool-registry.md). Will feed strategy selection in the [brain](../modules/brain.md).

## Unknowns
Defaults are inferred from README examples; the spec doesn't list preferences explicitly.
