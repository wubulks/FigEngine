# **1. 引言**
`feimg` 是一个基于 `FigEngine` 的命令行单图处理工具。

它的主要目标是：

1. 让单张图片处理过程可复现
2. 让图像处理步骤可以稳定写进脚本和工作流
3. 尽量让 CLI 参数名与 `FigEngine.Image` 的 API 参数保持一致

如果把整个制图流程拆开来看：

1. `feimg` 负责单图处理
2. `felayout` 负责多图排版
3. `FigEngine` 是底层图像与排版库

因此，`feimg` 更适合做：

1. 预处理 panel
2. 添加标注
3. 调整大小和画布
4. 添加边框和叠加元素
5. 输出用于后续拼版的单图

---

# **2. 与 FigEngine 的关系**
`feimg` 不是独立图像引擎，而是 `FigEngine.Image` 的 CLI 包装。

多数命令都可以直接对应到一个 `FigEngine.Image` 方法：

| `feimg` 命令 | 对应方法 |
| --- | --- |
| `new` | `Image.new()` |
| `info` | `Image(...)` + 属性读取 |
| `ticks` | `Image.add_ticks()` |
| `text` | `Image.add_text()` |
| `labeled` | `Image.labeled()` |
| `line` | `Image.add_line()` |
| `rect` | `Image.add_rect()` |
| `oval` | `Image.add_oval()` |
| `marker` | `Image.add_marker()` |
| `resize` | `Image.resize()` |
| `crop` / `clip` | `Image.crop()` |
| `pad` | `Image.pad_to_size()` |
| `border` | `Image.add_border()` |
| `overlay` | `Image.overlay()` |
| `rotate` | `Image.rotate()` |

为了兼顾 CLI 易用性和 API 一致性，当前策略是：

1. 优先新增与 API 一致的参数名
2. 保留旧参数作为兼容别名

典型例子：

1. `new` 推荐使用 `--size W H`
同时兼容 `--width W --height H`

2. `pad` 推荐使用 `--target-size W H`
同时兼容 `--target-width W --target-height H`

3. `overlay` 推荐使用 `--other`
同时兼容 `--overlay`

---

# **3. 安装与验证**
## **3.1. 安装**
从 PyPI 安装：

```bash
pip install feimg
```

从源码安装：

```bash
cd feimg
pip install -e .
```

---

## **3.2. 验证**
```bash
feimg --help
feimg resize --help
feimg text --help
```

如果这些命令能正常显示帮助信息，说明安装成功。

---

# **4. 基本命令结构**
基本形式：

```bash
feimg [全局参数] <command> [命令参数]
```

例如：

```bash
feimg info -i input.png
feimg resize -i input.png -o output.png --width 4 --unit inch
```

---

# **5. 全局参数与配置文件**
## **5.1. 全局参数**
所有子命令都支持：

1. `--config`
指定 JSON 配置文件路径

2. `--log-level`
设置日志级别  
支持：
`DEBUG`、`INFO`、`WARNING`、`ERROR`

示例：

```bash
feimg --config config.json --log-level INFO resize -i in.png -o out.png --width 4
```

---

## **5.2. 配置文件格式**
`feimg` 当前支持 JSON 配置文件。

示例：

```json
{
    "dpi": 300,
    "unit": "inch",
    "log_level": "WARNING",
    "overwrite": false,
    "bg_color": "#FFFFFF"
}
```

字段说明：

1. `dpi`
默认 DPI

2. `unit`
默认单位

3. `log_level`
默认日志级别

4. `overwrite`
是否默认允许覆盖已有输出

5. `bg_color`
默认背景色

---

## **5.3. 参数优先级**
当前优先级为：

1. 命令行参数
2. 配置文件参数
3. 程序默认值

---

# **6. 参数输入风格说明**
很多初次使用 CLI 的用户最容易在这里困惑。建议先认真看这一节。

## **6.1. 单个数值**
表示只传一个数字。

例如：

```bash
--width 4
--fontsize 24
--angle 30
```

---

## **6.2. 成对数值**
表示传一个二元组，通常用于尺寸或坐标。

