"""Logging: one rich handler on stderr so stdout stays clean for command output."""

from __future__ import annotations

import logging
import os

from rich.console import Console
from rich.logging import RichHandler

LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


def setup_logging(level: str | None = None) -> logging.Logger:
    """Configure the 'synkage' logger. Level: arg > SYNKAGE_LOG_LEVEL > INFO."""
    name = (level or os.environ.get("SYNKAGE_LOG_LEVEL") or "INFO").upper()
    if name not in LEVELS:
        name = "INFO"
    logger = logging.getLogger("synkage")
    logger.setLevel(name)
    logger.handlers.clear()
    handler = RichHandler(console=Console(stderr=True), show_path=False, rich_tracebacks=True)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger
