# md2slides 需求文档

> 文档层级：L1 系统级
> 版本：v0.5 | 创建日期：2026-03-23 | 更新日期：2026-03-25

## 1. 项目背景

用户经常需要将原始材料或文档转化为可演示的幻灯片。现有方案（如 Obsidian Slides、Marp）要求用户手动添加分页符和样式，门槛较高。md2slides skill 旨在让 AI 辅助完成从原始材料到演示文稿的两阶段转换，并支持后续元素级的精细调整。

## 2. 核心工作流

### 2.1 两阶段生成

```
阶段一：内容策划（AI 对话）
  用户提供原始材料/文档
    → AI 分析内容，规划演示结构
    → 识别数据内容 → 提取数据 → 保存为 CSV
    → 生成 MD 格式演示稿（明确分页、每页内容、图表块）
    → 用户确认或修改 MD 内容

阶段二：版式规划（AI 对话）
  用户确认 MD 内容
    → AI 逐页分析内容密度与元素构成
    → 从 27 种版式模板中为每页选定最佳版式
    → 将版式决策写入 slide-tree.json 的 layout 字段
    → 向用户展示版式摘要，等待确认

阶段三：HTML 生成（脚本）
  用户确认版式方案
    → 运行 convert.py（MD + slide-tree.json → HTML）
    → 输出自包含 HTML + 更新 slide-tree.json
```

### 2.2 后续调整（样式）

```
样式调整
  用户指定某页或某元素的视觉属性
    → AI 定位树形结构中的对应节点
    → 直接修改 HTML 文件中的 style 属性
    → 同步更新树形结构数据
    （不修改 MD 文件，不重新生成）
```

### 2.3 内容变更

```
内容变更
  用户描述对演示文稿内容的修改意图
    → AI 判断属于内容变更（见 §3.6 判断标准）
    → AI 更新 MD 文件（修改文字/增删页面/调整图表参数）
    → 重新运行 convert.py（--preserve-styles 模式）
        读取旧元素树中已定制的 style 字段
        将旧样式合并回新生成的对应元素上
    → 覆盖输出 HTML 文件和元素树
    → 告知用户变更摘要及样式保留情况
```

**内容变更 vs 样式调整的选择规则**：

| 操作类型            | 路径   | 是否修改 MD |
| --------------- | ---- | ------- |
| 修改文字内容（要点措辞、标题） | 内容变更 | ✅       |
| 增减列表条目          | 内容变更 | ✅       |
| 增加/删除/移动页面      | 内容变更 | ✅       |
| 修改图表类型、数据源、字段   | 内容变更 | ✅       |
| 修改字体大小/颜色/粗细    | 样式调整 | ❌       |
| 修改间距/对齐/背景色     | 样式调整 | ❌       |
| 修改图表位置/宽高比例     | 样式调整 | ❌       |

## 3. 功能需求

### 3.1 阶段一：MD 内容策划

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 内容分析 | 理解用户提供的原始材料，提炼演示要点 | P0 |
| 结构规划 | 规划封面页、目录页、内容页、结尾页等结构 | P0 |
| MD 分页生成 | 用 `---` 明确分隔每一页，每页包含标题和内容 | P0 |
| 内容精简 | 将大段文字提炼为适合演示的要点格式 | P0 |
| 分页预览 | 生成 MD 后向用户展示页数和每页标题摘要 | P1 |

**MD 分页格式规范**：

```markdown
---
title: 演示文稿标题
ratio: 16:9
theme: professional-dark
---

<!-- Slide 1: 封面 -->
# 演示标题
## 副标题

---

<!-- Slide 2: 目录 -->
# 目录
- 第一章：背景
- 第二章：方案
- 第三章：总结

---

<!-- Slide 3: 内容页 -->
# 背景
- 要点一
- 要点二
- 要点三
```

### 3.2 阶段二：HTML 生成

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 宽高比确认 | 必须让用户明确选择 16:9 或 4:3 | P0 |
| 样式风格选择 | 根据内容特点或用户要求选择配色方案 | P0 |
| HTML 生成 | 将 MD 转换为完整的单文件 HTML 演示文稿 | P0 |
| 键盘导航 | 支持左右方向键和空格键翻页 | P0 |
| 页码显示 | 右下角显示当前页/总页数（如 3 / 12） | P0 |
| 元素树输出 | 生成后输出每页的元素树形结构数据 | P0 |
| 单文件输出 | 生成自包含的单个 HTML 文件，可离线使用 | P1 |
| 过渡动画 | 支持幻灯片切换动画（fade/slide/zoom 等） | P1 |
| 代码高亮 | 代码块保留语法高亮 | P1 |
| 演讲者注释 | 支持 `Note:` 语法转换为演讲者注释 | P2 |

