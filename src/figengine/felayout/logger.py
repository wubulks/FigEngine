"""
Logging helpers for felayout.
"""

from __future__ import annotations

import logging


def setup_logger(level: str = "WARNING") -> logging.Logger:
    logger = logging.getLogger("felayout")
    logger.setLevel(getattr(logging, level.upper(), logging.WARNING))

    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)
    return logger
