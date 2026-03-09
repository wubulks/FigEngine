# FigEngine
[![PyPI version](https://img.shields.io/pypi/v/FigEngine)](https://pypi.org/project/FigEngine/)
[![Python versions](https://img.shields.io/pypi/pyversions/FigEngine)](https://pypi.org/project/FigEngine/)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Documentation](https://img.shields.io/badge/docs-user%20manual-blue)](https://github.com/wubulks/FigEngine/blob/main/doc/FigEngine用户手册.pdf)

**FigEngine** 是面向科研绘图与论文排版的 Python 项目。它现在包含三个互相配合的部分：

- `figengine`：核心 Python API，负责图片对象、排版对象和底层渲染。
- `feimg`：官方单图处理 CLI，负责裁剪、缩放、标注、叠加、绘制图元等。
- `felayout`：官方多图排版 CLI，负责通过 JSON/YAML 布局文件生成最终 Figure。

这三部分共享同一套底层能力、同一套参数语义和同一个项目发布入口。

## 核心特性

- 物理单位感知：支持 `pixel`、`inch`、`cm`、`mm`、`ratio`。
- 高质量单图处理：支持 `crop`、`resize`、`rotate`、`overlay`、`add_text`、`add_border` 等常用操作。
- 自动多行排版：支持 `Figure.add_row(...)` 驱动的流式布局。
- 命令行工作流：支持先用 `feimg` 处理单图，再用 `felayout` 拼接最终组合图。
- 面向科研输出：适合论文图、补充材料图、海报图和可复现实验流程。

## 安装

通过 PyPI 安装：

```bash
pip install figengine
```

从 GitHub 安装开发版：

```bash
pip install git+https://github.com/wubulks/FigEngine.git
```

安装完成后，以下入口都会可用：

```bash
feimg --help
felayout --help
```

## 项目结构

### 1. Python API

适合在脚本、Notebook 或更复杂的批处理逻辑中直接调用：

```python
import figengine as fe

img = fe.Image.new(size=(4, 3), unit="inch", facecolor="#E0E0E0")
img = img.labeled("a", fontsize=24)
img = img.add_text("Demo", position="center", fontsize=20)
img.save("panel_a.png")
```

### 2. `feimg` 单图 CLI

适合把单张图的处理流程固定成命令行步骤：

```bash
feimg new -o blank.png --size 6 4 --unit inch --dpi 600
feimg text -i blank.png -o labeled.png --text "(a)" --loc top_left --unit ratio --fontsize 24
feimg border -i labeled.png -o final.png --thickness 0.02 --unit inch --color "#000000"
```

### 3. `felayout` 布局 CLI

适合把多行布局写入配置文件后统一构建：

```bash
felayout init -o layout.yaml
felayout validate --layout layout.yaml
felayout build --layout layout.yaml
```

## 快速开始

### 1. 使用 Python API 创建单图

```python
import figengine as fe

img = fe.Image.new(size=(4, 3), unit="inch", facecolor="#F2F2F2")
img = img.labeled("a", fontsize=24)
img = img.add_text(r"$\sum_{i=0}^{\infty} x_i$", position="center", fontsize=30)
img.save("panel_a.png")
```

### 2. 使用 Python API 拼接 Figure

```python
import figengine as fe

fig = fe.Figure(width=12, unit="inch", background="white")

img_a = fe.Image("panel_a.png")
img_b = fe.Image.new((4, 3), unit="inch", facecolor="#87CEEB").labeled("b")
img_c = fe.Image.new((8, 2), unit="inch", facecolor="#98FB98").labeled("c")

fig.add_row([img_a, img_b], left_gaps=0.0, right_gaps=0.1, unit="inch")
fig.add_row([img_c], top_margin=0.2, unit="inch", v_align="center")
fig.save("output_figure.png")
```

### 3. 使用 `feimg` + `felayout` 完成端到端流程

先处理单图：

```bash
feimg text -i assets/panel_a.png -o output/panel_a_labeled.png --text "(a)" --loc top_left --unit ratio
feimg text -i assets/panel_b.png -o output/panel_b_labeled.png --text "(b)" --loc top_left --unit ratio
```

再用布局文件拼版：

```yaml
figure:
    width: 8
    unit: inch
    dpi: 600

rows:
    - row_index: 0
      items:
          - output/panel_a_labeled.png
          - output/panel_b_labeled.png
      left_gaps: 0.02
      right_gaps: 0.02
      unit: ratio

output:
    path: output/final_figure.png
```

```bash
felayout build --layout layout.yaml
```

## 参数一致性

`feimg` 和 `felayout` 的设计目标是尽量贴近 `FigEngine` 核心 API：

- `feimg new --size W H` 对应 `Image.new(size=(W, H), ...)`
- `feimg resize --ref-image ref.png` 对应 `Image.resize(ref_image=...)`
- `feimg pad --target-size W H` 对应 `Image.pad_to_size(target_size=(W, H), ...)`
- `feimg overlay --other overlay.png` 对应 `Image.overlay(other=...)`
- `felayout` 中的 `rows[].left_gaps`、`rows[].right_gaps`、`top_margin`、`bottom_margin` 对应 `Figure.add_row(...)`

## 文档

- 项目用户手册：[`doc/FigEngine用户手册.md`](doc/FigEngine用户手册.md)
- 单图处理工具：`figengine.feimg`
- 布局工具：`figengine.felayout`

## 贡献

欢迎提交 Issue 和 Pull Request。

1. Fork 本仓库。
2. 创建分支：`git checkout -b feature/your-feature`
3. 提交修改：`git commit -m "Add your feature"`
4. 推送分支：`git push origin feature/your-feature`
5. 发起 Pull Request。

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE)。