**宽高比对应尺寸**：

| 比例 | 宽 × 高 | 使用场景 |
|------|---------|---------|
| 16:9 | 1280 × 720 | 现代显示器、投影仪（推荐） |
| 4:3  | 1024 × 768 | 传统投影仪、老式显示器 |

**样式风格预设**

| 风格名称 | 配色描述 | 适用场景 |
|---------|---------|---------|
| professional-dark | 深色背景，蓝白文字 | 技术/商业汇报 |
| professional-light | 白色背景，深灰文字 | 学术/正式场合 |
| creative-gradient | 渐变背景，活泼配色 | 创意/产品介绍 |
| minimal-clean | 极简白底，细线分割 | 设计/简报 |
| warm-earth | 暖色调，米白棕色 | 人文/教育 |

### 3.3 数据可视化

#### 3.3.1 数据提取与存储

当原始材料中包含数据内容（表格、统计数字、对比数据、趋势数据等）时，AI 需在策划阶段提取数据并持久化保存，不直接将原始数据硬编码进 HTML。

**支持的存储格式**：

| 格式 | 适用场景 | 文件扩展名 |
|------|---------|-----------|
| CSV | 通用数据，结构化表格，兼容性最好 | `.csv` |
| Obsidian Dataview | 已有 Obsidian 知识库，需与笔记联动 | `.md`（含 dataview 代码块） |

**默认使用 CSV**，除非用户明确要求 Obsidian Dataview 格式。

**CSV 文件命名规则**：`data/{演示文稿名}-s{页码}-{数据描述}.csv`

示例：`data/report-s4-revenue.csv`

```csv
季度,收入(万元),增长率(%)
Q1,120,—
Q2,145,20.8
Q3,168,15.9
Q4,203,20.8
```

**Obsidian Dataview 格式**（备选）：

```markdown
```dataview
table 季度, 收入, 增长率
from "data/report"
where type = "revenue"
` ``
```

#### 3.3.2 MD 策划阶段的图表标注

在 MD 内容策划阶段，含数据的页面必须用特定注释块标注图表参数：

```markdown
---

<!-- Slide 4: 收入增长 -->
# 季度收入增长趋势

<!-- chart
type: bar
dataSource: data/report-s4-revenue.csv
xField: 季度
yField: 收入(万元)
title: 2024年季度收入（万元）
position: right        # left | right | center | full
width: 55%
height: 70%
colorScheme: theme     # theme（跟随主题配色）| 自定义色值数组
-->

- 全年总收入 636 万元，同比增长 58%
- Q4 单季突破 200 万元
```

**图表类型（`type` 字段）**：

| 类型值 | 图表名称 | 适用数据 |
|--------|---------|---------|
| `bar` | 柱状图 | 分类对比、排名 |
| `bar-horizontal` | 条形图 | 横向对比、长标签 |
| `line` | 折线图 | 趋势、时间序列 |
| `area` | 面积图 | 趋势+量级感 |
| `pie` | 饼图 | 占比（类别 ≤ 6） |
| `donut` | 环形图 | 占比+中间显示数值 |
| `scatter` | 散点图 | 分布、相关性 |
| `table` | 数据表格 | 精确数值展示 |

**图表位置参数（`position` 字段）**：

| 值 | 含义 | 典型布局 |
|----|------|---------|
| `full` | 占满内容区 | 纯图表页 |
| `right` | 右侧（文字在左） | 图文各占约一半 |
| `left` | 左侧（文字在右） | 图文各占约一半 |
| `center` | 居中，文字在上下 | 小图 + 说明文字 |
| `bottom` | 底部（文字在上） | 标题+文字+图 |

**宽高参数**：以幻灯片内容区为基准的百分比，如 `width: 55%`、`height: 70%`。

#### 3.3.3 HTML 生成阶段的图表渲染

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 图表渲染库 | 使用 Chart.js（CDN）渲染所有图表类型 | P0 |
| 数据内联 | 将 CSV 数据读取后内联至 HTML（`<script>` 中的 JS 数组） | P0 |
| 位置布局 | 按 MD 中 position/width/height 参数生成对应 CSS 布局 | P0 |
| 主题配色 | 图表配色跟随演示文稿主题，保持视觉统一 | P0 |
| 数据表格 | `type: table` 时渲染为样式化 HTML 表格而非图表 | P1 |
| 图表标题 | 显示 `title` 字段内容，位于图表上方或下方 | P1 |
| 响应式 | 图表随幻灯片缩放自适应大小 | P1 |

