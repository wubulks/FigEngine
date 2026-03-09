"""
Border command implementation.
"""

from __future__ import annotations

from typing import Optional

from ._utils import parse_scalar_or_quad, prepare_output, require_figengine


def execute(
    *,
    input_path: str,
    output: str,
    thickness: str,
    left: Optional[float],
    top: Optional[float],
    right: Optional[float],
    bottom: Optional[float],
    unit: Optional[str],
    color: str,
    dpi: Optional[int],
    overwrite: bool,
    config,
    logger,
) -> None:
    """
    Execute add-border operation.
    """

    fe = require_figengine()
    output_path = prepare_output(output, overwrite=bool(overwrite or config.overwrite))
    resolved_dpi = dpi if dpi is not None else config.dpi
    resolved_unit = unit or config.unit

    logger.info("Loading image: %s", input_path)
    img = fe.Image(source=input_path, dpi=resolved_dpi)
    parsed_thickness = parse_scalar_or_quad(thickness)

    kwargs = {
        "thickness": parsed_thickness,
        "unit": resolved_unit,
        "color": color,
    }
    if left is not None:
        kwargs["left"] = left
    if top is not None:
        kwargs["top"] = top
    if right is not None:
        kwargs["right"] = right
    if bottom is not None:
        kwargs["bottom"] = bottom

    logger.info("Adding border -> thickness=%s, unit=%s, color=%s", parsed_thickness, resolved_unit, color)
    out = img.add_border(**kwargs)
    out.save(str(output_path))
    logger.info("Saved: %s", output_path)
