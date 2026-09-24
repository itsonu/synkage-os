---
type: Runbook
title: Local setup
description: Install, run, and test Synkage locally.
timestamp: 2026-09-24T18:48:53Z
---

## Steps
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt ruff
playwright install            # browser binaries; needed from Phase 5
cp .env.example .env          # optional overrides
python scripts/run_synkage.py # prints system state
python -m pytest -q
ruff check . && ruff format --check .
```
Starts the [startup flow](../flows/startup.md).
