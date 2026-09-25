#!/usr/bin/env python3
"""Run the night cycle once (for cron/launchd), or keep running it daily.

python scripts/nightly_update.py              # once, then exit 0
python scripts/nightly_update.py --schedule   # stay up; run daily at memory.yaml schedule
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from apscheduler.schedulers.blocking import BlockingScheduler  # noqa: E402
from apscheduler.triggers.cron import CronTrigger  # noqa: E402

from synkage.config import ConfigError, SynkageConfig, load_config  # noqa: E402
from synkage.memory.night_cycle import NightCycle  # noqa: E402
from synkage.memory.store import MemoryStore  # noqa: E402

JOB_ID = "night_cycle"


def run_once(config: SynkageConfig) -> int:
    report = NightCycle(MemoryStore(config)).run()
    print(
        f"night cycle: trust {report.trust_before:.3f} -> {report.trust_after:.3f} "
        f"(outcomes {report.outcomes or 'none'}); compressed {report.compressed_records} record(s), "
        f"kept {report.kept_records}"
    )
    return 0


def build_scheduler(config: SynkageConfig, scheduler=None):
    """Scheduler with the night-cycle job registered (not started)."""
    scheduler = scheduler or BlockingScheduler()
    s = config.memory.schedule
    scheduler.add_job(
        run_once, CronTrigger(hour=s.hour, minute=s.minute), args=[config], id=JOB_ID, replace_existing=True
    )
    return scheduler


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--schedule", action="store_true", help="stay running; run the cycle daily")
    ap.add_argument("--config-dir", default=None)
    args = ap.parse_args(argv)
    try:
        config = load_config(args.config_dir)
    except ConfigError as e:
        print(f"config error: {e}", file=sys.stderr)
        return 1
    if not args.schedule:
        return run_once(config)
    s = config.memory.schedule
    print(f"night cycle scheduled daily at {s.hour:02d}:{s.minute:02d}; Ctrl-C to stop")
    try:
        build_scheduler(config).start()
    except (KeyboardInterrupt, SystemExit):
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
