# -*- coding: utf-8 -*-
import sys
import os
from PIL import Image as PILImage

import figengine as fe


DPI = 600

def main():
    # 1. 初始化日志 (开启 DEBUG 模式以检查内部逻辑)
    print(">>> Setting up logger...")
    fe.setup_logger(level="WARNING")

    # 2. 准备测试素材 (自动生成 red.png, blue.png, green.png)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(current_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # 3. 初始化 Figure
    print("\n>>> Initializing Figure...")
    fig = fe.Figure(background="white", dpi=DPI)
    
    # 设置边距 (5%)
    fig.set_margins(top=0.01, bottom=0.02, left=0.03, right=0.04)

    # 4. 创建 Image 对象
    print("\n>>> Creating Image...")
    img1 = fe.Image.new(size=(6.0, 5.0), facecolor="#FFB8CD", unit="inch", dpi=DPI)

    # 打印图片信息
    print(">>> img1 size (pixel):", img1.size)
    print(">>> img1 size (inch):", img1.get_size(unit="inch"))
    print(">>> img1 size (cm):", img1.get_size(unit="cm"))
    print(">>> img1 dpi:", img1.dpi)

    # 旋转图片15度 (逆时针)
    print(">>> img1 rotated by 15 degrees.")
    img1_=img1.rotate(15, expand=True)

    # 旋转图片25度 (顺时针)
    print(">>> img1 rotated by -25 degrees.")
    img1__=img1.rotate(-25, expand=True)

    # 保存图片
    img1_path = os.path.join(assets_dir, "img1.png")
    img1.save(img1_path)
    img1_path_ = os.path.join(assets_dir, "img1_rotated_15.png")
    img1_.save(img1_path_)
    img1_path__ = os.path.join(assets_dir, "img1_rotated_neg25.png")
    img1__.save(img1_path__)

if __name__ == "__main__":
    main()

