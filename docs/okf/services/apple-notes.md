---
type: Integration
title: Apple Notes
description: Native macOS notes via osascript.
timestamp: 2026-09-24T19:40:06Z
sources:
  - synkage/tools/desktop/apple_notes.py
---

## Status
built; tested with a faked `osascript` on Linux. **The real-Mac check is pending** (`SYNKAGE_MANUAL=1`, see [manual checks](../runbooks/phase5-manual-checks.md)).

## Flow
`osascript -e 'on run argv' -e 'tell application "Notes"' -e 'make new note with properties {name:(item 1 of argv), body:(item 2 of argv)}' … <title> <html>`. The title and HTML body are **arguments**, never part of the script. The body is HTML: `<h1>` title plus a `<ul>` when the note is all bullets. The first run makes macOS ask for permission to control Notes. Off macOS it refuses without running anything.

## Connections
Driven by `AppleNotesHandler` in the [adapters](../modules/adapters.md). It uses the builder's `note` (from the `format_note` [skill](../modules/skills.md)) when present. Registry id `apple_notes`; this is the macOS notes preference ([app preferences](../data-models/app-preferences.md)).
