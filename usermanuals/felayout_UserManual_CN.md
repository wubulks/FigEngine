# **1. 引言**
`felayout` 是一个基于 `FigEngine` 的命令行排版工具，用来把多张图片按照预先定义好的布局规则拼接成最终的科研 Figure。

它解决的问题很直接：

1. 你有多张已经处理好的图片，需要稳定、可重复地排版。
2. 你不想每次都手动拖拽、对齐、调整边距。
3. 你希望布局本身也能进入版本管理，像代码一样可追踪、可比较。

`felayout` 的核心思路不是“在命令行里把所有参数一股脑写完”，而是：

1. 先写一个布局文件。
2. 再让 `felayout` 根据这个文件构建最终图像。

这样做的好处是：

1. 布局结构清楚，适合长期维护。
2. 同一个布局可以多次重复生成。
3. 非常适合论文、报告、项目图册这类需要反复微调的场景。
4. 非常适合与 `feimg` 或其他单图预处理工具配合使用。

---

# **2. 系统环境要求**
`felayout` 是一个命令行多图排版工具，没有图形化界面（GUI）。  
它不会提供拖拽图片、鼠标对齐或可视化面板编辑功能，而是通过命令行读取布局文件并生成最终 Figure。

因此，在使用之前，建议先确认你的运行环境满足以下要求。

## **2.1. 操作系统要求**
`felayout` 可以运行在常见的桌面和服务器操作系统中，包括：

- Windows 10 或更高版本
- macOS 10.14 或更高版本
- Linux（推荐 Ubuntu 18.04 或更高版本）

只要系统能正常运行 Python 和命令行环境，通常就可以使用 `felayout`。

## **2.2. Python 与依赖要求**
建议使用：

- Python 3.9 或更高版本

`felayout` 底层依赖 `FigEngine` 的排版能力，并依赖若干 Python 库完成配置文件读取、CLI 解析和结果输出。常见依赖包括：

- `FigEngine`
- `Pillow`
- `matplotlib`
- `numpy`
- `PyYAML`
- `pdf2image`
- `typer`
- `rich`

正常通过 `pip` 安装时，这些依赖一般会自动安装；但如果你是源码开发或手工部署，建议明确检查。

## **2.3. 命令行环境要求**
由于 `felayout` 没有 GUI，实际使用完全依赖命令行环境。建议确认以下几点：

1. 系统中有可用终端  
例如：
- Windows PowerShell
- Windows Terminal
- macOS Terminal
- Linux Shell

2. 可以正常调用 Python  
例如：

```bash
python --version
```

3. 安装后可以正常识别 `felayout` 命令  
例如：

```bash
felayout --help
```

如果这些命令能正常运行，说明基本环境已经具备。

## **2.4. 不提供 GUI 的含义**
这里需要特别强调：

- `felayout` 不是拖拽式排版软件
- 它不会打开可视化排版窗口
- 它不会像 PowerPoint、Keynote 或 Illustrator 那样让你直接鼠标拖动图片

它的设计目标是：

1. 让排版规则写进配置文件
2. 让最终图版可以重复构建
3. 让布局调整过程更适合版本管理

因此，`felayout` 更适合：

- 论文 Figure 排版
- 需要长期维护的图版工程
- 希望布局配置可追踪、可复现的项目

## **2.5. 推荐使用方式**
实际使用时，建议采用下面的方式：

1. 在终端中执行 `felayout init / validate / build`
2. 用文本编辑器维护 `layout.json` 或 `layout.yaml`
3. 每次调整布局后重新运行构建命令

最典型的工作流是：

```bash
felayout init -o layout.yaml
felayout validate --layout layout.yaml
felayout build --layout layout.yaml
```

如果你已经习惯命令行、配置文件和脚本化工作流，那么 `felayout` 会比手动拖拽图片稳定得多。

总之，需要明确的一点是：  
`felayout` 是命令行软件，不是图形化桌面排版软件。

---

# **3. 安装与验证**
## **3.1. 安装**
通过 `pip` 安装：

```bash
pip install felayout
```

如果你在源码目录中开发：

```bash
cd felayout
pip install -e .
```

---

## **3.2. 验证安装**
安装后建议先检查命令是否可用：

```bash
felayout --help
felayout init --help
felayout validate --help
felayout build --help
```

如果这些命令都能正常显示帮助信息，说明 CLI 已经安装成功。

---

# **4. 基本使用流程**
## **4.1. 第一步：生成模板**
可以先生成 JSON 模板：

```bash
felayout init -o layout.json
```

也可以直接生成 YAML 模板：

```bash
felayout init -o layout.yaml
```

如果目标文件已存在，并且你确定要覆盖它：

```bash
felayout init -o layout.yaml --overwrite
```

---

