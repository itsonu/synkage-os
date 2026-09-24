#!/usr/bin/env python3
"""Start the Synkage CLI: python scripts/run_synkage.py [status|version] [--config-dir DIR]."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from synkage.interfaces.cli import app  # noqa: E402

if __name__ == "__main__":
    app()
