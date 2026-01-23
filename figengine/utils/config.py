# figengine/utils/config.py
# -*- coding: utf-8 -*-

"""
Project: FigEngine
File: config.py
Author: Mute
Date: 2026/01/18
License: MIT License
Description: Configuration Parser. Converts external configuration files (YAML/JSON)
             into executable Figure objects.
"""

import yaml
import json
import os
from typing import Dict, Any, Union
from ..utils.logger import get_logger

logger = get_logger()

class Config:
    """
    配置管理器 (Configuration Manager).
    
    负责将外部声明式配置文件 (YAML/JSON) 解析并转换为 Python 端的 Figure 实例。
    这允许用户通过编写简单的配置文件来生成复杂的图表布局，而无需编写 Python 代码。
    """

    @staticmethod
    def from_yaml(file_path: str) -> Any:
        """
        从 YAML 文件加载配置并构建 Figure。
        
        :param file_path: YAML 文件路径 (type: str)。
        :return: Figure 对象。
        """
        if not os.path.exists(file_path):
             logger.error(f"Config file not found: {file_path}")
             raise FileNotFoundError(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
             config = yaml.safe_load(f)
             
        logger.info(f"Loading configuration from YAML: {file_path}")
        return Config.parse_dict(config)

    @staticmethod
    def from_json(file_path: str) -> Any:
        """
        从 JSON 文件加载配置并构建 Figure。
        
        :param file_path: JSON 文件路径 (type: str)。
        :return: Figure 对象。
        """
        if not os.path.exists(file_path):
             logger.error(f"Config file not found: {file_path}")
             raise FileNotFoundError(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        logger.info(f"Loading configuration from JSON: {file_path}")
        return Config.parse_dict(config)

    @staticmethod
    def parse_dict(data: Dict[str, Any]) -> Any:
        """
        核心解析逻辑 (Dict -> Figure)。
        
        将字典数据映射到 FigEngine 的 API 调用。
        
        :param data: 配置字典 (type: Dict)。
        :return: Figure 对象。
        """
        # ========================================================
        # [Import Strategy] Runtime Import to avoid Circular Dependency
        # Config depends on Figure, but Figure might use Config utils.
        # ========================================================
        from ..core.figure import Figure
        # ========================================================

        # 1. 实例化 Figure (Global Settings)
        settings = data.get("settings", {})
        fig = Figure(
            background=settings.get("background", "white"),
            dpi=settings.get("dpi", 300),
            width=settings.get("width", 0),
            height=settings.get("height", 0)
        )

        # 2. 设置全局边距 (Margins)
        margins = data.get("margins", {})
        unit = margins.get("unit", "ratio") # 默认单位
        
        fig.set_margins(
            top=margins.get("top", 0),
            bottom=margins.get("bottom", 0),
            left=margins.get("left", 0),
            right=margins.get("right", 0),
            unit=unit
        )

        # 3. 构建布局行 (Layout Rows)
        layout = data.get("layout", [])
        
        for row_cfg in layout:
            # 获取行配置
            images = row_cfg.get("images", [])
            align = row_cfg.get("align", "top")
            
            # 获取间距配置 (支持单值或列表)
            left_gaps = row_cfg.get("padding_left", 0)
            right_gaps = row_cfg.get("padding_right", 0.01)
            
            top_margin = row_cfg.get("margin_top", 0)
            bottom_margin = row_cfg.get("margin_bottom", 0)
            
            row_unit = row_cfg.get("unit", "ratio")

            # 添加行
            # 注意：这里的参数映射必须与 Figure.add_row 保持一致
            fig.add_row(
                items=images, 
                left_gaps=left_gaps,
                right_gaps=right_gaps,
                top_margin=top_margin,
                bottom_margin=bottom_margin,
                unit=row_unit,
                align=align
            )

        logger.info("Successfully parsed configuration into Figure object.")
        return fig