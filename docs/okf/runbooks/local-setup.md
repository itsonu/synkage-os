---
type: Runbook
title: Local setup
description: Install, run, and test Synkage locally.
timestamp: 2026-09-25T13:38:13Z
---

## Steps
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt ruff
playwright install chromium   # browser for WhatsApp/Gmail and the mock-page tests
python scripts/run_synkage.py login   # sign in once (profile: ~/.synkage/browser-profile)
cp .env.example .env          # optional overrides
python scripts/run_synkage.py # prints system state
python scripts/nightly_update.py      # night cycle once (schedule it with cron/launchd, or --schedule)
python -m pytest -q
ruff check . && ruff format --check .
```
Starts the [startup flow](../flows/startup.md).
