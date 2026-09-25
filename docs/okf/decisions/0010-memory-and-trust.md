---
type: Decision
title: ADR-0010 Memory outside the repo; trust from outcomes; lossless compression
description: Where personal memory lives, how trust moves, and what the night cycle does to old logs.
timestamp: 2026-09-25T13:38:13Z
tags: [adr, decision]
---

## Status
accepted (Phase 7). The user chose these defaults ("use your suggestions").

## Context
`docs/proj.md` puts memory files in the repo's `memory/` folder. They hold personal data (message text, trust), which must never be committed. `docs/architecture.md` lists the night-cycle tasks: log compression, pattern promotion, trust adjustment, behaviour decay.

## Decision
1. **Location:** `~/.synkage/memory/` (`SYNKAGE_MEMORY_DIR`), created owner-only (0700) on first run. The **audit log moves there too** (`logs.jsonl`); it *is* the spec's interaction log. `SYNKAGE_AUDIT_LOG` still overrides it.
2. **Trust** ∈ [0, 1], starting at neutral 0.5. Per night: decay toward neutral by `decay_per_day` per elapsed day, then add a delta per outcome logged since the last cycle: confirmed success +0.02, declined −0.03, failed −0.05. Auto-run successes don't count (they give no user signal).
3. **Trust never loosens safety.** It is stored and shown only; it is not yet wired into autonomy. When it is, it may not touch never-autonomous categories or high/critical risk.
4. **Compression is lossless:** audit records older than `retention_days` (30) become per-day summaries (`log_summaries.json`), and their raw lines go to `archive/logs-YYYY-MM.jsonl.gz`. The night cycle is the audit log's **only** rewriter, and it takes the same flock as `AuditLog.append`.

## Alternatives considered
- Repo `memory/` folder (as the spec says) — rejected: personal data next to code, one `git add -A` away from being committed.
- Delete raw records after summarizing — rejected: irreversible loss of the user's audit trail.

## Consequences
- An existing `logs.jsonl` at the repo root (from Phases 4–6) is no longer written. It stays gitignored and can be deleted by the user.
- `runs/` (agent artifacts) is unchanged, still in the repo folder (gitignored).
- Not built: pattern promotion.

## Related
[memory](../modules/memory.md), [memory store](../data-models/memory-store.md), [night cycle](../flows/night-cycle.md), [audit log](../data-models/audit-log.md).
