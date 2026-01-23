# %% [markdown]
# # **FigEngine: A High-Performance Structured Figure Engine**

# %% [markdown]
# ##### **1. 导入库**

# %%
import os
import sys
# 导入FigEngine库
import figengine as fe

# %%
# 定义常量
DPI = 600

# %% [markdown]
# ##### **2. 可打印的基础信息**

# %%
# 打印FigEngine库基础信息
print(f"version: {fe.__version__}")
print(f"file: {fe.__file__}")
print(f"author: {fe.__author__}")
print(f"author email: {fe.__author_email__}")
print(f"license: {fe.__license__}")
fe.Tools.print_valid_fonts()

# %% [markdown]
# ##### **3. 日志系统等级设置**

# %%
# 初始化日志记录系统
logger = fe.setup_logger(level="Warning")

# %% [markdown]
# ##### **4. 读取图片创建Image对象**
# 
# 
# 
# **函数签名:**
# 
# `fe.Image(source, label, dpi)`
# 
# **参数:**
# 
# - `source`: 文件路径或已经创建的Image对象。(支持: `.jpg`, `.png`, `.svg`, `.pdf`, `.tif`)
# - `label`: 图像标签, 后续可用于生成子图编号
# - `dpi`: 图像分辨率(默认 300), 如果 source 是文件且包含 DPI 信息，则自动读取

# %%
# 从文件加载一个Image对象
img2 = fe.Image(source="assets/img1_rotated_neg25.png", dpi=DPI, label="Test Image from File")
img2.show(width=500)

# %% [markdown]
# ##### **5. 创建空白的Image对象**
# 
# **函数签名:**
# 
# `fe.Image.new(size, facecolor, unit, dpi, label)`
# 
# **参数:**
# 
# - `size`: 图像尺寸 (width, height)
# - `facecolor`: 背景颜色(默认白色)
# - `unit`: 尺寸单位(支持: "pixel", "inch", "cm", "mm"，默认 "inch")
# - `dpi`: 图像分辨率(默认 300)
# - `label`: 图像标签, 后续可用于生成子图编号

# %%
# 创建一个空白的Image对象
img1 = fe.Image.new(size=(6.0, 5.0), facecolor="#FFB8CD", unit="inch", dpi=DPI, label="Test Image")

# %% [markdown]
# ##### **6. 图片属性**
# **函数签名:**
# 
# `Image.size`
# 
# `Image.get_size(unit)`
# 
# **尺寸:**
# 
# - `Image.size`: 图片尺寸(以像素为单位)
# - `Image.get_size(unit)`: 图片尺寸，(unit支持: "pixel", "inch", "cm", "mm"，默认 "pixel")
# 
# **分辨率:**
# 
# - `Image.dpi`: 图片分辨率
# 
# **标签:**
# 
# - `Image.label`: 图像标签

# %%
print(f"img1.size: {img1.size}")
print(f"img1.get_size(pixel): {img1.get_size('pixel')}")   # 打印像素尺寸 
print(f"img1.get_size(inch): {img1.get_size('inch')}")     # 打印英寸尺寸
print(f"img1.get_size(cm): {img1.get_size('cm')}")         # 打印厘米尺寸
print(f"img1.get_size(mm): {img1.get_size('mm')}")         # 打印毫米尺寸
print(f"img1.dpi: {img1.dpi}")                               # 打印DPI值
print(f"img1.label: {img1.label}")                             # 打印图像模式

# %% [markdown]
# ##### **7. 调整图片大小**
# 
# **函数签名:**
# 
# `Image.resize(width, height, scale, ref_image, unit, resample)`
# 
# **参数:**
# 
# - `width`: 图像宽度
# - `height`: 图像高度
# - `scale`: 缩放比例
# - `ref_image`: 参考图片
# - `unit`: 尺寸单位（支持: "pixel", "inch", "cm", "mm"，默认 "pixel"）
# - `resample`: 插值算法  
#   * `"auto"`: 智能选择（放大用 bicubic，缩小用 lanczos）, 默认方案
#   * `"lanczos"`: 高质量缩小
#   * `"bicubic"`: 平滑放大
#   * `"nearest"`: 最近邻（保硬边）

