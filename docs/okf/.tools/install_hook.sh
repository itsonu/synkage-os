#!/usr/bin/env bash
# Install OKF git hooks.
#
#   post-commit : runs okf_sync.py --check on the commit's changed files and
#                 prints an assertive stale report. If OKF_AUTO_UPDATE=1 is set
#                 in the environment, it shells out to `claude -p` to update the
#                 affected concepts (off by default — auto-rewrite is powerful
#                 but should be opted into consciously).
#   pre-push    : (with --with-pre-push) runs okf_lint.py --strict --git and
#                 blocks the push if the bundle has drifted.
#
# Usage:
#   bash install_hook.sh --repo . --bundle docs/okf [--with-pre-push]
#
# The scripts must be reachable at runtime. By default the hook calls them via
# their vendored location docs/okf/.tools/ — copy okf_*.py there, or edit
# TOOLS_DIR below to point at wherever they live.
set -euo pipefail

REPO="."
BUNDLE="docs/okf"
WITH_PRE_PUSH=0
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) REPO="$2"; shift 2;;
    --bundle) BUNDLE="$2"; shift 2;;
    --with-pre-push) WITH_PRE_PUSH=1; shift;;
    *) echo "unknown arg: $1"; exit 2;;
  esac
done

REPO="$(cd "$REPO" && pwd)"
HOOKS="$REPO/.git/hooks"
if [ ! -d "$HOOKS" ]; then
  echo "ERROR: $HOOKS not found — is this a git repo?"; exit 2
fi

TOOLS_DIR="$BUNDLE/.tools"   # relative to repo root at hook runtime

cat > "$HOOKS/post-commit" <<HOOK
#!/usr/bin/env bash
# OKF post-commit: detect stale concepts for this commit.
set -euo pipefail
BUNDLE="$BUNDLE"
TOOLS="$TOOLS_DIR"
CHANGED=\$(git diff --name-only HEAD~1..HEAD 2>/dev/null || true)
if [ -z "\$CHANGED" ]; then exit 0; fi
REPORT=\$(python "\$TOOLS/okf_sync.py" --repo . --bundle "\$BUNDLE" --since HEAD~1 || true)
if echo "\$REPORT" | grep -q "Affected concepts"; then
  echo "──────── OKF DRIFT ────────"
  echo "\$REPORT"
  echo "These OKF concepts describe files you just changed and are now stale."
  if [ "\${OKF_AUTO_UPDATE:-0}" = "1" ] && command -v claude >/dev/null 2>&1; then
    echo "OKF_AUTO_UPDATE=1 → updating concepts with claude -p ..."
    JSON=\$(python "\$TOOLS/okf_sync.py" --repo . --bundle "\$BUNDLE" --since HEAD~1 --json)
    printf '%s' "\$JSON" | claude -p "You maintain an OKF knowledge bundle at \$BUNDLE. The JSON on stdin lists concepts whose source files changed in the last commit. For each affected concept: read the listed source files, update the concept body to match current behaviour, refresh the timestamp to now (ISO-8601 UTC), and fix any broken links. Ground everything in the real code; record anything unverifiable under a ## Unknowns section. Do not touch unaffected concepts. Then run the linter. Keep edits tight."
  else
    echo "Fix them (or set OKF_AUTO_UPDATE=1 for headless auto-fix)."
  fi
  echo "───────────────────────────"
fi
exit 0
HOOK
chmod +x "$HOOKS/post-commit"
echo "installed: .git/hooks/post-commit"

if [ "$WITH_PRE_PUSH" = "1" ]; then
  cat > "$HOOKS/pre-push" <<HOOK
#!/usr/bin/env bash
# OKF pre-push: block push if the bundle has drifted.
set -euo pipefail
python "$TOOLS_DIR/okf_lint.py" --repo . --bundle "$BUNDLE" --strict --git
HOOK
  chmod +x "$HOOKS/pre-push"
  echo "installed: .git/hooks/pre-push"
fi

echo
echo "NOTE: hooks call the scripts at $TOOLS_DIR/ — make sure okf_*.py are copied there:"
echo "  mkdir -p $BUNDLE/.tools && cp okf_common.py okf_lint.py okf_sync.py $BUNDLE/.tools/"
