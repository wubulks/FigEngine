"""
Add a line or arrow to an image.
"""

from __future__ import annotations

from typing import Optional, Tuple

from ._utils import prepare_output, require_figengine


def execute(
    *,
    input_path: str,
    output: str,
    start: Tuple[float, float],
    end: Tuple[float, float],
    unit: Optional[str],
    color: str,
    width: float,
    arrow: Optional[str],
    arrow_size: Optional[float],
    arrow_style: Optional[str],
    arrow_angle: Optional[float],
    arrow_shorten: Optional[float],
    arrow_fill: Optional[bool],
    dpi: Optional[int],
    overwrite: bool,
    config,
    logger,
) -> None:
    fe = require_figengine()
    output_path = prepare_output(output, overwrite=bool(overwrite or config.overwrite))
    resolved_unit = unit or "ratio"
    resolved_dpi = dpi if dpi is not None else config.dpi

    logger.info("Loading image: %s", input_path)
    img = fe.Image(source=input_path, dpi=resolved_dpi)
    kwargs = {
        "start": start,
        "end": end,
        "unit": resolved_unit,
        "color": color,
        "width": width,
    }
    if arrow is not None:
        kwargs["arrow"] = arrow
    if arrow_size is not None:
        kwargs["arrow_size"] = arrow_size
    if arrow_style is not None:
        kwargs["arrow_style"] = arrow_style
    if arrow_angle is not None:
        kwargs["arrow_angle"] = arrow_angle
    if arrow_shorten is not None:
        kwargs["arrow_shorten"] = arrow_shorten
    if arrow_fill is not None:
        kwargs["arrow_fill"] = arrow_fill

    out = img.add_line(**kwargs)
    out.save(str(output_path))
    logger.info("Saved: %s", output_path)