# %%
# 调整图像大小
print("原始比例", img1.size, img1.get_size("inch"), img1.get_size("cm"))

# 强制指定高度和宽度
img2 = img1.resize(width=4.0, height=2.5, unit="inch")
print("强制指定高度和宽度", img2.size, img1.get_size("inch"), img1.get_size("cm"))

# 仅指定宽度，高度等比例缩放
img3 = img1.resize(width=4.0, unit="inch")
print("仅指定宽度，高度等比例缩放", img3.size, img3.get_size("inch"), img3.get_size("cm"))

# 仅指定高度，宽度等比例缩放
img4 = img1.resize(height=10, unit="cm")
print("仅指定高度，宽度等比例缩放", img4.size, img4.get_size("inch"), img4.get_size("cm"))

# 按比例缩放50%
img5 = img1.resize(scale=0.5)
print("按比例缩放50%", img5.size, img5.get_size("inch"), img5.get_size("cm"))

# 参照另一张图像的大小进行缩放
img6 = img1.resize(ref_image=img2)
print("参照另一张图像的大小进行缩放", img6.size, img6.get_size("inch"), img6.get_size("cm"))


# %% [markdown]
# ##### **8. 图片裁剪**
# **函数签名:**
# 
# `Image.crop(box, left, top, right, bottom, unit)`
# 
# **参数:**
# 
# *两种模式*
# - 模式1: 绝对坐标模式
#   - `box`: box=(x1, y1, x2, y2)，则代表提取该绝对坐标区域。box 优先级最高。
# - 模式2: 裁剪量模式
#   - `left`: 左侧切除量
#   - `top`: 顶部切除量
#   - `right`: 右侧切除量
#   - `bottom`: 右侧切除量
#   
# - 共有参数: 
#   - `unit`: 单位（支持: "pixel", "ratio", "inch", "cm", "mm"，默认 "pixel"）

# %%
print("原始比例", img1.size)

# 绝对坐标模式
img2 = img1.crop(box=(1.0, 1.0, 5.0, 4.0), unit="inch")
print("绝对坐标模式", img2.size)

# 裁剪量模式
img3 = img1.crop(left=1.0, top=1.0, right=1.0, bottom=1.0, unit="inch")
print("裁剪量模式(英寸)", img3.size)
img4 = img1.crop(left=0.1, top=0.1, right=0.1, bottom=0.1, unit="ratio")
print("裁剪量模式(比例)", img4.size)

# %% [markdown]
# ##### **9. 添加图片标尺**
# *图片位置定位器, 强烈推荐只是用ratio模式, 对于其他功能也是有ratio尽量使用ratio*
# 
# **函数签名:**
# 
# `Image.add_ticks(step, unit, color, font, fontsize, show_grid)`
# 
# **参数:**
# - `step`: 刻度步长
# - `unit`: 坐标单位 (支持:"pixel", "ratio", "inch", "cm", "mm"，默认 "ratio")
# - `color`: 线条和文字颜色
# - `font`: 字体名称
# - `fontsize`: 字体大小, 默认"sans-serif"
# - `show_grid`: 是否显示内部网格线, False只在边缘显示刻度 (默认 True)

# %%
img2 = img1.add_ticks(step=0.01, unit='ratio', color='black', fontsize=0.008)
img2.show(width=500)

