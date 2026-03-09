"""
Add a rectangle to an image.
"""

from __future__ import annotations

from typing import Optional, Tuple

from ._utils import prepare_output, require_figengine


def execute(
    *,
    input_path: str,
    output: str,
    start: Optional[Tuple[float, float]],
    end: Optional[Tuple[float, float]],
    center: Optional[Tuple[float, float]],
    size: Optional[Tuple[float, float]],
    unit: Optional[str],
    linewidth: float,
    color: Optional[str],
    edgecolor: Optional[str],
    facecolor: Optional[str],
    fill: bool,
    dpi: Optional[int],
    overwrite: bool,
    config,
    logger,
) -> None:
    if (start is None) != (end is None):
        raise ValueError("--start and --end must be provided together.")
    if (center is None) != (size is None):
        raise ValueError("--center and --size must be provided together.")
    if start is None and center is None:
        raise ValueError("Provide either --start/--end or --center/--size.")

    fe = require_figengine()
    output_path = prepare_output(output, overwrite=bool(overwrite or config.overwrite))
    resolved_unit = unit or "ratio"
    resolved_dpi = dpi if dpi is not None else config.dpi

    logger.info("Loading image: %s", input_path)
    img = fe.Image(source=input_path, dpi=resolved_dpi)
    kwargs = {
        "unit": resolved_unit,
        "linewidth": linewidth,
        "fill": fill,
    }
    if start is not None:
        kwargs["start"] = start
        kwargs["end"] = end
    if center is not None:
        kwargs["center"] = center
        kwargs["size"] = size
    if color is not None:
        kwargs["color"] = color
    if edgecolor is not None:
        kwargs["edgecolor"] = edgecolor
    if facecolor is not None:
        kwargs["facecolor"] = facecolor

    out = img.add_rect(**kwargs)
    out.save(str(output_path))
    logger.info("Saved: %s", output_path)
