# figengine/core/image.py
# -*- coding: utf-8 -*-

"""
Project: FigEngine
File: image.py
Author: Omarjan Obulkasim @ SYSU
Date: 2026/01/18
License: MIT License
Description: Core Image class. Wraps PIL.Image to provide enhanced features 
             like physical units support, smart resizing, and easy annotations.
"""

import os

from typing import Union, Tuple, Optional, Literal, Dict, Any
from PIL import Image as PILImage, ImageDraw, ImageFont
from ..engine.io import IOEngine
from ..engine.renderer import TextRenderer
from ..utils.logger import get_logger
from ..utils.validators import Validator
from ..utils.tools import Tools
from ..utils.consts import Consts
PILImage.MAX_IMAGE_PIXELS = Consts.MAX_IMAGE_PIXEL

logger = get_logger()

# [修改] 重命名为 PositionType，表示 9 个方位
PositionType = Literal["center", "top", "bottom", "left", "right", 
                        "top_left", "top_right", "bottom_left", "bottom_right"]

class Image:
    """
    基础图像类。
    
    它是 FigEngine 的核心数据结构，封装了 PIL.Image 对象，
    增加了物理尺寸感知、智能缩放、标注等科研绘图常用功能。
    """
    
    def __init__(self, source: Union[str, PILImage.Image], label: Optional[str] = None, dpi: Optional[int] = None):
        """
        初始化 Image 对象。

        :param source: 图像来源 (type: str | PIL.Image)。
                       可以是文件路径，也可以是已存在的 PIL Image 对象。
        :param label: (可选) 图像标签 (type: str)。
                      后续可用于生成子图编号 (e.g. "a", "b")。
        :param dpi: (可选) 图像分辨率 (type: int, default: 300)。
                    如果 source 是文件且包含 DPI 信息，则自动读取；否则默认 300。
        """
        if label is not None:
            self.label = label
        else:
            if isinstance(source, str):    
                self.label = os.path.basename(source).split('.')[0]  # 默认标签为文件名（不含扩展名）
            else:
                self.label = "Unnamed Image"
        # 加载逻辑委托给 Engine
        if isinstance(source, str):
            self._pil_image = IOEngine.load(source, dpi=dpi)
            file_dpi = self._pil_image.info.get('dpi')
            self.dpi = dpi if dpi else (round(file_dpi[0]) if file_dpi else Consts.DPI)
            self.source_path = source
        elif isinstance(source, PILImage.Image):
            self._pil_image = source
            self.source_path = None
            self.dpi = dpi if dpi else Consts.DPI
        else:
            raise TypeError(f"Source must be file path or PIL Image object, got {type(source)}")
        Validator.validate_dpi(self.dpi)


    @classmethod
    def new(cls, size: Tuple[Union[int, float], Union[int, float]], 
            facecolor: Union[str, Tuple[int, int, int]] = "white", 
            unit: Literal["pixel", "inch", "cm", "mm"] = "inch",
            dpi: int = Consts.DPI, label: Optional[str] = None,) -> 'Image':
        """
        创建一个指定尺寸和颜色的空白图像。

        :param size: 图像尺寸 (width, height) (type: Tuple)。
        :param facecolor: 背景颜色 (type: str | Tuple, default: "white")。
        :param unit: 尺寸单位 (type: str, default: "inch")。
                     options: ["pixel", "inch", "cm", "mm"]。
        :param dpi: 图像分辨率 (type: int, default: 300)。
        :return: 新的 Image 实例。
        """
        w, h = size
        unit = unit.lower()
        
        # 1. 验证参数
        Validator.validate_dpi(dpi)
        Validator.validate_unit(unit)

        # 2. 使用 Tools 进行统一换算
        # 注意: 新建图片时不需要 reference (相对尺寸)，所以 reference=0 或不传
        w_px = Tools.to_px(w, unit, dpi=dpi)
        h_px = Tools.to_px(h, unit, dpi=dpi)

        # 3. 安全检查
        if w_px <= 0 or h_px <= 0:
            raise ValueError(f"Calculated image size is invalid: {w_px}x{h_px} px. (Input: {w}x{h} {unit})")

        logger.debug(f"Created new image: {size} {unit} -> {w_px}x{h_px} px @ {dpi} DPI")

        # 4. 创建 PIL 图像
        # PIL.new 接受的 color 可以是字符串名 ("white") 或 RGBA 元组
        pil_img = PILImage.new("RGBA", (w_px, h_px), facecolor)
        
        return cls(pil_img, dpi=dpi, label=label)


    @property
    def size(self) -> Tuple[int, int]:
        """获取图像尺寸 (width, height) (pixel)。"""
        return self._pil_image.size
    

    def get_size(self, unit: Literal["pixel", "inch", "cm", "mm"] = 'pixel') -> Tuple[float, float]:
        """
        获取图像尺寸，支持单位转换。

        :param unit: 目标单位 (type: str, default: "pixel")。
        :return: (width, height) in target unit。
        """
        unit = unit.lower()
        w_px, h_px = self._pil_image.size
        if unit == "pixel":
            return (w_px, h_px)
        return (Tools.px_to_unit(w_px, unit, dpi=self.dpi), Tools.px_to_unit(h_px, unit, dpi=self.dpi))


    @property
    def width(self) -> int:
        """获取图像宽度 (pixel)。"""
        return self._pil_image.width


    @property
    def height(self) -> int:
        """获取图像高度 (pixel)。"""
        return self._pil_image.height
    

    @property
    def aspect_ratio(self) -> float:
        """获取图像宽高比 (width / height)。"""
        return self.width / self.height


    def save(self, path: str, dpi: int = Consts.DPI):
        """
        保存图像到文件。

        :param path: 输出路径 (type: str)。
        :param dpi: 输出分辨率 (type: int, default: Consts.DPI)。
        """
        Validator.validate_dpi(dpi)
        IOEngine.save(self._pil_image, path, dpi=dpi)


    def get_internal_image(self) -> PILImage.Image:
        """仅供 Engine 内部使用的接口，返回底层的 PIL Image 对象。"""
        return self._pil_image


    def resize(self, 
               width: Optional[Union[int, float]] = None, 
               height: Optional[Union[int, float]] = None, 
               scale: Union[float, Tuple[float, float]] = None,
               ref_image: Optional['Image'] = None,
               unit: Literal["pixel", "inch", "cm", "mm"] = "pixel",
               resample: Literal["auto", "lanczos", "bicubic", "bilinear", "nearest", "box"] = "auto") -> 'Image':
        """
        多功能图像缩放。
        
        优先级逻辑:
        1. ref_image: 若存在，强制缩放到与参考图完全一致 (忽略其他参数)。
        2. width/height: 
           - 若两者都有: 强制拉伸到指定尺寸 (忽略原比例)。
           - 若只有一个: 保持原图宽高比，自动计算另一个维度。
           - 支持 unit 参数 (pixel, inch, cm, mm)。
        3. scale:
           - float: 整体等比缩放。
           - tuple (sx, sy): 宽高分别缩放。
        
        :param width: 目标宽度 (type: float | int)。
        :param height: 目标高度 (type: float | int)。
        :param scale: 缩放比例 (type: float | Tuple)。e.g. 0.5 for 50%.
        :param ref_image: 参考图片对象 (type: Image)。
        :param unit: 仅在 width/height 模式下生效，指定尺寸的单位 (type: str, default: "pixel")。
        :param resample: 插值算法 (type: str, default: "auto")。
                         options:
                         - "auto": 智能选择 (放大用 bicubic, 缩小用 lanczos)。
                         - "lanczos": 高质量缩小。
                         - "bicubic": 平滑放大。
                         - "nearest": 最近邻 (保硬边)。
        :return: 缩放后的新 Image 对象。
        """
        # 0. 准备插值映射表
        resample_map = {
            "lanczos": PILImage.Resampling.LANCZOS,
            "bicubic": PILImage.Resampling.BICUBIC,
            "bilinear": PILImage.Resampling.BILINEAR,
            "nearest": PILImage.Resampling.NEAREST,
            "box": PILImage.Resampling.BOX,
            "hamming": PILImage.Resampling.HAMMING,
        }

        # 获取当前像素尺寸
        w_curr, h_curr = self.width, self.height
        w_target, h_target = w_curr, h_curr
        
        # --- 策略 1: 参考图模式 (Reference) ---
        if ref_image is not None:
            w_target = ref_image.width
            h_target = ref_image.height
            
        # --- 策略 2: 指定尺寸模式 (Dimension with Unit) ---
        elif width is not None or height is not None:
            # 辅助函数：将输入值根据 unit 转为像素
            def convert(val):
                if val is None: return None
                # 注意：这里不需要 reference，因为 resize 的 inch/cm 是绝对物理单位
                return Tools.to_px(val, unit, dpi=self.dpi)

            w_px = convert(width)
            h_px = convert(height)

            if w_px is not None and h_px is not None:
                # 2.1 双向指定 (强制变形)
                w_target = w_px
                h_target = h_px
            elif w_px is not None:
                # 2.2 只指定宽 (保持比例) -> h = w / ar
                w_target = w_px
                h_target = int(w_target / self.aspect_ratio)
            else:
                # 2.3 只指定高 (保持比例) -> w = h * ar
                h_target = h_px
                w_target = int(h_target * self.aspect_ratio)
                
        # --- 策略 3: 比例模式 (Scale) ---
        elif scale is not None:
            if isinstance(scale, (int, float)):
                # 3.1 整体缩放
                w_target = int(w_curr * scale)
                h_target = int(h_curr * scale)
            elif isinstance(scale, (tuple, list)) and len(scale) == 2:
                # 3.2 异向缩放 (width_scale, height_scale)
                w_target = int(w_curr * scale[0])
                h_target = int(h_curr * scale[1])
            else:
                 raise ValueError("Scale must be a number or a tuple (scale_w, scale_h)")
        
        # --- 兜底：无参数则返回副本 ---
        else:
            return Image(self._pil_image.copy(), label=self.label, dpi=self.dpi)

        # --- 执行缩放 ---
        # 边界检查：防止计算出 0 或 负数
        w_target = max(1, int(w_target))
        h_target = max(1, int(h_target))
        
        method_name = resample.lower().strip()
        pil_method = None

        if method_name == "auto":
            # 智能选择：只要有任一维度变大，就视为放大，倾向于平滑
            if w_target > w_curr or h_target > h_curr:
                pil_method = PILImage.Resampling.BICUBIC
            else:
                pil_method = PILImage.Resampling.LANCZOS
        elif method_name in resample_map:
            pil_method = resample_map[method_name]
        else:
            # 容错：如果用户传了 raw PIL constant (int)，尝试兼容
            if isinstance(resample, int):
                pil_method = resample
            else:
                valid_keys = ", ".join(resample_map.keys())
                raise ValueError(f"Invalid resample method '{resample}'. Options: auto, {valid_keys}")
        
        resized_pil = self._pil_image.resize((w_target, h_target), pil_method)
        
        return Image(resized_pil, label=self.label, dpi=self.dpi)


    def crop(self, 
             box: Union[Tuple[float, float, float, float], Dict[str, float]] = None,
             left: Union[float, int] = 0, 
             top: Union[float, int] = 0, 
             right: Union[float, int] = 0, 
             bottom: Union[float, int] = 0, 
             unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "ratio") -> 'Image':
        """
        裁剪图像。支持两种模式：Inset (边缘切除) 和 ROI (区域提取)。
        
        模式 A (Inset/Trim):
        如果不传 box，则 left/top/right/bottom 代表 **向内切除的量** (Amount to cut)。
        例如: right=10 代表从右边界向内切掉 10 个单位。

        模式 B (ROI/Box):
        如果传 box=(x1, y1, x2, y2)，则代表提取该绝对坐标区域。box 优先级高于 Inset 参数。
        
        :param box: (可选) ROI 区域 (x1, y1, x2, y2) 或 dict {'left':.., 'top':..}。
        :param left: 左侧切除量 (type: float | int)。
        :param top: 顶部切除量 (type: float | int)。
        :param right: 右侧切除量 (type: float | int)。
        :param bottom: 底部切除量 (type: float | int)。
        :param unit: 数值单位 (type: str, default: "ratio")。
        :return: 裁剪后的新 Image 对象。
        """
        unit = unit.lower()
        Validator.validate_unit(unit)

        # -------------------------------------------------------
        # 模式 A: 绝对坐标模式 (通过 box 传入)
        # 用于提取特定区域 (ROI)
        # -------------------------------------------------------
        if box is not None:
            l, t, r, b = 0, 0, self.width, self.height
            
            if isinstance(box, dict):
                l = box.get('left', 0)
                t = box.get('top', 0)
                r = box.get('right', self.width)
                b = box.get('bottom', self.height)
            elif isinstance(box, (tuple, list)) and len(box) == 4:
                l, t, r, b = box
            
            # 转换坐标
            x1 = Tools.to_px(l, unit, reference=self.width, dpi=self.dpi)
            y1 = Tools.to_px(t, unit, reference=self.height, dpi=self.dpi)
            x2 = Tools.to_px(r, unit, reference=self.width, dpi=self.dpi)
            y2 = Tools.to_px(b, unit, reference=self.height, dpi=self.dpi)

        # -------------------------------------------------------
        # 模式 B: 裁剪量模式 (通过 left/right... 传入)
        # 用于去除边缘 (Trim/Inset)
        # -------------------------------------------------------
        else:
            # 1. 将输入的“裁剪量”转换为像素
            # 注意：reference 依然是 width/height，这对于 ratio 单位很重要 (切掉 10% 宽度)
            cut_l = Tools.to_px(left, unit, reference=self.width, dpi=self.dpi)
            cut_t = Tools.to_px(top, unit, reference=self.height, dpi=self.dpi)
            cut_r = Tools.to_px(right, unit, reference=self.width, dpi=self.dpi)
            cut_b = Tools.to_px(bottom, unit, reference=self.height, dpi=self.dpi)

            # 2. 计算保留下来的区域坐标
            x1 = cut_l
            y1 = cut_t
            x2 = self.width - cut_r
            y2 = self.height - cut_b

        # 3. 边界检查与执行
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(self.width, x2), min(self.height, y2)

        if x1 >= x2 or y1 >= y2:
            raise ValueError(f"Crop area is empty! Result coords: ({x1}, {y1}, {x2}, {y2}). Input size: {self.get_size()}")

        pil_img = self._pil_image.crop((int(x1), int(y1), int(x2), int(y2)))
        return Image(pil_img, label=self.label, dpi=self.dpi)


    def pad_to_size(self, 
                    target_size: Tuple[Union[int, float], Union[int, float]], 
                    unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "pixel",
                    loc: PositionType = "center", 
                    axis: Literal["both", "height", "width"] = "both",
                    bg_color: Union[str, Tuple[int, int, int, int]] = (255, 255, 255, 0)) -> 'Image':
        """
        智能调整画布尺寸 (Pad OR Crop)。
        
        类似于 Photoshop 的 "Canvas Size"。保持原图内容不变，增加背景或裁剪边缘。
        
        :param target_size: 目标尺寸 (w, h)。
        :param unit: 尺寸单位 (type: str, default: "pixel")。
                     options: ["pixel", "ratio", "inch", "cm", "mm"]。
                     - "ratio": 相对于当前尺寸的倍数 (e.g. 1.5 = 1.5倍大)。
        :param loc: 原图在新画布中的锚点位置 (type: str, default: "center")。
                         e.g. "top_left" 表示原图固定在左上角，向右下方扩展。
        :param axis: 仅调整某个轴向 (type: str, default: "both")。
                     options: ["both", "width", "height"]。
        :param bg_color: 新增区域的填充背景色 (type: str | tuple, default: 透明)。
        :return: 调整画布后的新 Image 对象。
        """
        unit = unit.lower()
        Validator.validate_unit(unit)
        
        req_w_raw, req_h_raw = target_size
        cur_w, cur_h = self.width, self.height

        # 1. 将目标尺寸转换为像素
        # reference 参数用于支持 unit="ratio" 的情况 (基于当前宽高计算)
        req_w = Tools.to_px(req_w_raw, unit, reference=cur_w, dpi=self.dpi)
        req_h = Tools.to_px(req_h_raw, unit, reference=cur_h, dpi=self.dpi)
        
        # 2. 根据 axis 决定最终画布尺寸
        target_w, target_h = cur_w, cur_h
        
        if axis == "both":
            target_w, target_h = req_w, req_h
        elif axis == "width":
            target_w = req_w
            # target_h 保持原图高度
        elif axis == "height":
            target_h = req_h
            # target_w 保持原图宽度

        # 3. 解析对齐位置
        pos_x, pos_y = self._parse_position(loc)
        
        # 4. 计算粘贴坐标 (Paste Coordinate)
        paste_x, paste_y = 0, 0
        
        if pos_x == "left": 
            paste_x = 0
        elif pos_x == "right": 
            paste_x = target_w - cur_w
        else: # center
            paste_x = (target_w - cur_w) // 2
            
        if pos_y == "top": 
            paste_y = 0
        elif pos_y == "bottom": 
            paste_y = target_h - cur_h
        else: # center
            paste_y = (target_h - cur_h) // 2

        # 5. 执行绘图
        bg_rgba = Tools.parse_color(bg_color)
        # 必须取整，因为 PIL 不支持 float 尺寸
        new_canvas = PILImage.new("RGBA", (int(target_w), int(target_h)), bg_rgba)
        
        mask = self._pil_image if self._pil_image.mode == 'RGBA' else None
        new_canvas.paste(self._pil_image, (int(paste_x), int(paste_y)), mask=mask)
        
        return Image(new_canvas, dpi=self.dpi, label=self.label)


    def add_border(
            self,
            thickness: Optional[
                Union[
                    int, float,
                    Tuple[Union[int, float], Union[int, float], Union[int, float], Union[int, float]]
                ]
            ] = None,
            unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "ratio",
            *,
            left: Optional[Union[int, float]] = None,
            right: Optional[Union[int, float]] = None,
            top: Optional[Union[int, float]] = None,
            bottom: Optional[Union[int, float]] = None,
            color: Union[str, Tuple[int, int, int, int]] = (255, 255, 255, 255),
        ) -> "Image":
        """
        添加边框/白边（Padding only，不裁剪、不缩放）。

        - thickness 可选：
            * None：默认四边为 0（此时可用 left/right/top/bottom 单独指定）
            * 单个数值：四边同厚度
            * (left, right, top, bottom)：分别指定四边厚度
        - unit：pixel/ratio/inch/cm/mm
        - left/right/top/bottom：可覆盖 thickness 指定的对应边
        - color：边框颜色（支持字符串或 RGBA tuple）
        """
        unit = unit.lower()
        Validator.validate_unit(unit)

        cur_w, cur_h = self.width, self.height

        # 1) 解析 thickness（raw 值，未转像素）
        if thickness is None:
            t_left = t_right = t_top = t_bottom = 0
        elif isinstance(thickness, tuple):
            if len(thickness) != 4:
                raise ValueError("thickness tuple must be (left, right, top, bottom)")
            t_left, t_right, t_top, t_bottom = thickness
        else:
            t_left = t_right = t_top = t_bottom = thickness

        # 关键字参数覆盖（优先级最高）
        if left is not None:   t_left = left
        if right is not None:  t_right = right
        if top is not None:    t_top = top
        if bottom is not None: t_bottom = bottom

        # 2) 转像素：左右基于宽 reference，上下基于高 reference（对 ratio 更直观）
        px_left = int(max(0, Tools.to_px(t_left, unit, reference=cur_w, dpi=self.dpi)))
        px_right = int(max(0, Tools.to_px(t_right, unit, reference=cur_w, dpi=self.dpi)))
        px_top = int(max(0, Tools.to_px(t_top, unit, reference=cur_h, dpi=self.dpi)))
        px_bottom = int(max(0, Tools.to_px(t_bottom, unit, reference=cur_h, dpi=self.dpi)))

        # 3) 如果四边都为 0，直接返回自身（避免无意义 copy）
        if px_left == px_right == px_top == px_bottom == 0:
            return self

        # 4) 新画布大小
        new_w = cur_w + px_left + px_right
        new_h = cur_h + px_top + px_bottom
        if new_w <= 0 or new_h <= 0:
            raise ValueError(f"Invalid border thickness -> new canvas size ({new_w}, {new_h})")

        # 5) 新建画布并贴图
        bg_rgba = Tools.parse_color(color)
        new_canvas = PILImage.new("RGBA", (new_w, new_h), bg_rgba)

        mask = self._pil_image.split()[3] if self._pil_image.mode == "RGBA" else None
        new_canvas.paste(self._pil_image, (px_left, px_top), mask=mask)

        return Image(new_canvas, dpi=self.dpi, label=self.label)


    def overlay(self, 
                other: 'Image', 
                x: Union[float, int] = 0.5, 
                y: Union[float, int] = 0.5, 
                anchor: PositionType = "center", 
                unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "ratio",
                scale: float = 1.0, 
                expand: bool = False,
                bg_color: Union[str, Tuple[int, int, int, int]] = (0,0,0,0)) -> 'Image':
        """
        叠加另一张图片到当前图片上 (Overlay / Inset)。
        
        :param other: 要叠加的图片对象 (type: Image)。
        :param x: 叠加基准点 x (type: float | int, default: 0.5)。
        :param y: 叠加基准点 y (type: float | int, default: 0.5)。
        :param anchor: Overlay 图片自身的对齐点 (type: str, default: "center")。
                       决定 Overlay 的哪个点对齐到 (x, y)。
        :param unit: 坐标单位 (type: str, default: "ratio")。
                     "ratio" (0.0~1.0) or "pixel".
        :param scale: Overlay 图片的缩放比例 (type: float, default: 1.0)。
        :param expand: 是否扩展画布 (type: bool, default: False)。
                       - False: 裁剪超出边界的部分 (画中画模式)。
                       - True: 自动扩大 Base 画布以容纳 Overlay (拼贴模式)。
        :param bg_color: 扩展画布时的背景色 (type: str | tuple)。
        :return: 叠加后的新 Image 对象。
        """
        # 1. 准备 Base 和 Overlay
        base_pil = self._pil_image.convert("RGBA")
        
        overlay_img = other
        if abs(scale - 1.0) > 1e-6:
            overlay_img = overlay_img.resize(scale=scale)
            
        over_pil = overlay_img.get_internal_image().convert("RGBA")
        
        bw, bh = base_pil.size
        ow, oh = over_pil.size

        # 2. 计算目标坐标 (Target Coordinate on Base)
        target_x = Tools.to_px(x, unit, reference=bw, dpi=self.dpi)
        target_y = Tools.to_px(y, unit, reference=bh, dpi=self.dpi)

        # 3. 计算锚点偏移
        # 公式：Paste_Pos = Target_Pos + Anchor_Offset
        # Anchor_Offset 是一个向量，从 Anchor 点指向 Overlay 左上角
        anchor_dx, anchor_dy = self._get_anchor_offset(ow, oh, anchor)
        
        paste_x = int(target_x + anchor_dx)
        paste_y = int(target_y + anchor_dy)

        # 4. 绘制逻辑
        if not expand:
            base_pil.paste(over_pil, (paste_x, paste_y), mask=over_pil)
            return Image(base_pil, dpi=self.dpi, label=self.label)
        else:
            # 扩展画布
            min_x = min(0, paste_x)
            min_y = min(0, paste_y)
            max_x = max(bw, paste_x + ow)
            max_y = max(bh, paste_y + oh)
            
            new_w = max_x - min_x
            new_h = max_y - min_y
            
            bg_rgba = Tools.parse_color(bg_color)
            new_canvas = PILImage.new("RGBA", (new_w, new_h), bg_rgba)
            
            # Base 偏移
            new_canvas.paste(base_pil, (-min_x, -min_y), mask=base_pil)
            # Overlay 偏移
            new_canvas.paste(over_pil, (paste_x - min_x, paste_y - min_y), mask=over_pil)
            
            return Image(new_canvas, dpi=self.dpi, label=self.label)



    def add_ticks(self, 
                  step: Union[float, int] = 0.1, 
                  unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "ratio",
                  color: str = "black",
                  font: str = "sans-serif", 
                  fontsize: Union[int, float] = 6, 
                  show_grid: bool = True) -> 'Image':
        """
        在图片上绘制辅助刻度和网格线 (Grid & Ticks)。
        
        改进：
        1. 使用 add_text 绘制标签，确保背景透明且排版精准。
        2. 四周全显示，上下文字垂直排列。

        :param step: 刻度步长。
        :param unit: 步长单位
        :param color: 线条和文字颜色。
        :param font: 字体名称。
        :param fontsize: 字体大小。
        :param show_grid: 是否显示网格。
        :return: 新 Image 对象。
        """
        # 1. 准备基础画布并绘制线条 (这部分用 PIL 原生绘制最高效)
        base = self._pil_image.copy().convert("RGBA")
        draw = ImageDraw.Draw(base)
        w, h = base.size
        
        step_px_x = Tools.to_px(step, unit, reference=w, dpi=self.dpi)
        step_px_y = Tools.to_px(step, unit, reference=h, dpi=self.dpi)

        if step_px_x <= 0 or step_px_y <= 0: return self

        # 定义常量
        TICK_LEN = 10   
        GRID_COLOR = (200, 200, 200, 100) 
        # 标签留白：刻度线长度 + 5px 间隙
        LABEL_MARGIN = TICK_LEN + 5 

        # --- 阶段 A：绘制线条 (Grid & Ticks) ---
        # 辅助函数：生成安全的坐标点列表
        def get_points(length, step_val):
            pts = []
            curr = 0
            while curr <= length:
                pts.append(int(curr))
                curr += step_val
            if length not in pts: pts.append(length) # 确保边缘有点
            return pts

        x_points = get_points(w, step_px_x)
        y_points = get_points(h, step_px_y)

        # 绘制 X 轴线条
        for x in x_points:
            if x == 0 or x == w: continue # 跳过角落
            draw.line([(x, 0), (x, TICK_LEN)], fill=color, width=2)
            draw.line([(x, h - TICK_LEN), (x, h)], fill=color, width=2)
            if show_grid: draw.line([(x, 0), (x, h)], fill=GRID_COLOR, width=1)

        # 绘制 Y 轴线条
        for y in y_points:
            if y == 0 or y == h: continue
            draw.line([(0, y), (TICK_LEN, y)], fill=color, width=2)
            draw.line([(w - TICK_LEN, y), (w, y)], fill=color, width=2)
            if show_grid: draw.line([(0, y), (w, y)], fill=GRID_COLOR, width=1)

        # 绘制外边框
        draw.rectangle([(0, 0), (w - 1, h - 1)], outline=color, width=2)
        
        # 将画好线的图包装回对象，准备开始加字
        # 这里的 self.__class__ 确保返回的是 Image 类实例
        current_img = self.__class__(base, dpi=self.dpi, label=self.label)

        # --- 阶段 B：复用 add_text 绘制透明标签 ---
        # 统一样式参数
        # 注意：不传 box_style，add_text 会默认使用透明背景
        text_kwargs = {
            "font": font,
            "fontsize": fontsize,
            "color": color,
            "unit": "pixel",
            "dpi": self.dpi
        }

        # 1. X 轴标签 (上下边缘，垂直显示)
        for x in x_points:
            if x == 0 or x == w: continue
            label = f"{x}" if unit == "pixel" else f"{x/w:.2f}"
            
            # Top: 文字位于 margin 处，向下生长
            # anchor="top" 意味着：
            #   - 水平方向：居中 (center) -> 对齐刻度线 x
            #   - 垂直方向：顶对齐 (top) -> 顶端贴着 LABEL_MARGIN
            current_img = current_img.add_text(
                label, x=x, y=LABEL_MARGIN, 
                rotation=-90, anchor="top", **text_kwargs
            )
            
            # Bottom: 文字位于 h - margin 处，向上生长
            # anchor="bottom" 意味着：
            #   - 水平方向：居中 (center)
            #   - 垂直方向：底对齐 (bottom) -> 底端贴着 h - LABEL_MARGIN
            current_img = current_img.add_text(
                label, x=x, y=h - LABEL_MARGIN, 
                rotation=90, anchor="bottom", **text_kwargs
            )

        # 2. Y 轴标签 (左右边缘，水平显示)
        for y in y_points:
            if y == 0 or y == h: continue
            label = f"{y}" if unit == "pixel" else f"{y/h:.2f}"

            # Left: 靠左
            # anchor="left" 意味着：
            #   - 垂直方向：居中 (center) -> 对齐刻度线 y
            #   - 水平方向：左对齐 (left) -> 左侧贴着 LABEL_MARGIN
            current_img = current_img.add_text(
                label, x=LABEL_MARGIN, y=y, 
                rotation=0, anchor="left", **text_kwargs
            )

            # Right: 靠右
            # anchor="right" 意味着：
            #   - 垂直方向：居中 (center)
            #   - 水平方向：右对齐 (right) -> 右侧贴着 w - LABEL_MARGIN
            current_img = current_img.add_text(
                label, x=w - LABEL_MARGIN, y=y, 
                rotation=0, anchor="right", **text_kwargs
            )
            
        return current_img


    def rotate(self, angle: float, expand: bool = True, bg_color: Union[str, Tuple[int, int, int, int]] = (0,0,0,0)) -> 'Image':
        """
        逆时针旋转图像。
        
        :param angle: 旋转角度 (度) (type: float)。
        :param expand: 是否扩展画布 (type: bool, default: True)。
                       - True: 画布变大以容纳旋转后的所有内容。
                       - False: 画布尺寸不变，裁剪超出部分。
        :param bg_color: 填充的背景色 (type: str | tuple, default: 透明)。
        :return: 旋转后的新 Image 对象。
        """
        # 解析背景色
        # PIL rotate 的 fillcolor 参数需要 (R,G,B) 或 (R,G,B,A) 元组，不支持字符串
        fill_color_tuple = Tools.parse_color(bg_color)
        
        # PIL 的 rotate 方法
        # resample: 使用双三次插值以获得更好的旋转质量
        rotated_pil = self._pil_image.rotate(
            angle, 
            resample=PILImage.Resampling.BICUBIC, 
            expand=expand, 
            fillcolor=fill_color_tuple
        )
        
        # 返回新的 Image 实例 (保持原有 label 和 dpi)
        return Image(rotated_pil, label=self.label, dpi=self.dpi)


    def add_text(self, 
                 text: str, 
                 x: Optional[Union[float, int]] = None, 
                 y: Optional[Union[float, int]] = None, 
                 loc: str = "top_left",   
                 anchor: Optional[str] = None, 
                 offset: Union[float, int, tuple] = 0.1,
                 unit: Literal["pixel", "ratio"] = "ratio",
                 font: str = "sans-serif", 
                 fontsize: Union[int, float] = 24, 
                 fontweight: str = "normal", 
                 rotation: float = 0, 
                 color: str = "black", 
                 box_style: Optional[Dict[str, Any]] = None,
                 dpi: int = None) -> 'Image':
        """
        向图像添加文本标注，支持语义化定位和自定义样式。

        :param text: 文本内容。
        :param x, y: (可选) 绝对坐标。若不提供则使用 semantic position。
        :param loc: 语义化位置 (e.g. "top_left", "center")，当 x,y 为 None 时生效。
        :param anchor: 文本自身的锚点 (e.g. "center", "left")。
                       - Absolute Mode 默认: "top_left"
                       - Semantic Mode 默认: 等同于 loc
        :param offset: 边距 (像素或比例)。
        :param unit: 坐标/Offset 的单位 ("pixel" 或 "ratio")。
        :param fontsize: 字体大小。
        :param fontweight: 字重。
        :param rotation: 旋转角度。
        :param color: 文本颜色。
        :param font: 字体名。
        :param box_style: (可选) 控制文本背景框样式。
            - None (默认): 无背景，无边框（透明）。
            - {'facecolor': 'white'}: 白底。
            - {'edgecolor': 'red', 'linewidth': 2}: 红框透明底。
            - {'boxstyle': 'circle', 'facecolor': 'yellow'}: 黄色圆底。
        :param dpi: 渲染分辨率。
        :return: 新的 Image 对象。
        """
        target_dpi = dpi if dpi else self.dpi
        
        # 1. 智能计算 FontSize
        actual_fontsize = 24
        if isinstance(fontsize, float) and fontsize < 1.0:
            img_h_inch = self.height / target_dpi
            target_pt = (fontsize * img_h_inch) * 72
            actual_fontsize = int(target_pt)
        else:
            actual_fontsize = int(fontsize)

        ref_width_inch = Tools.px_to_unit(self.width, unit="inch", dpi=self.dpi)
        ref_height_inch = Tools.px_to_unit(self.height, unit="inch", dpi=self.dpi)

        # 2. 渲染文字 (调用 TextRenderer)
        # box_style 会被直接传入。如果为 None，Renderer 会生成透明背景。
        text_sprite = TextRenderer.render(
            text, 
            fontsize=actual_fontsize, 
            color=color, 
            font=font,
            weight=fontweight,
            rotation=rotation,
            dpi=target_dpi,
            box_width_inch=ref_width_inch,
            box_height_inch=ref_height_inch,
            box_style=box_style,
        )
        
        tw, th = text_sprite.size
        bw, bh = self.width, self.height
        
        # 3. 确定 参考点 (Base Point) 和 锚点 (Anchor)
        base_x, base_y = 0, 0
        final_anchor = anchor 

        # 场景 A: 显式坐标 (x, y)
        if x is not None and y is not None:
            base_x = Tools.to_px(x, unit, reference=bw, dpi=self.dpi)
            base_y = Tools.to_px(y, unit, reference=bh, dpi=self.dpi)
            
            # 绝对坐标模式下，如果没指定 anchor，默认以文字左上角对齐该点
            if final_anchor is None: 
                final_anchor = "top_left"

        # 场景 B: 语义化定位 (loc + Offset)
        else:
            # 1. 解析 Offset
            off_x, off_y = 0, 0
            if isinstance(offset, (int, float)):
                off_x = Tools.to_px(offset, unit, reference=bw, dpi=self.dpi)
                off_y = Tools.to_px(offset, unit, reference=bh, dpi=self.dpi)
            elif isinstance(offset, (tuple, list)):
                off_x = Tools.to_px(offset[0], unit, reference=bw, dpi=self.dpi)
                off_y = Tools.to_px(offset[1], unit, reference=bh, dpi=self.dpi)
            
            # 2. 根据 loc 确定 参考点
            pos_x, pos_y = self._parse_position(loc)
            
            if pos_x == 'left': base_x = off_x
            elif pos_x == 'right': base_x = bw - off_x
            else: base_x = bw // 2 + off_x # Center 模式下 offset 用于微调
            
            if pos_y == 'top': base_y = off_y
            elif pos_y == 'bottom': base_y = bh - off_y
            else: base_y = bh // 2 + off_y
            
            # 3. 如果没指定 anchor，默认跟随 loc
            if final_anchor is None: 
                final_anchor = loc

        # 4. 根据 Anchor 计算最终粘贴坐标
        # 我们需要计算：为了让文字的 anchor 点与 base 点重合，图片左上角应该在哪？
        anchor_dx, anchor_dy = self._get_anchor_offset(tw, th, final_anchor)
        
        dest_x = int(base_x + anchor_dx)
        dest_y = int(base_y + anchor_dy)

        # 5. 粘贴
        # 必须使用 .convert("RGBA") 确保底图支持 Alpha 通道
        base_copy = self._pil_image.copy().convert("RGBA")
        
        # 确保 sprite 也是 RGBA
        if text_sprite.mode != 'RGBA': 
            text_sprite = text_sprite.convert("RGBA")
        
        # [核心] 使用 mask=text_sprite 实现透明背景叠加
        base_copy.paste(text_sprite, (dest_x, dest_y), mask=text_sprite)
        
        # 返回新对象 (这里假设你的类构造函数接受 base_copy, dpi 等)
        return self.__class__(base_copy, dpi=self.dpi, label=self.label)



    def _parse_position(self, pos: str) -> Tuple[str, str]:
        """解析位置字符串为 (x_pos, y_pos)。"""
        pos = pos.lower().strip()
        pos_x, pos_y = "center", "center"
        
        if "_" in pos:
            parts = pos.split("_")
            for p in parts:
                if p in ["top", "bottom"]: pos_y = p
                elif p in ["left", "right"]: pos_x = p
        else:
            if pos in ["left", "right"]: pos_x = pos
            elif pos in ["top", "bottom"]: pos_y = pos
            
        return pos_x, pos_y


    def _get_anchor_offset(self, w: int, h: int, anchor: str) -> Tuple[int, int]:
        """
        计算锚点相对于左上角 (0,0) 的偏移量。
        此偏移量用于将 Anchor 点拉回到 Base Point。
        例如：anchor='center'，我们需要把图片往左上移动 (w/2, h/2)，所以 offset 是 (-w/2, -h/2)。
        """
        ax, ay = self._parse_position(anchor) # 复用解析逻辑
        
        dx, dy = 0, 0
        
        if ax == "center": dx = -w // 2
        elif ax == "right": dx = -w
        # left: dx = 0
        
        if ay == "center": dy = -h // 2
        elif ay == "bottom": dy = -h
        # top: dy = 0
        
        return dx, dy


    def add_line(
        self,
        start: Tuple[Union[float, int], Union[float, int]],
        end: Tuple[Union[float, int], Union[float, int]],
        unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "ratio",
        color: str = "black",
        width: float = 0.01,
        arrow: Optional[Literal["start", "end", "both"]] = None,
        arrow_size: float = 0.01,
        arrow_style: Literal["triangle", "open", "bar", "diamond", "circle"] = "triangle",
        arrow_angle: float = 25.0,  # 稍微改小了默认角度，让箭头更修长
        arrow_shorten: Optional[float] = None,
        arrow_fill: bool = True,
    ) -> "Image":
        """
        在图像上绘制直线，已优化箭头样式（使用燕尾形替代普通三角形）。
        """
        import math
        from PIL import ImageDraw

        base = self._pil_image.copy().convert("RGBA")
        # 开启抗锯齿的常规操作通常是放大绘制再缩小，这里保持原逻辑以保证性能，
        # 但通过几何形状的优化来提升视觉观感。
        draw = ImageDraw.Draw(base)
        bw, bh = base.size

        # --- 1) 坐标与尺寸转换为像素 ---
        x1 = Tools.to_px(start[0], unit, reference=bw, dpi=self.dpi)
        y1 = Tools.to_px(start[1], unit, reference=bh, dpi=self.dpi)
        x2 = Tools.to_px(end[0], unit, reference=bw, dpi=self.dpi)
        y2 = Tools.to_px(end[1], unit, reference=bh, dpi=self.dpi)

        w_px = Tools.to_px(width, unit, reference=bh, dpi=self.dpi)
        a_px = Tools.to_px(arrow_size, unit, reference=bh, dpi=self.dpi)

        # 自动计算缩短量
        if arrow_shorten is None:
            # 如果是圆形箭头，缩短量小一点
            if arrow_style == "circle":
                shorten_px = a_px * 0.6
            else:
                shorten_px = a_px * 0.5
        else:
            shorten_px = Tools.to_px(arrow_shorten, unit, reference=bh, dpi=self.dpi)

        rgba = Tools.parse_color(color)

        # --- 2) 基础几何：方向向量、长度、角度 ---
        dx, dy = (x2 - x1), (y2 - y1)
        L = math.hypot(dx, dy)

        # 极短线段直接画点
        if L <= 1e-6:
            r = max(1, int(round(w_px / 2)))
            draw.ellipse((x1 - r, y1 - r, x1 + r, y1 + r), fill=rgba)
            return Image(base, dpi=self.dpi, label=self.label)

        ux, uy = dx / L, dy / L
        line_angle = math.atan2(dy, dx)

        # --- 3) 根据箭头位置缩短主线端点 ---
        sx1, sy1 = x1, y1
        sx2, sy2 = x2, y2

        # 限制最大缩短量，防止线段消失
        safe_cut = 0.45 * L
        
        if arrow in ("start", "both"):
            cut = min(shorten_px, safe_cut)
            sx1, sy1 = x1 + ux * cut, y1 + uy * cut
        if arrow in ("end", "both"):
            cut = min(shorten_px, safe_cut)
            sx2, sy2 = x2 - ux * cut, y2 - uy * cut

        # --- 4) 绘制主线 ---
        # 只有当缩短后的长度依然为正时才画线
        if math.hypot(sx2 - sx1, sy2 - sy1) > 0.5:
            draw.line([(sx1, sy1), (sx2, sy2)], fill=rgba, width=max(1, int(round(w_px))))

        # --- 5) 箭头绘制函数集 ---

        def _dot(cx, cy, r):
            if r <= 0: return
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgba)

        def _draw_stealth_tip(px, py, theta):
            """
            燕尾形箭头：替代原有的等腰三角形。
            形状像隐形战机或鼠标指针，底部内凹，更有现代感。
            """
            # 几何参数
            # 使用传入的 angle，但稍微收窄一点以保证锐利度
            alpha = math.radians(arrow_angle)
            
            # 1. 计算两个翼尖 (Wings)
            p1 = (
                px - a_px * math.cos(theta + alpha),
                py - a_px * math.sin(theta + alpha),
            )
            p2 = (
                px - a_px * math.cos(theta - alpha),
                py - a_px * math.sin(theta - alpha),
            )
            
            # 2. 计算内凹点 (Recessed Center)
            # 0.75 表示内凹深度，数值越小凹得越深
            concave_factor = 0.75 
            p_center = (
                px - (a_px * concave_factor) * math.cos(theta),
                py - (a_px * concave_factor) * math.sin(theta)
            )

            if arrow_fill:
                # 绘制四边形：尖端 -> 翼1 -> 内凹点 -> 翼2 -> 尖端
                draw.polygon([(px, py), p1, p_center, p2], fill=rgba)
            else:
                # 描边模式：只画 V 形
                lw = max(1, int(round(w_px)))
                draw.line([p1, (px, py), p2], fill=rgba, width=lw)


        def _draw_open_tip(px, py, theta):
            """开放式箭头 (V形线)"""
            lw = max(1, int(round(w_px)))
            alpha = math.radians(arrow_angle)
            
            # 稍微加长一点翼展，因为 open 样式视觉上容易显小
            wing_len = a_px * 1.1 
            
            # 留出尖端空隙，避免叠墨
            gap = max(1.0, 0.5 * w_px)

            # 两个翼的方向
            dirs = [theta + alpha, theta - alpha]
            
            for d in dirs:
                # 起点（退后 gap）
                s_x = px - gap * math.cos(d)
                s_y = py - gap * math.sin(d)
                # 终点（再退后 wing_len）
                e_x = px - (gap + wing_len) * math.cos(d)
                e_y = py - (gap + wing_len) * math.sin(d)
                
                draw.line([(s_x, s_y), (e_x, e_y)], fill=rgba, width=lw)
                
                # 给线条端点加圆帽，看起来更圆润
                cap_r = lw / 2.0
                _dot(s_x, s_y, cap_r)
                _dot(e_x, e_y, cap_r)


        def _draw_bar_tip(px, py, theta):
            """垂直短横线"""
            half = a_px * 0.6
            nx, ny = -math.sin(theta), math.cos(theta)
            p1 = (px + nx * half, py + ny * half)
            p2 = (px - nx * half, py - ny * half)
            draw.line([p1, p2], fill=rgba, width=max(1, int(round(w_px))))


        def _draw_diamond_tip(px, py, theta):
            """菱形"""
            side = a_px * 0.5
            back = a_px * 0.9 # 拉长一点
            nx, ny = -math.sin(theta), math.cos(theta)
            
            p_tip = (px, py)
            p_back = (px - math.cos(theta) * back, py - math.sin(theta) * back)
            p_left = (px - math.cos(theta) * (back/2) + nx * side, 
                      py - math.sin(theta) * (back/2) + ny * side)
            p_right = (px - math.cos(theta) * (back/2) - nx * side, 
                       py - math.sin(theta) * (back/2) - ny * side)

            pts = [p_tip, p_left, p_back, p_right]
            if arrow_fill:
                draw.polygon(pts, fill=rgba)
            else:
                pts.append(p_tip) # 闭合
                draw.line(pts, fill=rgba, width=max(1, int(round(w_px))))
        

        def _draw_circle_tip(px, py, theta):
            """实心圆点"""
            r = a_px * 0.5
            draw.ellipse((px - r, py - r, px + r, py + r), fill=rgba)


        def _draw_tip(px, py, theta):
            style = arrow_style
            if style == "triangle":
                _draw_stealth_tip(px, py, theta) # 默认使用好看的燕尾
            elif style == "open":
                _draw_open_tip(px, py, theta)
            elif style == "bar":
                _draw_bar_tip(px, py, theta)
            elif style == "diamond":
                _draw_diamond_tip(px, py, theta)
            elif style == "circle":
                _draw_circle_tip(px, py, theta)
            else:
                _draw_stealth_tip(px, py, theta)

        # --- 6) 绘制箭头 ---
        # 注意：start 端的箭头需要旋转 180 度 (math.pi)
        if arrow in ("end", "both"):
            _draw_tip(x2, y2, line_angle)
        if arrow in ("start", "both"):
            _draw_tip(x1, y1, line_angle + math.pi)

        return Image(base, dpi=self.dpi, label=self.label)



    def add_marker(
        self,
        x: Union[float, int],
        y: Union[float, int],
        unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "pixel",
        style: Literal[
            "circle", "square", "cross", "plus", "diamond", 
            "triangle_up", "triangle_down", "star", "pentagon", "hexagon", "target"
        ] = "circle",
        size: float = 10,
        color: str = "red",
        outline: Optional[str] = None,
        width: float = 1,
    ) -> "Image":
        """
        在图像上绘制特征点 (Marker)，支持多种几何形状。

        :param x: 点的横坐标。
        :param y: 点的纵坐标。
        :param unit: 坐标单位 (default: "pixel")。
        :param style: 点的样式:
                      基础: "circle", "square", "cross", "plus", "diamond"
                      几何: "triangle_up", "triangle_down", "pentagon", "hexagon"
                      特殊: "star", "target"
        :param size: 点的大小 (直径/外接圆直径，单位像素)。
        :param color: 填充颜色 (对于线条类样式如 plus/cross，指线条颜色)。
        :param outline: 边框颜色 (None 则无边框，对 plus/cross 无效)。
        :param width: 边框或线条宽度。
        :return: 绘制后的新 Image 对象。
        """
        import math
        from PIL import ImageDraw

        base = self._pil_image.copy().convert("RGBA")
        draw = ImageDraw.Draw(base)
        bw, bh = base.size

        # --- 1. 统一转换所有单位 (坐标、尺寸、线宽) ---
        # 坐标
        px = Tools.to_px(x, unit, reference=bw, dpi=self.dpi)
        py = Tools.to_px(y, unit, reference=bh, dpi=self.dpi)
        
        # 尺寸：基于 reference=min(bw, bh) 比较合理，保证标记在长宽图里视觉大小一致
        # 如果你希望它只跟高度相关，也可以 reference=bh
        ref_size = min(bw, bh) 
        
        # 转换 size 和 width
        s_px = Tools.to_px(size, unit, reference=ref_size, dpi=self.dpi)
        w_px = Tools.to_px(width, unit, reference=ref_size, dpi=self.dpi)
        
        # 确保至少有 1 像素，否则画不出来
        w_px = max(1, int(round(w_px)))
        
        # 半径 r (半边长)
        r = s_px / 2

        rgba = Tools.parse_color(color)
        out_rgba = Tools.parse_color(outline) if outline else None

        # 辅助函数：生成正多边形顶点
        def _get_polygon_points(cx, cy, radius, sides, start_angle=0):
            points = []
            for i in range(sides):
                angle = start_angle + (2 * math.pi * i) / sides
                pt_x = cx + radius * math.cos(angle - math.pi / 2)
                pt_y = cy + radius * math.sin(angle - math.pi / 2)
                points.append((pt_x, pt_y))
            return points

        # 2. 根据样式绘制
        if style == "circle":
            draw.ellipse([px - r, py - r, px + r, py + r], fill=rgba, outline=out_rgba, width=width)

        elif style == "square":
            draw.rectangle([px - r, py - r, px + r, py + r], fill=rgba, outline=out_rgba, width=width)

        elif style == "diamond":
            draw.polygon([(px, py - r), (px + r, py), (px, py + r), (px - r, py)], fill=rgba, outline=out_rgba)

        elif style == "triangle_up":
            # 正三角形
            pts = _get_polygon_points(px, py, r, 3)
            draw.polygon(pts, fill=rgba, outline=out_rgba)
            if outline: # 补画边框以确保 width 生效 (polygon outline 某些版本支持不佳)
                draw.line(pts + [pts[0]], fill=out_rgba, width=width)

        elif style == "triangle_down":
            # 倒三角形 (起始角度转 180度，即 pi)
            pts = _get_polygon_points(px, py, r, 3, start_angle=math.pi)
            draw.polygon(pts, fill=rgba, outline=out_rgba)
            if outline:
                draw.line(pts + [pts[0]], fill=out_rgba, width=width)

        elif style == "pentagon":
            # 五边形
            pts = _get_polygon_points(px, py, r, 5)
            draw.polygon(pts, fill=rgba, outline=out_rgba)
            if outline:
                draw.line(pts + [pts[0]], fill=out_rgba, width=width)

        elif style == "hexagon":
            # 六边形
            pts = _get_polygon_points(px, py, r, 6)
            draw.polygon(pts, fill=rgba, outline=out_rgba)
            if outline:
                draw.line(pts + [pts[0]], fill=out_rgba, width=width)

        elif style == "star":
            # 五角星
            points = []
            inner_r = r * 0.382  # 黄金分割比例，使星形比较标准
            for i in range(10): # 5个外角 + 5个内角 = 10个点
                angle = (2 * math.pi * i) / 10
                curr_r = r if i % 2 == 0 else inner_r
                pt_x = px + curr_r * math.cos(angle - math.pi / 2)
                pt_y = py + curr_r * math.sin(angle - math.pi / 2)
                points.append((pt_x, pt_y))
            draw.polygon(points, fill=rgba, outline=out_rgba)
            if outline:
                draw.line(points + [points[0]], fill=out_rgba, width=width)

        elif style == "target":
            # 靶心：外圆空心(或填充)，内圆实心
            # 外圆
            draw.ellipse([px - r, py - r, px + r, py + r], fill=rgba, outline=out_rgba, width=width)
            # 内圆 (颜色与 outline 相同，如果没有 outline 则为白色或反色，这里简化为白色或者比外圆更亮的颜色)
            # 这里的逻辑是：Target 样式下，size 是外圆大小，内圆是中心点
            inner_r = r * 0.3
            center_color = out_rgba if out_rgba else (255, 255, 255, 255) # 默认白点
            draw.ellipse([px - inner_r, py - inner_r, px + inner_r, py + inner_r], fill=center_color)

        elif style == "plus":
            # 为了保证线条居中且清晰，不缩减长度
            draw.line([(px - r, py), (px + r, py)], fill=rgba, width=w_px)
            draw.line([(px, py - r), (px, py + r)], fill=rgba, width=w_px)

        elif style == "cross":
            # 这样视觉上 cross 和 square 一样大
            draw.line([(px - r, py - r), (px + r, py + r)], fill=rgba, width=w_px)
            draw.line([(px - r, py + r), (px + r, py - r)], fill=rgba, width=w_px)
        return Image(base, dpi=self.dpi, label=self.label)



    def add_rect(
            self,
            start: Optional[Tuple[Union[float, int], Union[float, int]]] = None,
            end: Optional[Tuple[Union[float, int], Union[float, int]]] = None,
            center: Optional[Tuple[Union[float, int], Union[float, int]]] = None,
            size: Optional[Tuple[Union[float, int], Union[float, int]]] = None,
            unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "ratio",
            linewidth: Union[int, float] = 0.01,
            color: Union[str, Tuple[int, int, int, int]] = "red",
            edgecolor: Optional[Union[str, Tuple[int, int, int, int]]] = None,
            facecolor: Optional[Union[str, Tuple[int, int, int, int]]] = None,
            fill: bool = False,
        ) -> "Image":
        """
        添加矩形区域指示器。
        :param start: 矩形左上角坐标 (x1, y1)。
        :param end: 矩形右下角坐标 (x2, y2)。
        :param center: 矩形中心点坐标 (cx, cy)。
        :param size: 矩形尺寸 (width, height)。
        :param unit: 坐标/尺寸单位。
            该单位适用于 start/end 或 center/size 以及 linewidth。
            其中 ratio 单位是相对于图像宽度/高度的比例。
            例如 unit="ratio" 且 start=(0.1, 0.1) 表示左上角在图像宽高的 10% 处。
            另外，linewidth 使用 min(width, height) 作为参考尺寸进行转换。
            这样可以保证在不同宽高比的图像上，线宽视觉效果一致。
            当然，你也可以选择 inch/cm/mm 等绝对单位，结合 dpi 使用。
        :param color: 基本颜色，若未指定 edgecolor/facecolor 则以此为准。
        :param edgecolor: 边框颜色，覆盖 color。
        :param facecolor: 填充颜色，覆盖 color。
        :param linewidth: 边框宽度。
        :param fill: 是否填充。
        """
        base = self._pil_image.copy().convert("RGBA")
        draw = ImageDraw.Draw(base)
        bw, bh = base.size

        unit = unit.lower()
        Validator.validate_unit(unit)

        # 颜色逻辑处理
        actual_edge = edgecolor if edgecolor is not None else color
        actual_face = facecolor if facecolor is not None else color
        
        outline_rgba = Tools.parse_color(actual_edge)
        fill_rgba = Tools.parse_color(actual_face) if fill else None

        lw_px = Tools.to_px(linewidth, unit, reference=min(bw, bh), dpi=self.dpi)
        lw_px = max(1, int(round(lw_px)))

        if start is not None and end is not None:
            x1 = Tools.to_px(start[0], unit, reference=bw, dpi=self.dpi)
            y1 = Tools.to_px(start[1], unit, reference=bh, dpi=self.dpi)
            x2 = Tools.to_px(end[0], unit, reference=bw, dpi=self.dpi)
            y2 = Tools.to_px(end[1], unit, reference=bh, dpi=self.dpi)
        elif center is not None and size is not None:
            cx = Tools.to_px(center[0], unit, reference=bw, dpi=self.dpi)
            cy = Tools.to_px(center[1], unit, reference=bh, dpi=self.dpi)
            w = Tools.to_px(size[0], unit, reference=bw, dpi=self.dpi)
            h = Tools.to_px(size[1], unit, reference=bh, dpi=self.dpi)
            x1, y1 = cx - w / 2, cy - h / 2
            x2, y2 = cx + w / 2, cy + h / 2
        else:
            raise ValueError("Rect requires start+end or center+size.")

        draw.rectangle([x1, y1, x2, y2], outline=outline_rgba, width=lw_px, fill=fill_rgba)
        return Image(base, dpi=self.dpi, label=self.label)



    def add_oval(
        self,
        start: Optional[Tuple[Union[float, int], Union[float, int]]] = None,
        end: Optional[Tuple[Union[float, int], Union[float, int]]] = None,
        center: Optional[Tuple[Union[float, int], Union[float, int]]] = None,
        radius: Optional[Union[float, int]] = None,
        axis_ratio: float = 1.0,
        unit: Literal["pixel", "ratio", "inch", "cm", "mm"] = "ratio",
        linewidth: Union[int, float] = 2,
        color: Union[str, Tuple[int, int, int, int]] = "red",
        edgecolor: Optional[Union[str, Tuple[int, int, int, int]]] = None,
        facecolor: Optional[Union[str, Tuple[int, int, int, int]]] = None,
        fill: bool = False,
    ) -> "Image":
        """
        添加圆形/椭圆区域指示器。
        :param start: 外接矩形左上角坐标 (x1, y1)。
        :param end: 外接矩形右下角坐标 (x2, y2)。
        :param center: 椭圆中心点坐标 (cx, cy)。
        :param radius: 短轴半径。
        :param unit: 坐标/尺寸单位。
        :param axis_ratio: 长轴/短轴比例，1.0 表示圆形。
        :param color: 基本颜色。
        :param edgecolor: 边框颜色。
        :param facecolor: 填充颜色。
        :param linewidth: 边框宽度。
        :param fill: 是否填充。
        """
        base = self._pil_image.copy().convert("RGBA")
        draw = ImageDraw.Draw(base)
        bw, bh = base.size

        unit = unit.lower()
        Validator.validate_unit(unit)

        # 颜色逻辑处理
        actual_edge = edgecolor if edgecolor is not None else color
        actual_face = facecolor if facecolor is not None else color
        
        outline_rgba = Tools.parse_color(actual_edge)
        fill_rgba = Tools.parse_color(actual_face) if fill else None

        lw_px = Tools.to_px(linewidth, unit, reference=min(bw, bh), dpi=self.dpi)
        lw_px = max(1, int(round(lw_px)))

        if start is not None and end is not None:
            x1 = Tools.to_px(start[0], unit, reference=bw, dpi=self.dpi)
            y1 = Tools.to_px(start[1], unit, reference=bh, dpi=self.dpi)
            x2 = Tools.to_px(end[0], unit, reference=bw, dpi=self.dpi)
            y2 = Tools.to_px(end[1], unit, reference=bh, dpi=self.dpi)
        elif center is not None and radius is not None:
            if axis_ratio <= 0:
                raise ValueError("axis_ratio must be positive.")
            ratio = axis_ratio if axis_ratio >= 1.0 else (1.0 / axis_ratio)

            cx = Tools.to_px(center[0], unit, reference=bw, dpi=self.dpi)
            cy = Tools.to_px(center[1], unit, reference=bh, dpi=self.dpi)
            r_short = Tools.to_px(radius, unit, reference=min(bw, bh), dpi=self.dpi)
            r_long = r_short * ratio

            x1, y1 = cx - r_long, cy - r_short
            x2, y2 = cx + r_long, cy + r_short
        else:
            raise ValueError("Oval requires start+end or center+radius.")

        draw.ellipse([x1, y1, x2, y2], outline=outline_rgba, width=lw_px, fill=fill_rgba)
        return Image(base, dpi=self.dpi, label=self.label)


    def labeled(self, 
                label: Optional[str] = None, 
                loc: PositionType = "top_left", 
                offset: Union[float, int, Tuple[float, float]] = (0.02, 0.02),
                format_str: str = "({})", 
                case: Literal[None, "upper", "lower"] = None,
                fontsize: Union[int, float] = Consts.DEFAULT_FONT_SIZE, 
                fontweight: str = "bold", 
                color: str = "black", 
                font: str = "sans-serif", 
                box_style: Optional[Dict[str, Any]] = None) -> 'Image':
        """
        [智能标注] 为图像添加子图编号或标题 (e.g., "(a)", "Fig. 1")。
        
        相比 add_text，它更专注于科研子图的自动编号，具有以下特性：
        1. 自动内容: 默认使用初始化时的 label (e.g. Image(..., label="a"))。
        2. 格式化: 通过 format_str 自动包裹括号或添加点。
        3. 默认样式: 默认粗体、左上角、留出适量边距，符合 SCI 常见标准。

        :param label: (可选) 强制指定标签内容。若为 None，则使用 self.label。
        :param loc: 位置 (default: "top_left")。
        :param offset: 距离边缘的内边距。
                       建议使用 tuple (x_off, y_off) 做微调。
                       默认 (0.02, 0.02) 表示宽高各 2% 的间距。
        :param format_str: 格式化字符串 (default: "({})")。
                           - "({})" -> "(a)"
                           - "{}"   -> "a"
                           - "{}."  -> "a."
                           - "Fig. {}" -> "Fig. a"
        :param case: 大小写转换 (default: None)。
                     - "upper": 强制大写 (a -> A)。
                     - "lower": 强制小写 (A -> a)。
        :param fontsize: 字体大小 (通常比普通文本稍大)。
        :param fontweight: 字重 (默认 "bold")。
        :param color: 颜色。
        :param font: 字体。
        :param box_style: 背景框样式。
                          e.g. {'facecolor': 'white', 'alpha': 200} 用于复杂背景。
        :return: 新 Image 对象。
        """
        # 1. 确定原始内容
        # 优先级: 参数 label > self.label > "?"
        content = label if label is not None else self.label
        if content is None:
            content = "?" # 提醒用户缺失 label
        
        content = str(content)

        # 2. 处理大小写
        if case == None:
            pass # 保持原样
        elif case == "upper":
            content = content.upper()
        elif case == "lower":
            content = content.lower()

        # 3. 应用格式化 (e.g. "({})" + "a" -> "(a)")
        # 容错：如果用户忘了写 {}，我们默认就是追加
        if "{}" in format_str:
            final_text = format_str.format(content)
        else:
            final_text = format_str + content

        # 4. 调用通用的 add_text
        # 这里我们将 offset 默认为 unit="ratio"，因为科研绘图通常希望
        # 标签位置相对于图片大小是固定的比例（无论图片缩放多大）。
        return self.add_text(
            text=final_text,
            loc=loc,
            offset=offset,
            unit="ratio",     # 强制使用相对比例，适应性更强
            fontsize=fontsize,
            fontweight=fontweight,
            color=color,
            font=font,
            box_style=box_style,
            anchor=loc        # 让锚点自动跟随位置 (top_left 对应 top_left anchor)
        )


    def show(self, width: int = None, scale: float = None):
        """
        在 Jupyter/IPython 中显示图片。
        
        优势：
        1. 使用 IPython 原生 display，兼容 VS Code。
        2. 支持 display-time resizing (只改变显示大小，不修改原图像素)。
        3. 自动检测环境，如果在非 Jupyter 环境下运行，回退到系统默认查看器。

        :param width: 指定显示的宽度 (像素)。例如 width=500。
        :param scale: 指定缩放比例。例如 scale=0.5 (缩小一半显示)。
                      (注意：width 优先级高于 scale)。
        """
        try:
            # 1. 尝试导入 IPython 的显示工具
            # 如果不在 Jupyter 环境下，这里可能会报错或者没有任何反应，
            # 但通常只要安装了 IPython 库就能导入。
            from IPython.display import display, Image as IPyImage
            from io import BytesIO

            # 2. 将当前 PIL 图片转为 PNG 字节流
            b = BytesIO()
            self._pil_image.save(b, format='PNG')
            data = b.getvalue()

            # 3. 计算显示尺寸 (HTML 渲染层面)
            # 这里的 resize 只是为了在网页上看着舒服，不会改变 self._pil_image 本身
            display_width = width
            
            if display_width is None:
                if scale is not None:
                    # 用户指定了缩放比例
                    display_width = int(self.width * scale)
                elif self.dpi > 100:
                    # [智能默认值]: 如果既没指定宽也没指定缩放，且是高 DPI (如300)
                    # 默认缩小显示，模拟在 100 DPI 屏幕上的物理尺寸
                    # 这样 6英寸的图在屏幕上看起来就是 6英寸，而不是巨大的一张
                    display_width = int(self.width * (100 / self.dpi))
            
            # 4. 调用 Jupyter 的 display 函数
            # IPyImage 是 HTML 标签的封装，width 参数控制 <img width="...">
            display(IPyImage(data=data, width=display_width))

        except ImportError:
            # 5. [Fallback] 如果没有 IPython (比如在纯终端脚本运行)
            # 回退到 PIL 的标准 show，调用操作系统图片查看器
            logger.warning("IPython not found. Falling back to system viewer.")
            self._pil_image.show()


    def _repr_png_(self):
        """让 Jupyter Notebook 能够直接渲染 Image 对象。"""
        from io import BytesIO
        byte_io = BytesIO()
        self._pil_image.save(byte_io, format='PNG')
        return byte_io.getvalue()
    

    def save(self, path: str, **kwargs):
        """
        保存并导出图片。
        
        :param path: 输出文件路径 (e.g. "output/fig1.png") (type: str)。
        :param **kwargs: 传递给 IOEngine.save 的额外参数。
                         例如 quality=95 (JPG), compression="tiff_lzw" (TIFF) 等。
        """
        final_img = self._pil_image
        
        logger.debug(f"Saving Figure to: {path}")
        IOEngine.save(
            final_img,
            path, 
            dpi=self.dpi, 
            **kwargs
        )
