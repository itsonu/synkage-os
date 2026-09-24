#!/usr/bin/env python3
"""Regenerate config/schema/tool_registry.schema.json from the pydantic model.

Run after changing Tool/ToolRegistry in synkage/config.py; tests fail until you do.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from synkage.config import tool_registry_json_schema  # noqa: E402

OUT = ROOT / "config" / "schema" / "tool_registry.schema.json"

if __name__ == "__main__":
    OUT.write_text(json.dumps(tool_registry_json_schema(), indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
