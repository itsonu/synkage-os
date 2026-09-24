#!/usr/bin/env python3
"""Map changed source files to the OKF concepts that describe them.

Reads the set of changed files from --files, or --since <ref>, or (default) the
last commit. Prints affected concepts (need updating), uncovered new files
(candidate new concepts), and dangling references (source deleted but still
declared). Emit --json to drive an agent update pass. --check exits nonzero when
any concept is affected (for git hooks / CI gating).

Usage:
  python okf_sync.py --repo . --bundle docs/okf --since HEAD~1
  python okf_sync.py --repo . --bundle docs/okf --files src/a.js src/b.js
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import okf_common as ok

# source extensions we consider "code" for uncovered-file suggestions
CODE_EXT = {".js", ".ts", ".jsx", ".tsx", ".dart", ".py", ".go", ".rs",
            ".java", ".kt", ".rb", ".php", ".sql", ".sol", ".c", ".cpp",
            ".cs", ".swift", ".m", ".mm"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--bundle", default="docs/okf")
    ap.add_argument("--since", default=None, help="git ref; diff since..HEAD")
    ap.add_argument("--files", nargs="*", default=None, help="explicit changed files")
    ap.add_argument("--check", action="store_true", help="exit 1 if any concept affected")
    ap.add_argument("--json", action="store_true", help="emit JSON report")
    args = ap.parse_args()

    repo = os.path.abspath(args.repo)
    bundle_rel = args.bundle
    bundle = os.path.abspath(os.path.join(repo, bundle_rel)) if not os.path.isabs(bundle_rel) else bundle_rel

    if args.files is not None:
        changed = args.files
    else:
        changed = ok.git_changed_files(repo, since=args.since)

    src_index = ok.build_source_index(bundle)  # src path -> [concepts]
    declared_sources = set(src_index.keys())

    affected = {}            # concept -> [source files that changed]
    uncovered = []           # changed code files with no concept
    for f in changed:
        f = f.replace(os.sep, "/")
        # ignore changes inside the bundle itself
        if f.startswith(bundle_rel.replace(os.sep, "/").rstrip("/") + "/"):
            continue
        if f in src_index:
            for c in src_index[f]:
                affected.setdefault(c, []).append(f)
        else:
            if os.path.splitext(f)[1] in CODE_EXT:
                uncovered.append(f)

    dangling = sorted(s for s in declared_sources if not ok.source_exists(repo, s))

    report = {
        "changed_files": changed,
        "affected_concepts": {k: sorted(v) for k, v in sorted(affected.items())},
        "uncovered_new_files": sorted(uncovered),
        "dangling_sources": dangling,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"OKF sync: {len(changed)} changed file(s) vs bundle {bundle_rel}")
        if affected:
            print("Affected concepts (update body + timestamp):")
            for c, fs in sorted(affected.items()):
                print(f"  * {c}  <- {', '.join(fs)}")
        if uncovered:
            print("Uncovered new code files (consider a concept):")
            for f in uncovered:
                print(f"  + {f}")
        if dangling:
            print("Dangling sources (deleted but still declared):")
            for s in dangling:
                print(f"  ! {s}")
        if not (affected or uncovered or dangling):
            print("  clean — no concept impact detected")

    if args.check and (affected or dangling):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