例如：

```bash
--size 6 5
--target-size 6 4
--start 0.1 0.2
--end 0.8 0.9
--center 0.5 0.5
```

这些写法分别对应底层 API 中的 tuple 参数。

---

## **6.3. 单值或双值字符串**
有些参数支持单值和双值两种形式。

例如：

```bash
--scale 0.5
--scale 0.5,0.8
--offset 0.02
--offset 0.02,0.03
```

通常含义是：

1. 单值
统一缩放或统一偏移

2. 双值
分别指定 `x/y` 或 `width/height`

---

## **6.4. 单值或四值字符串**
`border` 的 `--thickness` 有两种常用写法：

```bash
--thickness 0.1
--thickness 0.1,0.2,0.3,0.4
```

含义：

1. 单值
四边统一厚度

2. 四值
分别指定：
`left,right,top,bottom`

---

## **6.5. 单位怎么选**
常见单位：

1. `pixel`
2. `ratio`
3. `inch`
4. `cm`
5. `mm`

经验建议：

1. 与论文版面尺寸对齐：优先 `inch / cm / mm`
2. 按相对位置做标注：优先 `ratio`
3. 需要像素级精确处理：使用 `pixel`

---

# **7. 常见工作流**
## **7.1. 查看图片信息**
```bash
feimg info -i input.png
```

## **7.2. 创建空白图**
```bash
feimg new -o blank.png --size 6 5 --unit inch --dpi 600
```

## **7.3. 按宽度缩放**
```bash
feimg resize -i input.png -o resized.png --width 4 --unit inch
```

## **7.4. 按参考图缩放**
```bash
feimg resize -i input.png -o resized.png --ref-image ref.png
```

## **7.5. 添加文字**
```bash
feimg text -i input.png -o labeled.png --text "A" --loc top_left --unit ratio --fontsize 24
```

## **7.6. 添加边框**
```bash
feimg border -i in.png -o out.png --thickness 0.02 --unit ratio --color black
```

## **7.7. 叠加 logo**
```bash
feimg overlay -i base.png --other logo.png -o out.png --x 0.9 --y 0.1 --anchor top_right --unit ratio --scale 0.25
```

---

# **8. 命令与 API 对照**
如果你同时使用 Python 和 CLI，可以用这张表快速对应。

| `feimg` 命令 | 对应 `FigEngine` 方法 | 主要 API 参数 |
| --- | --- | --- |
| `new` | `Image.new()` | `size`, `facecolor`, `unit`, `dpi`, `label` |
| `info` | `Image(...)` | `source`, `dpi` |
| `ticks` | `Image.add_ticks()` | `step`, `unit`, `color`, `font`, `fontsize`, `show_grid` |
| `text` | `Image.add_text()` | `text`, `x`, `y`, `loc`, `anchor`, `offset`, `unit`, `font`, `fontsize`, `fontweight`, `rotation`, `color`, `box_style`, `dpi` |
| `labeled` | `Image.labeled()` | `label`, `loc`, `offset`, `format_str`, `case`, `fontsize`, `fontweight`, `color`, `font`, `box_style` |
| `line` | `Image.add_line()` | `start`, `end`, `unit`, `color`, `width`, `arrow`, `arrow_size`, `arrow_style`, `arrow_angle`, `arrow_shorten`, `arrow_fill` |
| `rect` | `Image.add_rect()` | `start`, `end`, `center`, `size`, `unit`, `linewidth`, `color`, `edgecolor`, `facecolor`, `fill` |
| `oval` | `Image.add_oval()` | `start`, `end`, `center`, `radius`, `axis_ratio`, `unit`, `linewidth`, `color`, `edgecolor`, `facecolor`, `fill` |
| `marker` | `Image.add_marker()` | `x`, `y`, `unit`, `style`, `size`, `color`, `outline`, `width` |
| `resize` | `Image.resize()` | `width`, `height`, `scale`, `ref_image`, `unit`, `resample` |
| `crop` / `clip` | `Image.crop()` | `box`, `left`, `top`, `right`, `bottom`, `unit` |
| `pad` | `Image.pad_to_size()` | `target_size`, `unit`, `loc`, `axis`, `bg_color` |
| `border` | `Image.add_border()` | `thickness`, `unit`, `left`, `right`, `top`, `bottom`, `color` |
| `overlay` | `Image.overlay()` | `other`, `x`, `y`, `anchor`, `unit`, `scale`, `expand`, `bg_color` |
| `rotate` | `Image.rotate()` | `angle`, `expand`, `bg_color` |

