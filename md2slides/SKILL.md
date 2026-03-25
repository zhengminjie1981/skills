---
name: md2slides
description: |
  将原始材料或 Markdown 文件转换为 HTML 格式的演示文稿，支持 AI 版式规划（27 种布局模板）、数据图表、图片嵌入、键盘导航、元素级样式调整和 HTML→PDF 导出。

  **触发场景**（包含以下关键词时加载）：
  - 生成演示文稿：做成演示文稿、做成幻灯片、做成 PPT、转成 HTML、生成 slides、制作演示
  - 版式规划：设计版式、帮我排版、版式规划、选布局、换版式、换布局、重新排版
  - 内容调整：把第X页、修改幻灯片、标题改、字体改、颜色改、图表移、内容变更、重新生成
  - 数据图表：数据可视化、柱状图、折线图、饼图、图表、Chart
  - PDF 导出：转成 PDF、导出 PDF、html2pdf
  - 斜杠指令：/md2slides

  **不触发场景**：
  - 纯 Markdown 编辑（无演示文稿意图）
  - 仅问"什么是幻灯片"等定义性问题
  - 制作网页、文档（非演示文稿）
---

# md2slides

> 将材料或 Markdown 文件转换为可在浏览器中演示的 HTML 幻灯片，支持数据图表与 PDF 导出。

## 快速开始

```bash
# 阶段一：AI 策划 MD 内容（直接对话）

# 阶段二：AI 版式规划 → 写入 slide-tree.json（直接对话，无需脚本）

# 阶段三：MD + slide-tree.json → HTML
python scripts/convert.py --input demo.md --output demo.html --tree slide-tree.json

# 推荐：内联资源，离线可用，中国网络友好
python scripts/convert.py --input demo.md --output demo.html --tree slide-tree.json --inline-assets

# 内容变更后重新生成（保留版式和样式）
python scripts/convert.py --input demo.md --output demo.html --tree slide-tree.json --preserve-styles

# 生成后直接用默认浏览器打开（file:// 协议，无需 HTTP 服务）
python scripts/convert.py --input demo.md --output demo.html --tree slide-tree.json --serve

# HTML → PDF
python scripts/html2pdf.py --input demo.html --output demo.pdf

# 批量预览截图（输出到 preview/ 目录，便于快速检查所有页面）
python scripts/preview.py --input demo.html
```

## 核心功能

| 功能 | 说明 | 触发示例 |
|------|------|---------|
| 内容策划 | 分析材料，规划页面结构，生成 MD | "帮我把这份报告做成演示文稿" |
| **版式规划** | **AI 逐页分析内容，选定最佳版式，写入 tree** | **"帮我设计版式"** |
| HTML 生成 | MD + tree 版式 → 自包含 HTML，支持 5 套主题 | "生成 16:9 深色主题的幻灯片" |
| 数据图表 | 自动提取数据到 CSV，用 Chart.js 渲染 | "数据用折线图展示" |
| 样式调整 | 直接修改 HTML + 同步元素树 | "第3页标题改成黄色" |
| 内容变更 | 更新 MD 后重新生成，保留旧版式和样式 | "第4页加一条要点" |
| PDF 导出 | playwright 渲染，每页对应一张 PDF | "转成 PDF" |

## 决策树：收到调整请求时

```
用户发出调整请求
│
├── 是否涉及内容（文字/结构/图表类型）？
│   ├── YES → 内容变更路径
│   │         1. 定位 MD 中对应页面
│   │         2. 修改 MD 文件
│   │         3. 运行 convert.py --preserve-styles
│   │         4. 告知变更摘要和样式保留情况
│   │
│   └── NO → 样式调整路径
│             1. 读取 slide-tree.json 定位元素 ID
│             2. 直接编辑 HTML 文件 style 属性
│             3. 同步更新 slide-tree.json
│             4. 告知修改了哪个 ID 和具体变更

内容变更 vs 样式调整 快速判断：
  修改文字/要点/标题文本     → 内容变更
  增加/删除/移动页面         → 内容变更
  修改图表类型/数据源/字段   → 内容变更
  修改字体大小/颜色/粗细     → 样式调整
  修改间距/对齐/背景色       → 样式调整
  修改图表位置/宽高百分比    → 样式调整
```

## 典型场景

### 场景 A：从原始材料生成演示文稿

```
用户: 帮我把下面这份产品季报做成演示文稿：[材料]

AI 步骤：
1. 分析材料，识别可视化数据段落
2. 规划页面结构（封面/目录/内容页/数据页/结语）
3. 提取数据 → 创建 data/{名称}-s{N}-{描述}.csv
4. 生成 MD 文件，含 <!-- chart --> 块
5. 展示摘要（页数 + 每页标题）并确认

AI: 已完成内容策划，共 8 页：
    1 封面 / 2 目录 / 3-6 内容页 / 7 数据页（含折线图）/ 8 结语
    涉及数据文件：data/report-s7-users.csv（已创建）
    请确认内容，或告知需要调整的地方。

用户: 好的，继续

AI: 请选择宽高比：A. 16:9（推荐） B. 4:3
用户: 16:9

AI: 根据商务汇报风格，建议 professional-dark 主题。是否采用？
用户: 好的

AI 执行：python scripts/convert.py --input report.md --output report.html --tree slide-tree.json
AI: HTML 已生成：report.html（8 页）
    [展示页面结构摘要]
```

