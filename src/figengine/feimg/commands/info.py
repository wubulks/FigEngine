"""
Read and print image metadata.
"""

from __future__ import annotations

import json
from typing import Optional

import typer

from ._utils import require_figengine


def execute(
    *,
    input_path: str,
    dpi: Optional[int],
    config,
    logger,
) -> None:
    fe = require_figengine()
    resolved_dpi = dpi if dpi is not None else config.dpi

    logger.info("Loading image: %s", input_path)
    img = fe.Image(source=input_path, dpi=resolved_dpi)
    payload = {
        "size": list(img.size),
        "size_pixel": list(img.get_size("pixel")),
        "size_inch": list(img.get_size("inch")),
        "size_cm": list(img.get_size("cm")),
        "size_mm": list(img.get_size("mm")),
        "dpi": img.dpi,
        "label": getattr(img, "label", None),
    }
    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
