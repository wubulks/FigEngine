# FigEngine 🎨
[![PyPI version](https://img.shields.io/pypi/v/FigEngine)](https://pypi.org/project/FigEngine/)
[![Python versions](https://img.shields.io/pypi/pyversions/FigEngine)](https://pypi.org/project/FigEngine/)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Documentation](https://img.shields.io/badge/docs-user%20manual-blue)](https://github.com/wubulks/FigEngine/blob/main/doc/FigEngine用户手册.pdf)

**A High-Performance Structured Figure Engine for Python.**
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
### 从 GitHub 安装最新开发版
```bash
pip install git+https://github.com/wubulks/FigEngine.git
```

### 通过 PyPI 安装 (推荐)
```
pip install figengine
```

### 通过 Conda 安装
```
conda install omarjan::figengine
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
fig.add_row([img_c], top_margin=0.2, unit="inch", v_align="center")
# 5. 渲染并显示
fig.image.show(width=500)
# 6. 保存为高清图片
fig.image.save("output_figure.png")
fig.image.save("output_figure.pdf")
```

---

**功能详解请参阅用户手册**
User Manual (PDF): FigEngine用户手册(https://github.com/wubulks/FigEngine/blob/main/doc/FigEngine用户手册.pdf)

---
## 🤝 贡献指南
欢迎提交 Issue 和 Pull Request！
1.  Fork 本仓库。
2.  创建你的特性分支 (`git checkout -b feature/AmazingFeature`)。
3.  提交你的修改 (`git commit -m 'Add some AmazingFeature'`)。
4.  推送到分支 (`git push origin feature/AmazingFeature`)。
5.  打开一个 Pull Request。
6.  
## 📄 许可证
本项目采用 **MIT 许可证** - 详情请参阅 [LICENSE](LICENSE) 文件。
