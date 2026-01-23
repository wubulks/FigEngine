# figengine/core/row.py
# -*- coding: utf-8 -*-

"""
Project: FigEngine
File: row.py
Author: Mute
Date: 2026/01/18
License: MIT License
Description: Row container class. Acts as a data structure to hold a list of images 
             and their spacing configurations for the LayoutEngine.
"""

from typing import List, Union, Any, Literal
from .image import Image
from ..utils.logger import get_logger
from ..utils.validators import Validator
from ..utils.tools import Tools

logger = get_logger()

class Row:
    """
    行容器 (Row Container)。
    
    Row 是 LayoutEngine 的基本排版单元。它并不直接进行像素操作或坐标计算，
    而是作为数据结构，存储一行内的图片对象列表以及该行的布局约束（间距、对齐方式）。
    具体的坐标计算逻辑由 LayoutEngine 完成。
    """

    def __init__(self, 
                 images: List[Any], 
                 left_gaps: Union[float, int, List[Union[float, int]]] = 0,
                 right_gaps: Union[float, int, List[Union[float, int]]] = 0,
                 top_margin: Union[float, int] = 0,
                 bottom_margin: Union[float, int] = 0,
                 unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "ratio",
                 align: Literal["top", "center", "bottom", "full"] = "top",
                 ):
        """
        初始化 Row 对象。
        
        :param images: 图片列表 (type: List[str | Image])。
                       支持文件路径字符串或已加载的 Image 对象。
        :param left_gaps: 每个元素左侧的间距/填充 (Padding Left) (type: float | int | List)。
                          - 单个值: 应用于该行所有图片。
                          - 列表: 对应每个图片的左间距。
        :param right_gaps: 每个元素右侧的间距/填充 (Padding Right) (type: float | int | List)。
        :param top_margin: 整行的上方外边距 (Margin Top) (type: float | int)。
                           影响该行与上一行(或画布顶端)的距离。
        :param bottom_margin: 整行的下方外边距 (Margin Bottom) (type: float | int)。
        :param unit: 间距数值的单位 (type: str, default: "ratio")。
                     options: ["pixel", "ratio", "inch", "cm", "mm"]。
        :param align: 行内对齐方式 (type: str, default: "top")。
                      options:
                      - "full": 强制两端对齐 (Justified)。图片会自动缩放以填满行宽。
                      - "top": 顶部对齐 (垂直方向)。
                      - "center": 垂直居中对齐。
                      - "bottom": 底部对齐。
        """
        
        # 1. 基础配置验证
        self.unit = unit.lower()
        Validator.validate_unit(self.unit)
        
        self.align = align.lower()
        valid_aligns = {"top", "center", "bottom", "full"}
        if self.align not in valid_aligns:
            raise ValueError(f"Invalid row alignment '{self.align}'. Options: {valid_aligns}")

        # 2. 统一转换为 Image 对象列表
        # 属性名: self.images (LayoutEngine 依赖此名称)
        self.images: List[Image] = []
        for img in images:
            if isinstance(img, str):
                self.images.append(Image(img))
            elif isinstance(img, Image):
                self.images.append(img)
            else:
                raise TypeError(f"Row element must be str or Image, got {type(img)}")
        
        # 3. 处理间距序列 (关键步骤)
        # LayoutEngine 期望的属性名是: item_lefts, item_rights, margin_top, margin_bottom
        # 我们在这里做参数名到属性名的映射，并使用 Tools 归一化列表长度。
        
        # 将传入的 left_gaps (单值或列表) 归一化为与 images 等长的列表
        # e.g. 如果 left_gaps=10, images有3个 -> [10, 10, 10]
        # e.g. 如果 left_gaps=[10, 20], images有3个 -> [10, 20, 20]
        self.item_lefts = Tools.normalize_to_list(left_gaps, len(self.images))
        self.item_rights = Tools.normalize_to_list(right_gaps, len(self.images))
        
        self.margin_top = top_margin
        self.margin_bottom = bottom_margin
        
        # 4. 布局结果缓存 (LayoutEngine 计算后会更新这些值，此处初始化为 0)
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0


    @property
    def raw_width(self) -> int:
        """计算该行所有图片的自然宽度之和 (像素)。不包含间距。"""
        return sum([img.width for img in self.images])
    

    @property
    def raw_height(self) -> int:
        """计算该行所有图片的自然高度中的最大值 (像素)。不包含边距。"""
        if not self.images:
            return 0
        return max([img.height for img in self.images])
    
    @property
    def aspect_ratios(self) -> List[float]:
        """返回该行所有图片的宽高比列表 (width/height)。"""
        return [img.aspect_ratio for img in self.images]