**技术实现**：

```html
<!-- 图表容器示例（position: right，width: 55%） -->
<div class="slide-layout-split">
  <div class="text-panel" style="width: 42%">
    <!-- 文字内容 -->
  </div>
  <div class="chart-panel" style="width: 55%">
    <canvas id="s4-chart1"></canvas>
  </div>
</div>

<script>
new Chart(document.getElementById('s4-chart1'), {
  type: 'bar',
  data: {
    labels: ['Q1','Q2','Q3','Q4'],
    datasets: [{ label: '收入(万元)', data: [120,145,168,203] }]
  }
});
</script>
```

#### 3.3.4 图表的生成后调整

图表元素也纳入元素树，支持后续调整：

```
用户: 把第4页的柱状图改成折线图
AI: 更新 s4-chart1 type: bar → line，重新生成图表代码，同步元素树。

用户: 图表宽度改成70%，移到左边
AI: 更新 s4-chart1 width: 55% → 70%，position: right → left，调整布局，同步元素树。
```

### 3.4 元素树形结构

生成 HTML 后，以树形结构数据记录每页的元素，用于后续精准定位和修改。

**数据格式**（JSON）：

```json
{
  "presentation": {
    "ratio": "16:9",
    "theme": "professional-dark",
    "totalSlides": 8,
    "slides": [
      {
        "index": 1,
        "type": "cover",
        "comment": "封面",
        "elements": [
          {
            "id": "s1-title",
            "type": "h1",
            "content": "演示标题",
            "style": {
              "fontSize": "2.5em",
              "color": "#ffffff",
              "textAlign": "center"
            }
          },
          {
            "id": "s1-subtitle",
            "type": "h2",
            "content": "副标题",
            "style": {
              "fontSize": "1.2em",
              "color": "#aaccff"
            }
          }
        ]
      },
      {
        "index": 2,
        "type": "content",
        "comment": "目录页",
        "elements": [
          {
            "id": "s2-title",
            "type": "h1",
            "content": "目录"
          },
          {
            "id": "s2-list",
            "type": "ul",
            "items": ["第一章：背景", "第二章：方案", "第三章：总结"]
          }
        ]
      },
      {
        "index": 4,
        "type": "data",
        "comment": "收入增长趋势",
        "elements": [
          {
            "id": "s4-title",
            "type": "h1",
            "content": "季度收入增长趋势"
          },
          {
            "id": "s4-list",
            "type": "ul",
            "layout": "left",
            "style": { "width": "42%" },
            "items": ["全年总收入 636 万元", "Q4 单季突破 200 万元"]
          },
          {
            "id": "s4-chart1",
            "type": "chart",
            "layout": "right",
            "chartType": "bar",
            "dataSource": "data/report-s4-revenue.csv",
            "xField": "季度",
            "yField": "收入(万元)",
            "title": "2024年季度收入（万元）",
            "style": {
              "width": "55%",
              "height": "70%"
            },
            "colorScheme": "theme"
          }
        ]
      }
    ]
  }
}
```

**元素 ID 命名规则**：`s{页码}-{元素类型}{序号}`，如 `s3-img1`、`s3-p2`、`s4-chart1`

**元素 `type` 枚举**：`h1`、`h2`、`p`、`ul`、`ol`、`img`、`code`、`table`、`chart`

### 3.5 生成后调整

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 页面级调整 | 修改某页的整体背景色、布局方式 | P0 |
| 元素级调整 | 通过元素 ID 精准修改特定元素的属性 | P0 |
| 可调整属性 | 布局、大小、字体、颜色、间距、对齐方式等 | P0 |
| 图表调整 | 修改图表类型、数据源字段、位置、尺寸、配色 | P0 |
| 树结构同步 | 每次修改后同步更新元素树数据 | P0 |
| 批量调整 | 修改所有页面的某类元素（如统一字体） | P1 |

**调整交互示例**：

```
用户: 把第3页的标题字体改大一点，颜色改成黄色
AI: 定位到 s3-title，将 fontSize 从 2em 改为 2.5em，color 改为 #FFD700
    已更新 HTML 文件，同步更新元素树。
```