## **4.2. 第二步：编辑布局文件**
布局文件中最重要的三个部分是：

1. `figure`
作用：定义整体画布，例如宽度、背景色、页边距。

2. `rows`
作用：定义每一行放哪些图、各行之间和行内元素之间如何留白。

3. `output`
作用：定义输出路径，以及保存时附加给 `Figure.save()` 的参数。

---

## **4.3. 第三步：校验布局文件**
正式构建前，建议先执行校验：

```bash
felayout validate --layout layout.json
```

或：

```bash
felayout validate --layout layout.yaml
```

这个命令会检查布局文件的基本结构，并输出摘要，例如行数、图片数、输出路径等。

---

## **4.4. 第四步：生成最终排版**
构建 JSON 布局：

```bash
felayout build --layout layout.json
```

构建 YAML 布局：

```bash
felayout build --layout layout.yaml
```

如果你想临时覆盖输出路径：

```bash
felayout build --layout layout.yaml -o output/final_figure.png
```

如果目标文件已存在并允许覆盖：

```bash
felayout build --layout layout.yaml -o output/final_figure.png --overwrite
```

---

# **5. 为什么支持 JSON 和 YAML**
`felayout` 同时支持 `JSON` 和 `YAML`。

你可以按自己的习惯选择：

## **5.1. JSON 适合什么场景**
`JSON` 更适合：

1. 你已经习惯写 JSON。
2. 你希望结构严格、格式统一。
3. 你可能会用脚本自动生成布局文件。
4. 你希望与其他程序的数据交换更直接。

## **5.2. YAML 适合什么场景**
`YAML` 更适合：

1. 你主要手工编辑配置。
2. 你希望文件更接近自然层级阅读。
3. 你希望列表、多行结构看起来更清楚。
4. 你希望将来在文件里加入较多注释。

## **5.3. 这两种格式在功能上是否等价**
是的。  
对 `felayout` 来说，`layout.json` 和 `layout.yaml` 描述的是同一套布局结构，支持的字段完全一致。

区别只在书写方式，不在功能。

---

# **5.4. 与 FigEngine API 的关系**
`felayout` 不是重新发明一套排版概念，而是把 `FigEngine.Figure` 的核心排版参数组织进一个配置文件。

可以把它理解为：

1. `FigEngine` 负责底层排版能力
2. `felayout` 负责把这些能力写成可保存、可复用、可验证的布局文件

最重要的对应关系如下：

1. `figure.background`
对应 `Figure(background=...)`

2. `figure.dpi`
对应 `Figure(dpi=...)`

3. `figure.width`
对应 `Figure(width=...)`

4. `figure.height`
对应 `Figure(height=...)`

5. `figure.unit`
对应 `Figure(unit=...)`

6. `figure.margins`
对应 `Figure.set_margins(margins=...)`

7. `figure.margins_unit`
对应 `Figure.set_margins(unit=...)`

8. `rows[].items`
对应 `Figure.add_row(items=...)`

9. `rows[].left_gaps`
对应 `Figure.add_row(left_gaps=...)`

10. `rows[].right_gaps`
对应 `Figure.add_row(right_gaps=...)`

11. `rows[].top_margin`
对应 `Figure.add_row(top_margin=...)`

12. `rows[].bottom_margin`
对应 `Figure.add_row(bottom_margin=...)`

13. `rows[].unit`
对应 `Figure.add_row(unit=...)`

14. `rows[].v_align`
对应 `Figure.add_row(v_align=...)`

15. `rows[].h_align`
对应 `Figure.add_row(h_align=...)`

另外还有少量字段是 `felayout` 自己加的配置层字段：

1. `name`
用于提高配置文件可读性，不属于 `Figure.add_row(...)` 的原生参数

2. `row_index`
用于显式指定行顺序，不属于 `Figure.add_row(...)` 的原生参数

3. `output`
属于 CLI 输出层，不属于 `Figure` 构造参数

---

# **6. 布局文件格式总览**
一个完整的布局文件由三部分组成：

1. `figure`
整体画布设置。

2. `rows`
按行定义要拼接的图片。

3. `output`
输出设置。

最小结构如下。

## **6.1. JSON 最小结构**
```json
{
    "figure": {},
    "rows": [],
    "output": {}
}
```

## **6.2. YAML 最小结构**
```yaml
figure: {}
rows: []
output: {}
```

---

# **7. 完整示例**
这一节先给出完整示例，后面再逐项拆开解释。

