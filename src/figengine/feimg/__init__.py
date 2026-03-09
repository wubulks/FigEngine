"""
Project: FigEngine
File: feimg/__init__.py
Author: Omarjan Obulkasim @ SYSU
Date: 2026/03/08
License: MIT License
Description: Official FigEngine single-image CLI package.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, metadata, version

from .. import Figure, Image, Tools
from ..logos import FEIMG_LOGO

try:
    __version__ = version("figengine")
    dist_metadata = metadata("figengine")
    __author__ = dist_metadata.get("Author") or dist_metadata.get("Author-email") or "Unknown"
    if "<" in __author__ and ">" in __author__:
        __author__ = __author__.split("<")[0].strip()
    __author_email__ = dist_metadata.get("Author-email", "")
    __license__ = dist_metadata.get("License", "Unknown")
except PackageNotFoundError:
    __version__ = "0.0.0"
    __author__ = "Unknown"
    __author_email__ = ""
    __license__ = "Unknown"

logo = FEIMG_LOGO

__all__ = [
    "Figure",
    "Image",
    "Tools",
    "__version__",
    "__author__",
    "__author_email__",
    "__license__",
    "logo",
]