### 3.6 内容变更

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 文字内容修改 | 修改某页的标题、要点文字、段落内容，更新 MD 后重新生成 | P0 |
| 列表条目增减 | 向某页添加或删除要点，更新 MD 后重新生成 | P0 |
| 页面管理 | 增加新页、删除现有页、调整页面顺序，更新 MD 后重新生成 | P0 |
| 图表内容变更 | 修改图表类型、数据源文件、X/Y 字段，更新 MD 的 chart 块后重新生成 | P0 |
| 样式保留 | 重新生成时，自动从旧元素树中提取已定制的 style 字段，合并回新生成的对应元素 | P0 |
| 变更摘要 | 重新生成后向用户展示页面级差异（新增 N 页、修改 N 页、删除 N 页） | P1 |
| 样式丢失告知 | 当页面结构变化导致元素 ID 不再匹配时，告知用户该元素的样式已重置为主题默认值 | P1 |

**样式保留策略（策略 A）**：

重新生成时，`convert.py` 以 `--preserve-styles` 模式运行：

```
1. 生成新 HTML 和新元素树（使用主题默认样式）
2. 读取旧元素树中所有带有非默认 style 字段的元素
3. 按元素 ID 匹配：
   - ID 在新树中存在 → 将旧 style 合并覆盖到新树对应节点，并更新 HTML 内联样式
   - ID 在新树中不存在（页面被删除或 ID 变化） → 旧样式丢弃，告知用户
   - 新树中存在但旧树无记录（新增元素） → 使用主题默认样式
```

**触发条件**：凡是通过"内容变更路径"重新生成，均自动启用 `--preserve-styles`。

### 3.7 HTML 转 PDF

| 功能 | 描述 | 优先级 |
|------|------|--------|
| HTML → PDF | 将演示文稿 HTML 转换为 PDF 文件 | P0 |
| 演示文稿分页 | PDF 按幻灯片页面分页，每张幻灯片对应一页 PDF | P0 |
| 保持宽高比 | PDF 页面尺寸与演示文稿宽高比一致 | P0 |
| 工具脚本 | 提供 `scripts/html2pdf.py` 脚本执行转换 | P0 |

**PDF 转换技术方案**：

优先使用 `playwright` (Python)：
```bash
pip install playwright
playwright install chromium
python scripts/html2pdf.py input.html output.pdf
```

备选方案（如 playwright 不可用）：
- `weasyprint`：纯 Python，但对 JS 渲染支持有限
- `wkhtmltopdf`：外部命令行工具，需单独安装
- 提示用户使用浏览器打印（Ctrl+P → 另存为 PDF）

**PDF 分页实现原理**：

通过 CSS `@page` 和 `page-break-after` 确保每张幻灯片对应一页 PDF：
```css
.slide {
  page-break-after: always;
  width: 1280px;  /* 16:9 */
  height: 720px;
}
```

## 4. 用户交互流程

### 4.1 完整交互示例

```
用户: 帮我把这份产品介绍材料做成演示文稿 [附材料]

AI阶段一:
  分析材料...
  我为您规划了以下结构（共 8 页）：
  1. 封面 - 产品名称 & 口号
  2. 问题背景 - 用户痛点
  3. 解决方案概述
  4. 核心功能 ①
  5. 核心功能 ②
  6. 数据与效果
  7. 商业模式
  8. 结语 & 联系方式

  已生成 MD 文件，请确认内容后继续？

用户: 看起来不错，帮我生成 HTML

AI:
  请问您需要哪种宽高比？
  A. 16:9（推荐，适合现代投影仪）
  B. 4:3（适合传统投影仪）

用户: 16:9

AI:
  根据产品介绍的内容风格，我建议使用 creative-gradient 主题（活泼渐变，适合产品演示）。
  是否采用此主题，或您有其他偏好？

用户: 好的

AI:
  HTML 已生成：product-intro.html（8 页幻灯片）
  支持左右键 / 空格键翻页，右下角显示页码。
  [输出元素树数据...]

用户: 把封面的副标题字体改小一些，颜色改成白色

AI:
  已更新 s1-subtitle：fontSize 1.2em → 0.9em，color → #ffffff
  HTML 文件已保存。

用户: 帮我转成 PDF

AI:
  正在使用 playwright 转换...
  PDF 已生成：product-intro.pdf（8 页，每页 1280×720）
```

### 4.2 快捷路径

- 用户直接说"用默认配置"→ 跳过样式确认，使用 professional-dark + 16:9
- 用户提供 frontmatter 配置 → 跳过对应询问步骤

## 5. 技术选型

### 5.1 核心框架

| 组件 | 选型 | 理由 |
|------|------|------|
| 幻灯片框架 | 自定义 HTML/CSS/JS | 完全控制样式和元素树，不依赖 reveal.js 限制 |
| MD 解析 | Python `markdown` + `python-frontmatter` | 轻量，Python 生态 |
| 图表渲染 | Chart.js v4（CDN） | 支持所有常用图表类型，MIT 许可，无需 Node.js |
| 代码高亮 | highlight.js（CDN） | 零额外 Python 依赖 |
| PDF 转换 | `playwright` (Python) | 完整 JS 渲染，精确分页 |