## **7.1. JSON 完整示例**
```json
{
    "figure": {
        "background": "#FFFFFF",
        "dpi": 600,
        "width": 12,
        "height": 0,
        "unit": "inch",
        "margins": {
            "top": 0.02,
            "bottom": 0.02,
            "left": 0.02,
            "right": 0.02
        },
        "margins_unit": "ratio"
    },
    "rows": [
        {
            "name": "row_0",
            "row_index": 0,
            "items": [
                "assets/panel_a.png",
                "assets/panel_b.png",
                "assets/panel_c.png"
            ],
            "left_gaps": 0.01,
            "right_gaps": 0.01,
            "top_margin": 0.01,
            "bottom_margin": 0.01,
            "unit": "ratio",
            "v_align": "center",
            "h_align": "full"
        },
        {
            "name": "row_1",
            "row_index": 1,
            "items": [
                "assets/panel_d.png",
                "assets/panel_e.png",
                "assets/panel_f.png"
            ],
            "left_gaps": [
                0.00,
                0.01,
                0.02
            ],
            "right_gaps": [
                0.02,
                0.01,
                0.00
            ],
            "top_margin": 0.01,
            "bottom_margin": 0.01,
            "unit": "ratio",
            "v_align": "top",
            "h_align": "center"
        }
    ],
    "output": {
        "path": "output/layout.png",
        "save_kwargs": {}
    }
}
```

## **7.2. YAML 完整示例**
```yaml
figure:
    background: "#FFFFFF"
    dpi: 600
    width: 12
    height: 0
    unit: inch
    margins:
        top: 0.02
        bottom: 0.02
        left: 0.02
        right: 0.02
    margins_unit: ratio

rows:
    - name: row_0
      row_index: 0
      items:
          - assets/panel_a.png
          - assets/panel_b.png
          - assets/panel_c.png
      left_gaps: 0.01
      right_gaps: 0.01
      top_margin: 0.01
      bottom_margin: 0.01
      unit: ratio
      v_align: center
      h_align: full

    - name: row_1
      row_index: 1
      items:
          - assets/panel_d.png
          - assets/panel_e.png
          - assets/panel_f.png
      left_gaps:
          - 0.00
          - 0.01
          - 0.02
      right_gaps:
          - 0.02
          - 0.01
          - 0.00
      top_margin: 0.01
      bottom_margin: 0.01
      unit: ratio
      v_align: top
      h_align: center

output:
    path: output/layout.png
    save_kwargs: {}
```

---

# **8. 如何阅读 JSON 和 YAML**
如果你之前完全没有接触过这类文件，可以先记住下面几点。

## **8.1. JSON 的阅读方式**
JSON 的特点是：

1. 对象用 `{}` 表示。
2. 数组用 `[]` 表示。
3. 键必须用双引号包起来。
4. 字符串值也通常写成双引号。
5. 每一项之间用逗号分隔。

例如：

```json
{
    "width": 12,
    "unit": "inch"
}
```

表示一个对象，它有两个字段：

1. `width`
值是数字 `12`

2. `unit`
值是字符串 `"inch"`

---

## **8.2. YAML 的阅读方式**
YAML 的特点是：

1. 通常不用 `{}` 和 `[]`。
2. 主要靠缩进表示层级。
3. 列表项用 `-` 开头。
4. 书写时更接近“层级化笔记”。

例如：

```yaml
width: 12
unit: inch
```

和上面的 JSON 表达的是同一件事。

再比如列表：

```yaml
items:
    - a.png
    - b.png
    - c.png
```

表示 `items` 是一个列表，里面有三项。

---

# **9. `figure` 部分详解**
`figure` 用来定义整体画布。

你可以把它理解为“最终大图”的全局设置。

## **9.1. `background`**
作用：设置画布背景颜色。

常见值：

1. 颜色名，例如 `white`
2. 十六进制颜色，例如 `#FFFFFF`

### JSON 写法
```json
{
    "figure": {
        "background": "#FFFFFF"
    }
}
```

### YAML 写法
```yaml
figure:
    background: "#FFFFFF"
```

---

## **9.2. `dpi`**
作用：设置输出分辨率。

这是一个整数。通常科研图像常见值有：

1. `300`
2. `600`

### JSON 写法
```json
{
    "figure": {
        "dpi": 600
    }
}
```

### YAML 写法
```yaml
figure:
    dpi: 600
```

---

## **9.3. `width`**
作用：设置画布宽度。

注意：这个值本身只表示“数值”，真正的单位由 `unit` 决定。

例如：

1. `width: 12` 且 `unit: inch`
表示宽度为 12 英寸。

2. `width: 18` 且 `unit: cm`
表示宽度为 18 厘米。

### JSON 写法
```json
{
    "figure": {
        "width": 12,
        "unit": "inch"
    }
}
```

### YAML 写法
```yaml
figure:
    width: 12
    unit: inch
```

---

## **9.4. `height`**
作用：设置画布高度。

这个字段有两种常见用法：

1. `height: 0`
表示不强制指定高度，由内容自动推断。