# %% [markdown]
# ##### **10. 添加文本**
# **函数签名:**
# 
# `Image.add_text(text, x, y, position, anchor, offset, unit, fontsize, fontweight, rotation, color, font, box_style, dpi)`
# 
# 1. 语义化定位 (Semantic Mode): 不传 x, y
#    使用 position (e.g. "top_left") + offset (内边距) 来定位
# 2. 绝对坐标 (Absolute Mode): 传 x, y
#    使用 anchor (e.g. "center") 决定文字如何对齐到 (x, y)
# 
# **参数:**
# - `text`: 文本内容
# - `x`: 目标位置x (绝对坐标模式)
# - `y`: 标位置y(绝对坐标模式)
# - `loc`: 语义化位置, 不传入x, y时生效(支持: "center", "top", "bottom", "left", "right" 以及复合位置，如: top_left， 默认"top_left")
# - `anchor`: 文字自身的锚点 (支持: "center", "top", "bottom", "left", "right" 以及复合位置，如: top_left， 在绝对坐标模式下默认center, 在语义化定位模式下默认与`loc`相同)
# - `offset`: 内边距
# - `unit`: 坐标/Offset 的单位(支持: "pixel", "ratio", "inch", "cm", "mm"，默认 "ratio")
# - `fontsize`: 字体大小
#   - int: 像素值 (e.g. 24)
#   - float < 1.0: 相对高度比例 (e.g. 0.05 = 5% image height)
# - `fontweight`: 字重, 默认"normal"，支持常见的所有类型
# - `rotation`: 文字旋转角度, 默认为0
# - `color`: 文本颜色, 默认为"black"
# - `font`: 字体名称, 默认"sans-serif"
# - `box_style`: (可选) 文本边框样式, 需要传入字典 (例如: {'facecolor': 'white', 'edgecolor': 'red', 'boxstyle': 'round,pad=0.5,rounding_size=0.2'}), 与matplotlib相同
# - `dpi`: (可选) 渲染时的目标 DPI, 默认与图片dpi相同

# %%
img1_=img1.add_text("Hello, FigEngine!", loc="center", anchor="center",
                  fontsize=0.05, color="blue")
img1_=img1_.add_text("Top Left", loc="top_left", anchor="top_left",
                  fontsize=25, color="red")
img1_=img1_.add_text("Top Left", loc="top_right", anchor="top_right", offset=0.25,
                  unit="ratio", fontsize=25, color="red")
img1_=img1_.add_text("Bottom Right", x=0.9, y=0.9, unit="ratio", anchor="bottom_right",
                  fontsize=18, color="green")
img1_=img1_.add_text("Bottom Center", x=0.5, y=0.9, unit="ratio", anchor="top_left",
                  fontsize=18, color="green")
img1_=img1_.add_text("Bottom Center", x=0.7, y=0.7, unit="ratio", anchor="center",
                  fontsize=18, color="green", box_style={'facecolor': 'white', 'boxstyle': 'round,pad=0.5,rounding_size=0.4'})

formula_pi = r"$\frac{1}{\pi} = \frac{2\sqrt{2}}{9801} \sum_{k=0}^\infty \frac{(4k)!(1103+26390k)}{(k!)^4 396^{4k}}$"
img1_=img1_.add_text(formula_pi, x=0.3, y=0.4, unit="ratio", anchor="center",
                  fontsize=18, color="green", box_style={'facecolor': 'white', 'boxstyle': 'round,pad=0.5,rounding_size=0.4'})
formula_ns = r"$\rho \left( \frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u} \right) = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$"
img1_=img1_.add_text(formula_ns, x=0.3, y=0.8, unit="ratio", anchor="center",
                  fontsize=18, color="blue")
img1_.show(width=500)

# %% [markdown]
# ##### **11. 添加线条**
# **函数签名:**
# 
# `Image.add_line(start, end, unit, color, width, arrow, arrow_size, arrow_style, arrow_angle, arrow_shorten, arrow_fill)`
# 
# **参数:**
# - `start`: 起点坐标 (x1, y1)
# - `end`: 终点坐标 (x2, y2)
# - `unit`: 坐标单位 (支持: "pixel", "ratio", "inch", "cm", "mm"，默认 "ratio")
# - `color`: 线条颜色
# - `width`: 线条宽度
# - `arrow`: 箭头位置 (支持: "start", "end", "both" 或 None, 默认 None)
# - `arrow_size`: 箭头斜边长度 (像素)
# - `arrow_style`: 箭头样式: (支持: "triangle", "open", "bar", "diamond", "circle", 默认: "triangle")
# - `arrow_angle`: 箭头夹角(度), 仅triangle/open有效
# - `arrow_shorten`: 主线缩短量, None 时默认=arrow_size*0.5
# - `arrow_fill`: triangle/diamond 时是否填充(True=填充；False=只描边,默认填充)

