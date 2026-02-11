# figengine/core/figure.py
# -*- coding: utf-8 -*-

"""
Project: FigEngine
File: figure.py
Author: Omarjan Obulkasim @ SYSU
Date: 2026/01/18
License: MIT License
Description: Figure layout class. Manages the layout lifecycle: 
             Add Rows -> Calculate Layout -> Render -> Output.
"""

from typing import List, Union, Dict, Tuple, Literal, Optional
from PIL import Image as PILImage
PILImage.MAX_IMAGE_PIXELS = 1_000_000_000

# 内部模块导入
from .image import Image
from .row import Row
from ..engine.layout import LayoutEngine
from ..engine.renderer import RenderEngine
from ..engine.io import IOEngine
from ..utils.logger import get_logger
from ..utils.validators import Validator
from ..utils.tools import Tools

logger = get_logger()

class Figure:
    """
    排版器 (Figure Layout Manager)。
    
    Figure 是整个排版流程的控制器。它负责管理图片行(Rows)，调用布局引擎计算坐标，
    并最终通过渲染引擎生成结果。
    """

    def __init__(self, 
                 background: str = "white", 
                 dpi: int = 300,
                 width: int = 0,   
                 height: int = 0,
                 unit: Literal["pixel", "inch", "cm", "mm"] = "inch", 
                 ): 
        """
        初始化 Figure 画布。

        :param background: 画布背景颜色 (type: str, default: "white")。
                           支持颜色名称 (e.g. "red") 或 Hex 代码 (e.g. "#FFFFFF")。
        :param dpi: 输出图像的分辨率 (type: int, default: 300)。
                    用于物理单位 (cm, inch) 与像素之间的换算。
        :param unit: 尺寸单位 (type: str, default: "inch")。
                     options: ["pixel", "inch", "cm", "mm"]。
        :param width: (可选) 独立指定画布宽度 (type: int, default: 0)。
                      如果为 0，宽度将根据内容自动推断 (Auto-detect)。
        :param height: (可选) 独立指定画布高度 (type: int, default: 0)。
        """
        
        # 参数验证
        Validator.validate_dpi(dpi)

        # 1. 基础属性
        self.background_color = background
        self.dpi = dpi
        
        # 2. 画布最终像素尺寸 (由 LayoutEngine 计算得出)
        self._width_px = 0
        self._height_px = 0
        
        # 3. 容器：存放 Row 对象
        self.rows: List[Row] = []
        
        # 4. 间距配置
        self.margins: Dict[str, Union[float, int]] = {
            'top': 0, 'bottom': 0, 'left': 0, 'right': 0
        }
        self.margins_unit = "ratio"  # 默认单位为 ratio

        # 5. 基准尺寸配置 (Base Constraints)
        # 如果为 0，表示由引擎自动推断 (Auto-detect)
        self.base_width = 0
        self.base_height = 0

        # 优先使用 tuple，其次使用独立参数
        self.forced_method = []
        if width > 0: 
            self.base_width = Tools.to_px(width, unit, dpi=self.dpi)
            self.forced_method.append("width")
        if height > 0:
            self.base_height = Tools.to_px(height, unit, dpi=self.dpi)
            self.forced_method.append("height")
        if ("width" in self.forced_method) and ("height" in self.forced_method):
            self.forced_method = ["both"]

        if not self.forced_method:
            self.forced_method.append("auto") # 自动推断

        # 6. 状态管理
        self._is_dirty = True   # 布局是否过时
        self._cached_layout = None # 布局数据缓存
        self._cached_image = None  # 渲染结果缓存

        logger.debug(f"Initialized Figure (DPI: {dpi}, BG: {background}, Base: {self.base_width}x{self.base_height})")


    def set_margins(self, 
                    top: Optional[Union[float, int]] = None, 
                    bottom: Optional[Union[float, int]] = None, 
                    left: Optional[Union[float, int]] = None, 
                    right: Optional[Union[float, int]] = None, 
                    margins: Dict[str, Union[float, int]] = None,
                    unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "ratio",
                    ) -> 'Figure':
        """
        设置画布的页边距 (Margins)。
        
        注意：修改边距会立即导致当前的布局缓存失效 (Set dirty)。

        :param top: 顶部边距 (type: float | int)。
        :param bottom: 底部边距 (type: float | int)。
        :param left: 左侧边距 (type: float | int)。
        :param right: 右侧边距 (type: float | int)。
        :param margins: 字典形式批量设置 (type: Dict[str, float])。
                        e.g. {'top': 10, 'left': 10}。优先级低于独立参数。
        :param unit: 边距数值的单位 (type: str, default: "ratio")。
                     options: ["pixel", "ratio", "inch", "cm", "mm"]。
                     - "ratio": 相对于画布尺寸的比例 (0.0~1.0)。
                     - "pixel": 绝对像素值。
                     - "inch"/"cm"/"mm": 物理长度 (基于 DPI 换算)。
        :return: self (支持链式调用)。
        """
        Validator.validate_unit(unit)
        new_margins = self.margins.copy()

        if margins:
            new_margins.update(margins)
        
        if top is not None: new_margins['top'] = top
        if bottom is not None: new_margins['bottom'] = bottom
        if left is not None: new_margins['left'] = left
        if right is not None: new_margins['right'] = right

        Validator.validate_margins(new_margins)

        self.margins = new_margins
        self.margins_unit = unit
        self._is_dirty = True
        self._cached_image = None 
        
        logger.debug(f"Margins updated: {self.margins}")
        return self


    def add_row(self, items: List[Union[str, Image]], 
                left_gaps: Union[float, int, List[Union[float, int]]] = 0,    
                right_gaps: Union[float, int, List[Union[float, int]]] = 0.01,
                top_margin: Union[float, int] = 0,
                bottom_margin: Union[float, int] = 0,
                unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "ratio",
                v_align: Literal["full", "top", "center", "bottom"] = "top",
                h_align: Literal["left", "center", "right", "justify", "full"] = "full",
                ) -> 'Figure':
        """
        向画布添加一行图片 (Row)。

        :param items: 图片列表 (type: List[str | Image])。
                      可以是文件路径字符串，也可以是已加载的 Image 对象。
        :param left_gaps: 图片左侧间距 (padding left) (type: float | int | List)。
                          如果是单个值，应用于该行所有图片；如果是列表，对应每个图片。
        :param right_gaps: 图片右侧间距 (padding right) (type: float | int | List, default: 0.01)。
        :param top_margin: 该行距离上一行的间距 (type: float | int, default: 0)。
        :param bottom_margin: 该行距离下一行的间距 (type: float | int, default: 0)。
        :param unit: 间距数值的单位 (type: str, default: "ratio")。
                     options: ["pixel", "ratio", "inch", "cm", "mm"]。
        :param v_align: 行内图片的垂直对齐/排版方式 (type: str, default: "top")。
                        options:
                        - "full": 强制两端对齐 (Justified)。自动缩放图片以等高并填满行宽。
                        - "top": 顶部对齐。
                        - "center": 垂直居中对齐。
                        - "bottom": 底部对齐。
        :param h_align: 行内容的水平对齐方式 (type: str, default: "full")。
                        options: "left", "center", "right", "justify", "full"。
                        - "full": 按行宽等比缩放图片 (间距固定)。
        :return: self (支持链式调用)。
        """
        img_objects = []
        for item in items:
            if isinstance(item, str):
                img_objects.append(Image(item))
            elif isinstance(item, Image):
                img_objects.append(item)
            else:
                raise TypeError(f"Item must be path string or Image object, got {type(item)}")
        
        Validator.validate_unit(unit)

        # 创建 Row 对象
        # 注意：这里的参数名要对应 Row.__init__
        new_row = Row(
            images=img_objects, 
            left_gaps=left_gaps,      # 对应 Row 的 lefts
            right_gaps=right_gaps,    # 对应 Row 的 rights
            top_margin=top_margin, 
            bottom_margin=bottom_margin, 
            unit=unit, 
            v_align=v_align,
            h_align=h_align,
        )
        
        self.rows.append(new_row)
        
        self._is_dirty = True
        self._cached_image = None
        
        logger.debug(
            f"Added row {len(self.rows)} (Count: {len(items)}, V-Align: {v_align}, H-Align: {h_align})"
        )
        return self


    def update_layout(self):
        """
        [核心] 触发布局计算。
        
        调用 LayoutEngine 根据当前的 Rows、Margins 和 Base Constraints 计算所有元素
        在画布上的最终像素坐标。
        如果布局未发生变化 (not dirty)，则直接使用缓存。
        """
        if not self._is_dirty and self._cached_layout:
            return

        if not self.rows:
            logger.warning("Attempted to update layout with an empty Figure.")
            self._width_px, self._height_px = 0, 0
            return

        logger.debug("Calculating layout geometry via LayoutEngine...")
        
        # 如果 base_width 为 0，Engine 会自动推断最大自然宽度
        result = LayoutEngine.calculate(
            rows=self.rows, 
            margins=self.margins,
            unit=self.margins_unit,
            base_width=self.base_width, 
            base_height=self.base_height,
            dpi=self.dpi,
        )
        
        self._width_px = result['total_width']
        self._height_px = result['total_height']
        self._cached_layout = result['placements'] # 存储布局列表
        
        self._is_dirty = False
        logger.debug(f"Layout updated: {self._width_px}x{self._height_px} px")


    @property
    def width(self) -> int:
        """获取计算后的画布宽度 (pixel)。"""
        self.update_layout()
        return self._width_px


    @property
    def height(self) -> int:
        """获取计算后的画布高度 (pixel)。"""
        self.update_layout()
        return self._height_px


    @property
    def size(self) -> Tuple[int, int]:
        """获取计算后的画布尺寸 (width, height) (pixel)。"""
        return (self.width, self.height)


    @property
    def image(self) -> Image:
        """
        获取渲染结果 (Lazy Evaluation)。
        如果布局已更新但未渲染，会触发 render()。
        渲染后，会根据初始化时的 width/height 参数自动缩放结果。
        :return: 渲染完成的 Image 对象。
        """
        # 1. 如果布局脏了或者没有缓存，重新渲染
        if self._is_dirty or self._cached_image is None:
            self._cached_image = self.render()

        # 2. 执行强制尺寸调整 (Resizing)
        if "both" in self.forced_method:
            logger.debug(f"Resizing Figure to fixed size: {self.base_width}x{self.base_height} px")
            self._cached_image = self._cached_image.resize(
                width=self.base_width, 
                height=self.base_height, 
                unit="pixel"
            )
        elif "width" in self.forced_method:
            logger.debug(f"Resizing Figure to fixed width: {self.base_width} px")
            self._cached_image = self._cached_image.resize(
                width=self.base_width, 
                unit="pixel"
            )
        elif "height" in self.forced_method:
            logger.debug(f"Resizing Figure to fixed height: {self.base_height} px")
            self._cached_image = self._cached_image.resize(
                height=self.base_height, 
                unit="pixel"
            )
        return self._cached_image


    def render(self) -> Image:
        """
        执行像素绘制。
        
        1. 确保布局数据 (Coordinates) 是最新的。
        2. 调用 RenderEngine 将图片粘贴到画布上。
        
        :return: 包含最终结果的 Image 对象。
        """
        # 1. 确保布局是最新的
        self.update_layout()
        
        if not self._cached_layout:
             # 返回 1x1 空白图防止报错
             return Image(PILImage.new('RGB', (1, 1), self.background_color), dpi=self.dpi)

        # 2. 调用 Engine 进行绘制
        pil_canvas = RenderEngine.draw_layout({
            'total_width': self._width_px,
            'total_height': self._height_px,
            'placements': self._cached_layout 
        }, self.background_color)
        
        # 3. 包装成 FigEngine 的 Image 对象
        result_img = Image(pil_canvas, dpi=self.dpi)
        self._cached_image = result_img
        
        return result_img


    def replace_row(self, index: int, 
                    items: List[Union[str, Image]], 
                    left_gaps: Union[float, int, List[Union[float, int]]] = 0,    
                    right_gaps: Union[float, int, List[Union[float, int]]] = 0.01,
                    top_margin: Union[float, int] = 0,
                    bottom_margin: Union[float, int] = 0,
                    unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "ratio",
                    v_align: Literal["full", "top", "center", "bottom"] = "top",
                    h_align: Literal["left", "center", "right", "justify", "full"] = "full",
                    ) -> 'Figure':
        """
        在指定索引位置替换已有行。

        适用于在不重新构建整个 Figure 的情况下，对布局中的某一部分进行局部调整或微调。

        :param index: 需要被替换的行索引（从 0 开始）。
        :param items: 新的图像对象或图像路径列表。
        ...（其余参数与 add_row 方法保持一致）...
        """
        if index < 0 or index >= len(self.rows):
            raise IndexError(f"Row index out of range: {index}. Current row count: {len(self.rows)}")

        # 1. 加载并准备 Image 对象
        img_objects = []
        for item in items:
            if isinstance(item, str):
                img_objects.append(Image(item))
            elif isinstance(item, Image):
                img_objects.append(item)
            else:
                raise TypeError(f"Item must be path string or Image object, got {type(item)}")
        
        Validator.validate_unit(unit)

        # 2. 创建新的 Row 对象
        new_row = Row(
            images=img_objects, 
            left_gaps=left_gaps,      
            right_gaps=right_gaps,    
            top_margin=top_margin, 
            bottom_margin=bottom_margin, 
            unit=unit, 
            v_align=v_align,
            h_align=h_align,
        )
        
        # 3. 替换指定索引的行
        self.rows[index] = new_row
        
        # 4. 标记布局为脏
        self._is_dirty = True
        self._cached_image = None
        
        logger.debug(f"Replaced row at index {index}.")
        return self


    def remove_row(self, index: int) -> 'Figure':
        """
        删除指定索引的行
        :param index: 需要被删除的行索引（从 0 开始）
        :return: self (支持链式调用)
        """
        if index < 0 or index >= len(self.rows):
            raise IndexError(f"Row index out of range: {index}")
            
        del self.rows[index]
        
        self._is_dirty = True
        self._cached_image = None
        
        logger.debug(f"Removed row at index {index}.")
        return self


    def get_row(self, index: int) -> Row:
        """
        获取指定索引的行对象，供检查使用
        """
        if index < 0 or index >= len(self.rows):
            raise IndexError(f"Row index out of range: {index}")
        return self.rows[index]


    def save(self, path: str, **kwargs):
        """
        保存并导出图片。
        
        :param path: 输出文件路径 (e.g. "output/fig1.png") (type: str)。
        :param **kwargs: 传递给 IOEngine.save 的额外参数。
                         例如 quality=95 (JPG), compression="tiff_lzw" (TIFF) 等。
        """
        final_img = self.image
        
        logger.debug(f"Saving Figure to: {path}")
        IOEngine.save(
            final_img.get_internal_image(), # 传入 PIL Image
            path, 
            dpi=self.dpi, 
            **kwargs
        )