2. `height: 正数`
表示强制指定画布高度。

### JSON 写法
```json
{
    "figure": {
        "height": 0
    }
}
```

### YAML 写法
```yaml
figure:
    height: 0
```

---

## **9.5. `unit`**
作用：指定 `width` 和 `height` 的单位。

支持的值：

1. `pixel`
2. `inch`
3. `cm`
4. `mm`

### JSON 写法
```json
{
    "figure": {
        "unit": "inch"
    }
}
```

### YAML 写法
```yaml
figure:
    unit: inch
```

---

## **9.6. `margins`**
作用：设置整张图的页边距。

它本身是一个对象，包含四个方向：

1. `top`
2. `bottom`
3. `left`
4. `right`

### JSON 写法
```json
{
    "figure": {
        "margins": {
            "top": 0.02,
            "bottom": 0.02,
            "left": 0.02,
            "right": 0.02
        }
    }
}
```

### YAML 写法
```yaml
figure:
    margins:
        top: 0.02
        bottom: 0.02
        left: 0.02
        right: 0.02
```

---

## **9.7. `margins_unit`**
作用：指定 `margins` 的单位。

支持：

1. `pixel`
2. `ratio`
3. `inch`
4. `cm`
5. `mm`

当使用 `ratio` 时，通常表示相对于画布宽度的比例。

### JSON 写法
```json
{
    "figure": {
        "margins_unit": "ratio"
    }
}
```

### YAML 写法
```yaml
figure:
    margins_unit: ratio
```

---

# **10. `rows` 部分详解**
`rows` 是整个布局文件中最核心的部分。

它表示“最终大图由哪几行组成”。

每一行都是一个对象，表示一次 `Figure.add_row(...)` 调用。

## **10.1. JSON 中的 `rows` 是怎么写的**
JSON 里，`rows` 是数组：

```json
{
    "rows": [
        {
            "name": "row_0",
            "items": ["a.png", "b.png"]
        },
        {
            "name": "row_1",
            "items": ["c.png", "d.png"]
        }
    ]
}
```

## **10.2. YAML 中的 `rows` 是怎么写的**
YAML 里，`rows` 也是列表，只是用 `-` 表示每一项：

```yaml
rows:
    - name: row_0
      items:
          - a.png
          - b.png

    - name: row_1
      items:
          - c.png
          - d.png
```

---

## **10.3. `name`**
作用：为这一行起一个容易识别的名称。

这个字段主要用于增强可读性。  
例如你有很多行时，用 `row_0`、`row_1`、`row_2` 会比“只看数组顺序”更直观。

### JSON 写法
```json
{
    "name": "row_0"
}
```

### YAML 写法
```yaml
name: row_0
```

---

## **10.4. `row_index`**
作用：指定这一行的显式顺序。

如果提供了 `row_index`，`felayout` 会优先按 `row_index` 排序，而不是按文件中出现的先后顺序。

建议：

1. 从 `0` 开始编号。
2. 保持连续，例如 `0, 1, 2, 3`。

### JSON 写法
```json
{
    "row_index": 0
}
```

### YAML 写法
```yaml
row_index: 0
```

### 实际作用说明
如果你在文件中把行顺序写乱了，但 `row_index` 是正确的，`felayout` 仍然会优先按 `row_index` 排序构建。

例如：

1. 文件里先写 `row_index: 2`
2. 后写 `row_index: 0`
3. 再写 `row_index: 1`

最终构建顺序仍然是：

`0 -> 1 -> 2`

---

## **10.5. `items`**
作用：定义这一行有哪些图片。

它必须是一个列表。

每个元素目前最常见的写法是字符串路径。

也就是说，通常你会这样写：

1. 一张图片一个路径
2. 路径顺序就是这一行中 panel 的顺序

### JSON 写法
```json
{
    "items": [
        "assets/panel_a.png",
        "assets/panel_b.png",
        "assets/panel_c.png"
    ]
}
```

### YAML 写法
```yaml
items:
    - assets/panel_a.png
    - assets/panel_b.png
    - assets/panel_c.png
```

---

## **10.6. `left_gaps`**
作用：定义这一行中，每个图片左侧的留白。

这是一个非常重要的字段，而且它有两种输入风格。

### 风格 A：写成单个数值
含义：这一行中的所有图片，都使用同一个左侧间距。

这是最简单、最常见的写法。

#### JSON 写法
```json
{
    "left_gaps": 0.01
}
```

#### YAML 写法
```yaml
left_gaps: 0.01
```

适合场景：

1. 这一行所有 panel 的左边留白一致。
2. 你不需要对某一个 panel 单独微调。

### 风格 B：写成数组
含义：为这一行中的每个图片分别指定左侧间距。

#### JSON 写法
```json
{
    "left_gaps": [
        0.00,
        0.01,
        0.02
    ]
}
```

