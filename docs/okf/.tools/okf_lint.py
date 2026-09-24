#!/usr/bin/env python3
"""Validate an OKF bundle.

Errors (always fail): missing `type`, broken internal links, `sources:` paths
that don't exist. Warnings: missing recommended fields, stale concepts, orphans.
With --strict, warnings and staleness also fail the exit code (use in CI /
pre-push). With --git, staleness uses the source's last git-commit time.

Usage:
  python okf_lint.py --repo . --bundle docs/okf [--strict] [--git]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import okf_common as ok

RECOMMENDED = ["title", "description", "timestamp"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--bundle", default="docs/okf")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--git", action="store_true")
    args = ap.parse_args()

    repo = os.path.abspath(args.repo)
    bundle = os.path.abspath(os.path.join(repo, args.bundle)) if not os.path.isabs(args.bundle) else args.bundle
    if not os.path.isdir(bundle):
        print(f"ERROR: bundle not found: {bundle}")
        return 2

    errors, warnings = [], []
    all_concepts = {}
    link_graph = {}

    for ap_, rel, fm, body in ok.iter_concepts(bundle):
        all_concepts[rel] = fm
        fn = os.path.basename(rel)

        if fn not in ok.RESERVED and "type" not in fm:
            errors.append(f"{rel}: missing required `type`")

        if fn not in ok.RESERVED:
            for field in RECOMMENDED:
                if field not in fm:
                    warnings.append(f"{rel}: missing recommended `{field}`")

        # link resolution
        targets = ok.extract_links(body, bundle, ap_)
        link_graph[rel] = targets
        for t in targets:
            if not os.path.exists(os.path.join(bundle, t)):
                errors.append(f"{rel}: broken link -> {t}")

        # sources existence + staleness
        srcs = fm.get("sources", []) or []
        ts = ok.parse_ts(fm.get("timestamp"))
        for src in srcs:
            if not ok.source_exists(repo, src):
                errors.append(f"{rel}: source not found -> {src}")
                continue
            smt = ok.source_mtime(repo, src, use_git=args.git)
            if ts and smt and smt > ts:
                warnings.append(f"{rel}: STALE — source `{src}` changed after timestamp")
            elif not ts and srcs:
                warnings.append(f"{rel}: has sources but no timestamp (can't check staleness)")

    # orphan detection (no inbound and no outbound links), excluding reserved files
    inbound = {rel: 0 for rel in all_concepts}
    for _src, targets in link_graph.items():
        for t in targets:
            if t in inbound:
                inbound[t] += 1
    for rel in all_concepts:
        if os.path.basename(rel) in ok.RESERVED:
            continue
        out = len(link_graph.get(rel, []))
        if inbound.get(rel, 0) == 0 and out == 0:
            warnings.append(f"{rel}: orphan — no links in or out")

    print(f"OKF lint: {len(all_concepts)} concept file(s) in {args.bundle}")
    for e in errors:
        print(f"  ERROR   {e}")
    for w in warnings:
        print(f"  WARN    {w}")
    print(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s)")

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
