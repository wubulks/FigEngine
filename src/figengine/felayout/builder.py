"""
Figure construction from a declarative layout spec.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import figengine as fe

from .spec import ordered_rows, validate_layout_spec


def _resolve_item(item: Any, base_dir: Path) -> str:
    if isinstance(item, str):
        path = Path(item)
    elif isinstance(item, dict) and isinstance(item.get("path"), str):
        path = Path(item["path"])
    else:
        raise ValueError(f"Unsupported item value: {item!r}")

    if path.is_absolute():
        return str(path)
    return str((base_dir / path).resolve())


def build_figure(spec: Dict[str, Any], *, base_dir: Path) -> fe.Figure:
    validate_layout_spec(spec)

    figure_cfg = spec.get("figure", {})
    fig = fe.Figure(
        background=figure_cfg.get("background", "#FFFFFF"),
        dpi=figure_cfg.get("dpi", 600),
        width=figure_cfg.get("width", 0),
        height=figure_cfg.get("height", 0),
        unit=figure_cfg.get("unit", "inch"),
    )

    margins = figure_cfg.get("margins")
    if margins:
        fig.set_margins(
            margins=margins,
            unit=figure_cfg.get("margins_unit", "ratio"),
        )

    for row in ordered_rows(spec):
        items: List[str] = [_resolve_item(item, base_dir) for item in row["items"]]
        fig.add_row(
            items=items,
            left_gaps=row.get("left_gaps", 0),
            right_gaps=row.get("right_gaps", 0.01),
            top_margin=row.get("top_margin", 0),
            bottom_margin=row.get("bottom_margin", 0),
            unit=row.get("unit", "ratio"),
            v_align=row.get("v_align", "top"),
            h_align=row.get("h_align", "full"),
        )
    return fig


def build_and_save(
    spec: Dict[str, Any],
    *,
    layout_path: Path,
    output_override: Optional[str] = None,
    overwrite: bool = False,
) -> Path:
    fig = build_figure(spec, base_dir=layout_path.parent)

    output_cfg = spec.get("output", {})
    output_path = Path(output_override or output_cfg.get("path", "layout.png"))
    if not output_path.is_absolute():
        output_path = (layout_path.parent / output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output file already exists: {output_path}")

    save_kwargs = output_cfg.get("save_kwargs", {})
    fig.save(str(output_path), **save_kwargs)
    return output_path
