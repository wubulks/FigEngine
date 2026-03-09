"""
Crop command implementation.

Supports two modes:
1) Box mode via `box=(left, top, right, bottom)`
2) Trim mode via `left/top/right/bottom`
"""

from __future__ import annotations

from typing import Optional, Tuple

from ._utils import prepare_output, require_figengine


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
    Execute image crop.
    """

    fe = require_figengine()
    output_path = prepare_output(output, overwrite=bool(overwrite or config.overwrite))
    resolved_dpi = dpi if dpi is not None else config.dpi
    resolved_unit = unit or config.unit

    logger.info("Loading image: %s", input_path)
    img = fe.Image(source=input_path, dpi=resolved_dpi)

    if box:
        logger.info("Cropping by box mode: %s", box)
        out = img.crop(box=tuple(box), unit=resolved_unit)
    else:
        logger.info(
            "Cropping by trim mode: left=%s top=%s right=%s bottom=%s",
            left,
            top,
            right,
            bottom,
        )
        out = img.crop(
            left=left,
            top=top,
            right=right,
            bottom=bottom,
            unit=resolved_unit,
        )

    out.save(str(output_path))
    logger.info("Saved: %s", output_path)
