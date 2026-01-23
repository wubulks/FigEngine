# figengine/__init__.py
# -*- coding: utf-8 -*-

"""
Project: FigEngine
File: __init__.py
Author: Omarjan Obulkasim @ SYSU
Date: 2026/01/18
License: MIT License
Description: Top-level package initialization. 
             Exposes core classes (Figure, Image, Row) and utilities (Config, Logger) 
             for easy access.
"""

from __future__ import annotations


from .core.figure import Figure
from .core.image import Image
from .core.row import Row
from .utils.logger import setup_logger
from .utils.config import Config
from .utils.tools import Tools


from importlib.metadata import version, metadata, PackageNotFoundError

try:
    __version__ = version("figengine")
    dist_metadata = metadata("figengine")
    
    # 核心修改：如果 Author 为空，则取 Author-email
    # 逻辑：dist_metadata.get("Author") 可能返回空字符串或 None
    __author__ = dist_metadata.get("Author") or dist_metadata.get("Author-email") or "Unknown"
    
    # 进阶：如果结果是 "Name <email>" 格式，可以只保留名字
    if "<" in __author__ and ">" in __author__:
        # 比如 "Omarjan Obulkasim <email>" -> "Omarjan Obulkasim"
        __author__ = __author__.split("<")[0].strip()
    
    __author_email__ = dist_metadata.get("Author-email", "")
    __license__ = dist_metadata.get("License", "Unknown")

except PackageNotFoundError:
    __version__ = "0.0.0"
    __author__ = "Unknown"
    __author_email__ = ""
    __license__ = "Unknown"
    

# 定义导出的公共接口
__all__ = [
    "Figure", 
    "Image", 
    "Row", 
    "Config", 
    "Tools",
    "setup_logger", 
    "__version__",
    "__author__",
    "__author_email__",
    "__license__",
]