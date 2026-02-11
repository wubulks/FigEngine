# figengine/engine/io.py
# -*- coding: utf-8 -*-

"""
Project: FigEngine
File: io.py
Author: Omarjan Obulkasim @ SYSU
Date: 2026/01/18
License: MIT License
Description: Input/Output Engine. Handles file reading/writing with specific 
             optimizations for scientific publication formats (TIFF LZW, PDF DPI).
"""

import os
from PIL import Image as PILImage
PILImage.MAX_IMAGE_PIXELS = 1_000_000_000
from pdf2image import convert_from_path

from ..utils.validators import Validator
from ..utils.logger import get_logger
logger = get_logger()

class IOEngine:
    """
    I/O 引擎 (Input/Output Engine)。
    
    负责处理所有的文件读取与写入操作。
    封装了针对不同文件格式（特别是 PDF 和 TIFF）的特殊处理逻辑，
    确保输出结果符合科研出版的 DPI 和压缩标准。
    """

    @staticmethod
    def load(path: str, dpi: int = 600) -> PILImage.Image:
        """
        从文件加载图像。
        
        :param path: 文件路径 (type: str)。
        :return: 转换后的 RGBA 模式 PIL Image 对象。
        :raises FileNotFoundError: 如果文件不存在。
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image file not found: {path}")
        dpi = int(dpi or 600)

        ext = os.path.splitext(path)[1].lower()

        if ext == '.pdf':
            # 将 PDF 第一页转换为 PIL Image
            # dpi 参数决定了读取时的清晰度
            Validator.validate_pdf_backend()
            logger.debug(f"Converting PDF page to Image: {path}")
            images = convert_from_path(path, dpi=dpi)
            if len(images) == 0:
                raise ValueError(f"Could not convert PDF: {path}")
            return images[0].convert("RGBA") # 返回第一页
        
        # 通用位图读取
        return PILImage.open(path).convert("RGBA")


    @staticmethod
    def save(image: PILImage.Image, path: str, dpi: int = 600, **kwargs):
        """
        将图像保存到磁盘。
        
        自动处理目录创建、格式识别和特定格式的参数优化。
        
        :param image: 要保存的 PIL Image 对象 (type: PILImage.Image)。
        :param path: 保存路径，包含文件名和后缀 (e.g. "out/fig1.tiff") (type: str)。
        :param dpi: 输出分辨率 (Dots Per Inch) (type: int, default: 300)。
                    对于科研绘图，建议设置为 300 (常规) 或 600 (高精/线图)。
        :param **kwargs: 传递给底层 PIL.save() 的额外参数 (e.g. quality=95)。
        """
        if image is None:
            logger.error("No image data to save.")
            return

        # 1. 自动创建不存在的目录
        output_dir = os.path.dirname(path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.debug(f"Created directory: {output_dir}")

        # 2. 根据后缀名处理特殊逻辑
        ext = os.path.splitext(path)[1].lower()

        try:
            if ext == '.pdf':
                IOEngine._save_as_pdf(image, path, dpi, **kwargs)
            elif ext in ['.tiff', '.tif']:
                IOEngine._save_as_tiff(image, path, dpi, **kwargs)
            else:
                # 通用保存逻辑（PNG, JPG）
                image.save(path, dpi=(dpi, dpi), **kwargs)
            
            logger.debug(f"File exported successfully: {path} @ {dpi} DPI")

        except Exception as e:
            logger.error(f"Failed to save image to {path}: {str(e)}")
            raise


    @staticmethod
    def _save_as_pdf(image: PILImage.Image, path: str, dpi: int, **kwargs):
        """
        [内部方法] 专门处理 PDF 导出。
        
        逻辑特点：
        1. 强制设置分辨率。
        2. 如果是 RGBA 模式，自动融合白色背景转为 RGB (PDF 对透明度支持不一，且出版通常要求扁平化)。
        """
        # PDF 默认以 72 DPI 为基准点，保存时需要明确指定分辨率
        # 如果有透明层 (RGBA)，PDF 导出通常需要转为 RGB
        if image.mode == 'RGBA':
            logger.debug("Converting RGBA to RGB for PDF export.")
            background = PILImage.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background

        image.save(path, "PDF", resolution=float(dpi), save_all=True)


    @staticmethod
    def _save_as_tiff(image: PILImage.Image, path: str, dpi: int, **kwargs):
        """
        [内部方法] 专门处理 TIFF 导出。
        
        逻辑特点：
        1. 默认开启 "tiff_lzw" 无损压缩 (减小体积但不损失画质)。
        2. 写入 DPI 元数据。
        """
        # 默认使用 LZW 压缩以减小体积但不损失质量
        params = {
            "compression": "tiff_lzw",
            "dpi": (dpi, dpi),
            "save_all": True
        }
        params.update(kwargs) # 允许用户覆盖压缩设置
        
        image.save(path, **params)