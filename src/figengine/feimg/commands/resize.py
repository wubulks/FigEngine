"""
Resize command implementation.

This module contains only execution logic and is independent from CLI parser
details. The Typer layer in `main.py` passes parameters directly to `execute`.
"""

from __future__ import annotations

from typing import Optional

from ._utils import parse_scale, prepare_output, require_figengine


def execute(
    *,
    input_path: str,
    output: str,
    width: Optional[float],
    height: Optional[float],
    scale: Optional[str],
    ref_image: Optional[str],
    unit: Optional[str],
    resample: Optional[str],
    dpi: Optional[int],
    overwrite: bool,
    config,
    logger,
) -> None:
    """
    Execute image resize.

    At least one of width/height/scale must be provided.
    """

    if width is None and height is None and scale is None and ref_image is None:
        raise ValueError("resize requires --width, --height, --scale, or --ref-image.")

    fe = require_figengine()
    output_path = prepare_output(output, overwrite=bool(overwrite or config.overwrite))
    resolved_dpi = dpi if dpi is not None else config.dpi
    resolved_unit = unit or config.unit

    logger.info("Loading image: %s", input_path)
    img = fe.Image(source=input_path, dpi=resolved_dpi)
    ref_img = fe.Image(source=ref_image, dpi=resolved_dpi) if ref_image else None

    kwargs = {
        "width": width,
        "height": height,
        "scale": parse_scale(scale),
        "ref_image": ref_img,
        "unit": resolved_unit,
    }
    if resample:
        kwargs["resample"] = resample

    logger.info("Resizing image -> width=%s, height=%s, scale=%s", width, height, scale)
    out = img.resize(**kwargs)
    out.save(str(output_path))
    logger.info("Saved: %s", output_path)