---

# **9. 命令详解**
## **9.1. `new`：创建空白图片**
### **功能说明**
创建一张指定尺寸、背景色和 DPI 的空白图像。

### **与 API 对应**
```python
Image.new(size=(w, h), facecolor=..., unit=..., dpi=..., label=...)
```

### **命令签名**
```bash
feimg new -o OUTPUT [--size W H | --width W --height H] [--facecolor C] [--unit U] [--dpi D] [--label L] [--overwrite]
```

### **参数说明**
1. `--size W H`
推荐写法，直接对应 API 的 `size`

2. `--width W --height H`
兼容写法，等价于 `--size W H`

3. `--facecolor`
背景色

4. `--unit`
尺寸单位

5. `--dpi`
输出 DPI

6. `--label`
图像标签

### **示例**
```bash
feimg new -o blank.png --size 6 5 --unit inch --dpi 600
feimg new -o blank.png --width 6 --height 5 --unit inch --dpi 600
feimg new -o black_bg.png --size 1200 800 --unit pixel --facecolor "#000000"
```

---

## **9.2. `info`：查看图片信息**
### **命令签名**
```bash
feimg info -i INPUT [--dpi D]
```

### **输出内容**
通常包含：

1. `size`
2. `size_pixel`
3. `size_inch`
4. `size_cm`
5. `size_mm`
6. `dpi`
7. `label`

### **示例**
```bash
feimg info -i input.png
feimg info -i input.tif --dpi 600
```

---

## **9.3. `ticks`：添加刻度或网格**
### **命令签名**
```bash
feimg ticks -i INPUT -o OUTPUT --step S [--unit U] [--color C] [--font F] [--fontsize N] [--show-grid|--edge-only] [--dpi D] [--overwrite]
```

### **示例**
```bash
feimg ticks -i in.png -o out.png --step 0.1 --unit ratio --show-grid
feimg ticks -i in.png -o out.png --step 50 --unit pixel --edge-only --color red
```

---

## **9.4. `text`：添加文本**
### **命令签名**
```bash
feimg text -i INPUT -o OUTPUT --text TEXT [--x X --y Y] [--loc LOC] [--anchor A] [--offset V] [--unit U] [--font F] [--fontsize N] [--fontweight W] [--rotation R] [--color C] [--box-style JSON] [--dpi D] [--overwrite]
```

### **关键参数**
1. `--text`
文本内容

2. `--x --y`
绝对坐标模式

3. `--loc`
语义位置模式

4. `--anchor`
文字锚点

5. `--offset`
支持：
`0.02`
或
`0.02,0.03`

6. `--box-style`
JSON 字符串，对应 API 中的 `box_style`

### **示例**
```bash
feimg text -i in.png -o out.png --text "Top Left" --loc top_left --offset 0.02,0.02 --unit ratio --fontsize 24
feimg text -i in.png -o out.png --text "Center" --x 0.5 --y 0.5 --anchor center --unit ratio
feimg text -i in.png -o out.png --text "Note" --x 120 --y 60 --unit pixel --box-style '{"facecolor":"white","boxstyle":"round,pad=0.3"}'
```

---

## **9.5. `labeled`：添加子图标签**
### **命令签名**
```bash
feimg labeled -i INPUT -o OUTPUT [--label L] [--loc LOC] [--offset V] [--format-str FMT] [--case CASE] [--fontsize N] [--fontweight W] [--color C] [--font F] [--box-style JSON] [--dpi D] [--overwrite]
```

### **示例**
```bash
feimg labeled -i in.png -o out.png --label a --format-str "({})" --case upper
feimg labeled -i in.png -o out.png --label 1 --loc top_right --format-str "Fig. {}"
```

