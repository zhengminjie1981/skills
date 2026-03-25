# md2slides 详细设计文档

> 文档层级：L2 详细设计
> 版本：v1.3 | 创建日期：2026-03-24 | 更新日期：2026-03-25
> 依赖文档：[requirements.md](requirements.md)

---

## 目录

1. [系统架构](#1-系统架构)
2. [AI 工作流设计](#2-ai-工作流设计)
3. [数据结构设计](#3-数据结构设计)
4. [HTML 模板与渲染引擎](#4-html-模板与渲染引擎)
5. [主题系统设计](#5-主题系统设计)
6. [图表渲染设计](#6-图表渲染设计)
7. [脚本模块设计](#7-脚本模块设计)
8. [PDF 转换设计](#8-pdf-转换设计)
9. [元素树设计](#9-元素树设计)
10. [错误处理策略](#10-错误处理策略)
11. [文件组织与命名规范](#11-文件组织与命名规范)

---

## 1. 系统架构

### 1.1 总体架构

md2slides 由两个层次协同工作：

```
┌─────────────────────────────────────────────────────┐
│                    AI 层（Claude）                   │
│                                                     │
│  内容策划  →  数据提取  →  HTML生成指令  →  调整指令  │
└──────────────────────┬──────────────────────────────┘
                       │ 调用
┌──────────────────────▼──────────────────────────────┐
│                   脚本层（Python）                   │
│                                                     │
│  convert.py   extract_data.py   html2pdf.py         │
│  （MD→HTML）  （数据→CSV）      （HTML→PDF）         │
└──────────────────────┬──────────────────────────────┘
                       │ 读写
┌──────────────────────▼──────────────────────────────┐
│                    文件层                            │
│                                                     │
│  *.md（演示稿）  data/*.csv  *.html  *.pdf           │
│  slide-tree.json（元素树）                           │
└─────────────────────────────────────────────────────┘
```

### 1.2 组件职责

| 组件 | 类型 | 职责 |
|------|------|------|
| Claude AI | 智能层 | 内容理解、结构规划、风格决策、调整判断 |
| `convert.py` | 脚本 | 解析 MD，读取 CSV，生成 HTML，输出元素树 |
| `extract_data.py` | 脚本 | 从原始材料中提取表格/数据，写入 CSV |
| `html2pdf.py` | 脚本 | 用 playwright 渲染 HTML，导出分页 PDF |
| `preview.py` | 脚本 | 批量截图生成缩略图，--temp/--clean 管理临时目录 |
| `references/template.html` | 模板 | HTML 骨架，含变量占位符 |
| `references/themes/*.css` | 样式 | 各主题的 CSS 变量和样式规则 |
| `references/chart-defaults.json` | 配置 | 各图表类型的 Chart.js 默认参数 |
| `slide-tree.json` | 数据 | 生成后的元素树，随调整同步更新 |

### 1.3 数据流

```
原始材料
   │
   ▼ [AI 策划]
演示稿.md + data/*.csv
   │
   ▼ [convert.py]
演示稿.html + slide-tree.json
   │
   ├──▶ 浏览器直接查看
   │
   ├──▶ [AI 样式调整] → 直接更新 .html（下次生成时自动同步 slide-tree.json）
   │
   ├──▶ [AI 内容变更] → 更新 .md → [convert.py --preserve-styles]
   │                               → 覆盖 .html + slide-tree.json
   │
   └──▶ [html2pdf.py] → 演示稿.pdf
```

---

## 2. AI 工作流设计

### 2.1 阶段一：内容策划

#### 2.1.1 内容分析步骤

AI 收到原始材料后，按以下顺序处理：

```
步骤1: 识别材料类型
  → 报告/文章 / 数据表格 / 混合内容

步骤2: 提取核心主题和关键信息
  → 主标题、核心论点、支撑数据

步骤3: 识别数据内容
  → 扫描所有数字、表格、对比、百分比、时间序列
  → 标记需要图表化的数据段落

步骤4: 规划演示结构
  → 封面（必须）
  → 目录（页数 ≥ 5 时自动加入）
  → 内容页（每个主要论点一页）
  → 数据页（每组图表数据一页）
  → 结语/联系方式（必须）

步骤5: 控制总页数
  → 建议范围：6-15 页
  → 超过 15 页时合并相似内容
  → 少于 6 页时适当拆分细化
```

#### 2.1.2 MD 生成规则

每一页的内容遵循以下原则：

| 页面类型 | 内容规则 |
|---------|---------|
| 封面 | H1（主标题）+ H2（副标题/日期/作者），无列表 |
| 目录 | H1（"目录"或自定义）+ 有序列表，列出所有内容章节 |
| 内容页 | H1（页面主题）+ 要点列表（≤6条）或短段落 |
| 数据页 | H1（页面主题）+ `<!-- chart -->` 块 + 简短说明文字 |
| 结语 | H1 + 简短总结或 CTA |

**文字密度控制**：
- 列表每条 ≤ 20 字（中文）
- 单页文字总量 ≤ 120 字（不含标题）
- 标题 ≤ 15 字

#### 2.1.3 数据识别与提取判断

AI 判断是否需要提取为图表的标准：

```
满足以下任一条件 → 提取为图表：
  ✓ 包含 3 个或以上可比较的数值
  ✓ 存在时间序列数据（按季度/月份/年份）
  ✓ 存在明确的占比/分布数据
  ✓ 原材料中有表格且列为数值型

以下情况 → 保留为文字：
  ✗ 仅有单个数字（"增长了 30%"）
  ✗ 文字说明性表格（非数值为主）
  ✗ 数据少于 3 个数据点
```

#### 2.1.4 图表类型自动选择

```
时间序列 / 趋势 → line 或 area
分类对比（≤8类）→ bar
分类对比（标签长）→ bar-horizontal
占比（≤6类）→ pie 或 donut
多维分布 → scatter
精确数值参考 → table
```

#### 2.1.5 策划结果输出

AI 生成 MD 文件后，向用户展示摘要：

```
已完成内容策划，共 X 页：

页码  类型    标题
1     封面    [标题]
2     目录    目录
3     内容    [章节名]
...
6     数据    [数据主题]（包含柱状图：[数据描述]）
...

涉及数据文件：
- data/{名称}-s6-{描述}.csv（已创建）

请确认内容，或告知需要调整的地方，确认后将生成 HTML。
```

### 2.2 阶段二：HTML 生成

#### 2.2.1 生成前确认流程

```
if 用户未指定宽高比:
    询问: "请选择宽高比：A. 16:9（推荐）  B. 4:3"
    等待用户回复

if 用户未指定主题:
    根据内容类型推荐主题:
        商务汇报/客户演示   → professional-dark
        正式文档/打印版本   → professional-light
        产品发布/对外演讲台 → keynote-white
        工程师技术分享      → tech-terminal
        年会/颁奖/纪念日    → celebration
        员工关怀/企业文化   → caring-green
        产品/创意/AI展示    → creative-gradient
        极简/设计简报       → minimal-clean
        企业历史/文化宣讲   → warm-earth
    告知推荐理由，询问是否采用

if 用户说"默认" or "用默认配置":
    ratio = 16:9
    theme = professional-dark
    skip 询问
```

#### 2.2.2 HTML 生成调用

确认参数后，AI 调用 `convert.py`：

```bash
python scripts/convert.py \
  --input 演示稿.md \
  --output 演示稿.html \
  --ratio 16:9 \
  --theme professional-dark \
  --tree slide-tree.json
```

生成完成后，AI 读取 `slide-tree.json` 并向用户展示元素树摘要（不展示完整 JSON，而是结构化摘要）：

```
HTML 已生成：演示稿.html（X 页）
- 键盘左/右键、空格键翻页
- 右下角显示页码

页面结构摘要：
├── 第1页（封面）: title, subtitle
├── 第2页（目录）: title, list[5项]
├── 第3页（内容）: title, list[4项]
├── 第4页（数据）: title, list[2项], chart[bar]
└── ...
```

### 2.3 调整工作流

#### 2.3.0 路由判断：内容变更 vs 样式调整

AI 收到调整请求时，首先判断走哪条路径：

```
以下情况 → 内容变更路径（更新 MD → convert.py --preserve-styles）
  ✓ 修改文字内容（标题措辞、要点文字、段落内容）
  ✓ 增减列表条目
  ✓ 增加 / 删除 / 移动页面
  ✓ 修改图表类型、数据源文件、xField、yField

以下情况 → 样式调整路径（直接编辑 HTML + 同步树）
  ✓ 字体大小 / 颜色 / 粗细
  ✓ 间距 / 对齐方式 / 背景色
  ✓ 图表在页面内的位置（position）/ 宽高百分比
```

> 注：图表类型变更（bar → line）归入**内容变更**，因为需要修改 MD 中的 `<!-- chart -->` 块参数。

#### 2.3.1 样式调整请求解析

AI 收到调整请求时，执行以下步骤：

```
步骤1: 解析目标
  → 定位页码（"第3页" → index=3）
  → 定位元素（"标题" → type=h1 → id=s3-title）
  → 如有多个同类元素，询问用户确认

步骤2: 解析属性变更
  → 字体大小变更 → fontSize
  → 颜色变更 → color / backgroundColor
  → 大小变更 → width / height
  → 位置变更 → 可能涉及 position / layout

步骤3: 执行修改
  → 直接编辑 HTML 文件中对应元素的 style 属性或类名
  → 同步更新 slide-tree.json 中对应节点

步骤4: 确认结果
  → 告知用户已修改的元素 ID 和具体变更内容
```

#### 2.3.2 常用调整场景映射

| 用户说法 | 对应操作 |
|---------|---------|
| "标题改大/小" | fontSize ±0.3em~0.5em |
| "颜色改成 X" | color = CSS颜色值（支持中文颜色名转换） |
| "移到左边/右边" | 调整 layout/position |
| "字体粗一点" | fontWeight: bold |
| "间距大一点" | padding/margin +0.5em |
| "背景改成 X" | 修改 .slide 的 background |
| "图表移到左边" | chart.layout: right → left，text.layout 对应反转 |

**颜色中文名映射**（常用）：

```python
COLOR_MAP = {
    "白色": "#ffffff", "黑色": "#000000",
    "红色": "#e74c3c", "蓝色": "#3498db",
    "绿色": "#2ecc71", "黄色": "#f1c40f",
    "橙色": "#e67e22", "紫色": "#9b59b6",
    "灰色": "#95a5a6", "深灰": "#2c3e50",
    "浅蓝": "#aaccff", "深蓝": "#1a3a6b",
}
```

---

### 2.4 内容变更工作流

#### 2.4.1 处理步骤

AI 确认属于内容变更后，按以下步骤处理：

```
步骤1: 定位 MD 中的目标位置
  → 确定要修改的是哪一页（按 <!-- Slide N --> 注释定位）
  → 确定要修改的是文字内容、列表条目、chart 块参数，还是页面结构

步骤2: 更新 MD 文件
  → 修改对应页面的内容
  → 若增加页面：在合适位置插入 --- 和新页内容
  → 若删除页面：移除对应页面的全部内容（含 --- 分隔符）
  → 若修改图表类型：更新 <!-- chart --> 块中的 type 字段

步骤3: 重新生成 HTML（--preserve-styles 模式）
  → 调用 convert.py --preserve-styles
  → 生成新 HTML 和新元素树
  → 按 ID 匹配从旧树提取已定制 style，合并回新树和 HTML

步骤4: 汇报变更结果
  → 展示页面级差异摘要
  → 若有元素 ID 不匹配（样式丢失），明确告知用户
```

#### 2.4.2 样式保留合并规则

| 情况 | 处理方式 |
|------|----------|
| 新旧 ID 均存在，旧树有自定义 style | 将旧 style 合并覆盖到新 HTML 元素和新树节点 |
| 新旧 ID 均存在，旧树无自定义 style | 使用主题默认样式 |
| ID 仅在新树中（新增元素） | 使用主题默认样式 |
| ID 仅在旧树中（已删除元素） | 丢弃旧样式，向用户告知 |

> 注：层级变动（增/删页面导致页码后移）会导致相应页的所有 ID 发生变化，
这些页的手工样式将被重置。AI 应在这种情况下提前告知用户。

#### 2.4.3 对话示例

```
修改文字：
  用户: 第3页第二条要点改成"月活用户超过 30 万，同比增长 45%"
  AI: 已更新 MD 第3页列表第2项。重新生成 HTML，已保留现有样式。

增加页面：
  用户: 在第5页后面加一页"风险分析"，包含三条要点
  AI: 已在 MD 第5页后插入新页。原第6页及之后页码后移，
      这些页的已定制样式将重置。是否继续？

修改图表类型：
  用户: 第4页的柱状图改成折线图
  AI: 已更新 MD 第4页 chart 块 type: bar → line。
      重新生成，图表 position/width/height 样式已保留。
```

---

## 3. 数据结构设计

### 3.1 MD 文件结构规范

#### 3.1.1 Frontmatter

```yaml
---
title: string          # 演示文稿标题（必填）
ratio: "16:9" | "4:3"  # 宽高比（必填，AI 生成时写入）
theme: string          # 主题名（必填，AI 生成时写入）
transition: string     # 切换动画：fade|slide|zoom（可选，默认 fade）
author: string         # 作者（可选）
date: string           # 日期（可选）
---
```

#### 3.1.2 图表注释块语法

```
<!-- chart
type: <图表类型>          必填
dataSource: <CSV路径>     必填（相对于 MD 文件目录）
xField: <列名>            必填（X轴/标签字段）
yField: <列名>            必填（Y轴/数值字段）；多系列时为逗号分隔列表
title: <图表标题>          可选
position: <位置>          可选，默认 full
width: <百分比>            可选，默认按 position 自动设置
height: <百分比>           可选，默认 65%
colorScheme: theme | [...] 可选，默认 theme
legend: true | false      可选，默认 true
-->
```

**position 与默认宽度对应关系**：

| position | 图表默认宽度 | 文字区域宽度 |
|----------|------------|------------|
| full | 100% | — |
| right | 55% | 42% |
| left | 55% | 42% |
| center | 70% | 100%（上下） |
| bottom | 100% | 100%（上下） |

> 注：left/right 布局下，图表 + 文字 + 间距 = 100%（间距约 3%）。

#### 3.1.3 完整 MD 示例

```markdown
---
title: 2024年产品运营报告
ratio: 16:9
theme: professional-dark
transition: fade
author: 张三
date: 2026-03-24
---

<!-- Slide 1: 封面 -->
# 2024年产品运营报告
## 张三 · 2026-03-24

---

<!-- Slide 2: 目录 -->
# 目录
1. 年度概览
2. 用户增长
3. 收入分析
4. 问题与展望

---

<!-- Slide 3: 年度概览 -->
# 年度概览
- 注册用户突破 100 万
- 月活跃用户 32 万，同比增长 45%
- 全年营收 636 万元，同比增长 58%
- App Store 评分 4.8 分

---

<!-- Slide 4: 用户增长 -->
# 季度用户增长

<!-- chart
type: line
dataSource: data/report-s4-users.csv
xField: 季度
yField: 月活(万)
title: 月活跃用户趋势（万人）
position: right
width: 58%
height: 70%
-->

- Q4 月活首次突破 30 万
- 增长主要来自渠道投放
- 自然流量占比提升至 38%

---

<!-- Slide 5: 收入分析 -->
# 季度收入结构

<!-- chart
type: bar
dataSource: data/report-s5-revenue.csv
xField: 季度
yField: 订阅收入(万),广告收入(万)
title: 2024年季度收入结构（万元）
position: full
colorScheme: theme
-->

---

<!-- Slide 6: 结语 -->
# 谢谢
## 联系方式：zhang@example.com
```

### 3.2 CSV 数据格式规范

#### 3.2.1 基础规范

- 编码：UTF-8（无 BOM）
- 分隔符：逗号
- 第一行：表头（字段名）
- 数值字段：纯数字，不含单位或货币符号
- 空值：留空（不填 0 或 N/A，除非确实为 0）

#### 3.2.2 单系列图表 CSV

```csv
季度,月活(万)
Q1,18.2
Q2,22.5
Q3,27.8
Q4,32.1
```

#### 3.2.3 多系列图表 CSV

`yField` 指定多个字段时（逗号分隔），CSV 包含多个数值列：

```csv
季度,订阅收入(万),广告收入(万)
Q1,85,35
Q2,102,43
Q3,120,48
Q4,158,45
```

#### 3.2.4 饼图/环形图 CSV

```csv
来源,占比(%)
自然搜索,38
渠道投放,31
社交媒体,18
口碑推荐,13
```

> 饼图的 `xField` 为类别字段，`yField` 为数值字段，数值不必加总为 100。

### 3.3 元素树 JSON Schema

完整 Schema 定义（`references/slide-schema.json`）：

```json
{
  "$schema": "http://json-schema.org/draft-07/schema",
  "title": "SlideTree",
  "type": "object",
  "properties": {
    "presentation": {
      "type": "object",
      "required": ["ratio", "theme", "totalSlides", "slides"],
      "properties": {
        "ratio":       { "type": "string", "enum": ["16:9", "4:3"] },
        "theme":       { "type": "string" },
        "transition":  { "type": "string", "default": "fade" },
        "totalSlides": { "type": "integer" },
        "slides":      { "type": "array", "items": { "$ref": "#/$defs/slide" } }
      }
    }
  },
  "$defs": {
    "slide": {
      "type": "object",
      "required": ["index", "type", "elements"],
      "properties": {
        "index":    { "type": "integer" },
        "type":     { "type": "string", "enum": ["cover","toc","content","data","end"] },
        "comment":  { "type": "string" },
        "background": { "type": "string" },
        "layout":   { "type": "string", "enum": ["default","split","full-chart","stacked"] },
        "elements": { "type": "array", "items": { "$ref": "#/$defs/element" } }
      }
    },
    "element": {
      "type": "object",
      "required": ["id", "type"],
      "properties": {
        "id":      { "type": "string", "pattern": "^s[0-9]+-[a-z]+[0-9]*$" },
        "type":    { "type": "string", "enum": ["h1","h2","h3","p","ul","ol","img","code","table","chart"] },
        "content": { "type": "string" },
        "items":   { "type": "array", "items": { "type": "string" } },
        "layout":  { "type": "string" },
        "style":   { "type": "object" },
        "chartConfig": { "$ref": "#/$defs/chartConfig" }
      }
    },
    "chartConfig": {
      "type": "object",
      "required": ["chartType", "dataSource", "xField", "yField"],
      "properties": {
        "chartType":   { "type": "string" },
        "dataSource":  { "type": "string" },
        "xField":      { "type": "string" },
        "yField":      { "type": "string" },
        "title":       { "type": "string" },
        "legend":      { "type": "boolean", "default": true },
        "colorScheme": { "type": ["string", "array"] }
      }
    }
  }
}
```

---

## 4. HTML 模板与渲染引擎

### 4.1 HTML 整体结构

`references/template.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{TITLE}}</title>
  <style>
    /* === 基础重置 === */
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { overflow: hidden; background: #000; }

    /* === 幻灯片容器 === */
    #presentation {
      width: 100vw; height: 100vh;
      display: flex; align-items: center; justify-content: center;
    }

    /* === 单张幻灯片 === */
    .slide {
      position: absolute;
      width: {{SLIDE_WIDTH}}px;
      height: {{SLIDE_HEIGHT}}px;
      display: none;
      flex-direction: column;
      padding: {{CONTENT_PADDING}};
      /* 主题变量覆盖 */
      background: var(--slide-bg);
      color: var(--slide-fg);
      font-family: var(--font-body);
    }
    .slide.active { display: flex; }

    /* === 缩放适配（保持宽高比） === */
    #presentation { transform-origin: center center; }

    /* === 页码 === */
    #page-counter {
      position: fixed;
      bottom: 18px; right: 24px;
      font-size: 0.75em;
      color: var(--page-counter-color, rgba(255,255,255,0.5));
      font-family: var(--font-mono, monospace);
      z-index: 100;
      user-select: none;
    }

    /* === 进度条（可选）=== */
    #progress-bar {
      position: fixed; bottom: 0; left: 0;
      height: 3px;
      background: var(--accent-color);
      transition: width 0.3s ease;
      z-index: 99;
    }

    /* === 主题样式 === */
    {{THEME_CSS}}

    /* === 布局系统 === */
    {{LAYOUT_CSS}}
  </style>
  <!-- highlight.js（代码高亮）-->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11/styles/{{HIGHLIGHT_THEME}}.min.css">
</head>
<body>

<div id="presentation">
  {{SLIDES_HTML}}
</div>

<div id="page-counter">
  <span id="cur-page">1</span> / <span id="tot-pages">{{TOTAL}}</span>
</div>
<div id="progress-bar" style="width: {{FIRST_PROGRESS}}%"></div>

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<!-- highlight.js -->
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11/lib/core.min.js"></script>

<script>
// === 幻灯片核心逻辑 ===
{{SLIDE_JS}}

// === 图表初始化 ===
{{CHARTS_JS}}

// === 代码高亮初始化 ===
document.querySelectorAll('pre code').forEach(el => hljs.highlightElement(el));
</script>
</body>
</html>
```

### 4.2 幻灯片核心 JS

`SLIDE_JS` 占位符内容（由 `convert.py` 直接嵌入）：

```javascript
const slides = document.querySelectorAll('.slide');
const total = slides.length;
let current = 0;

document.getElementById('tot-pages').textContent = total;

function goTo(n) {
  if (n < 0 || n >= total) return;
  slides[current].classList.remove('active');
  current = n;
  slides[current].classList.add('active');
  document.getElementById('cur-page').textContent = current + 1;
  document.getElementById('progress-bar').style.width =
    ((current + 1) / total * 100) + '%';
}

function nextSlide() { goTo(current + 1); }
function prevSlide() { goTo(current - 1); }

document.addEventListener('keydown', (e) => {
  const next = ['ArrowRight', 'ArrowDown', ' ', 'PageDown', 'Enter'];
  const prev = ['ArrowLeft', 'ArrowUp', 'PageUp'];
  if (next.includes(e.key)) { e.preventDefault(); nextSlide(); }
  else if (prev.includes(e.key)) { e.preventDefault(); prevSlide(); }
});

// 触摸滑动支持
let touchStartX = 0;
document.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; });
document.addEventListener('touchend', e => {
  const dx = e.changedTouches[0].clientX - touchStartX;
  if (Math.abs(dx) > 50) { dx < 0 ? nextSlide() : prevSlide(); }
});

// 视口缩放适配
function scalePresentation() {
  const slideW = {{SLIDE_WIDTH}}, slideH = {{SLIDE_HEIGHT}};
  const scaleX = window.innerWidth / slideW;
  const scaleY = window.innerHeight / slideH;
  const scale = Math.min(scaleX, scaleY);
  document.getElementById('presentation').style.transform = `scale(${scale})`;
}
window.addEventListener('resize', scalePresentation);
scalePresentation();

// 初始化第一页
goTo(0);
```

### 4.3 幻灯片 HTML 结构

每张幻灯片生成的 HTML 结构（以数据页为例）：

```html
<!-- 普通内容页 -->
<div class="slide" id="slide-3" data-index="3" data-type="content">
  <div class="slide-content">
    <h1 id="s3-title">年度概览</h1>
    <ul id="s3-list1">
      <li>注册用户突破 100 万</li>
      <li>月活跃用户 32 万</li>
    </ul>
  </div>
</div>

<!-- 数据页：position=right -->
<div class="slide" id="slide-4" data-index="4" data-type="data">
  <div class="slide-content">
    <h1 id="s4-title">季度用户增长</h1>
    <div class="layout-split">
      <div class="text-panel" id="s4-text-panel">
        <ul id="s4-list1">
          <li>Q4 月活首次突破 30 万</li>
          <li>增长主要来自渠道投放</li>
        </ul>
      </div>
      <div class="chart-panel" id="s4-chart-panel" style="width:58%;height:70%;">
        <p class="chart-title" id="s4-chart1-title">月活跃用户趋势（万人）</p>
        <canvas id="s4-chart1"></canvas>
      </div>
    </div>
  </div>
</div>
```

### 4.4 布局系统 CSS

`LAYOUT_CSS` 定义（由 `convert.py` 嵌入）：

```css
/* === 通用幻灯片内容区 === */
.slide-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0.5em 0;
  gap: 0.6em;
  overflow: hidden;
}

/* === 分割布局（left/right）=== */
.layout-split {
  flex: 1;
  display: flex;
  flex-direction: row;
  gap: 3%;
  align-items: center;
}
.text-panel  { display: flex; flex-direction: column; gap: 0.5em; }
.chart-panel { display: flex; flex-direction: column; align-items: center; }
.chart-panel canvas { flex: 1; width: 100%; }
.chart-title { font-size: 0.75em; text-align: center; opacity: 0.7; margin-bottom: 0.3em; }

/* === 全图布局（full）=== */
.layout-full-chart {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.layout-full-chart canvas { flex: 1; width: 90%; max-height: 75%; }

/* === 堆叠布局（center/bottom）=== */
.layout-stacked {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5em;
}

/* === 封面专属 === */
.slide[data-type="cover"] .slide-content {
  justify-content: center;
  align-items: center;
  text-align: center;
}

/* === 列表样式 === */
.slide ul, .slide ol {
  padding-left: 1.4em;
  line-height: 1.8;
}
.slide li { margin-bottom: 0.2em; }

/* === 代码块 === */
.slide pre {
  border-radius: 6px;
  padding: 0.8em 1em;
  font-size: 0.8em;
  overflow-x: auto;
  background: var(--code-bg);
}

/* === 数据表格 === */
.slide table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.82em;
}
.slide th, .slide td {
  padding: 0.4em 0.8em;
  border: 1px solid var(--table-border);
  text-align: center;
}
.slide th { background: var(--table-header-bg); font-weight: 600; }
.slide tr:nth-child(even) { background: var(--table-row-even-bg); }
```

### 4.5 视口缩放机制

幻灯片以固定像素尺寸（1280×720 或 1024×768）设计，通过 CSS `transform: scale()` 适配任意屏幕：

```javascript
function scalePresentation() {
  const slideW = 1280;  // 16:9 示例
  const slideH = 720;
  const scaleX = window.innerWidth / slideW;
  const scaleY = window.innerHeight / slideH;
  const scale = Math.min(scaleX, scaleY);  // 保持宽高比，不裁切
  document.getElementById('presentation').style.transform = `scale(${scale})`;
}
```

这确保：
- 字体大小单位用 `em`（相对于幻灯片基准字体），不受屏幕尺寸影响
- PDF 导出时以原始像素尺寸渲染，确保清晰度

---

## 5. 主题系统设计

### 5.1 CSS 变量体系

所有主题通过覆盖同一套 CSS 变量实现，`template.html` 中的 `{{THEME_CSS}}` 占位符替换为对应主题的变量定义。

**完整变量列表**：

```css
:root {
  /* 背景与前景 */
  --slide-bg: ;          /* 幻灯片背景（纯色/渐变/图片） */
  --slide-fg: ;          /* 主文字颜色 */
  --slide-fg-dim: ;      /* 次要文字颜色 */

  /* 标题 */
  --heading-color: ;     /* 标题颜色 */
  --heading-underline: ; /* 标题下划线颜色（none 表示无） */

  /* 强调色 */
  --accent-color: ;      /* 进度条、链接、高亮 */

  /* 字体 */
  --font-body: ;         /* 正文字体栈 */
  --font-heading: ;      /* 标题字体栈 */
  --font-mono: ;         /* 等宽字体 */
  --font-size-base: ;    /* 基准字号（通常 20-24px） */

  /* 代码块 */
  --code-bg: ;

  /* 表格 */
  --table-border: ;
  --table-header-bg: ;
  --table-row-even-bg: ;

  /* 页码 */
  --page-counter-color: ;

  /* 覆盖层（fullbleed/cover-image-bg 使用） */
  --overlay-text-color: ;  /* 覆盖层上的文字色 */
  --overlay-mask-bg: ;     /* 覆盖层遮罩色 */

  /* 高亮 */
  --highlight-text-color: ; /* mark.hl 文字色（与 accent-color 对比） */

  /* 图表配色数组（用于 Chart.js）*/
  /* 通过 JS 变量传递，非 CSS 变量 */
}
```

### 5.2 九套主题定义

#### professional-dark（商务汇报/客户演示）

- 背景：深蓝渐变，前景白色，蓝色强调
- 装饰：左侧蓝色竖条 + 右上角光晕
- `CHART_COLORS: ["#4a90d9","#50c8a8","#f5a623","#e74c3c","#9b59b6","#1abc9c"]`

#### professional-light（正式文档/打印版）

- 背景：纯白，深灰文字，蓝色强调
- 装饰：顶部全宽渐变色带 + 右下角点阵
- `CHART_COLORS: ["#2980b9","#27ae60","#f39c12","#e74c3c","#8e44ad","#16a085"]`

#### keynote-white（产品发布/All-hands/对外演讲）

- 背景：纯白，苹果字色 #1d1d1f，苹果蓝 #0071e3 强调
- 装饰：顶部左对齐短横线（38% 宽）
- `CHART_COLORS: ["#0071e3","#34c759","#ff9500","#ff3b30","#af52de","#5ac8fa"]`

#### tech-terminal（工程师技术分享/架构评审）

- 背景：近黑 #0d1117，亮绿 #3fb950 强调，等宽字体标题
- 装饰：左侧绿色竖条 + 右上角半透明二进制字符水印
- `CHART_COLORS: ["#3fb950","#58a6ff","#e3b341","#f85149","#bc8cff","#39d353"]`

#### celebration（年会/颁奖/纪念日/节日祝贺）

- 背景：深金渐变，金黄 #f5c842 强调
- 装饰：右上角大金色光晕 + 底部金色渐变横线
- `CHART_COLORS: ["#f5c842","#e8a030","#ff6b35","#c8e85a","#f5a0c8","#80d4ff"]`

#### caring-green（员工关怀/团建/企业文化）

- 背景：极浅薄荷绿 #f0f7f4，沉绿 #2d7a52 强调
- 装饰：左侧柔和绿竖线 + 右下角有机圆圈组
- `CHART_COLORS: ["#2d7a52","#5aad7a","#8bc8a0","#1a5c3a","#4aaa70","#3d9060"]`

#### creative-gradient（AI 展示/创意提案/产品介绍）

- 背景：紫蓝渐变，白色文字，金色 #ffd700 强调
- 装饰：左上大光晕 + 右下金色光晕
- `CHART_COLORS: ["#ffd700","#ff6b6b","#74b9ff","#55efc4","#fd79a8","#a29bfe"]`

#### minimal-clean（极简风/内部分享/设计评审）

- 背景：浅灰白 #f7f7f5，深灰文字，极简无彩色强调
- 装饰：顶部极细��线 + 右侧极细竖线
- `CHART_COLORS: ["#333333","#888888","#555555","#aaaaaa","#222222","#666666"]`

#### warm-earth（企业历史/品牌故事/文化宣讲）

- 背景：米黄 #fdf6e3，深棕文字，棕橙 #c17f3b 强调，衬线字体
- 装饰：顶部宽横条 + 右下角有机圆圈组
- `CHART_COLORS: ["#c17f3b","#8b5e3c","#e8a25c","#5b8c5a","#c17f3b","#7a4a2e"]`

### 5.3 标题样式规范

各主题的标题在模板中统一定义，通过变量驱动：

```css
.slide h1 {
  font-family: var(--font-heading);
  font-size: 1.9em;
  color: var(--heading-color);
  line-height: 1.25;
  border-bottom: var(--heading-underline);
  padding-bottom: 0.25em;
  margin-bottom: 0.5em;
}
.slide h2 {
  font-family: var(--font-heading);
  font-size: 1.1em;
  color: var(--slide-fg-dim);
  font-weight: 400;
  margin-top: -0.3em;
}
.slide h3 {
  font-size: 1em;
  color: var(--heading-color);
  font-weight: 600;
}
```

---

## 6. 图表渲染设计

### 6.1 Chart.js 配置生成

`convert.py` 读取 CSV 后，将数据内联为 JS 并生成 Chart.js 配置对象。

#### 6.1.1 基础配置生成逻辑

```python
def build_chart_config(chart_params, csv_data, theme_colors):
    """
    chart_params: dict，来自 MD 中的 <!-- chart --> 块
    csv_data:     list[dict]，从 CSV 读取的数据
    theme_colors: list[str]，当前主题的图表配色数组
    返回: dict，Chart.js 配置对象
    """
    chart_type = chart_params['type']
    x_field = chart_params['xField']
    y_fields = [f.strip() for f in chart_params['yField'].split(',')]
    labels = [row[x_field] for row in csv_data]

    # 图表类型映射到 Chart.js type
    CHARTJS_TYPE_MAP = {
        'bar':             'bar',
        'bar-horizontal':  'bar',   # + indexAxis: 'y'
        'line':            'line',
        'area':            'line',  # + fill: true
        'pie':             'pie',
        'donut':           'doughnut',
        'scatter':         'scatter',
        'table':           None,    # 不用 Chart.js，用 HTML table
    }

    datasets = []
    for i, yf in enumerate(y_fields):
        values = [float(row[yf]) for row in csv_data]
        ds = {
            'label': yf,
            'data': values,
            'backgroundColor': theme_colors[i % len(theme_colors)],
        }
        if chart_type in ('line', 'area'):
            ds['borderColor'] = theme_colors[i % len(theme_colors)]
            ds['backgroundColor'] = hex_to_rgba(theme_colors[i], 0.2)
            ds['tension'] = 0.4
            ds['borderWidth'] = 2
            ds['pointRadius'] = 4
            if chart_type == 'area':
                ds['fill'] = True
        elif chart_type in ('pie', 'donut'):
            ds['backgroundColor'] = theme_colors[:len(values)]

        datasets.append(ds)

    config = {
        'type': CHARTJS_TYPE_MAP[chart_type],
        'data': { 'labels': labels, 'datasets': datasets },
        'options': build_chart_options(chart_params, chart_type)
    }

    if chart_type == 'bar-horizontal':
        config['options']['indexAxis'] = 'y'

    return config
```

#### 6.1.2 Chart.js 选项配置

```python
def build_chart_options(chart_params, chart_type):
    is_dark = False  # 由主题决定，深色主题文字用白色

    opts = {
        'responsive': True,
        'maintainAspectRatio': False,
        'animation': { 'duration': 0 },  # PDF 导出时禁用动画
        'plugins': {
            'legend': {
                'display': chart_params.get('legend', True),
                'labels': { 'color': 'var(--slide-fg)' }
            },
            'title': { 'display': False }  # 标题用 HTML 元素，不用 Chart.js 内置
        }
    }

    if chart_type not in ('pie', 'donut'):
        opts['scales'] = {
            'x': {
                'ticks': { 'color': 'var(--slide-fg-dim)' },
                'grid':  { 'color': 'rgba(128,128,128,0.15)' }
            },
            'y': {
                'ticks': { 'color': 'var(--slide-fg-dim)' },
                'grid':  { 'color': 'rgba(128,128,128,0.15)' }
            }
        }

    return opts
```

#### 6.1.3 生成的 JS 代码示例

```javascript
// s4-chart1: bar chart
(function() {
  const labels = ["Q1","Q2","Q3","Q4"];
  const datasets = [{
    label: "月活(万)",
    data: [18.2, 22.5, 27.8, 32.1],
    backgroundColor: "#4a90d9",
    borderColor: "#4a90d9",
    tension: 0.4,
    borderWidth: 2,
    pointRadius: 4
  }];
  new Chart(document.getElementById('s4-chart1'), {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 0 },
      plugins: { legend: { display: true, labels: { color: '#9ab0cc' } } },
      scales: {
        x: { ticks: { color: '#9ab0cc' }, grid: { color: 'rgba(128,128,128,0.15)' } },
        y: { ticks: { color: '#9ab0cc' }, grid: { color: 'rgba(128,128,128,0.15)' } }
      }
    }
  });
})();
```

### 6.2 数据表格渲染（type: table）

当 `type: table` 时，不使用 Canvas，直接生成 HTML 表格：

```python
def render_data_table(chart_params, csv_data):
    headers = list(csv_data[0].keys())
    rows = [[row[h] for h in headers] for row in csv_data]

    html = f'<table id="{chart_params["id"]}">\n'
    html += '<thead><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead>\n'
    html += '<tbody>\n'
    for row in rows:
        html += '<tr>' + ''.join(f'<td>{v}</td>' for v in row) + '</tr>\n'
    html += '</tbody></table>'
    return html
```

### 6.3 图表配色方案

`references/chart-defaults.json` 中存储各主题的图表配色：

```json
{
  "professional-dark": {
    "colors": ["#4a90d9","#50c8a8","#f5a623","#e74c3c","#9b59b6","#1abc9c"],
    "gridColor": "rgba(255,255,255,0.1)",
    "textColor": "#9ab0cc"
  },
  "professional-light": {
    "colors": ["#2980b9","#27ae60","#f39c12","#e74c3c","#8e44ad","#16a085"],
    "gridColor": "rgba(0,0,0,0.08)",
    "textColor": "#7f8c8d"
  },
  "creative-gradient": {
    "colors": ["#ffd700","#ff6b6b","#74b9ff","#55efc4","#fd79a8","#a29bfe"],
    "gridColor": "rgba(255,255,255,0.15)",
    "textColor": "rgba(255,255,255,0.75)"
  },
  "minimal-clean": {
    "colors": ["#333333","#888888","#555555","#aaaaaa","#222222","#666666"],
    "gridColor": "rgba(0,0,0,0.06)",
    "textColor": "#888888"
  },
  "warm-earth": {
    "colors": ["#c17f3b","#8b5e3c","#e8a25c","#5b8c5a","#c17f3b","#7a4a2e"],
    "gridColor": "rgba(59,42,26,0.1)",
    "textColor": "#7a5c3e"
  }
}
```

---

## 7. 脚本模块设计

### 7.1 `convert.py`

**职责**：将 MD 文件转换为 HTML 演示文稿，并生成元素树 JSON。

**接口**：

```bash
python scripts/convert.py \
  --input <md_file>          # 必填
  --output <html_file>       # 可选，默认同名 .html
  --tree <json_file>         # 可选，默认 slide-tree.json
  --ratio "16:9"|"4:3"       # 可选，frontmatter 优先
  --theme <theme_name>       # 可选，frontmatter 优先
```

**处理流程**：

```
1. 读取 MD 文件（UTF-8）
2. 解析 frontmatter（python-frontmatter）
3. 确定 ratio 和 theme（参数 > frontmatter > 默认值）
4. 按 --- 分割为页面列表
5. 对每个页面：
   a. 解析 <!-- Slide N: ... --> 注释（提取页码和类型注释）
   b. 解析 <!-- chart ... --> 块（提取图表参数）
   c. 将剩余 MD 转换为 HTML（markdown 库）
   d. 读取对应 CSV 文件（如有图表）
   e. 生成 Chart.js 配置（build_chart_config）
   f. 根据 position 确定布局模板
   g. 生成该页的 HTML 片段
   h. 生成该页的元素树节点
6. 读取主题 CSS（references/themes/{theme}.css）
7. 填充 HTML 模板变量（TITLE, SLIDE_WIDTH, THEME_CSS 等）
8. 拼接所有 CHARTS_JS
9. 写入 HTML 文件
10. 写入元素树 JSON
```

**关键函数签名**：

```python
def parse_md(filepath: str) -> tuple[dict, list[str]]:
    """返回 (frontmatter, slides列表)"""

def parse_chart_block(comment_text: str) -> dict:
    """解析 <!-- chart ... --> 内容为参数字典"""

def read_csv(filepath: str) -> list[dict]:
    """读取 CSV，返回行列表（dict 格式）"""

def render_slide(index: int, md_content: str, chart_params: dict | None,
                 theme: str, slide_size: tuple) -> tuple[str, dict]:
    """返回 (html_fragment, tree_node)"""

def generate_html(slides_html: str, charts_js: str, meta: dict,
                  theme_css: str) -> str:
    """填充模板，返回完整 HTML 字符串"""

def build_element_tree(slides: list[dict], meta: dict) -> dict:
    """构建完整元素树 JSON"""

def merge_preserved_styles(new_tree: dict, old_tree: dict) -> tuple[dict, list[str]]:
    """
    将旧树中已定制的 style 字段合并回新树。
    返回 (merged_tree, lost_ids)：
      merged_tree -- 已合并样式的新树
      lost_ids    -- 旧树有自定义样式但新树中不存在的元素 ID 列表
    仅在 --preserve-styles 模式下调用。
    """
```

### 7.2 `extract_data.py`

**职责**：辅助脚本，从文本材料中提取数据表格并保存为 CSV。主要由 AI 在策划阶段使用。

**接口**：

```bash
python scripts/extract_data.py \
  --input <text_or_md_file>
  --output-dir data/
  --prefix report
```

**处理逻辑**：

```python
def extract_tables_from_text(text: str) -> list[dict]:
    """
    识别以下模式：
    1. Markdown 表格（| col | col |）
    2. 对齐数字列表（"Q1: 120万，Q2: 145万"）
    3. 简单 CSV 嵌入
    返回: [{"headers": [...], "rows": [[...], ...]}, ...]
    """

def save_as_csv(table: dict, filepath: str):
    """写入 CSV，UTF-8 无 BOM"""
```

> 注：此脚本主要作为 AI 的辅助工具，AI 在策划阶段可以直接创建 CSV 文件，无需强制调用此脚本。

### 7.3 `html2pdf.py`

详见第 8 节。

---

## 8. PDF 转换设计

### 8.1 技术方案

使用 `playwright` Python 包驱动 Chromium 渲染 HTML（含 JS 图表），截取每张幻灯片为 PDF 页面。

### 8.2 接口

```bash
python scripts/html2pdf.py \
  --input <html_file>        # 必填
  --output <pdf_file>        # 可选，默认同名 .pdf
  --wait 1000                # 等待 JS 渲染完成的毫秒数，默认 1000
```

### 8.3 实现逻辑

```python
from playwright.sync_api import sync_playwright
import json, os

def html_to_pdf(html_path: str, pdf_path: str, wait_ms: int = 1000):
    html_abs = os.path.abspath(html_path)

    # 从同目录的 slide-tree.json 读取幻灯片信息
    tree_path = os.path.join(os.path.dirname(html_abs), 'slide-tree.json')
    with open(tree_path, encoding='utf-8') as f:
        tree = json.load(f)

    ratio = tree['presentation']['ratio']
    total = tree['presentation']['totalSlides']

    # 页面尺寸
    if ratio == '16:9':
        width, height = 1280, 720
    else:
        width, height = 1024, 768

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': width, 'height': height})
        page.goto(f'file://{html_abs}')
        page.wait_for_timeout(wait_ms)  # 等待 Chart.js 渲染

        pdf_pages = []
        for i in range(total):
            # 跳转到第 i 页
            page.evaluate(f'goTo({i})')
            page.wait_for_timeout(100)

            # 截图为 PDF 页（通过打印模式）
            # 使用单页 PDF 后合并
            single_pdf = page.pdf(
                width=f'{width}px',
                height=f'{height}px',
                print_background=True,
                margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'}
            )
            pdf_pages.append(single_pdf)

        browser.close()

    # 合并 PDF 页面
    merge_pdfs(pdf_pages, pdf_path)
    print(f'PDF 已生成：{pdf_path}（{total} 页，{width}×{height}px）')
```

### 8.4 PDF 合并

使用 `pypdf` 合并多个单页 PDF：

```python
from pypdf import PdfWriter
import io

def merge_pdfs(pdf_bytes_list: list[bytes], output_path: str):
    writer = PdfWriter()
    for pdf_bytes in pdf_bytes_list:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            writer.add_page(page)
    with open(output_path, 'wb') as f:
        writer.write(f)
```

**依赖补充**：

```
pypdf>=4.0.0   # PDF 合并
```

### 8.5 降级方案

若 playwright 不可用，提示用户：

```
playwright 未安装，请选择备选方案：

方案 A（推荐）：安装 playwright
  pip install playwright pypdf
  playwright install chromium

方案 B：浏览器手动导出
  1. 用 Chrome/Edge 打开 HTML 文件
  2. 按 Ctrl+P（打印）
  3. 打印机选择"另存为 PDF"
  4. 更多设置 → 纸张大小选 16:9 对应尺寸
  注：手动导出可能导致图表未完全渲染

方案 C：wkhtmltopdf（不支持 JS，图表将缺失）
  wkhtmltopdf --page-width 1280px --page-height 720px input.html output.pdf
```

---

## 9. 元素树设计

### 9.1 元素树的生命周期

```
生成时：  convert.py 创建 slide-tree.json
         ↓
样式调整：AI 读取树 → 直接修改 HTML → 更新树 → 保存
         ↓
内容变更：AI 修改 .md → convert.py --preserve-styles
            → 读取旧树中的 style 字段
            → 生成新树并合并旧样式
            → 覆盖 HTML 和 slide-tree.json
         ↓
查询时：  AI 读取树 → 向用户展示结构摘要
         ↓
PDF 时：  html2pdf.py 读取树（获取总页数和尺寸）
```

### 9.2 元素树操作规范

#### 读取树（定位元素）

```python
def find_element(tree: dict, slide_index: int, element_id: str = None,
                 element_type: str = None) -> dict | None:
    """
    按页码 + ID 或 类型 定位元素
    slide_index: 1-based
    """
    slides = tree['presentation']['slides']
    slide = next((s for s in slides if s['index'] == slide_index), None)
    if not slide:
        return None
    if element_id:
        return next((e for e in slide['elements'] if e['id'] == element_id), None)
    if element_type:
        return next((e for e in slide['elements'] if e['type'] == element_type), None)
    return None
```

#### 更新树节点

```python
def update_element_style(tree: dict, element_id: str, style_updates: dict) -> dict:
    """更新指定元素的 style 字段，返回更新后的树"""
    for slide in tree['presentation']['slides']:
        for element in slide['elements']:
            if element['id'] == element_id:
                if 'style' not in element:
                    element['style'] = {}
                element['style'].update(style_updates)
                return tree
    raise ValueError(f'Element {element_id} not found')
```

### 9.3 AI 调整时的操作流程

AI 收到调整指令后执行：

```
1. 读取 slide-tree.json（Read 工具）
2. 定位目标元素（按页码 + 描述）
3. 计算新的属性值
4. 修改 HTML 文件中的对应元素（Edit 工具）
   - 找到 id="s{N}-{type}{N}" 的元素
   - 修改其 style 属性或 Chart.js 配置
5. 更新 slide-tree.json（Edit 工具）
6. 向用户确认：已修改 {element_id} 的 {属性} 从 {旧值} 改为 {新值}
```

**HTML 元素定位规则**：

| 元素类型 | HTML 中的定位 |
|---------|-------------|
| h1/h2/p | `<h1 id="s3-title">` → `style="..."` |
| ul/ol | `<ul id="s3-list1">` → 修改父容器或 li 的样式 |
| img | `<img id="s3-img1">` → style width/height |
| chart | `<canvas id="s4-chart1">` 的父容器 + `<script>` 中的配置对象 |
| 页面背景 | `<div id="slide-3" class="slide">` 的 style |

---

## 10. 错误处理策略

### 10.1 常见错误与处理

| 错误场景 | 检测时机 | 处理方式 |
|---------|---------|---------|
| CSV 文件不存在 | convert.py 运行时 | 报错说明缺失的文件路径，跳过该图表，用占位文字替代 |
| CSV 字段名不匹配 | convert.py 解析时 | 列出实际字段名，提示用户修正 MD 中的 xField/yField |
| CSV 数值解析失败 | convert.py 读取时 | 跳过非数值行，警告哪些行被忽略 |
| 主题文件不存在 | convert.py 启动时 | 回退到 professional-dark，警告用户 |
| playwright 未安装 | html2pdf.py 启动时 | 提示安装命令或降级方案（见 8.5） |
| HTML 文件过大 | html2pdf.py 转换时 | 正常处理，转换时间较长时显示进度 |
| 图片路径无效 | convert.py 处理时 | 用占位符替代，警告哪些图片路径无效 |

### 10.2 警告输出规范

所有脚本的警告/错误统一输出格式：

```
[WARNING] convert.py: CSV 字段 "月活(万)" 在 data/report-s4-users.csv 中不存在
          实际字段：季度, 月活用户数(万), 新增用户(万)
          请修正 MD 文件中 slide 4 的 yField 参数

[ERROR]   convert.py: 主题文件 references/themes/my-theme.css 不存在
          已回退到默认主题 professional-dark
```

---

## 11. 文件组织与命名规范

### 11.1 完整目录结构

```
md2slides/
├── SKILL.md                    # Skill 入口（待创建）
│
├── scripts/
│   ├── convert.py              # MD → HTML 主脚本
│   ├── html2pdf.py             # HTML → PDF 脚本
│   └── extract_data.py         # 数据提取辅助脚本
│
├── references/
│   ├── template.html           # HTML 骨架模板
│   ├── themes/
│   │   ├── professional-dark.css
│   │   ├── professional-light.css
│   │   ├── keynote-white.css
│   │   ├── tech-terminal.css
│   │   ├── celebration.css
│   │   ├── caring-green.css
│   │   ├── creative-gradient.css
│   │   ├── minimal-clean.css
│   │   └── warm-earth.css
│   ├── slide-schema.json       # 元素树 JSON Schema
│   └── chart-defaults.json     # 图表默认配置
│
├── docs/
│   ├── README.md               # 文档导航
│   ├── requirements.md         # 需求文档（L1）
│   └── design.md               # 本文档（L2）
│
└── examples/
    ├── sample.md               # 示例输入 MD
    ├── sample.html             # 示例输出 HTML
    └── data/
        └── sample-s4-revenue.csv
```

### 11.2 输出文件命名规范

| 文件类型 | 命名规则 | 示例 |
|---------|---------|------|
| HTML 演示文稿 | `{原始文件名}.html` | `report.html` |
| 元素树 | `{原始文件名}-tree.json` | `report-tree.json` |
| PDF 输出 | `{原始文件名}.pdf` | `report.pdf` |
| 数据 CSV | `data/{文件名}-s{页码}-{描述}.csv` | `data/report-s4-revenue.csv` |

所有输出文件与输入 MD 文件在**同一目录**，`data/` 子目录在该位置创建。

### 11.3 元素 ID 完整命名规则

格式：`s{页码}-{元素类型}{该页内序号}`

| 元素 | 命名示例 |
|------|---------|
| H1 标题 | `s1-title`（每页只有一个 H1，不加序号） |
| H2 副标题 | `s1-subtitle` |
| H3 小标题 | `s3-h31`, `s3-h32` |
| 段落 | `s3-p1`, `s3-p2` |
| 无序列表 | `s3-list1`, `s3-list2` |
| 有序列表 | `s3-olist1` |
| 图片 | `s3-img1` |
| 代码块 | `s3-code1` |
| 数据表格（HTML） | `s5-table1` |
| 图表（Canvas） | `s4-chart1`, `s4-chart2` |
| 图表标题文字 | `s4-chart1-title` |
| 图表文字区 | `s4-text-panel` |
| 图表画布区 | `s4-chart-panel` |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-03-24 | 初稿，基于 requirements.md v0.3 完整设计 |
| v1.1 | 2026-03-24 | 新增内容变更工作流（§2.3.0、§2.4）、路由判断逻辑、样式保留合并机制、convert.py --preserve-styles 接口 |
| v1.2 | 2026-03-25 | 重构为三阶段工作流；27种版式；版式规划阶段；section-header双变体；splitMode=group；stat-cards columns；card-grid；:::col预处理；rawHtml；preview.py；浏览器自动检测；PDF黑边修复 |