> **注**：放弃 reveal.js，改用自定义实现，以获得对元素树、样式和分页的完全控制。

### 5.2 文件结构

```
scripts/
├── convert.py        # MD → HTML 转换主脚本
├── html2pdf.py       # HTML → PDF 转换脚本
├── extract_data.py   # 从原始材料提取数据 → CSV
└── adjust.py         # 元素级调整脚本（可选）

references/
├── template.html     # HTML 基础模板
├── themes/           # 样式风格 CSS 文件
│   ├── professional-dark.css
│   ├── professional-light.css
│   ├── creative-gradient.css
│   ├── minimal-clean.css
│   └── warm-earth.css
├── slide-schema.json # 元素树 JSON Schema
└── chart-defaults.json  # 各图表类型默认配置

data/                 # 提取的数据文件（运行时生成）
└── {演示文稿名}-s{页码}-{描述}.csv
```

### 5.3 依赖

```
python-frontmatter>=1.0.0
markdown>=3.5.0
playwright>=1.40.0    # PDF 转换
# Chart.js 和 highlight.js 通过 CDN 加载，无需 pip 安装
```

### 5.4 键盘导航实现

```javascript
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'ArrowDown') {
    nextSlide();
  } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    prevSlide();
  }
});
```

### 5.5 页码显示

```html
<!-- 右下角固定定位 -->
<div id="page-counter" style="
  position: fixed; bottom: 20px; right: 30px;
  font-size: 0.8em; color: rgba(255,255,255,0.6);
">
  <span id="current-page">1</span> / <span id="total-pages">8</span>
</div>
```

## 6. Markdown 元素支持

| 元素 | 处理方式 |
|------|---------|
| 标题 H1-H6 | 正常渲染，H1 通常作为页面主标题 |
| 段落 | 正常渲染 |
| 无序/有序列表 | 正常渲染 |
| 代码块（含语言标注） | 语法高亮（highlight.js） |
| 表格 | 正常渲染 |
| 图片 | 本地图片转 Base64 内联 |
| 粗体/斜体/删除线 | 正常渲染 |
| 行内代码 | 正常渲染 |
| `Note:` 段落 | 转为演讲者注释（隐藏层） |
| `---` 分隔符 | 强制分页 |

## 7. Skill 触发场景

| 场景 | 示例用户输入 |
|------|------------|
| 原始材料转换 | "帮我把这份报告做成演示文稿" |
| MD 文件转换 | "把 report.md 转成 HTML 演示文稿" |
| 指定风格 | "用深色主题，16:9 生成幻灯片" |
| 元素调整 | "把第2页的标题改大一点" |
| 内容变更 | "第3页第二条要点改成…" |
| 增减页面 | "在第5页后面加一页，内容是…" |
| 图表内容变更 | "第4页的折线图改成柱状图" |
| PDF 导出 | "把演示文稿转成 PDF" |
| 斜杠指令 | `/md2slides convert report.md` |

## 8. 约束与限制

- 不支持复杂数学公式渲染（可后续添加 MathJax，P3）
- 本地图片仅支持相对路径，网络图片支持 HTTP URL
- 嵌套列表不超过 3 层（视觉效果差）
- PDF 转换需要 playwright 环境；系统已有 Edge/Chrome 时无需下载 Chromium
- HTML 代码高亮需要 CDN 访问（highlight.js）
- 内容变更重新生成后，元素 ID 不匹配的旧样式将被重置为主题默认值

## 9. 版本历史

| 版本   | 日期         | 变更内容                                                         |
| ---- | ---------- | ------------------------------------------------------------ |
| v0.1 | 2026-03-23 | 初稿，基于 reveal.js 的基础需求                                        |
| v0.2 | 2026-03-24 | 重构：两阶段工作流、元素树、键盘导航、页码、调整功能、PDF 导出；放弃 reveal.js 改用自定义实现       |
| v0.3 | 2026-03-24 | 新增数据可视化需求：数据提取存储（CSV/Dataview）、图表类型与参数标注、Chart.js 渲染、图表元素树支持 |
| v0.4 | 2026-03-24 | 新增内容变更路径、样式保留策略 |
| v0.5 | 2026-03-25 | 重构为三阶段工作流；27 种版式模板；版式规划阶段；splitMode=group、stat-cards columns、card-grid、:::col、rawHtml、section-header 双变体；preview.py；浏览器自动检测；PDF 黑边修复；原生 MD 表格支持 |