# %%
img2 = img1.add_line(start=(0.1, 0.1), end=(0.9, 0.1), color="#CAEFD6", width=0.01, arrow="end", arrow_size=0.05, arrow_shorten=0.02, arrow_style="triangle")
img2 = img2.add_line(start=(0.1, 0.3), end=(0.9, 0.3), color="#E8E490", width=0.01, arrow="end", arrow_size=0.05, arrow_shorten=0.01, arrow_style="open")
img2 = img2.add_line(start=(0.1, 0.5), end=(0.9, 0.5), color="#FFF325", width=0.01, arrow="end", arrow_size=0.05, arrow_shorten=0.00, arrow_style="bar")
img2 = img2.add_line(start=(0.1, 0.7), end=(0.9, 0.7), color="#F8ED13", width=0.01, arrow="end", arrow_size=0.05, arrow_shorten=0.005, arrow_style="diamond")
img2 = img2.add_line(start=(0.1, 0.9), end=(0.9, 0.9), color="#928A01", width=0.01, arrow="end", arrow_size=0.05, arrow_shorten=0.01, arrow_style="circle")
img2.show(width=500)

# %% [markdown]
# ##### **12. 添加特征点**
# **函数签名:**
# 
# `Image.add_marker(x, y, unit, style, size, color, outline, width)`
# 
# **参数:**
# - `x`: 目标位置x 
# - `y`: 标位置y
# - `style`: 点的样式
#   - `circle`: "●" 圆形 
#   - `square`: "■" 正方形
#   - `diamond`: "◆" 菱形 
#   - `triangle_up`: "▲" 正三角 
#   - `triangle_down`: "▼" 倒三角 
#   - `pentagon`: "⬠" 五边形 
#   - `target`: "◎" 靶心 
#   - `plus`: "+" 加号 
#   - `cross`: "×" 叉号 
# - `size`: 点的大小
# - `color`: 填充颜色
# - `outline`: 边框颜色 (None 则无边框, 对 plus/cross 无效)
# - `width`: 边框或线条宽度

# %%
img2 = img1.add_marker(x=0.1, y=0.1, unit="ratio", style="circle", size=0.02, color="red")
img2 = img2.add_marker(x=0.2, y=0.2, unit="ratio", style="square", size=0.02, color="red")
img2 = img2.add_marker(x=0.3, y=0.3, unit="ratio", style="cross", size=0.02, color="red", width=0.005)
img2 = img2.add_marker(x=0.4, y=0.4, unit="ratio", style="plus", size=0.02, color="red", width=0.005)
img2 = img2.add_marker(x=0.5, y=0.5, unit="ratio", style="diamond", size=0.02, color="red")
img2 = img2.add_marker(x=0.6, y=0.6, unit="ratio", style="triangle_up", size=0.02, color="red")
img2 = img2.add_marker(x=0.7, y=0.7, unit="ratio", style="triangle_down", size=0.02, color="red")
img2 = img2.add_marker(x=0.8, y=0.8, unit="ratio", style="star", size=0.02, color="red")
img2 = img2.add_marker(x=0.9, y=0.9, unit="ratio", style="target", size=0.02, color="red")
img2.show(width=500)

# %% [markdown]
# ##### **13. 调整画布尺寸**
# **函数签名:**
# 
# `Image.pad_to_size(target_size, unit, position, axis, bg_color)`
# 
# **参数:**
# 
# - `target_size`: 目标尺寸 (width, height)
# - `unit`: 单位(支持: "pixel", "ratio", "inch", "cm", "mm"，默认 "pixel")
# - `position`: 原图在新画布中的锚点位置 (支持: "center", "top", "bottom", "left", "right" 以及复合位置，如: top_left， 默认"center")
# - `axis`: 仅调整某个轴向(支持: "both", "width", "height", 默认"both")
# - `bg_color`: 新增区域的填充背景色， 默认透明

# %%
print("原始比例", img1.size)

# 以比例模式进行填充
img2 = img1.pad_to_size(target_size=(1.1, 1.1), unit="ratio", bg_color="#B8FFCD")
print("以比例模式进行填充", img2.size)
# img2

img3 = img1.pad_to_size(target_size=(1900, 1600), unit="pixel", bg_color="#B8FFCD")
print("以像素模式进行填充", img3.size)
# img3

