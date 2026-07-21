"""Central logging configuration. Call configure_logging() once from the CLI."""

from __future__ import annotations

import logging

from rich.console import Console
from rich.logging import RichHandler

_CONFIGURED = False


def configure_logging(level: str = "INFO") -> None:
    """Configure application logging once. Safe to call repeatedly."""
    global _CONFIGURED

    root = logging.getLogger()
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    if _CONFIGURED:
        root.setLevel(numeric_level)
        for handler in root.handlers:
            handler.setLevel(numeric_level)
        return

    root.handlers.clear()
    root.setLevel(numeric_level)

    handler = RichHandler(
        console=Console(stderr=True),
        show_path=False,
        rich_tracebacks=True,
        markup=True,
    )
    handler.setLevel(numeric_level)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root.addHandler(handler)
    _CONFIGURED = True
