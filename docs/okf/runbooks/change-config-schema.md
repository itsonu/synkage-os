---
type: Runbook
title: Change the tool registry schema
description: Keep the committed JSON Schema in sync with the pydantic model.
timestamp: 2026-09-24T18:48:53Z
---

## Steps
1. Edit `Tool` / `ToolRegistry` in `synkage/config.py` ([config loader](../modules/config-loader.md)).
2. `python scripts/gen_schema.py` → rewrites `config/schema/tool_registry.schema.json`.
3. `python -m pytest -q` — `test_committed_schema_matches_model` fails if you skip step 2.
4. Update [tool registry](../data-models/tool-registry.md).
