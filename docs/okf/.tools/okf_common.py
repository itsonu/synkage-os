"""Shared helpers for the OKF maintainer scripts.

Stdlib-only. The four scripts (okf_lint / okf_sync / okf_graph) import this,
so keep them together when vendoring into a repo (e.g. docs/okf/.tools/).
Frontmatter is parsed with a minimal tolerant parser so no PyYAML is required
and the bundle stays "just files".
"""
import os
import re
import subprocess
from datetime import datetime, timezone

RESERVED = {"index.md", "log.md"}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _strip_quotes(s):
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def parse_frontmatter(text):
    """Return (frontmatter_dict, body_str). Empty dict if no frontmatter."""
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    # first line is '---'; find the closing '---'
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text
    fm_lines = lines[1:end]
    body = "\n".join(lines[end + 1:])
    fm = {}
    key = None
    for raw in fm_lines:
        if not raw.strip():
            continue
        # block-list item
        m = re.match(r"^\s+-\s+(.*)$", raw)
        if m and key is not None and isinstance(fm.get(key), list):
            fm[key].append(_strip_quotes(m.group(1)))
            continue
        m = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.*)$", raw)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val == "":
            # could be a block list or empty; assume list until proven scalar
            fm[key] = []
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            fm[key] = [_strip_quotes(x) for x in inner.split(",") if x.strip()] if inner else []
        else:
            fm[key] = _strip_quotes(val)
    return fm, body


def iter_concepts(bundle_root):
    """Yield (abs_path, rel_path_from_bundle, frontmatter, body) for every .md."""
    for dirpath, _dirs, files in os.walk(bundle_root):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            ap = os.path.join(dirpath, fn)
            rel = os.path.relpath(ap, bundle_root).replace(os.sep, "/")
            try:
                with open(ap, "r", encoding="utf-8") as f:
                    text = f.read()
            except (OSError, UnicodeDecodeError):
                continue
            fm, body = parse_frontmatter(text)
            yield ap, rel, fm, body


def extract_links(body, bundle_root, concept_abs):
    """Return list of internal link targets as bundle-relative paths.

    Leading '/' means relative to bundle root; otherwise relative to the
    concept's own directory. http(s)/mailto/anchor-only links are skipped.
    """
    out = []
    concept_dir = os.path.dirname(concept_abs)
    for target in LINK_RE.findall(body):
        t = target.split("#")[0].strip()
        if not t or t.startswith(("http://", "https://", "mailto:")):
            continue
        if t.startswith("/"):
            abs_t = os.path.normpath(os.path.join(bundle_root, t.lstrip("/")))
        else:
            abs_t = os.path.normpath(os.path.join(concept_dir, t))
        rel = os.path.relpath(abs_t, bundle_root).replace(os.sep, "/")
        out.append(rel)
    return out


def parse_ts(value):
    """Parse an ISO-8601 timestamp to aware UTC datetime, or None."""
    if not value:
        return None
    v = value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(v)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def source_mtime(repo_root, rel_path, use_git=False):
    """Return aware UTC datetime of a source file's last change, or None."""
    abs_path = os.path.join(repo_root, rel_path)
    if use_git:
        try:
            out = subprocess.run(
                ["git", "-C", repo_root, "log", "-1", "--format=%cI", "--", rel_path],
                capture_output=True, text=True, timeout=15,
            )
            iso = out.stdout.strip()
            if iso:
                return parse_ts(iso)
        except (subprocess.SubprocessError, OSError):
            pass
    if os.path.exists(abs_path):
        return datetime.fromtimestamp(os.path.getmtime(abs_path), tz=timezone.utc)
    return None


def source_exists(repo_root, rel_path):
    return os.path.exists(os.path.join(repo_root, rel_path))


def git_changed_files(repo_root, since=None):
    """List changed files. If since given: diff since..HEAD; else last commit."""
    rng = f"{since}..HEAD" if since else "HEAD~1..HEAD"
    try:
        out = subprocess.run(
            ["git", "-C", repo_root, "diff", "--name-only", rng],
            capture_output=True, text=True, timeout=15,
        )
        files = [l.strip() for l in out.stdout.splitlines() if l.strip()]
        return files
    except (subprocess.SubprocessError, OSError):
        return []


def build_source_index(bundle_root):
    """Map repo-relative source path -> [concept rel paths that declare it]."""
    idx = {}
    for _ap, rel, fm, _body in iter_concepts(bundle_root):
        for src in fm.get("sources", []) or []:
            idx.setdefault(src, []).append(rel)
    return idx
