"""
Add text annotations to an image.
"""

from __future__ import annotations

from typing import Optional

from ._utils import parse_json_dict, parse_scalar_or_pair, prepare_output, require_figengine


def execute(
    *,
    input_path: str,
    output: str,
    text: str,
    x: Optional[float],
    y: Optional[float],
    loc: str,
    anchor: Optional[str],
    offset: Optional[str],
    unit: Optional[str],
    font: str,
    fontsize: float,
    fontweight: str,
    rotation: float,
    color: str,
    box_style: Optional[str],
    dpi: Optional[int],
    overwrite: bool,
    config,
    logger,
) -> None:
    fe = require_figengine()
    output_path = prepare_output(output, overwrite=bool(overwrite or config.overwrite))
    resolved_dpi = dpi if dpi is not None else config.dpi
    resolved_unit = unit or "ratio"

    logger.info("Loading image: %s", input_path)
    img = fe.Image(source=input_path, dpi=resolved_dpi)

    kwargs = {
        "text": text,
        "loc": loc,
        "unit": resolved_unit,
        "font": font,
        "fontsize": fontsize,
        "fontweight": fontweight,
        "rotation": rotation,
        "color": color,
        "dpi": resolved_dpi,
    }
    if x is not None:
        kwargs["x"] = x
    if y is not None:
        kwargs["y"] = y
    if anchor is not None:
        kwargs["anchor"] = anchor
    parsed_offset = parse_scalar_or_pair(offset)
    if parsed_offset is not None:
        kwargs["offset"] = parsed_offset
    parsed_box_style = parse_json_dict(box_style, arg_name="--box-style")
    if parsed_box_style is not None:
        kwargs["box_style"] = parsed_box_style

    out = img.add_text(**kwargs)
    out.save(str(output_path))
    logger.info("Saved: %s", output_path)
