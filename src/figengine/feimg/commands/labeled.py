"""
Add semantic subplot labels to an image.
"""

from __future__ import annotations

from typing import Optional

from ._utils import parse_json_dict, parse_scalar_or_pair, prepare_output, require_figengine


def execute(
    *,
    input_path: str,
    output: str,
    label: Optional[str],
    loc: str,
    offset: Optional[str],
    format_str: str,
    case: Optional[str],
    fontsize: float,
    fontweight: str,
    color: str,
    font: str,
    box_style: Optional[str],
    dpi: Optional[int],
    overwrite: bool,
    config,
    logger,
) -> None:
    fe = require_figengine()
    output_path = prepare_output(output, overwrite=bool(overwrite or config.overwrite))
    resolved_dpi = dpi if dpi is not None else config.dpi

    logger.info("Loading image: %s", input_path)
    img = fe.Image(source=input_path, dpi=resolved_dpi)

    kwargs = {
        "loc": loc,
        "format_str": format_str,
        "fontsize": fontsize,
        "fontweight": fontweight,
        "color": color,
        "font": font,
    }
    if label is not None:
        kwargs["label"] = label
    parsed_offset = parse_scalar_or_pair(offset)
    if parsed_offset is not None:
        kwargs["offset"] = parsed_offset
    if case is not None:
        kwargs["case"] = case
    parsed_box_style = parse_json_dict(box_style, arg_name="--box-style")
    if parsed_box_style is not None:
        kwargs["box_style"] = parsed_box_style

    out = img.labeled(**kwargs)
    out.save(str(output_path))
    logger.info("Saved: %s", output_path)
