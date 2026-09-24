---
type: Runbook
title: Phase 5 manual checks (on your Mac)
description: Verify WhatsApp, Gmail and Apple Notes against the real apps before enabling tools.
timestamp: 2026-09-24T19:40:06Z
---

These steps use **your real accounts**, so only you run them. Test with yourself as the recipient.

## 0. Setup
```bash
git pull && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp -r config ~/synkage-config      # a private copy, so enabling tools doesn't touch the repo yet
```
In `~/synkage-config/tool_registry.json`, set `"enabled": true` for `whatsapp_web`, `gmail` and `apple_notes`.

## 1. Apple Notes (phase-05 ac-4)
```bash
SYNKAGE_MANUAL=1 python -m pytest tests/test_apple_notes.py::test_real_apple_notes_on_macos -q
```
Allow Terminal to control Notes when macOS asks. **Pass:** a note "Synkage test note" appears in Notes. Then try the pipeline:
```bash
python scripts/run_synkage.py --config-dir ~/synkage-config run "save note buy milk; call mom"
```
Type `yes`. **Pass:** a note "Note (2 items)" with two bullets.

## 2. Sign in once
```bash
python scripts/run_synkage.py login
```
Scan the WhatsApp QR code and sign in to Gmail in the window that opens, then press Enter. The login stays in `~/.synkage/browser-profile`.

## 3. WhatsApp (phase-05 ac-2)
Use your own number (the "Message yourself" chat):
```bash
python scripts/run_synkage.py --config-dir ~/synkage-config run "send message to +<your number>: synkage test 1"
```
- **Pass A:** the draft appears in WhatsApp and the terminal waits at `Type 'yes'`. Type `no`: the draft is cleared and **nothing is sent**.
- Run it again with `synkage test 2` and type `yes`. **Pass B:** exactly that message is sent.
- Optional: repeat with a contact **name** instead of a number (this tests the search selectors).

## 4. Gmail (phase-05 ac-3)
```bash
python scripts/run_synkage.py --config-dir ~/synkage-config run "send email to <your address>: synkage test"
```
Type `yes`. **Pass:** a draft appears in Gmail **Drafts**, and nothing in **Sent**.

## 5. Report back
For each step: pass/fail, plus the `Execution: …` line. If a step times out, say which one. The WhatsApp/Gmail selectors are unverified and may need a fix. `logs.jsonl` has the audit trail. Once all checks pass, the tools get enabled in the repo (ac-5).
