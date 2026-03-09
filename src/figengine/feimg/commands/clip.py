"""
Clip command implementation.

`clip` is a compatibility alias of `crop`.
"""

from __future__ import annotations

from typing import Optional, Tuple

from . import crop


def execute(
    *,
    input_path: str,
    output: str,
    box: Optional[Tuple[float, float, float, float]],
    left: float,
    top: float,
    right: float,
    bottom: float,
    unit: Optional[str],
    dpi: Optional[int],
    overwrite: bool,
    config,
    logger,
) -> None:
    """
    Execute clip command by delegating to crop execution.
    """

    crop.execute(
        input_path=input_path,
        output=output,
        box=box,
        left=left,
        top=top,
        right=right,
        bottom=bottom,
        unit=unit,
        dpi=dpi,
        overwrite=overwrite,
        config=config,
        logger=logger,
    )