#### YAML 写法
```yaml
left_gaps:
    - 0.00
    - 0.01
    - 0.02
```

适合场景：

1. 你需要让每张图的留白不同。
2. 你在做精细对齐。
3. 某些 panel 需要额外向右推一点。

### 初学者建议
如果你刚开始写布局文件，建议先从单值写法开始。

只有当你发现：

1. 某一张图总是显得太靠左
2. 某两张图之间的视觉间距需要单独调整
3. 某一行存在非对称结构

再改成数组写法。

### 如何理解数组顺序
如果这一行 `items` 是：

```yaml
items:
    - a.png
    - b.png
    - c.png
```

而 `left_gaps` 是：

```yaml
left_gaps:
    - 0.00
    - 0.01
    - 0.02
```

那么含义就是：

1. `a.png` 左侧间距为 `0.00`
2. `b.png` 左侧间距为 `0.01`
3. `c.png` 左侧间距为 `0.02`

---

## **10.7. `right_gaps`**
作用：定义这一行中，每个图片右侧的留白。

它和 `left_gaps` 完全类似，也有两种输入风格。

### 风格 A：写成单个数值

#### JSON 写法
```json
{
    "right_gaps": 0.01
}
```

#### YAML 写法
```yaml
right_gaps: 0.01
```

### 风格 B：写成数组

#### JSON 写法
```json
{
    "right_gaps": [
        0.02,
        0.01,
        0.00
    ]
}
```

#### YAML 写法
```yaml
right_gaps:
    - 0.02
    - 0.01
    - 0.00
```

### 如何理解数组顺序
如果这一行中有三张图，那么 `right_gaps` 数组的第 1、2、3 项就分别对应第 1、2、3 张图的右侧间距。

### 与 `left_gaps` 的关系
通常情况下：

1. 如果整行结构比较规则
可以让 `left_gaps` 和 `right_gaps` 都写成单值

2. 如果你在做微调
可以只把其中一个写成数组

3. 如果你需要非常细致地控制每张图前后的留白
可以两个都写成数组

---

## **10.8. `top_margin`**
作用：定义这一行与上一行之间的上方间距。

这是单个数值，不是数组。

### JSON 写法
```json
{
    "top_margin": 0.01
}
```

### YAML 写法
```yaml
top_margin: 0.01
```

---

## **10.9. `bottom_margin`**
作用：定义这一行与下一行之间的下方间距。

这也是单个数值。

### JSON 写法
```json
{
    "bottom_margin": 0.01
}
```

### YAML 写法
```yaml
bottom_margin: 0.01
```

---

## **10.10. `unit`**
作用：指定这一行中与间距相关字段的单位。

常见可选值：

1. `pixel`
2. `ratio`
3. `inch`
4. `cm`
5. `mm`

### JSON 写法
```json
{
    "unit": "ratio"
}
```

### YAML 写法
```yaml
unit: ratio
```

### 初学者建议
对 `rows` 里的间距字段，初学者通常优先用 `ratio` 更容易上手。

因为：

1. 图片尺寸变化时更稳定
2. 不需要一开始就换算像素
3. 更适合描述相对布局

---

## **10.11. `v_align`**
作用：控制行内图片的垂直对齐方式。

支持：

1. `full`
2. `top`
3. `center`
4. `bottom`

### JSON 写法
```json
{
    "v_align": "center"
}
```

### YAML 写法
```yaml
v_align: center
```

---

## **10.12. `h_align`**
作用：控制整行内容的水平对齐方式。

支持：

1. `left`
2. `center`
3. `right`
4. `justify`
5. `full`

### JSON 写法
```json
{
    "h_align": "full"
}
```

### YAML 写法
```yaml
h_align: full
```

### 一般如何选
可以先这样理解：

1. `full`
希望这一行尽量铺满可用宽度

2. `center`
希望这一行内容整体居中

3. `left`
希望这一行靠左

4. `right`
希望这一行靠右

5. `justify`
希望在保留首尾 gap 的基础上，把额外空间分配到图与图之间

---

# **11. `output` 部分详解**
`output` 用来定义最终文件如何保存。

## **11.1. `path`**
作用：指定输出文件路径。

### JSON 写法
```json
{
    "output": {
        "path": "output/layout.png"
    }
}
```

### YAML 写法
```yaml
output:
    path: output/layout.png
```

---

## **11.2. `save_kwargs`**
作用：将附加参数透传给 `Figure.save()`。

如果你暂时没有特殊需求，可以先写空对象。

### JSON 写法
```json
{
    "output": {
        "save_kwargs": {}
    }
}
```

### YAML 写法
```yaml
output:
    save_kwargs: {}
```

---