---

## **9.6. `line`：绘制线段或箭头**
### **命令签名**
```bash
feimg line -i INPUT -o OUTPUT --start X1 Y1 --end X2 Y2 [--unit U] [--color C] [--width W] [--arrow POS] [--arrow-size S] [--arrow-style STYLE] [--arrow-angle A] [--arrow-shorten V] [--arrow-fill|--no-arrow-fill] [--dpi D] [--overwrite]
```

### **示例**
```bash
feimg line -i in.png -o out.png --start 0.1 0.1 --end 0.9 0.1 --unit ratio --arrow end
feimg line -i in.png -o out.png --start 50 50 --end 300 200 --unit pixel --color blue --width 2
```

---

## **9.7. `rect`：绘制矩形**
支持：

1. `--start + --end`
2. `--center + --size`

```bash
feimg rect -i in.png -o out.png --start 0.1 0.1 --end 0.9 0.9 --unit ratio --color red
feimg rect -i in.png -o out.png --center 0.5 0.5 --size 3 2 --unit inch --facecolor "#FFE8A3" --fill
```

---

## **9.8. `oval`：绘制圆或椭圆**
支持：

1. `--start + --end`
2. `--center + --radius`

```bash
feimg oval -i in.png -o out.png --center 0.5 0.5 --radius 0.2 --axis-ratio 1.5 --unit ratio --color blue
feimg oval -i in.png -o out.png --start 50 50 --end 180 120 --unit pixel --edgecolor green --no-fill
```

---

## **9.9. `marker`：添加标记点**
```bash
feimg marker -i in.png -o out.png --x 0.1 --y 0.1 --unit ratio --style circle --size 0.02 --color red
feimg marker -i in.png -o out.png --x 300 --y 200 --unit pixel --style target --size 20 --outline black
```

---

## **9.10. `resize`：缩放图片**
### **与 API 对应**
```python
Image.resize(width=..., height=..., scale=..., ref_image=..., unit=..., resample=...)
```

### **命令签名**
```bash
feimg resize -i INPUT -o OUTPUT [--width W] [--height H] [--scale S] [--ref-image PATH] [--unit U] [--resample R] [--dpi D] [--overwrite]
```

### **四种常见入口**
1. `--width`
2. `--height`
3. `--scale`
4. `--ref-image`

### **示例**
```bash
feimg resize -i in.png -o out.png --width 4 --unit inch
feimg resize -i in.png -o out.png --height 10 --unit cm
feimg resize -i in.png -o out.png --scale 0.5
feimg resize -i in.png -o out.png --scale 0.5,0.8
feimg resize -i in.png -o out.png --ref-image ref.png
```

---

## **9.11. `crop`：裁剪图片**
支持：

1. `--box L T R B`
2. `--left --top --right --bottom`

```bash
feimg crop -i in.png -o out.png --box 1 1 5 4 --unit inch
feimg crop -i in.png -o out.png --left 0.1 --top 0.1 --right 0.1 --bottom 0.1 --unit ratio
```

---

## **9.12. `clip`：`crop` 的兼容别名**
```bash
feimg clip -i in.png -o out.png --box 0.5 0.5 4.5 3.0 --unit inch
```

---

## **9.13. `pad`：扩展到目标画布尺寸**
### **与 API 对应**
```python
Image.pad_to_size(target_size=(w, h), unit=..., loc=..., axis=..., bg_color=...)
```

### **命令签名**
```bash
feimg pad -i INPUT -o OUTPUT [--target-size W H | --target-width W --target-height H] [--unit U] [--loc LOC] [--axis AXIS] [--bg-color C] [--dpi D] [--overwrite]
```

### **推荐写法**
优先使用：

```bash
--target-size W H
```

### **示例**
```bash
feimg pad -i in.png -o out.png --target-size 6 4 --unit inch --loc center
feimg pad -i in.png -o out.png --target-width 6 --target-height 4 --unit inch --loc center
feimg pad -i in.png -o out.png --target-size 1.1 1.1 --unit ratio --bg-color "#B8FFCD"
```

