"""
Add ticks/grid overlays to an image.
"""

from __future__ import annotations

from typing import Optional

from ._utils import prepare_output, require_figengine


def execute(
    *,
    input_path: str,
    output: str,
    step: float,
    unit: Optional[str],
    color: str,
    font: str,
    fontsize: float,
    show_grid: bool,
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
    out = img.add_ticks(
        step=step,
        unit=resolved_unit,
        color=color,
        font=font,
        fontsize=fontsize,
        show_grid=show_grid,
    )
    out.save(str(output_path))
    logger.info("Saved: %s", output_path)
