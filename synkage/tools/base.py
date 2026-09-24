"""What every tool controller returns. Controllers take plain arguments (a name,
a text) and know nothing about intents, autonomy, or adapters; the local_exec
adapter translates an ActionRequest into a controller call.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ControllerResult(BaseModel):
    ok: bool
    message: str
    output: dict[str, Any] = Field(default_factory=dict)
