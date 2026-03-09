"""
Rotate command implementation.
"""

from __future__ import annotations

from typing import Optional

from ._utils import prepare_output, require_figengine


def execute(
    *,
    input_path: str,
    output: str,
    angle: float,
    expand: bool,
    bg_color: Optional[str],
    dpi: Optional[int],
    overwrite: bool,
    config,
    logger,
) -> None:
    """
    Execute image rotation.
    """

    fe = require_figengine()
    output_path = prepare_output(output, overwrite=bool(overwrite or config.overwrite))
    resolved_dpi = dpi if dpi is not None else config.dpi
    resolved_bg_color = bg_color or config.bg_color

    logger.info("Loading image: %s", input_path)
    img = fe.Image(source=input_path, dpi=resolved_dpi)
    logger.info("Rotating image -> angle=%s, expand=%s", angle, expand)
    out = img.rotate(angle=angle, expand=expand, bg_color=resolved_bg_color)
    out.save(str(output_path))
    logger.info("Saved: %s", output_path)
