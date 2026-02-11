# figengine/engine/layout.py
# -*- coding: utf-8 -*-

"""
Project: FigEngine
File: layout.py
Author: Omarjan Obulkasim @ SYSU
Date: 2026/01/18
License: MIT License
Description: Core Layout Engine. Calculates the exact (x, y) coordinates and 
             dimensions (w, h) for every image in the figure based on flow layout logic.
"""

from typing import List, Dict, Any, Union
from ..utils.logger import get_logger
from ..utils.tools import Tools

logger = get_logger()

class LayoutEngine:
    """
    布局引擎 (Layout Engine)。
    
    这是 FigEngine 的“大脑”。它不处理像素，只处理几何逻辑。
    它负责接收一系列的 Rows 配置，根据间距 (Margins/Padding) 和对齐策略 (Alignment)，
    计算出每一张图片最终在画布上的绝对坐标和尺寸。
    """

    @staticmethod
    def calculate(rows: List[Any], 
                  margins: Dict[str, float], 
                  unit: str, 
                  dpi: int, 
                  base_width: int, 
                  base_height: int) -> Dict[str, Any]:
        """
        执行布局计算的核心逻辑。
        
        :param rows: 行对象列表 (List[Row])。
        :param margins: 全局画布边距字典 {'top':.., 'bottom':.., 'left':.., 'right':..}。
        :param unit: 边距的单位 (e.g. "ratio", "px", "cm")。
        :param dpi: 画布分辨率 (用于物理单位换算)。
        :param base_width: 基准宽度 (type: int)。
                           - 如果 > 0: 使用固定宽度布局。
                           - 如果 = 0: 引擎自动根据内容推断最大自然宽度 (Auto-detect)。
        :param base_height: 基准高度 (type: int)。
                            主要用于计算垂直方向的百分比边距。
        :return: 包含布局结果的字典:
                 {
                     "total_width": int,
                     "total_height": int,
                     "placements": [
                         {"image_ref": obj, "x": int, "y": int, "width": int, "height": int, "align": str},
                         ...
                     ]
                 }
        """
        if not rows:
            return {"total_width": 0, "total_height": 0, "placements": []}

        # =========================================================
        # 1. 确定基准宽度 (Auto-detect if 0)
        # =========================================================
        # 如果用户没有指定 base_width (即为0)，我们需要自动计算
        if base_width <= 0:
            max_natural_width = 0
            for row in rows:
                current_row_width = sum([img.width for img in row.images])
                if current_row_width > max_natural_width:
                    max_natural_width = current_row_width
            
            base_width = max_natural_width if max_natural_width > 0 else 1000
            logger.debug(f"Base width auto-detected: {base_width}px")
        else:
            logger.debug(f"Using fixed base width: {base_width}px")

        # =========================================================
        # 2. 解析全局 Margins
        # =========================================================
        # CSS 和大多数排版引擎都约定：百分比 Margin/Padding 均相对于容器的 Width 计算
        ref_size = base_width
        
        # 水平 margin 参考 width，垂直 margin 参考 height
        m_left = Tools.to_px(margins['left'], unit=unit, reference=ref_size, dpi=dpi)
        m_right = Tools.to_px(margins['right'], unit=unit, reference=ref_size, dpi=dpi)
        m_top = Tools.to_px(margins['top'], unit=unit, reference=ref_size, dpi=dpi)
        m_bottom = Tools.to_px(margins['bottom'], unit=unit, reference=ref_size, dpi=dpi)

        content_width = base_width
        placements = []
        current_y = m_top

        # =========================================================
        # 3. 逐行排版
        # =========================================================
        for i, row in enumerate(rows):
            # 定义该行的单位转换函数 (Closure)
            def to_px(val):
                return Tools.to_px(val, unit=row.unit, reference=content_width, dpi=300)

            # --- A. 垂直间距 (Row Top Margin) ---
            r_top_px = to_px(row.margin_top)
            r_bottom_px = to_px(row.margin_bottom)
            
            current_y += r_top_px
            
            # --- B. 水平间距 (Item Paddings) ---
            total_padding_width = 0
            left_px_list = []
            right_px_list = []
            
            # 批量解析 Padding
            for val in row.item_lefts:
                px = to_px(val)
                left_px_list.append(px)
                total_padding_width += px
                
            for val in row.item_rights:
                px = to_px(val)
                right_px_list.append(px)
                total_padding_width += px

            # 计算剩余给图片内容的净宽度
            images_avail_width = content_width - total_padding_width
            if images_avail_width < 0: 
                logger.warning(f"Row {i} padding ({total_padding_width}px) exceeds width. Clamping to 0.")
                images_avail_width = 0
            
            # --- C. 计算尺寸 (Strategy: Full vs Uniform) ---
            item_target_dims = [] # 存储 [(w, h), (w, h), ...]
            row_final_height = 0  # 这一行最终占据的高度
            
            # >>> 策略 1: FULL (强制对齐/Justified) <<<
            # 逻辑：忽略原图比例差异，强制所有图片等高，调整高度以填满行宽。
            if row.v_align == "full":
                total_aspect = sum([img.aspect_ratio for img in row.images])
                
                if total_aspect > 0:
                    row_final_height = int(images_avail_width / total_aspect)
                else:
                    row_final_height = 0

                for img in row.images:
                    t_w = int(row_final_height * img.aspect_ratio)
                    t_h = row_final_height
                    item_target_dims.append((t_w, t_h))
                
                logger.debug(f"Row {i} (FULL): height={row_final_height}px")

            # >>> 策略 2: Top / Center / Bottom (统一缩放/Uniform) <<<
            # 逻辑：保持原图相对大小关系不变。
            # - h_align="full": 等比缩放以填满宽度（间距固定）。
            # - 其他 h_align: 保留原尺寸，行内对齐由 h_align 控制。
            # 行高取缩放后最高的图，矮的图需要填充背景。
            else:
                # 1. 计算缩放比例 (Fit Width)
                sum_original_width = sum([img.width for img in row.images])
                
                scale_factor = 1.0
                if row.h_align == "full" and sum_original_width > 0:
                    scale_factor = images_avail_width / sum_original_width
                
                # 2. 计算缩放后的临时尺寸，并找出最大高度
                temp_dims = []
                max_h = 0
                
                for img in row.images:
                    t_w = int(img.width * scale_factor)
                    t_h = int(img.height * scale_factor)
                    temp_dims.append((t_w, t_h))
                    
                    if t_h > max_h:
                        max_h = t_h
                
                row_final_height = max_h
                
                # 3. 生成最终目标尺寸 (高度统一设为 max_h，触发 RenderEngine 的 pad_to_size)
                for (t_w, t_h) in temp_dims:
                    item_target_dims.append((t_w, row_final_height))
                
                logger.debug(f"Row {i} ({row.v_align.upper()}): height={row_final_height}px, scale={scale_factor:.2f}")

            # --- D0. 水平对齐策略 (Left/Center/Right/Justify/Full) ---
            sum_item_width = sum([w for (w, _) in item_target_dims])
            row_content_width = sum_item_width + total_padding_width
            remaining = content_width - row_content_width
            if remaining < 0:
                remaining = 0

            row_offset_x = 0
            extra_gap = 0
            if row.h_align == "center":
                row_offset_x = remaining / 2
            elif row.h_align == "right":
                row_offset_x = remaining
            elif row.h_align == "justify":
                if len(row.images) > 1 and remaining > 0:
                    extra_gap = remaining / (len(row.images) - 1)

            # --- D. 生成坐标 (Placement) ---
            current_x = m_left + row_offset_x
            
            for j, img in enumerate(row.images):
                p_left = left_px_list[j]
                p_right = right_px_list[j]
                
                # 1. 应用左边距
                current_x += p_left
                
                # 2. 获取目标尺寸
                target_w, target_h = item_target_dims[j]
                
                # 3. 记录数据
                placements.append({
                    "image_ref": img,
                    "x": current_x,
                    "y": current_y,
                    "width": target_w,
                    "height": target_h,
                    "align": row.v_align  # 传递垂直对齐方式给 RenderEngine
                })
                
                # 4. 推进 X 坐标
                current_x += target_w + p_right
                if extra_gap and j < (len(row.images) - 1):
                    current_x += extra_gap
            
            # --- E. 推进 Y 坐标 ---
            current_y += row_final_height
            current_y += r_bottom_px

        # =========================================================
        # 4. 汇总结果
        # =========================================================
        total_width = content_width + m_left + m_right
        total_height = current_y + m_bottom
        
        logger.debug(f"Final layout size: {total_width}x{total_height}px")

        return {
            "total_width": total_width,
            "total_height": total_height,
            "placements": placements
        }
