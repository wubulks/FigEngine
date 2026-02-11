# figengine/utils/validators.py
# -*- coding: utf-8 -*-

"""
Project: FigEngine
File: validators.py
Author: Omarjan Obulkasim @ SYSU
Date: 2026/01/18
License: MIT License
Description: Parameter Validation Utility. Ensures data integrity and parameter 
             validity before layout or rendering processes begin.
"""

import os
import shutil
import platform
from typing import Any, Union, List, Tuple
from ..utils.logger import get_logger

logger = get_logger()


class ValidationError(Exception):
    """FigEngine 专属的验证异常类 (Validation Error Exception)."""
    pass


class Validator:
    """
    参数验证器 (Parameter Validator).
    
    用于在排版开始前，确保数据完整性和参数合法性。
    已集成全链路日志记录，验证失败时会记录 ERROR 日志并抛出 ValidationError。
    """

    @staticmethod
    def validate_image_path(path: str):
        """
        验证图片路径是否存在且格式是否支持。
        
        :param path: 文件路径 (type: str)。
        :raises ValidationError: 如果文件不存在。
        """
        logger.debug(f"Validating image path: {path}")
        
        if not os.path.exists(path):
            msg = f"Image not found at path: {path}"
            logger.error(msg)
            raise ValidationError(msg)
        
        valid_extensions = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp'}
        ext = os.path.splitext(path)[1].lower()
        if ext not in valid_extensions:
            logger.warning(f"File extension {ext} for '{path}' might not be supported. Proceed with caution.")


    @staticmethod
    def validate_pdf_backend():
        """
        验证 pdf2image 的后端（Poppler）是否可用。
        pdf2image 需要系统可执行程序：pdftoppm 或 pdftocairo。
        """
        if shutil.which("pdftoppm") or shutil.which("pdftocairo"):
            return

        system = platform.system()
        if system == "Windows":
            hint = (
                "Poppler is required for PDF support but was not found.\n"
                "Windows options:\n"
                "  1) Install via conda:  conda install -c conda-forge poppler\n"
                "  2) Install poppler for Windows and add its 'bin' folder to PATH "
                "(it must contain pdftoppm.exe/pdftocairo.exe).\n"
            )
        elif system == "Darwin":
            hint = (
                "Poppler is required for PDF support but was not found.\n"
                "Install on macOS:\n"
                "  brew install poppler\n"
            )
        else:
            hint = (
                "Poppler is required for PDF support but was not found.\n"
                "Install on Linux (Debian/Ubuntu):\n"
                "  sudo apt-get update && sudo apt-get install -y poppler-utils\n"
                "Or (Fedora):\n"
                "  sudo dnf install -y poppler-utils\n"
            )

        raise RuntimeError(hint)


    @staticmethod
    def validate_numeric_param(value: Union[int, float], name: str, min_val: float = 0):
        """
        验证数值参数 (如 DPI, Gap, Margins) 是否合法。
        
        :param value: 待验证的数值。
        :param name: 参数名称 (用于日志报错)。
        :param min_val: 允许的最小值 (default: 0)。
        :raises ValidationError: 如果不是数值或小于最小值。
        """
        
        if not isinstance(value, (int, float)):
            msg = f"Parameter '{name}' must be a number, got {type(value)} (Value: {value})"
            logger.error(msg)
            raise ValidationError(msg)
        
        if value < min_val:
            msg = f"Parameter '{name}' cannot be less than {min_val} (Got: {value})"
            logger.error(msg)
            raise ValidationError(msg)


    @staticmethod
    def validate_figure_state(figure: Any):
        """
        渲染前检查 Figure 对象是否包含必要内容。
        
        :param figure: Figure 实例。
        :raises ValidationError: 如果 Figure 为空或 Row 为空。
        """
        logger.debug("Validating figure state before rendering...")
        
        if not figure.rows:
            msg = "Figure contains no rows. Add at least one row before rendering."
            logger.error(msg)
            raise ValidationError(msg)
        
        for i, row in enumerate(figure.rows):
            # [修正]: Row 类属性为 images，而非 elements
            if not row.images:
                msg = f"Row {i} is empty. Each row must contain at least one image."
                logger.error(msg)
                raise ValidationError(msg)
        
        logger.debug("Figure state valid.")


    @staticmethod
    def validate_output_path(path: str):
        """
        检查输出目录是否可写。如果目录不存在，尝试创建。
        
        :param path: 输出文件路径 (e.g. "output/fig.png")。
        :raises ValidationError: 如果无法创建目录。
        """
        logger.debug(f"Validating output path: {path}")
        
        output_dir = os.path.dirname(path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                logger.info(f"Created output directory: {output_dir}")
            except Exception as e:
                msg = f"Cannot create output directory {output_dir}: {str(e)}"
                logger.error(msg)
                raise ValidationError(msg)


    @staticmethod
    def validate_dpi(dpi: int):
        """
        检查 DPI 参数是否合法。
        
        :param dpi: 分辨率 (type: int)。必须为正整数。
        """
        logger.debug(f"Validating DPI: {dpi}")
        if not isinstance(dpi, int) or dpi <= 0:
            msg = f"DPI must be a positive integer, got {dpi}"
            logger.error(msg)
            raise ValidationError(msg)


    @staticmethod
    def validate_unit(unit: str):
        """
        检查单位参数是否合法。
        
        :param unit: 单位字符串 (type: str)。
                     valid options: ["pixel", "ratio", "inch", "cm", "mm"]。
        """
        logger.debug(f"Validating unit: {unit}")
        valid_unit = {"pixel", "ratio", "inch", "cm", "mm"}
        if unit.lower() not in valid_unit:
            msg = f"Invalid unit '{unit}'. Valid options are: {valid_unit}"
            logger.error(msg)
            raise ValidationError(msg)


    @staticmethod
    def validate_color(color: Any):
        """
        简单检查颜色参数类型是否合法。
        
        :param color: 颜色值。支持字符串 (e.g. "red") 或 RGB/RGBA 元组。
        """
        # logger.debug(f"Validating color: {color}")
        if not (isinstance(color, str) or 
                (isinstance(color, tuple) and len(color) >= 3 and all(isinstance(c, int) and 0 <= c <= 255 for c in color[:3]))):
            msg = f"Color must be a string or RGB tuple, got {color}"
            logger.error(msg)
            raise ValidationError(msg)


    @staticmethod
    def validate_margins(margins: dict):
        """
        检查边距字典是否包含所有必要的键且值合法。
        
        :param margins: 边距字典 {'top':.., 'bottom':.., 'left':.., 'right':..}。
        """
        # logger.debug(f"Validating margins: {margins}")
        for side in ['top', 'bottom', 'left', 'right']:
            if side not in margins:
                msg = f"Margin configuration error: '{side}' is missing."
                logger.error(msg)
                raise ValidationError(msg)
            if not isinstance(margins[side], (int, float)) or margins[side] < 0:
                msg = f"Margin '{side}' must be a non-negative number, got {margins[side]}"
                logger.error(msg)
                raise ValidationError(msg)


    @staticmethod
    def validate_size(size: Any):
        """
        检查尺寸参数是否为合法的 (width, height) 元组。
        
        :param size: 尺寸元组 (w, h)。
        """
        logger.debug(f"Validating size: {size}")
        if not (isinstance(size, tuple) and len(size) == 2 and 
                all(isinstance(dim, (int, float)) and dim > 0 for dim in size)):
            msg = f"Size must be a tuple of two positive numbers (width, height), got {size}"
            logger.error(msg)
            raise ValidationError(msg)


    @staticmethod
    def validate_position(position: str):
        """
        检查文本位置参数是否合法。
        
        :param position: 位置字符串 (e.g. "top_left", "center")。
        """
        logger.debug(f"Validating position: {position}")
        valid_positions = {"top_left", "top_right", "bottom_left", "bottom_right", "center", 
                           "top", "bottom", "left", "right"} 
        
        if position.lower() not in valid_positions:
            msg = f"Invalid position '{position}'. Valid options are: {valid_positions}"
            logger.error(msg)
            raise ValidationError(msg)


    @staticmethod
    def validate_vertical_alignment(alignment: str):
        """
        检查垂直对齐方式参数是否合法。
        
        :param alignment: 对齐字符串 (e.g. "top", "full")。
        """
        logger.debug(f"Validating alignment: {alignment}")
        valid_alignments = {"top", "center", "bottom", "full"}
        if alignment.lower() not in valid_alignments:
            msg = f"Invalid alignment '{alignment}'. Valid options are: {valid_alignments}"
            logger.error(msg)
            raise ValidationError(msg)
        

    @staticmethod
    def validate_horizontal_alignment(alignment: str):
        """
        检查水平对齐方式参数是否合法。
        
        :param alignment: 对齐字符串 (e.g. "left", "full")。
        """
        logger.debug(f"Validating horizontal alignment: {alignment}")
        valid_alignments = {"left", "center", "right", "justify", "full"}
        if alignment.lower() not in valid_alignments:
            msg = f"Invalid horizontal alignment '{alignment}'. Valid options are: {valid_alignments}"
            logger.error(msg)
            raise ValidationError(msg)


    @staticmethod
    def validate_fontsize(fontsize: Union[float, int]):
        """
        检查字体大小参数是否合法。
        
        :param fontsize: 字体大小 (像素或比例)。必须大于 0。
        """
        # logger.debug(f"Validating fontsize: {fontsize}")
        if not (isinstance(fontsize, (int, float)) and fontsize > 0):
            msg = f"Font size must be a positive number, got {fontsize}"
            logger.error(msg)
            raise ValidationError(msg)
        
        