# **12. 单值与数组两种输入风格，什么时候该用哪种**
这是第一次使用 `felayout` 时最容易疑惑的部分。

## **12.1. 什么时候用单值**
当这一行中所有图片都采用相同间距时，用单值最简单：

### JSON
```json
{
    "left_gaps": 0.01,
    "right_gaps": 0.01
}
```

### YAML
```yaml
left_gaps: 0.01
right_gaps: 0.01
```

优点：

1. 文件短。
2. 容易看。
3. 适合大多数规则整齐的布局。

## **12.2. 什么时候用数组**
当你需要逐项微调时，用数组：

### JSON
```json
{
    "left_gaps": [
        0.00,
        0.01,
        0.02
    ],
    "right_gaps": [
        0.02,
        0.01,
        0.00
    ]
}
```

### YAML
```yaml
left_gaps:
    - 0.00
    - 0.01
    - 0.02

right_gaps:
    - 0.02
    - 0.01
    - 0.00
```

优点：

1. 每个 panel 都能单独调。
2. 适合非对称布局。
3. 适合精细对齐。

## **12.3. 初学者建议**
如果你刚开始使用：

1. 先从单值写法开始。
2. 当你发现某一张图总是“差一点点”时，再改成数组写法。
3. 不要一开始就把所有字段都写成数组，否则文件会变复杂。

---

# **13. 命令详解**
## **13.1. `felayout init`**
作用：生成一个示例布局模板。

命令：

```bash
felayout init [-o OUTPUT] [--overwrite]
```

参数：

1. `-o, --output`
输出模板路径。支持：
`layout.json`、`layout.yaml`、`layout.yml`

2. `--overwrite`
如果目标文件已存在，允许覆盖。

示例：

```bash
felayout init
felayout init -o examples/layout.json --overwrite
felayout init -o examples/layout.yaml --overwrite
```

---

## **13.2. `felayout validate`**
作用：检查布局文件的基本结构是否合理。

命令：

```bash
felayout validate --layout PATH
```

示例：

```bash
felayout validate --layout layout.json
felayout validate --layout layout.yaml
```

建议：

1. 每次编辑完布局文件后先跑一次 `validate`。
2. 确认结构没问题，再执行 `build`。

---

## **13.3. `felayout build`**
作用：根据布局文件构建最终图像。

命令：

```bash
felayout build --layout PATH [-o OUTPUT] [--overwrite]
```

参数：

1. `--layout`
布局文件路径。

2. `-o, --output`
临时覆盖 `output.path`。

3. `--overwrite`
允许覆盖已有输出文件。

示例：

```bash
felayout build --layout layout.json
felayout build --layout layout.yaml
felayout build --layout layout.yaml -o output/final_figure.png --overwrite
```

---

# **14. 与 `feimg` 的关系**
推荐工作流如下：

1. 使用 `feimg` 处理单张图片。
例如：裁剪、补边、旋转、标注、缩放。

2. 将处理后的图片写入布局文件。

3. 使用 `felayout build` 完成统一拼版。

这种分层的好处是：

1. `feimg` 负责“单图处理”。
2. `felayout` 负责“多图排版”。
3. 工具职责更清楚。

---

# **15. 常见布局实例**
这一节给出几种最常见的布局方式。它们不是唯一写法，但非常适合作为起点模板。

## **15.1. 两张图并排，统一间距**
适合最常见的左右并排双图布局。

### JSON
```json
{
    "rows": [
        {
            "name": "row_0",
            "row_index": 0,
            "items": [
                "assets/a.png",
                "assets/b.png"
            ],
            "left_gaps": 0.01,
            "right_gaps": 0.01,
            "top_margin": 0.01,
            "bottom_margin": 0.01,
            "unit": "ratio",
            "v_align": "center",
            "h_align": "full"
        }
    ]
}
```

### YAML
```yaml
rows:
    - name: row_0
      row_index: 0
      items:
          - assets/a.png
          - assets/b.png
      left_gaps: 0.01
      right_gaps: 0.01
      top_margin: 0.01
      bottom_margin: 0.01
      unit: ratio
      v_align: center
      h_align: full
```

---

## **15.2. 三张图一行，逐项微调间距**
适合某些 panel 宽度、留白需求不一致的布局。

### JSON
```json
{
    "rows": [
        {
            "name": "row_0",
            "row_index": 0,
            "items": [
                "assets/a.png",
                "assets/b.png",
                "assets/c.png"
            ],
            "left_gaps": [
                0.00,
                0.01,
                0.02
            ],
            "right_gaps": [
                0.02,
                0.01,
                0.00
            ],
            "top_margin": 0.01,
            "bottom_margin": 0.01,
            "unit": "ratio",
            "v_align": "top",
            "h_align": "center"
        }
    ]
}
```