---

## **9.14. `border`：添加边框**
### **与 API 对应**
```python
Image.add_border(thickness=..., unit=..., left=..., right=..., top=..., bottom=..., color=...)
```

### **命令签名**
```bash
feimg border -i INPUT -o OUTPUT --thickness T [--left L] [--top T] [--right R] [--bottom B] [--unit U] [--color C] [--dpi D] [--overwrite]
```

### **`--thickness` 的两种风格**
1. 单值：
```bash
--thickness 0.005
```

2. 四值：
```bash
--thickness 0.005,0.006,0.007,0.008
```

顺序是：

`left,right,top,bottom`

### **示例**
```bash
feimg border -i in.png -o out.png --thickness 0.005 --unit ratio --color black
feimg border -i in.png -o out.png --thickness 0.005,0.006,0.007,0.008 --unit ratio --color black
feimg border -i in.png -o out.png --thickness 0.005 --left 0.01 --unit ratio --color black
```

---

## **9.15. `overlay`：叠加图片**
### **与 API 对应**
```python
Image.overlay(other=..., x=..., y=..., anchor=..., unit=..., scale=..., expand=..., bg_color=...)
```

### **命令签名**
```bash
feimg overlay -i BASE [--other TOP | --overlay TOP] -o OUTPUT [--x X] [--y Y] [--anchor A] [--unit U] [--scale S] [--expand] [--bg-color C] [--dpi D] [--overwrite]
```

### **推荐写法**
优先使用：

```bash
--other
```

### **示例**
```bash
feimg overlay -i base.png --other logo.png -o out.png --x 0.1 --y 0.1 --unit ratio --anchor center --scale 0.3
feimg overlay -i base.png --overlay top.png -o out.png --x 30 --y 40 --unit pixel --expand
```

---

## **9.16. `rotate`：旋转图片**
```bash
feimg rotate -i in.png -o out.png --angle 30
feimg rotate -i in.png -o out.png --angle 30 --expand --bg-color "#FFFFFF"
```

---

# **10. 错误示例与常见陷阱**
这一节专门讲“看起来像对的，但实际上很容易出错”的写法。

## **10.1. `--size` 不是逗号字符串**
错误写法：

```bash
feimg new -o blank.png --size 6,5 --unit inch
```

正确写法：

```bash
feimg new -o blank.png --size 6 5 --unit inch
```

原因：

`--size` 在 CLI 中是两个独立参数，对应一个二元组，而不是一个带逗号的字符串。

---

## **10.2. `--target-size` 也不是逗号字符串**
错误写法：

```bash
feimg pad -i in.png -o out.png --target-size 6,4 --unit inch
```

正确写法：

```bash
feimg pad -i in.png -o out.png --target-size 6 4 --unit inch
```

---

## **10.3. `--scale` 和 `--size` 的格式不一样**
这一点很容易混淆：

1. `--size` 用空格分开两个值
2. `--scale` 用单值或逗号字符串

正确示例：

```bash
--size 6 5
--scale 0.5
--scale 0.5,0.8
```

容易写错成：

```bash
--scale 0.5 0.8
```

这不是当前 `feimg` 的 `scale` 输入格式。

---

## **10.4. `--offset` 支持单值和双值，但不是两个独立参数**
推荐写法：

```bash
--offset 0.02
--offset 0.02,0.03
```

不要写成：

```bash
--offset 0.02 0.03
```

因为 CLI 会把第二个值当成额外参数，而不是同一个 `offset`。

---

## **10.5. `--thickness` 四值顺序容易写反**
`border` 命令中，四值顺序是：

`left,right,top,bottom`

例如：

```bash
--thickness 0.01,0.02,0.03,0.04
```

表示：

1. left = 0.01
2. right = 0.02
3. top = 0.03
4. bottom = 0.04

这不是 CSS 里常见的 `top,right,bottom,left` 顺序。

---

## **10.6. `--thickness` 四值写法不是四个独立参数**
错误理解：

```bash
--thickness 0.01 0.02 0.03 0.04
```

