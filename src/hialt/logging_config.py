"""Central logging configuration. Call configure_logging() once from the CLI."""

from __future__ import annotations

import logging

from rich.console import Console
from rich.logging import RichHandler

logger = logging.getLogger(__name__)

_HANDLER_NAME = "hialt-rich-console"


def configure_logging(level: str = "INFO") -> None:
    """Configure application logging once. Safe to call repeatedly."""
    root = logging.getLogger()
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root.setLevel(numeric_level)

    handler = next(
        (item for item in root.handlers if item.name == _HANDLER_NAME), None
    )
    if handler is None:
        handler = RichHandler(
            console=Console(stderr=True),
            show_path=False,
            rich_tracebacks=True,
            markup=True,
        )
        handler.name = _HANDLER_NAME
        handler.setFormatter(logging.Formatter("%(message)s"))
        root.addHandler(handler)
    handler.setLevel(numeric_level)
