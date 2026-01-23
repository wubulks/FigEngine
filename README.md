# FigEngine 🎨
**A High-Performance Structured Figure Engine for Python.**
[![License](https://img.shields.io/github/license/wubulks/FigEngine.svg)](https://github.com/wubulks/FigEngine)
**FigEngine** 是一个专为科研工作者设计的 Python 绘图排版引擎。它封装了 PIL 和 Matplotlib，让你能够以**物理单位**（英寸、厘米）精确控制图片的排版、缩放和标注，轻松生成用于论文发表的高质量组合图（Figure）。
不再为 matplotlib 的 subplot 坐标烦恼，也不用在 PPT 里手动对齐图片——FigEngine 帮你搞定。
## ✨ 核心特性
- **📏 物理单位感知**：原生支持 `inch`, `cm`, `mm`，所见即所得。
- **🏷️ 智能标注**：一键生成 `(a)`, `(b)`, `Fig. 1` 等符合期刊格式的子图编号。
- **🧩 自动排版引擎**：基于行（Row）的流式布局，自动计算间距和对齐。
- **✒️ 丰富的绘图能力**：支持 LaTeX 公式、箭头、几何标记、比例尺刻度。
- **🔍 字体管理**：内置系统字体探查工具，轻松查找并使用中文字体。
---
## 🛠️ 安装
### 从 GitHub 安装最新开发版 (暂时推荐)
```bash
pip install git+ssh://git@github.com/wubulks/FigEngine.git
```
---
## 🚀 快速开始
### 1. Hello World：创建并标注一张图片
```python
import figengine as fe
# 创建一个 4x3 英寸的空白画布
img = fe.Image.new(size=(4, 3), unit="inch", facecolor="#E0E0E0")
# 自动添加子图编号 "(a)"，默认位于左上角
img = img.labeled("a", fontsize=24)
# 添加一段文字 (支持 LaTeX)
img = img.add_text(r"$\sum_{i=0}^\infty x_i$", position="center", fontsize=40)
# 在 Jupyter 中预览 (自动缩放以适应屏幕)
img.show()
```
### 2. 组合排版 (Figure Layout)
这是 FigEngine 最强大的功能。我们可以轻松地将多张图片拼接成一个 Figure。
```python
import figengine as fe
# 1. 初始化排版器 (设定画布宽度为 12 英寸)
fig = fe.Figure(width=12, unit="inch", background="white")
# 2. 准备素材 (这里使用生成的图片演示，也可以使用 fe.Image("path/to/file.png"))
img_a = fe.Image.new((4, 3), unit="inch", facecolor="#FFB8CD").labeled("a")
img_b = fe.Image.new((4, 3), unit="inch", facecolor="#87CEEB").labeled("b")
img_c = fe.Image.new((8, 2), unit="inch", facecolor="#98FB98").labeled("c")
# 3. 添加第一行：两张图片并排，中间留 0.1 英寸间隙
fig.add_row([img_a, img_b], left_gaps=0.0, right_gaps=0.1, unit="inch")
# 4. 添加第二行：一张长图，顶部与上一行留 0.2 英寸间隙
fig.add_row([img_c], top_margin=0.2, unit="inch", align="center")
# 5. 渲染并显示
fig.show()
# 6. 保存为高清图片
# fig.save("output_figure.png", dpi=300)
# fig.save("output_figure.pdf")
```
---
## 📖 功能详解
### 图像操作 (Image Object)
`FigEngine.Image` 对象是不可变的（Immutable），所有操作都会返回一个新的对象，支持链式调用。
* **裁剪与缩放**：
    ```python
    # 裁剪掉四周各 10%
    img = img.crop(left=0.1, top=0.1, right=0.1, bottom=0.1, unit="ratio")
    # 强制缩放到 5cm 宽
    img = img.resize(width=5, unit="cm")
    ```
* **添加元素**：
    ```python
    # 添加刻度线 (用于调试坐标)
    img = img.add_ticks()
    # 添加箭头
    img = img.add_line(start=(0.1, 0.1), end=(0.9, 0.9), arrow="end", color="red")
    # 添加标记点
    img = img.add_marker(x=0.5, y=0.5, style="star", size=20, color="gold")
    ```
### 字体工具 (Tools)
不知道系统里有哪些字体？FigEngine 提供了美观的字体探查工具：
```python
from figengine import Tools
# 列出所有可用字体，并高亮推荐的中文字体
Tools.inspect_fonts()
# 搜索特定字体
Tools.inspect_fonts(filter_text="Arial")
```
---
## 🤝 贡献指南
欢迎提交 Issue 和 Pull Request！
1.  Fork 本仓库。
2.  创建你的特性分支 (`git checkout -b feature/AmazingFeature`)。
3.  提交你的修改 (`git commit -m 'Add some AmazingFeature'`)。
4.  推送到分支 (`git push origin feature/AmazingFeature`)。
5.  打开一个 Pull Request。
## 📄 许可证
本项目采用 **MIT 许可证** - 详情请参阅 [LICENSE](LICENSE) 文件。
---
*Author: Mute*