正确写法：

```bash
--thickness 0.01,0.02,0.03,0.04
```

因为 `--thickness` 当前读入的是一个字符串参数，内部再解析为单值或四值。

---

## **10.7. `--other` 和 `--overlay` 只需要选一个**
推荐：

```bash
feimg overlay -i base.png --other logo.png -o out.png
```

兼容旧写法：

```bash
feimg overlay -i base.png --overlay logo.png -o out.png
```

不建议同时混用两个名字，因为可读性会变差，也容易让人误解为两个不同参数。

---

## **10.8. `--ref-image` 与 `--width/--height/--scale` 同时写时要谨慎**
底层 `Image.resize()` 中，`ref_image` 的约束优先级很高。

这意味着：

```bash
feimg resize -i in.png -o out.png --width 4 --ref-image ref.png
```

这种写法虽然不一定报错，但从表达上容易让人误解。

更建议：

1. 只写 `--ref-image`
或
2. 只写 `--width/--height/--scale`

尽量不要混在同一条命令里。

---

## **10.9. `ratio` 不是百分数写法**
很多用户会误写成：

```bash
--x 50 --y 50 --unit ratio
```

如果你想表达 50%，通常应该写：

```bash
--x 0.5 --y 0.5 --unit ratio
```

因为：

1. `0.5` 表示 50%
2. `1.0` 表示 100%
3. `0.02` 表示 2%

---

## **10.10. 不同单位下，同一个数值含义完全不同**
例如：

```bash
--x 0.5 --y 0.5 --unit ratio
```

通常表示接近图像中心。

但：

```bash
--x 0.5 --y 0.5 --unit inch
```

表示的是“距原点 0.5 英寸”，不是“50%”。

---

## **10.11. `crop --box` 是区域坐标，不是裁掉的厚度**
例如：

```bash
feimg crop -i in.png -o out.png --box 1 1 5 4 --unit inch
```

这表示“保留 `(1,1)-(5,4)` 这个区域”。

而下面这种写法：

```bash
feimg crop -i in.png -o out.png --left 0.1 --right 0.1 --unit ratio
```

表示“从左右各裁掉 10%”。

这两种模式的含义完全不同。

---

## **10.12. `clip` 不是新功能**
`clip` 和 `crop` 行为一致，只是兼容别名。

如果你在团队内部想统一风格，建议长期只固定使用其中一个名称。

---

## **10.13. 忘记 `--overwrite` 是最常见报错来源之一**
如果输出文件已经存在，而你又没有显式传 `--overwrite`，命令会直接报错。

这是保护行为，不是程序异常。

---

# **11. 常见问题**
## **11.1. 输出文件已存在**
如果输出文件已存在，而你没有传 `--overwrite`，命令会报错。

---

## **11.2. `new` 应该用 `--size` 还是 `--width/--height`**
建议优先使用 `--size`，因为它与底层 API 更一致。

---

## **11.3. `pad` 应该用 `--target-size` 还是 `--target-width/--target-height`**
建议优先使用 `--target-size`。

---

## **11.4. `overlay` 为什么既有 `--other` 又有 `--overlay`**
因为：

1. `--other` 更贴近 API 参数名
2. `--overlay` 是兼容旧写法

---

## **11.5. `crop` 和 `clip` 有什么区别**
没有区别。  
`clip` 是兼容别名。

---

## **11.6. 如何查看命令支持哪些参数**
```bash
feimg <command> --help
```

例如：

```bash
feimg text --help
feimg overlay --help
feimg pad --help
```

---

## **11.7. 如何选择单位**
经验建议：

1. 与论文版面对齐：优先 `inch / cm / mm`
2. 按比例定位：优先 `ratio`
3. 做像素级控制：使用 `pixel`

---

# **12. 命令总览**
当前版本提供：

1. `new`
2. `info`
3. `ticks`
4. `text`
5. `labeled`
6. `line`
7. `rect`
8. `oval`
9. `marker`
10. `resize`
11. `crop`
12. `clip`
13. `pad`
14. `border`
15. `overlay`
16. `rotate`
