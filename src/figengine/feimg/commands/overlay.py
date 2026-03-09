"""
Overlay command implementation.
"""

from __future__ import annotations

from typing import Optional

from ._utils import prepare_output, require_figengine


def execute(
    *,
    input_path: str,
    other: str,
    output: str,
    x: float,
    y: float,
    anchor: str,
    unit: Optional[str],
    scale: float,
    expand: bool,
    bg_color: Optional[str],
    dpi: Optional[int],
    overwrite: bool,
    config,
    logger,
) -> None:
    """
    Execute image overlay operation.
    """

    fe = require_figengine()
    output_path = prepare_output(output, overwrite=bool(overwrite or config.overwrite))
    resolved_dpi = dpi if dpi is not None else config.dpi
    resolved_unit = unit or config.unit
    resolved_bg_color = bg_color or config.bg_color

    logger.info("Loading base image: %s", input_path)
    base = fe.Image(source=input_path, dpi=resolved_dpi)
    logger.info("Loading overlay image: %s", other)
    top = fe.Image(source=other, dpi=resolved_dpi)

    out = base.overlay(
        other=top,
        x=x,
        y=y,
        anchor=anchor,
        unit=resolved_unit,
        scale=scale,
        expand=expand,
        bg_color=resolved_bg_color,
    )
    out.save(str(output_path))
    logger.info("Saved: %s", output_path)