# %% [markdown]
# ##### **14. 图片旋转**
# **函数签名:**
# 
# `Image.rotate(angle, expand, bg_color)`
# 
# **参数:**
# 
# - `angle`: 要叠加的图片对象, >0 逆时针旋转，<0 顺时针
# - `expand`: 是否扩展画布
#   - False: 裁剪超出边界的部分 (画中画模式)。
#   - True: 自动扩大 Base 画布以容纳 Overlay (拼贴模式)。
# - `bg_color`: 扩展画布时的背景色， 默认透明

# %%
img2 = img1.rotate(angle=45, expand=False, bg_color="#FFFFFF")
print("旋转45度并扩展画布", img2.size)
img2.show(width=500)


# %% [markdown]
# ##### **15. 图片叠加**
# **函数签名:**
# 
# `Image.overlay(other, x, y, anchor, unit, scale, expand, bg_color)`
# 
# **参数:**
# 
# - `other`: 要叠加的图片对象
# - `x`: 叠加基准点 x
# - `y`: 叠加基准点 y
# - `anchor`: 叠加图片(other)自身的对齐点(支持: "center", "top", "bottom", "left", "right" 以及复合位置，如: top_left， 默认"center")
# - `unit`: 单位(支持: "pixel", "ratio", "inch", "cm", "mm"，默认 "ratio")
# - `scale`: 叠加图片(other)的缩放比例, 默认为1.0
# - `expand`: 是否扩展画布
#   - False: 裁剪超出边界的部分 (画中画模式)。
#   - True: 自动扩大 Base 画布以容纳 Overlay (拼贴模式)。
# - `bg_color`: 扩展画布时的背景色， 默认透明

# %%
# 创建一个空白的Image对象
img2 = fe.Image.new(size=(3.0, 3.0), facecolor="#FFFF25", unit="inch", dpi=DPI, label="Test Image")
img3 = fe.Image.new(size=(3.0, 3.0), facecolor="#A54BB7", unit="inch", dpi=DPI, label="Test Image")
img3 = img3.rotate(angle=-45, expand=True, bg_color="#FFFFFF")
img4 = fe.Image.new(size=(3.0, 3.0), facecolor="#D7455B", unit="inch", dpi=DPI, label="Test Image")
img4 = img4.rotate(angle=30, expand=False, bg_color="#FFFFFF")

# 叠加
img_ = img1.overlay(other=img2, x=0.1, y=0.1, unit="ratio", anchor="center", scale=0.3)
img_ = img_.overlay(other=img3, x=0.7, y=0.1, unit="ratio", anchor="top_left", scale=0.3)
img_ = img_.overlay(other=img4, x=0.5, y=0.1, unit="ratio", anchor="top_right", scale=0.3)
img_ = img_.add_marker(x=0.1, y=0.1, unit="ratio", style="circle", size=0.01, color="red")
img_ = img_.add_marker(x=0.7, y=0.1, unit="ratio", style="circle", size=0.01, color="red")
img_ = img_.add_marker(x=0.5, y=0.1, unit="ratio", style="circle", size=0.01, color="red")
img_.show(width=500)

# %% [markdown]
# ##### **16. 图片标注**
# **函数签名:**
# 
# `Image.labeled(label, loc, y, anchor, unit, scale, expand, bg_color)`
# 
# **参数:**
# 
# - `label`: (可选) 强制指定标签内容, 默认使用初始化时的 label
# - `loc`: 位置(默认, "top_left")
# - `offset`: 距离边缘的内边距, 建议使用 tuple (x_off, y_off) 做微调, 默认 (0.02, 0.02) 表示宽高各 2% 的间距
# - `format_str`: 格式化字符串(默认: "({})")
#   - "({})" -> "(a)"
#   - "{}" -> "a"
#   - "{}." -> "a."
#   - "Fig. {}" -> "Fig. a"
# - `case`: 大小写转换(默认: 强制小写)
#   - "upper": 强制大写 (a -> A)
#   - "lower": 强制小写 (A -> a)
# - `fontsize`: 字体大小, 与matplotlib一致
# - `fontweight`: 字重(默认: "bold")
# - `color`: 颜色(默认: "black")
# - `font`: 字体
# - `box_style`: 背景框样式 (默认: 透明), 与add_text一致

# %%
img1_ = img1.labeled(format_str="({})", fontsize=14, case="upper", font="Noto Sans")
img1_.show(width=500)