### 场景 B：样式调整

```
用户: 把第3页的标题改成黄色，字大一点

AI 步骤：
1. 读取 slide-tree.json，定位 s3-title1
2. 修改 HTML 中 id="s3-title1" 元素的 style：
   color → #FFD700；fontSize 1.9em → 2.3em
3. 同步更新 slide-tree.json 中 s3-title1 的 style 字段

AI: 已更新 s3-title1：
    fontSize: 1.9em → 2.3em
    color: → #FFD700
    HTML 文件已保存。
```

### 场景 C：内容变更

```
用户: 第4页加一条要点："Q4 净利润首次转正"

AI 步骤：
1. 判断为内容变更（增加列表条目）
2. 定位 MD 第4页（<!-- Slide 4 -->）
3. 在列表末尾添加该条目
4. 运行 convert.py --preserve-styles
5. 汇报结果

AI: 已更新第4页列表（+1条）。重新生成完成，已有样式全部保留。
```

### 场景 D：含图表的内容变更

```
用户: 第5页的柱状图改成折线图

AI 步骤：
1. 判断为内容变更（修改图表类型）
2. 定位 MD 第5页的 <!-- chart --> 块
3. 修改 type: bar → type: line
4. 运行 convert.py --preserve-styles
5. 汇报（图表 position/width/height 样式已保留）
```

### 场景 E：PDF 导出

```
用户: 帮我转成 PDF

# 主路径（需要 playwright + Chromium）
AI 执行：python scripts/html2pdf.py --input report.html --output report.pdf
AI: PDF 已生成：report.pdf（8 页，1280×720px）

# Chromium 下载失败（中国网络）时的备用方案：
#   方案 A：设置下载镜像（推荐）
#     Windows: set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
#     Linux/Mac: export PLAYWRIGHT_DOWNLOAD_HOST=...
#     然后: playwright install chromium
#
#   方案 B：MCP Playwright（已安装时）
#     前提：先用 --inline-assets 生成内联版 HTML（避免 file:// 跨域限制）
#     1. 用 MCP Playwright 打开 HTML 文件（file:// 直接打开）
#     2. 逐页截图（goTo(0)...goTo(N-1)）保存为 PNG
#     3. 用 Python Pillow 将 PNG 合并为 PDF：
#        from PIL import Image
#        imgs = [Image.open(f) for f in sorted(png_files)]
#        imgs[0].save("output.pdf", save_all=True, append_images=imgs[1:])
#
#   方案 C：手动浏览器（不依赖任何安装）
#     1. Chrome/Edge 打开 HTML
#     2. Ctrl+P → 另存为 PDF → 勾选"背景图形"
#     注意：图表可能渲染不完整
```

## 图片支持

在 MD 文件中用标准 Markdown 语法引用图片，生成 HTML 时路径自动修正：

```markdown
![产品截图](images/product.png)
![数据图](../assets/chart.jpg)
```

**路径规则**：
- 路径相对于 MD 文件所在目录
- 若 HTML 输出到不同目录，路径自动调整为相对 HTML 的路径
- 不支持外部 URL 的路径修正（`http://`、`https://` 保持原样）
- 文件不存在时打印警告，不中断转换

**样式**：图片自适应幻灯片内容区宽度，保持比例缩放。

## 调整操作速查

### 常见样式 → 元素 ID 定位

| 用户说法 | 定位方法 |
|---------|---------|
| "第N页标题" | slide-tree.json 中 index=N 的 h1 元素，通常为 sN-title1 |
| "第N页副标题" | sN-subtitle1 |
| "第N页列表/要点" | sN-list1（多个列表则为 list1, list2...） |
| "第N页图表" | sN-chart1 |
| "第N页背景" | HTML 中 id="slide-N" 的 .slide 元素 |

### 颜色中文名 → CSS 值

参见 `references/color-map.md`

### 调整幅度参考

| 用户说法 | 推荐调整量 |
|---------|---------|
| "大一点" / "小一点" | ±0.3em ~ 0.5em |
| "大很多" / "小很多" | ±0.8em ~ 1.2em |
| "加粗" | fontWeight: bold |
| "细一点" | fontWeight: 300 |
| "间距大一点" | margin/padding +0.3em ~ 0.5em |

### MD 结构 -> 版式行为速查

**版式由内容性质决定，数量只是辅助参考**：

| 内容性质 | 首选版式 | 不要用 |
|---------|---------|-------|
| 并列/对比关系（两组） | `text-two-column` | - |
| 并列/对比关系（三组） | `text-three-column` | - |
| 叙事流/连续段落 | `text-default` | `text-two-column` |
| 独立个体（功能/场景卡片） | `card-grid` | `text-two-column` |
| KPI 数字 | `stat-cards` | `text-default` |