### YAML
```yaml
rows:
    - name: row_0
      row_index: 0
      items:
          - assets/a.png
          - assets/b.png
          - assets/c.png
      left_gaps:
          - 0.00
          - 0.01
          - 0.02
      right_gaps:
          - 0.02
          - 0.01
          - 0.00
      top_margin: 0.01
      bottom_margin: 0.01
      unit: ratio
      v_align: top
      h_align: center
```

---

## **15.3. 上下两行混排**
适合第一行放多个 panel，第二行放一个宽图，或第二行放另一组 panel。

### JSON
```json
{
    "rows": [
        {
            "name": "row_0",
            "row_index": 0,
            "items": [
                "assets/a.png",
                "assets/b.png"
            ],
            "left_gaps": 0.01,
            "right_gaps": 0.01,
            "top_margin": 0.01,
            "bottom_margin": 0.02,
            "unit": "ratio",
            "v_align": "center",
            "h_align": "full"
        },
        {
            "name": "row_1",
            "row_index": 1,
            "items": [
                "assets/c_wide.png"
            ],
            "left_gaps": 0.00,
            "right_gaps": 0.00,
            "top_margin": 0.00,
            "bottom_margin": 0.01,
            "unit": "ratio",
            "v_align": "center",
            "h_align": "center"
        }
    ]
}
```

### YAML
```yaml
rows:
    - name: row_0
      row_index: 0
      items:
          - assets/a.png
          - assets/b.png
      left_gaps: 0.01
      right_gaps: 0.01
      top_margin: 0.01
      bottom_margin: 0.02
      unit: ratio
      v_align: center
      h_align: full

    - name: row_1
      row_index: 1
      items:
          - assets/c_wide.png
      left_gaps: 0.00
      right_gaps: 0.00
      top_margin: 0.00
      bottom_margin: 0.01
      unit: ratio
      v_align: center
      h_align: center
```

---

# **16. 错误示例与常见陷阱**
这一节专门讲那些“看起来很像对的，但实际上很容易出错”的布局写法。

## **16.1. `rows` 必须是列表，不是对象**
错误写法：

```json
{
    "rows": {
        "row_0": {
            "items": ["a.png", "b.png"]
        }
    }
}
```

原因：

`felayout` 当前要求 `rows` 必须是数组或 YAML 列表，因为它本质上表示“多行的有序集合”。

正确写法：

```json
{
    "rows": [
        {
            "name": "row_0",
            "row_index": 0,
            "items": ["a.png", "b.png"]
        }
    ]
}
```

---

## **16.2. 每一行里必须叫 `items`，不能随便改名**
错误写法：

```json
{
    "rows": [
        {
            "row_0": ["a.png", "b.png"]
        }
    ]
}
```

原因：

`items` 是 `felayout` 明确定义的字段名，对应底层的 `Figure.add_row(items=...)`。

正确写法：

```json
{
    "rows": [
        {
            "name": "row_0",
            "items": ["a.png", "b.png"]
        }
    ]
}
```

---

## **16.3. `row_index` 是整数，不是字符串**
错误写法：

```yaml
row_index: "1"
```

正确写法：

```yaml
row_index: 1
```

原因：

`row_index` 用于排序，它应该是一个非负整数。

---

## **16.4. `row_index` 不能重复**
错误写法：

```json
{
    "rows": [
        { "name": "row_0", "row_index": 0, "items": ["a.png"] },
        { "name": "row_1", "row_index": 0, "items": ["b.png"] }
    ]
}
```

这会导致排序语义冲突。

正确做法：

1. 每一行使用唯一的 `row_index`
2. 最好按 `0, 1, 2, 3` 连续编号

---

## **16.5. `left_gaps` / `right_gaps` 的数组顺序必须和 `items` 对齐**
错误理解：

有些用户会写了 3 张图，却把 gap 数组当成“图与图之间的两个间隙”。

例如：

```yaml
items:
    - a.png
    - b.png
    - c.png

left_gaps:
    - 0.01
    - 0.02
```

这类写法不是“只控制两个缝隙”的语义，而是会按内部规则补齐。

更稳妥的做法是：

1. 要么写单值
2. 要么明确写出与 `items` 对应的完整数组

推荐写法：

```yaml
left_gaps:
    - 0.00
    - 0.01
    - 0.02
```

---

## **16.6. 不要把 `left_gaps` 的数组写成字符串**
错误写法：

```json
{
    "left_gaps": "[0.01, 0.02]"
}
```

原因：

这会被解析成字符串，而不是数组。

正确写法：

```json
{
    "left_gaps": [0.01, 0.02]
}
```

---

## **16.7. `top_margin` / `bottom_margin` 是单值，不是数组**
错误写法：

```yaml
top_margin:
    - 0.01
    - 0.02
```

