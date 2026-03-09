"""
Application config management.

Design goals:
1. Keep the config format simple (JSON) so users can edit quickly.
2. Provide safe defaults so CLI can run even without a config file.
3. Make command code independent from config file parsing details.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class AppConfig:
    """
    Runtime config shared by all commands.

    Attributes:
        dpi: Default output DPI when not explicitly provided by command args.
        unit: Default physical unit passed to FigEngine APIs.
        log_level: Default log level for console logger.
        overwrite: Whether output file can overwrite an existing file.
        bg_color: Default background color used by commands that need a color.
    """

    dpi: int = 300
    unit: str = "inch"
    log_level: str = "WARNING"
    overwrite: bool = False
    bg_color: str = "#FFFFFF"


def _merge_config(base: AppConfig, data: Dict[str, Any]) -> AppConfig:
    """
    Merge user JSON config into default config.

    Only known keys are accepted to avoid silent typo-driven mistakes.
    """

    allowed = {
        "dpi",
        "unit",
        "log_level",
        "overwrite",
        "bg_color",
    }

    filtered = {k: v for k, v in data.items() if k in allowed}
    return AppConfig(**{**base.__dict__, **filtered})


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Load config from JSON file, or return defaults if no file is provided.

    Raises:
        FileNotFoundError: when config_path is provided but file does not exist.
        ValueError: when file content is not valid JSON object.
    """

    default = AppConfig()
    if not config_path:
        return default

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, dict):
        raise ValueError("Config file must be a JSON object.")

    return _merge_config(default, raw)


def apply_cli_overrides(
    config: AppConfig,
    log_level: Optional[str] = None,
) -> AppConfig:
    """
    Apply global CLI flags over loaded config.

    This keeps priority clear:
    CLI flag > config file > default value.
    """

    updates: Dict[str, Any] = {}
    if log_level:
        updates["log_level"] = log_level

    if not updates:
        return config

    return AppConfig(**{**config.__dict__, **updates})
