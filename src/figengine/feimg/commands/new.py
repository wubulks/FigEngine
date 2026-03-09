"""
Create a new blank image.
"""

from __future__ import annotations

from typing import Optional, Tuple

from ._utils import prepare_output, require_figengine


def execute(
    *,
    output: str,
    size: Optional[Tuple[float, float]],
    width: Optional[float],
    height: Optional[float],
    facecolor: str,
    unit: Optional[str],
    dpi: Optional[int],
    label: Optional[str],
    overwrite: bool,
    config,
    logger,
) -> None:
    fe = require_figengine()
    output_path = prepare_output(output, overwrite=bool(overwrite or config.overwrite))
    resolved_unit = unit or config.unit
    resolved_dpi = dpi if dpi is not None else config.dpi
    resolved_size = size

    if resolved_size is None:
        if width is None or height is None:
            raise ValueError("new requires --size W H or both --width and --height.")
        resolved_size = (width, height)

    kwargs = {
        "size": resolved_size,
        "facecolor": facecolor,
        "unit": resolved_unit,
        "dpi": resolved_dpi,
    }
    if label is not None:
        kwargs["label"] = label

    logger.info(
        "Creating blank image -> size=(%s, %s), unit=%s, dpi=%s",
        resolved_size[0],
        resolved_size[1],
        resolved_unit,
        resolved_dpi,
    )
    img = fe.Image.new(**kwargs)
    img.save(str(output_path))
    logger.info("Saved: %s", output_path)