原因：

这两个字段描述的是整一行的上下外边距，不是逐 panel 的数组参数。

正确写法：

```yaml
top_margin: 0.01
bottom_margin: 0.02
```

---

## **16.8. `unit`、`figure.unit`、`margins_unit` 不是同一层含义**
这也是最容易混淆的地方之一。

1. `figure.unit`
控制 `figure.width` 和 `figure.height` 的单位

2. `figure.margins_unit`
控制 `figure.margins` 的单位

3. `rows[].unit`
控制该行 gap 和 margin 的单位

也就是说，下面三处的 `unit` 并不是一回事：

```yaml
figure:
    width: 12
    unit: inch
    margins:
        top: 0.02
    margins_unit: ratio

rows:
    - unit: ratio
```

---

## **16.9. `ratio` 不是百分数字面值**
如果你写：

```yaml
left_gaps: 50
unit: ratio
```

通常不是你想要的结果。

在 `ratio` 模式下，更常见的写法应该是：

```yaml
left_gaps: 0.05
unit: ratio
```

因为：

1. `0.05` 表示 5%
2. `0.5` 表示 50%
3. `1.0` 表示 100%

---

## **16.10. 图片相对路径是相对于布局文件，不是当前终端目录**
例如布局文件在：

```text
project/specs/layout.yaml
```

而你写：

```yaml
items:
    - assets/a.png
```

程序会按下面这个路径去理解：

```text
project/specs/assets/a.png
```

而不是当前 shell 所在目录下的 `assets/a.png`。

因此，移动布局文件位置时，常常也要同步调整相对路径。

---

## **16.11. `output.path` 和 `felayout build -o ...` 的优先级要分清**
如果你在布局文件里写了：

```yaml
output:
    path: output/a.png
```

但命令行又写：

```bash
felayout build --layout layout.yaml -o output/b.png
```

那么最终会优先使用命令行里的 `-o output/b.png`。

这不是冲突，而是正常的“命令行覆盖配置文件”行为。

---

## **16.12. YAML 中空行没问题，但缩进必须稳定**
YAML 允许空行，这有助于提高可读性。

但要注意：

1. 同一层级缩进必须一致
2. 列表项下的字段要对齐
3. 不要混用 tab 和空格

例如：

```yaml
rows:
    - name: row_0
      row_index: 0
      items:
          - a.png
          - b.png
```

这种是正常的。

---

## **16.13. 忘记 `--overwrite` 是最常见报错之一**
如果输出文件已经存在，而你没有传 `--overwrite`，构建会被阻止。

这是故意设计的保护行为，用来避免误覆盖结果文件。

---

# **17. 常见问题**
## **17.1. 图片相对路径是相对于谁解析**
相对于布局文件所在目录解析。

例如：

1. 布局文件在 `project/layout.yaml`
2. 其中写了 `assets/panel_a.png`

那么程序会把它理解为：

`project/assets/panel_a.png`

---

## **17.2. 我能不能只写 YAML，不写 JSON**
可以。  
两者是等价的，选你更顺手的格式即可。

---

## **17.3. 我能不能只写 JSON，不写 YAML**
也可以。  
如果你已经习惯 JSON，完全没必要强制切换。

---

## **17.4. `left_gaps` 和 `right_gaps` 到底写单值还是数组**
简单判断：

1. 所有图间距相同，用单值。
2. 每张图间距不同，用数组。

---

## **17.5. 行顺序是按什么决定的**
优先按 `row_index`。  
如果没有写 `row_index`，则按文件中出现的顺序处理。

---

## **17.6. 为什么不用很多 CLI 参数直接排版**
因为排版本身是一个多层结构问题：

1. 有画布设置。
2. 有多行。
3. 每行里又有多个 panel。
4. 每个 panel 还可能有不同的间距。

如果把这些都挤进一条命令里，命令会非常难维护。  
布局文件更适合这个问题。

---

# **18. 建议的入门方式**
如果你是第一次使用，建议按这个顺序来：

1. 先运行 `felayout init -o layout.yaml`
2. 先只改 `items`
3. 再改 `width`
4. 再改 `margins`
5. 再改 `left_gaps/right_gaps`
6. 每次改完后先跑 `felayout validate`
7. 没问题再跑 `felayout build`

这样最不容易混乱。

---

# **19. 结语**
你可以把 `felayout` 理解为一种“可保存、可复用、可版本管理的排版说明书”。

比起一次次手工拖图，它更适合：

1. 需要重复生成的科研图版。
2. 需要多人协作的项目。
3. 需要长期维护和微调的论文图件。

建议先从最简单的模板开始，优先使用：

1. 单值间距
2. 少量行
3. YAML 或 JSON 中你最熟悉的一种

先把流程跑通，再逐步加复杂度。
