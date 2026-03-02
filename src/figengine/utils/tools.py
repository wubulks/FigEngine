# figengine/utils/tools.py
# -*- coding: utf-8 -*-

"""
Project: FigEngine
File: tools.py
Author: Omarjan Obulkasim @ SYSU
Date: 2026/01/18
License: MIT License
Description: General utility library for FigEngine. 
             Provides static helper methods for unit conversion, data normalization, 
             geometry calculation, and color parsing.
"""

from typing import Union, List, Tuple, Any, Literal
from PIL import ImageColor
from ..utils.consts import Consts
from .logger import get_logger
from .validators import Validator

# 懒加载 matplotlib 以加快启动速度，仅在需要字体时导入
try:
    import matplotlib.font_manager as fm
    from matplotlib.font_manager import FontProperties
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

logger = get_logger()


class Tools:
    """
    FigEngine 通用工具库 (General Utilities).
    
    这是一个静态工具类，提供以下核心功能：
    1. 单位转换 (Unit Conversion): 像素、比例、物理尺寸之间的互转。
    2. 数据归一化 (Normalization): 将输入参数统一为列表格式。
    3. 几何计算 (Geometry): 宽高比计算、自适应缩放尺寸计算。
    4. 颜色解析 (Color Parsing): 统一颜色输入格式。
    """

    # =========================================================================
    # 1. 单位转换 (Unit Conversion)
    # =========================================================================
    @staticmethod
    def to_px(value: Union[float, int], 
              unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "ratio", 
              reference: int = Consts.REF_LEN, 
              dpi: int = Consts.DPI) -> int:
        """
        将任意单位的数值转换为绝对像素值 (Integer Pixels)。
        
        计算公式：
        - pixel: value
        - ratio: value * reference
        - inch:  value * dpi
        - cm:    (value / 2.54) * dpi
        - mm:    (value / 25.4) * dpi

        :param value: 输入数值 (type: float | int)。
        :param unit: 单位 (type: str, default: "ratio")。
                     options: ["pixel", "ratio", "inch", "cm", "mm"]。
        :param reference: 参考长度 (type: int, default: 1000)。
                          当 unit="ratio" 时作为基准 (e.g. 画布宽度)。
        :param dpi: 屏幕/输出分辨率 (type: int, default: 300)。
                    当 unit 为物理单位 ("inch", "cm", "mm") 时用于换算。
        :return: 转换后的像素值 (int)。
        """
        unit = unit.lower()
        Validator.validate_unit(unit)
        Validator.validate_numeric_param(value, "value", min_val=0)
        Validator.validate_numeric_param(reference, "reference", min_val=0)
        Validator.validate_numeric_param(dpi, "dpi", min_val=1)
        
        # 1. 像素 (直接返回)
        if unit == "pixel":
            return int(value)
        
        # 2. 比例 (乘以参考值)
        if unit == "ratio":
            # 比例通常是 float，例如 0.5 * 1000 = 500
            return int(float(value) * reference)
        
        # 3. 物理尺寸 (基于 DPI)
        if dpi <= 0:
            logger.warning(f"Invalid DPI {dpi} for physical unit conversion. Defaulting to 300.")
            dpi = 300

        if unit == "inch":
            return int(float(value) * dpi)
        
        if unit == "cm":
            # 1 inch = 2.54 cm
            return int((float(value) / 2.54) * dpi)
        
        if unit == "mm":
            # 1 inch = 25.4 mm
            return int((float(value) / 25.4) * dpi)

        return int(value)


    @staticmethod
    def px_to_unit(px: int, 
                   unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "ratio", 
                   dpi: int = Consts.DPI,
                   reference: int = Consts.REF_LEN, 
                   ) -> float:
        """
        [逆向操作] 将像素值转换为指定单位的数值。

        :param px: 像素值 (type: int)。
        :param unit: 目标单位 (type: str)。
        :param dpi: 分辨率 (用于物理单位) (type: int, default: 300)。
        :param reference: 参考长度 (用于 ratio 单位) (type: int, default: 1000)。
        :return: 转换后的数值 (float)。
        """
        unit = unit.lower()
        Validator.validate_unit(unit)
        Validator.validate_numeric_param(px, "px", min_val=0)
        Validator.validate_numeric_param(reference, "reference", min_val=0)
        Validator.validate_numeric_param(dpi, "dpi", min_val=1)

        if unit == "pixel":
            return float(px)
        
        if unit == "ratio":
            if reference == 0:
                logger.warning("Reference length is zero for ratio conversion. Returning 0.")
                return 0.0
            return float(px) / reference
        
        if dpi <= 0:
            logger.warning(f"Invalid DPI {dpi} for physical unit conversion. Defaulting to 300.")
            dpi = 300

        if unit == "inch":
            return float(px) / dpi
        
        if unit == "cm":
            return (float(px) / dpi) * 2.54
        
        if unit == "mm":
            return (float(px) / dpi) * 25.4

        return float(px)


    # =========================================================================
    # 2. 列表归一化 (List Normalization)
    # =========================================================================
    @staticmethod
    def normalize_to_list(value: Any, length: int, default: Any = 0) -> List[Any]:
        """
        将输入转换为固定长度的列表 (Broadcasting)。
        常用于处理 Padding/Margin 参数，允许用户只传一个值应用于所有元素。
        
        规则：
        - 如果是单个值 -> 复制 N 次 (e.g. 10 -> [10, 10, 10])。
        - 如果是列表 -> 截断或用最后一个元素补齐 (e.g. [10, 20] -> [10, 20, 20])。
        
        :param value: 输入值 (单个对象 或 列表)。
        :param length: 目标列表长度。
        :param default: 当输入列表为空时的填充默认值。
        :return: 长度为 length 的列表。
        """
        if length <= 0:
            return []

        # 情况 A: 单个值 (非列表)
        if not isinstance(value, list):
            return [value] * length

        # 情况 B: 列表
        current_len = len(value)
        if current_len >= length:
            return value[:length]
        else:
            # 补齐逻辑：用列表最后一个元素补齐 (如果没有元素则用 default)
            fill_value = value[-1] if current_len > 0 else default
            return value + [fill_value] * (length - current_len)
        

    # =========================================================================
    # 3. 几何计算 (Geometry Helpers)
    # =========================================================================
    @staticmethod
    def calculate_aspect_fit(src_w: int, src_h: int, target_w: int = None, target_h: int = None) -> Tuple[int, int]:
        """
        计算保持长宽比的缩放尺寸 (Aspect Fit)。
        
        :param src_w, src_h: 原始尺寸。
        :param target_w: 目标宽度 (可选)。
        :param target_h: 目标高度 (可选)。
        :return: (new_w, new_h)。
        
        逻辑：
        1. 仅指定 target_w: 高度按比例缩放。
        2. 仅指定 target_h: 宽度按比例缩放。
        3. 同时指定: 类似于 CSS object-fit: contain。取较小的缩放比例，确保完整放入 box 内。
        """
        if src_w == 0 or src_h == 0:
            return (0, 0)
            
        aspect = src_w / src_h

        # 模式 1: 指定宽度，算高度
        if target_w is not None and target_h is None:
            return (int(target_w), int(target_w / aspect))
        
        # 模式 2: 指定高度，算宽度
        if target_h is not None and target_w is None:
            return (int(target_h * aspect), int(target_h))
            
        # 模式 3: 同时指定 (Box Fit)，取较小值以包含在内
        if target_w is not None and target_h is not None:
            scale_w = target_w / src_w
            scale_h = target_h / src_h
            scale = min(scale_w, scale_h)
            return (int(src_w * scale), int(src_h * scale))

        return (src_w, src_h)
    

    # =========================================================================
    # 4. 颜色解析 (Color Parsing)
    # =========================================================================
    @staticmethod
    def parse_color(color: Union[str, Tuple]) -> Tuple[int, int, int, int]:
        """
        解析颜色参数为标准 RGBA 元组。
        
        支持格式:
        - Hex Strings: "#FF0000", "#F00"
        - Color Names: "red", "white", "transparent"
        - RGB Tuples: (255, 0, 0) -> (255, 0, 0, 255)
        - RGBA Tuples: (255, 0, 0, 128)
        - CSS Strings: "rgb(255,0,0)", "rgba(0,0,0,0.5)"
        
        :param color: 输入颜色。
        :return: (R, G, B, A) 元组 (0-255)。
        """
        if isinstance(color, tuple):
            if len(color) == 3:
                return (*color, 255) # RGB -> RGBA
            return color
        
        if isinstance(color, str):
            try:
                return ImageColor.getrgb(color) # PIL 自带的强大解析器
            except ValueError:
                logger.warning(f"Cannot parse color '{color}', defaulting to transparent.")
                return (0, 0, 0, 0)
        
        return (255, 255, 255, 255) # Default White
    

    @staticmethod
    def print_valid_fonts(filter_text: str = None) -> List[str]:
        """
        美观地列出系统可用的字体名称。
        
        :param filter_text: (可选) 搜索关键词，例如 "Hei" 或 "Arial"。
        :return: 所有可用字体名称的列表。
        """
        if not HAS_MPL:
            logger.error("Matplotlib is not installed. Cannot inspect fonts.")
            return []

        print("🔍 Scanning system fonts... (This may take a moment)")
        
        # 1. 获取并去重
        font_paths = fm.findSystemFonts()
        font_names = set()
        for path in font_paths:
            try:
                # 使用 FontProperties 解析字体名，确保准确性
                prop = FontProperties(fname=path)
                name = prop.get_name()
                font_names.add(name)
            except:
                continue
        
        sorted_fonts = sorted(list(font_names))
        
        # 2. 过滤
        if filter_text:
            sorted_fonts = [f for f in sorted_fonts if filter_text.lower() in f.lower()]

        # 3. 优先展示常见中文字体 (Highlight Chinese Fonts)
        # 这些是科研绘图中常用的中文字体名
        common_cn = [
            "SimHei", "Microsoft YaHei", "SimSun", "KaiTi", "FangSong", # Windows
            "PingFang SC", "Heiti SC", "Songti SC", "Hiragino Sans GB", # Mac
            "Noto Sans CJK SC", "WenQuanYi Micro Hei" # Linux
        ]
        found_cn = [f for f in sorted_fonts if f in common_cn]

        # 4. 美观打印
        print("=" * 60)
        print(f"📦 FOUND {len(sorted_fonts)} FONTS")
        print("=" * 60)

        # 4.1 打印推荐的中文字体
        if found_cn:
            print(f"⭐️ RECOMMENDED CHINESE FONTS ({len(found_cn)}):")
            print("-" * 60)
            for f in found_cn:
                print(f"  • {f}")
            print("-" * 60)
            print("📝 ALL FONTS:")
        
        # 4.2 分栏打印所有字体 (3列布局)
        # 计算最大长度以对齐
        if not sorted_fonts:
            print("  (No fonts found)")
            return []

        col_width = 30 # 每列宽度
        cols = 3
        
        for i, font in enumerate(sorted_fonts):
            # 截断过长的名字
            display_name = (font[:col_width-3] + '..') if len(font) > col_width-1 else font
            # 不换行打印
            print(f"{display_name:<{col_width}}", end="")
            
            # 每3个换一行
            if (i + 1) % cols == 0:
                print()
        
        print("\n" + "=" * 60)
        
        return sorted_fonts