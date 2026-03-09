"""
Pad command implementation.
"""

from __future__ import annotations

from typing import Optional, Tuple

from ._utils import prepare_output, require_figengine


def execute(
    *,
    input_path: str,
    output: str,
    target_size: Optional[Tuple[float, float]],
    target_width: Optional[float],
    target_height: Optional[float],
    unit: Optional[str],
    loc: str,
    axis: Optional[str],
    bg_color: Optional[str],
    dpi: Optional[int],
    overwrite: bool,
    config,
    logger,
) -> None:
    """
    Execute image padding to a target canvas size.
    """

    fe = require_figengine()
    output_path = prepare_output(output, overwrite=bool(overwrite or config.overwrite))
    resolved_dpi = dpi if dpi is not None else config.dpi
    resolved_unit = unit or config.unit
    resolved_bg_color = bg_color or config.bg_color
    resolved_target_size = target_size

    if resolved_target_size is None:
        if target_width is None or target_height is None:
            raise ValueError("pad requires --target-size W H or both --target-width and --target-height.")
        resolved_target_size = (target_width, target_height)

    logger.info("Loading image: %s", input_path)
    img = fe.Image(source=input_path, dpi=resolved_dpi)

    kwargs = {
        "target_size": resolved_target_size,
        "unit": resolved_unit,
        "loc": loc,
        "bg_color": resolved_bg_color,
    }
    if axis:
        kwargs["axis"] = axis

    logger.info(
        "Padding image -> target_size=(%s, %s), unit=%s, loc=%s",
        resolved_target_size[0],
        resolved_target_size[1],
        resolved_unit,
        loc,
    )
    out = img.pad_to_size(**kwargs)
    out.save(str(output_path))
    logger.info("Saved: %s", output_path)
