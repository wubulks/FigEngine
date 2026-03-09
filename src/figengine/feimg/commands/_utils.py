"""
Shared helpers for command modules.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union


def require_figengine() -> Any:
    """
    Import FigEngine lazily.

    Lazy import keeps `feimg --help` usable even when FigEngine is not installed.
    """

    try:
        import figengine as fe
    except ImportError as exc:
        raise RuntimeError(
            "FigEngine is not installed. Please run: pip install figengine"
        ) from exc
    return fe


def prepare_output(output: str, overwrite: bool) -> Path:
    """
    Validate output path and create parent directory when needed.
    """

    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists() and not overwrite:
        raise FileExistsError(
            f"Output file already exists: {out_path}. Use --overwrite to replace it."
        )
    return out_path


def parse_scale(scale_text: Optional[str]) -> Optional[Union[float, Tuple[float, float]]]:
    """
    Parse scale argument.

    Supported forms:
    - "0.5"      -> 0.5
    - "0.5,0.8"  -> (0.5, 0.8)
    """

    if scale_text is None:
        return None

    if "," in scale_text:
        sx, sy = scale_text.split(",", maxsplit=1)
        return float(sx.strip()), float(sy.strip())
    return float(scale_text)


def parse_scalar_or_pair(value: Optional[str]) -> Optional[Union[float, Tuple[float, float]]]:
    """
    Parse a numeric string into a float or a 2-item float tuple.
    """

    if value is None:
        return None

    text = value.strip()
    if not text:
        return None

    normalized = text.replace(" ", ",")
    parts = [part.strip() for part in normalized.split(",") if part.strip()]
    if len(parts) == 1:
        return float(parts[0])
    if len(parts) == 2:
        return float(parts[0]), float(parts[1])
    raise ValueError(f"Expected one or two numeric values, got: {value}")


def parse_scalar_or_quad(
    value: Optional[str],
) -> Optional[Union[float, Tuple[float, float, float, float]]]:
    """
    Parse a numeric string into a float or a 4-item float tuple.
    """

    if value is None:
        return None

    text = value.strip()
    if not text:
        return None

    normalized = text.replace(" ", ",")
    parts = [part.strip() for part in normalized.split(",") if part.strip()]
    if len(parts) == 1:
        return float(parts[0])
    if len(parts) == 4:
        return float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])
    raise ValueError(f"Expected one or four numeric values, got: {value}")


def parse_json_dict(value: Optional[str], *, arg_name: str) -> Optional[Dict[str, Any]]:
    """
    Parse a JSON object string.
    """

    if value is None:
        return None

    try:
        data = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{arg_name} must be valid JSON.") from exc

    if not isinstance(data, dict):
        raise ValueError(f"{arg_name} must be a JSON object.")
    return data
