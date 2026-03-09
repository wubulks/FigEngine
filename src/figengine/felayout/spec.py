"""
Layout-spec loading, validation, and normalization.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List
import yaml


TEMPLATE_SPEC: Dict[str, Any] = {
    "figure": {
        "background": "#FFFFFF",
        "dpi": 600,
        "width": 12,
        "height": 0,
        "unit": "inch",
        "margins": {
            "top": 0.02,
            "bottom": 0.02,
            "left": 0.02,
            "right": 0.02,
        },
        "margins_unit": "ratio",
    },
    "rows": [
        {
            "name": "row_0",
            "row_index": 0,
            "items": ["assets/panel_a.png", "assets/panel_b.png", "assets/panel_c.png"],
            "left_gaps": 0.01,
            "right_gaps": 0.01,
            "top_margin": 0.01,
            "bottom_margin": 0.01,
            "unit": "ratio",
            "v_align": "center",
            "h_align": "full",
        },
        {
            "name": "row_1",
            "row_index": 1,
            "items": ["assets/panel_d.png", "assets/panel_e.png"],
            "left_gaps": [
                0.00,
                0.02,
            ],
            "right_gaps": [
                0.02,
                0.00,
            ],
            "top_margin": 0.01,
            "bottom_margin": 0.01,
            "unit": "ratio",
            "v_align": "top",
            "h_align": "center",
        }
    ],
    "output": {
        "path": "output/layout.png",
        "save_kwargs": {},
    },
}


SUPPORTED_LAYOUT_SUFFIXES = {".json", ".yaml", ".yml"}


def _validate_layout_suffix(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_LAYOUT_SUFFIXES:
        supported = ", ".join(sorted(SUPPORTED_LAYOUT_SUFFIXES))
        raise ValueError(f"Unsupported layout file format '{path.suffix}'. Supported formats: {supported}")
    return suffix


def load_layout_spec(path: str) -> Dict[str, Any]:
    spec_path = Path(path)
    if not spec_path.exists():
        raise FileNotFoundError(f"Layout file not found: {spec_path}")
    suffix = _validate_layout_suffix(spec_path)

    with spec_path.open("r", encoding="utf-8") as f:
        if suffix == ".json":
            raw = json.load(f)
        else:
            raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError("Layout file must contain an object at the top level.")
    return raw


def validate_layout_spec(spec: Dict[str, Any]) -> None:
    if "rows" not in spec:
        raise ValueError("Layout spec must contain a 'rows' field.")
    if not isinstance(spec["rows"], list) or not spec["rows"]:
        raise ValueError("'rows' must be a non-empty list.")

    figure = spec.get("figure", {})
    if figure and not isinstance(figure, dict):
        raise ValueError("'figure' must be a JSON object.")

    output = spec.get("output", {})
    if output and not isinstance(output, dict):
        raise ValueError("'output' must be a JSON object.")

    seen_row_indexes = set()

    for index, row in enumerate(spec["rows"]):
        if not isinstance(row, dict):
            raise ValueError(f"Row {index} must be a JSON object.")
        row_name = row.get("name")
        if row_name is not None and not isinstance(row_name, str):
            raise ValueError(f"Row {index} field 'name' must be a string.")
        row_index = row.get("row_index")
        if row_index is not None:
            if not isinstance(row_index, int) or row_index < 0:
                raise ValueError(f"Row {index} field 'row_index' must be a non-negative integer.")
            if row_index in seen_row_indexes:
                raise ValueError(f"Duplicate row_index detected: {row_index}")
            seen_row_indexes.add(row_index)
        items = row.get("items")
        if not isinstance(items, list) or not items:
            raise ValueError(f"Row {index} must contain a non-empty 'items' list.")
        for item_index, item in enumerate(items):
            if isinstance(item, str):
                continue
            if isinstance(item, dict) and isinstance(item.get("path"), str):
                continue
            raise ValueError(
                f"Row {index} item {item_index} must be a string path or an object with a 'path' field."
            )


def make_template_spec() -> Dict[str, Any]:
    return deepcopy(TEMPLATE_SPEC)


def dump_template(path: str, overwrite: bool = False) -> Path:
    output_path = Path(path)
    suffix = _validate_layout_suffix(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {output_path}")

    with output_path.open("w", encoding="utf-8") as f:
        payload = make_template_spec()
        if suffix == ".json":
            json.dump(payload, f, ensure_ascii=False, indent=2)
            f.write("\n")
        else:
            yaml.safe_dump(payload, f, allow_unicode=True, sort_keys=False)
    return output_path


def summarize_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = spec["rows"]
    return {
        "row_count": len(rows),
        "item_count": sum(len(row["items"]) for row in rows),
        "output_path": spec.get("output", {}).get("path"),
    }


def ordered_rows(spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = spec["rows"]
    indexed_rows = list(enumerate(rows))
    ordered = sorted(
        indexed_rows,
        key=lambda item: (
            item[1].get("row_index") is None,
            item[1].get("row_index", 0),
            item[0],
        ),
    )
    return [row for _, row in ordered]
