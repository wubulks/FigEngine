"""
Logging helpers for feimg.

Only console logging is enabled by default.
"""

from __future__ import annotations

import logging


def setup_logger(level: str = "WARNING") -> logging.Logger:
    """
    Create and configure the app logger.

    Args:
        level: Log level string such as "DEBUG", "INFO", "WARNING", "ERROR".

    Returns:
        Configured `logging.Logger` instance named "feimg".
    """

    logger = logging.getLogger("feimg")
    logger.setLevel(getattr(logging, level.upper(), logging.WARNING))

    # Avoid duplicate handlers when main() is called multiple times in tests.
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
