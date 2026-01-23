# figengine/engine/renderer.py
# -*- coding: utf-8 -*-

"""
Project: FigEngine
File: renderer.py
Author: Mute
Date: 2026/01/18
License: MIT License
Description: Rendering Engine. Responsible for drawing pixels onto the canvas 
             based on the coordinates calculated by the LayoutEngine. 
             Also handles high-quality text rendering using Matplotlib.
"""

import os
import numpy as np
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.font_manager import FontProperties
# import matplotlib.patches as patches # 暂未使用，可注释
from PIL import Image as PILImage
from typing import Tuple, Optional, Dict, Any, Union, List

from ..utils.logger import get_logger
from ..utils.tools import Tools
matplotlib.use('Agg') 

logger = get_logger()


class RenderEngine:
    """
    渲染引擎 (Rendering Engine)。
    
    职责：
    1. 接收 LayoutEngine 计算出的几何信息 (坐标、尺寸)。
    2. 执行实际的图像缩放、裁剪、填充操作。
    3. 将所有元素绘制到一个大的 PIL Canvas 上。
    """

    @staticmethod
    def draw_layout(layout_data: Dict[str, Any], bg_color: Union[str, Tuple[int, int, int]] = "white") -> PILImage.Image:
        """
        根据 LayoutEngine 计算的位置信息绘制最终图像。

        :param layout_data: 布局数据字典 (由 LayoutEngine.calculate 返回)。
                            结构: {
                                'total_width': int,
                                'total_height': int,
                                'placements': [
                                    {'image_ref': Image, 'x': int, 'y': int, 'width': int, 'height': int, 'align': str},
                                    ...
                                ]
                            }
        :param bg_color: 画布背景颜色 (type: str | tuple, default: "white")。
        :return: 绘制完成的 PIL Image 对象 (RGBA 模式)。
        """
        total_w = int(layout_data['total_width'])
        total_h = int(layout_data['total_height'])
        
        # 解析背景色
        bg_rgba = Tools.parse_color(bg_color)
        canvas = PILImage.new("RGBA", (total_w, total_h), bg_rgba)
        
        placements = layout_data.get('placements', [])
        
        for i, item in enumerate(placements):
            # 获取数据
            core_img = item['image_ref'] # Core.Image 对象
            target_w = item['width']
            target_h = item['height']
            dest_x = item['x']
            dest_y = item['y']
            
            # Row 中使用的是 "align" 属性 (top, center, bottom, full)
            # 但 Image.pad_to_size 中使用的是 "loc" 参数
            align_mode = item.get('align', 'full') 
            
            # --- 图像处理与调整 ---
            final_pil = None
            
            # 1. Full Mode (强制拉伸/两端对齐)
            # 如果图片需要完全填满目标区域 (改变宽高比)，则直接 resize
            if align_mode == 'full':
                if (core_img.width != target_w) or (core_img.height != target_h):
                    processed_img = core_img.resize(width=target_w, height=target_h)
                    final_pil = processed_img.get_internal_image()
                else:
                    final_pil = core_img.get_internal_image()
            
            # 2. Uniform Mode (统一比例 + 填充/裁剪)
            # 如果是 top/center/bottom 模式，说明图片高度可能不足 target_h
            # 需要先等比缩放至宽度一致，然后通过 pad_to_size 填充高度
            else:
                # 逻辑：先等比缩放到 Fit Width
                scaled_content_h = int(target_w / core_img.aspect_ratio)
                temp_img = core_img.resize(width=target_w, height=scaled_content_h)
                
                # 再调整高度 (Pad Height)
                # [关键修复]: 参数名需为 loc，而非 align
                padded_img = temp_img.pad_to_size(
                    target_size=(target_w, target_h),
                    loc=align_mode, # 映射 row.align -> image.loc
                    axis="height", 
                    bg_color=bg_color 
                )
                final_pil = padded_img.get_internal_image()

            # --- 绘制 ---
            dest_pos = (int(dest_x), int(dest_y))
            # 只有 RGBA 图片才需要 mask，否则透明度会丢失
            mask = final_pil if final_pil.mode == 'RGBA' else None
            canvas.paste(final_pil, dest_pos, mask=mask)
            
        return canvas