**多列版式的分列行为**：

| MD 结构 | 版式 | 实际行为 | layout 参数 |
|---------|------|---------|------------|
| 单个 ul（并列内容） | `text-two-column` | 均分 li 条目到两列 | 无需额外参数 |
| p+ul+p+ul（多组并列） | `text-two-column` | 默认只拆第一个 ul | 加 `splitMode:group` 按组分列 |
| p+ul×3 | `text-three-column` | 同上 | 加 `splitMode:group` |
| 3 张 KPI | `stat-cards` | 单行 | 无需额外参数 |
| 4 张 KPI | `stat-cards` | 单行四列 | 加 `columns:2`（2×2） |
| 5 张 KPI | `stat-cards` | 单行五列 | 加 `columns:3`（2+3） |
| 6 张 KPI | `stat-cards` | 单行六列 | 加 `columns:3`（2×3） |

> **`:::col` 内部约束**：列内标题用 `**粗体**`，不用 `##`；`splitMode:group` 要求 `p+ul` 交替结构（`##` 不触发）。
> **版式自检**：多列版式规划完成后，校验内容性质和左右列字数比（< 0.5 降级为单列）。详见 `references/workflow.md §2.4`。

## 样式调整效率说明

**优先用 JSON 定位，避免全量读 HTML**：
```
1. 读 slide-tree.json → 找到目标 ID（如 s3-title1）
2. Grep HTML 文件中该 ID → 精确定位行号
3. Edit 修改对应 style 属性
4. 同步更新 tree JSON 中的 style 字段
```
slide-tree.json 已包含所有元素 ID、类型和位置信息，无需全量读取 546 行 HTML。

## Windows 编码注意

**Write/Edit 工具在 Windows GBK 环境下可能腐蚀特定中文字符**（助、幅、工等 Unicode 编码与 GBK 冲突）：
- 建议：让用户直接用文本编辑器（VS Code）编写或修改 MD 文件，AI 负责策划内容结构
- 必须用 AI 写文件时：只写 ASCII + emoji，避免对会被腐蚀的字符直接输出
- 验证：`python -c "open('file.md', encoding='utf-8').read()"`

## 校验行为规范

### 优先路径：HTML 结构分析（无需浏览器）

生成 HTML 后，优先用以下方式校验，**不启动浏览器，不截图**：

```
1. Read slide-tree.json  → 确认 totalSlides、每页 layout.template、元素 ID
2. Grep HTML 文件        → 验证关键结构（如 class="layout-card-grid"、chart 块是否存在）
3. 检查 convert.py 输出  → 有无 WARNING（如多组 p+ul 未分列）
```

适用范围：文字内容、版式切换、样式调整——**99% 的场景不需要视觉截图**。

### 必要时：批量截图校验

仅在以下情况才使用 `preview.py` 截图：
- 图表渲染效果（Chart.js 动态渲染，HTML 结构无法预判）
- 复杂自定义布局（rawHtml 注入后的实际效果）
- 用户明确要求查看视觉效果

**使用规范（临时目录，自动清理）**：

```bash
# 截图到系统临时目录（不污染项目目录）
python scripts/preview.py --input demo.html --temp
# AI 读取截图确认效果后，立即清理
python scripts/preview.py --input demo.html --clean
```

### 禁止行为

- 禁止直接用 MCP Playwright 截图到项目目录或任意路径
- 禁止在不使用 `--temp` 的情况下运行 `preview.py`（避免在项目根留下 `preview/` 垃圾目录）
- 禁止截图后不清理临时目录

## 文件结构

```
md2slides/
├── SKILL.md                    ← 本文件（AI 入口）
├── scripts/
│   ├── convert.py              ← MD → HTML 主脚本（含 --serve 预览服务）
│   ├── html2pdf.py             ← HTML → PDF（自动检测 Edge/Chrome/Chromium）
│   └── preview.py              ← 批量截图缩略图（输出到 preview/ 目录）
├── references/                 ← AI 按需加载
│   ├── workflow.md             ← 完整工作流决策树与版式选择原则
│   ├── color-map.md            ← 中文颜色名映射
│   ├── template.html           ← HTML 骨架模板
│   ├── chart-defaults.json     ← 图表配色配置
│   ├── slide-schema.json       ← 元素树 JSON Schema
│   └── themes/                 ← 5套主题 CSS
├── assets/                     ← 缓存的 CDN 资源（首次 --inline-assets 时下载）
├── data/                       ← 运行时数据（CSV 文件）
├── examples/                   ← 示例文件
└── docs/                       ← 开发文档（不加载）
```

## 参考资源

按需加载的详细文档：

| 文档 | 内容 | 何时读取 |
|------|------|---------|
| `references/workflow.md` | 完整工作流决策树、版式选择原则、MD 编写规范 | 遇到复杂判断、分列异常、中文乱码时 |
| `references/color-map.md` | 中文颜色名 → CSS 值映射表 | 用户用中文指定颜色时 |

---

**版本**: 1.3 | **最后更新**: 2026-03-25
