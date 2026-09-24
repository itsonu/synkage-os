#!/usr/bin/env python3
"""Validate phases.json and print a status board + the next action.

Validation errors (exit 1): unknown status value; acceptance criterion with
met=true but no evidence; current_phase not found; a phase marked done/in_progress
whose depends_on aren't all done. Warnings don't fail unless --strict.

Usage:
  python phases_status.py --file docs/phases/phases.json [--strict]
"""
import argparse
import json
import os
import sys

PHASE_STATUS = {"todo", "in_progress", "done", "blocked"}
PROJ_STATUS = {"todo", "in_progress", "done", "blocked", "complete"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="docs/phases/phases.json")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.file):
        print(f"ERROR: not found: {args.file}")
        return 2
    try:
        with open(args.file, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON: {e}")
        return 1

    errors, warnings = [], []
    phases = data.get("phases", [])
    ids = {p.get("id") for p in phases}
    done_ids = {p.get("id") for p in phases if p.get("status") == "done"}

    if data.get("status") not in PROJ_STATUS:
        warnings.append(f"project status '{data.get('status')}' not in {sorted(PROJ_STATUS)}")

    cur = data.get("current_phase")
    if cur and cur not in ids:
        errors.append(f"current_phase '{cur}' not found among phases")

    for p in phases:
        pid = p.get("id", "<no-id>")
        st = p.get("status")
        if st not in PHASE_STATUS:
            errors.append(f"{pid}: status '{st}' not in {sorted(PHASE_STATUS)}")
        for dep in p.get("depends_on", []):
            if dep not in ids:
                errors.append(f"{pid}: depends_on '{dep}' not found")
            elif st in ("in_progress", "done") and dep not in done_ids:
                errors.append(f"{pid}: is '{st}' but dependency '{dep}' is not done")
        acs = p.get("acceptance_criteria", [])
        for ac in acs:
            if ac.get("met") and not ac.get("evidence"):
                errors.append(f"{pid}/{ac.get('id','?')}: met=true but no evidence")
        if st == "done" and acs and not all(ac.get("met") for ac in acs):
            errors.append(f"{pid}: marked done but not all criteria met")

    # board
    print(f"Project: {data.get('project','?')}  ·  status: {data.get('status','?')}")
    print(f"Current phase: {cur}")
    print("-" * 56)
    for p in phases:
        acs = p.get("acceptance_criteria", [])
        met = sum(1 for a in acs if a.get("met"))
        mark = {"done": "✓", "in_progress": "▶", "blocked": "✗", "todo": "·"}.get(p.get("status"), "?")
        print(f" {mark} {p.get('id'):<26} {met}/{len(acs)} criteria  [{p.get('status')}]")

    # next action
    active = next((p for p in phases if p.get("id") == cur), None)
    if active:
        nxt = next((a for a in active.get("acceptance_criteria", []) if not a.get("met")), None)
        print("-" * 56)
        if nxt:
            print(f"Next: satisfy {active['id']}/{nxt.get('id')} — {nxt.get('text')}")
        else:
            print(f"Next: all criteria met for {active['id']} — advance current_phase")

    for e in errors:
        print(f"  ERROR  {e}")
    for w in warnings:
        print(f"  WARN   {w}")

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