class TextRenderer:
    """
    基于 Matplotlib 的文本渲染器。
    
    特点：
    1. 强制画布背景透明，解决 PIL 粘贴时的白边问题。
    2. 支持复杂的 BBox (边框/背景) 样式。
    3. 优秀的字体回退机制。
    """
    @staticmethod
    def render(text: str, 
               fontsize: int = 24, 
               color: str = "black", 
               font: str = "sans-serif",
               weight: str = "normal",      
               rotation: float = 0,         
               dpi: int = 300,
               box_style: Optional[Dict[str, Any]] = None) -> PILImage.Image:
        """
        渲染文本为 RGBA 图像。

        :param text: 文本内容 (str)。
        :param fontsize: 字体大小 (int, points), 默认 24。
        :param color: 文本颜色 (str), 默认 "black"。支持 hex, 英文名等。
        :param font: 字体名或路径 (str), 默认 "sans-serif"。
        :param weight: 字重 (str), 默认 "normal"。可选 "bold", "light" 等。
        :param rotation: 旋转角度 (float), 默认 0。
        :param dpi: 渲染精度 (int), 默认 300。
        :param box_style: (可选) 文本边框与背景样式配置 (Dict)。
            若为 None (默认)，则背景完全透明，无边框。
            
            支持的键 (Key):
            - 'facecolor': 背景填充色 (str)。默认 'none' (透明)。
                           e.g. 'white', '#FF0000', 'blue'.
            - 'edgecolor': 边框颜色 (str)。默认 'none' (无边框)。
            - 'alpha': 背景/边框透明度 (float, 0~255 或 0.0~1.0)。
                       注意：mpl通常用0-1，为了兼容旧代码若>1则视为0-255。
            - 'boxstyle': 形状样式 (str)。默认 'square,pad=0.3'。
                          e.g. 'circle', 'round', 'larrow', 'rarrow'.
            - 'linewidth': 边框线宽 (float)。
            
        :return: 裁剪好的 PIL Image (Mode: RGBA)。
        """
        # 1. 配置字体
        font_props = TextRenderer._get_font_props(font, fontsize, weight)
        
        # 2. 创建画布
        # 给定足够大的画布防止旋转被裁剪
        fig = Figure(figsize=(10, 10), dpi=dpi)
        
        # [核心修复] 强制将 Matplotlib 画布背景设为全透明
        # 这样 canvas 抓取的非文字区域 alpha 才会是 0
        fig.patch.set_alpha(0)
        
        canvas = FigureCanvasAgg(fig)
        
        # 3. 创建文本对象 (Anchor 设为中心，方便后续计算)
        mpl_text = fig.text(0.5, 0.5, text, 
                            fontsize=fontsize, 
                            color=color, 
                            fontproperties=font_props,
                            rotation=rotation,
                            va='center', ha='center') 

        # 4. 设置文本背景框 (BBox)
        # 仅当 box_style 不为 None 时启用
        if box_style is not None:
            # 处理 Alpha: 兼容 0-255 和 0.0-1.0
            raw_alpha = box_style.get('alpha', 255)
            final_alpha = raw_alpha / 255.0 if raw_alpha > 1.0 else raw_alpha

            bbox_props = {
                'boxstyle': box_style.get('boxstyle', 'square,pad=0.3'), 
                'facecolor': box_style.get('facecolor', 'none'), # [重点] 默认无填充
                'edgecolor': box_style.get('edgecolor', 'none'), # [重点] 默认无边框
                'alpha': final_alpha,
                'linewidth': box_style.get('linewidth', box_style.get('width', 0))
            }
            mpl_text.set_bbox(bbox_props)

        # 5. 绘制并获取渲染器
        canvas.draw() 
        renderer = canvas.get_renderer()
        
        # 6. 计算裁剪区域 (文字 BBox U 背景框 BBox)
        bbox_text = mpl_text.get_window_extent(renderer)
        
        bbox_patch = None
        patch = mpl_text.get_bbox_patch()
        if patch:
            bbox_patch = patch.get_window_extent(renderer)
        
        if bbox_patch:
            x0 = min(bbox_text.x0, bbox_patch.x0)
            y0 = min(bbox_text.y0, bbox_patch.y0)
            x1 = max(bbox_text.x1, bbox_patch.x1)
            y1 = max(bbox_text.y1, bbox_patch.y1)
        else:
            x0, y0, x1, y1 = bbox_text.x0, bbox_text.y0, bbox_text.x1, bbox_text.y1
        
        # 增加 Padding 防止抗锯齿边缘被切
        extra_pad = 5
        if box_style and ('linewidth' in box_style or 'width' in box_style):
             # 简单的容错处理
             lw = box_style.get('linewidth', box_style.get('width', 1))
             extra_pad += int(lw)

        x0 = int(x0) - extra_pad
        y0 = int(y0) - extra_pad
        x1 = int(x1) + extra_pad
        y1 = int(y1) + extra_pad   
        
        # 7. Buffer 截取 (Matplotlib 坐标系转图像坐标系)
        w_canvas, h_canvas = canvas.get_width_height()
        buf = np.asarray(canvas.buffer_rgba())
        
        np_y0 = max(0, h_canvas - y1) 
        np_y1 = min(h_canvas, h_canvas - y0) 
        np_x0 = max(0, x0)
        np_x1 = min(w_canvas, x1)
        
        # 检查无效区域
        if np_y0 >= np_y1 or np_x0 >= np_x1:
            return PILImage.new("RGBA", (1, 1))
            
        cropped_buf = buf[np_y0:np_y1, np_x0:np_x1, :]
        return PILImage.fromarray(cropped_buf, mode="RGBA")

    @staticmethod
    def _get_font_props(font, fontsize, weight):
        """辅助函数：安全获取字体属性"""
        generic_families = {"sans-serif", "serif", "monospace", "cursive", "fantasy"}
        try:
            if font and os.path.exists(font) and os.path.isfile(font):
                fp = FontProperties(fname=font)
            elif font and font.lower() in generic_families:
                fp = FontProperties(family=[font]) 
            else:
                fp = FontProperties(family=font if font else ["sans-serif"])
            
            fp.set_size(fontsize)
            if weight: fp.set_weight(weight)
            return fp
        except Exception:
            return FontProperties(family=["sans-serif"], size=fontsize, weight=weight)