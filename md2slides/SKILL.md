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

feedback:
  enabled: true
  version: "2.3.0"
  author: "skills-team"
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

# HTML → PDF
python scripts/html2pdf.py --input demo.html --output demo.pdf
```

> ⚠️ **convert.py 每次运行都会读取已有 HTML 的 style 属性合并回 tree**。
> HTML 破损或样式错乱时，**必须删除旧 HTML 文件再重新生成**，否则坏样式会持续继承。

## 核心功能

| 功能       | 说明                               | 触发示例               |
| -------- | -------------------------------- | ------------------ |
| 内容策划     | 分析材料，规划页面结构，生成 MD                | "帮我把这份报告做成演示文稿"    |
| **版式规划** | **AI 逐页分析内容，选定最佳版式，写入 tree**     | **"帮我设计版式"**       |
| HTML 生成  | MD + tree 版式 → 自包含 HTML，支持 9 套主题 | "生成 16:9 深色主题的幻灯片" |
| 数据图表     | 自动提取数据到 CSV，用 Chart.js 渲染        | "数据用折线图展示"         |
| 样式调整     | 直接修改 HTML + 同步元素树                | "第3页标题改成黄色"        |
| 内容变更     | 更新 MD 后重新生成，保留旧版式和样式             | "第4页加一条要点"         |
| PDF 导出   | playwright 渲染，每页对应一张 PDF         | "转成 PDF"           |

## 决策树：收到调整请求时

> **阶段约束**：三阶段顺序不可逆——先定 MD → 再定 tree → 最后跑 convert。
> **tree 复用**：slide-tree.json 一旦确认，内容变更只需修 MD + 重跑 `convert.py --preserve-styles`，**不需要重新生成 tree**。

```
用户发出调整请求
│
├── 是否涉及内容（文字/结构/图表类型）？
│   ├── YES → 内容变更路径
│   │         1. 定位 MD 中对应页面
│   │         2. 修改 MD 文件
│   │         3. 运行 convert.py --preserve-styles
│   │
│   └── NO → 样式调整路径
│             1. 读取 slide-tree.json 定位元素 ID
│             2. 直接编辑 HTML 文件 style 属性
│             （下次重新生成时 convert.py 自动从 HTML 反向同步 tree）
```

> **多个调整时**：样式改 HTML + 内容改 MD → 用户满意后跑 `--preserve-styles` 批量同步。详见 `references/operations.md`。

## MD 分页规则（核心）

```markdown
---                          ← Front Matter 开始（不是分页）
title: 标题
ratio: "16:9"
theme: professional-dark
---                          ← Front Matter 结束（不是分页）

<!-- Slide 1: Cover -->      ← 页面注释（影响封面/结语样式）
# 封面标题
## 副标题

---                          ← 分页符（独立一行，上下空行）

<!-- Slide 2: 目录 -->
# 目录
- 第一章
```

**关键点**：`---` 分页；`#`/`##` 不分页；Front Matter 的 `---` 不算分页。

## 常见样式 → 元素 ID

| 用户说法 | 元素 ID |
|---------|---------|
| "第N页标题" | `sN-title1` |
| "第N页副标题" | `sN-subtitle1` |
| "第N页列表" | `sN-list1` |
| "第N页图表" | `sN-chart1` |

效率原则：读 slide-tree.json 找 ID → Grep HTML 定位行 → Edit 修改 style。

## 常见版式陷阱

| 版式 | 必须条件 | 错误写法 | 详细规范 |
|------|---------|---------|---------|
| stat-cards / card-grid | 必须用 `<li>` 列表项 | 段落 `<p>` → 无卡片 | `references/md-writing.md §4` |
| text-three-column | 需 3 组 `<p>`+`<ul>` 交替 | 少于 3 组 → 降级 | `references/md-writing.md §3` |
| chart 块 | 必须显式写 xField/yField | 省略 → 图表空白 | `references/md-writing.md §2` |

⚠️ **Windows 中文**：禁止 Write/Edit 工具写中文 MD → GBK 乱码，必须用 Python UTF-8。

## 校验行为规范（生成后必须执行）

每次生成或重新生成 HTML 后，**必须**完成以下结构校验：

```
1. Read slide-tree.json  → 确认 totalSlides、每页 layout.template
2. Grep HTML 文件        → 验证关键结构（slide 数量、图表容器、分页符）
3. 检查 convert.py 输出  → 有无 WARNING（缺字段、布局降级、资源失败）
```

**首次生成后**，额外运行截图确认视觉效果：

```bash
python scripts/preview.py --input demo.html       # 默认临时目录
python scripts/preview.py --input demo.html --clean  # 确认后清理截图
```

后续重新生成时，仅在图表渲染异常、复杂自定义布局、用户明确要求时才截图。

**禁止**：截图后不清理临时文件。

## 临时文件管理

AI 在操作过程中产生的**临时脚本**（如单次用途的 Python 辅助脚本）用完后必须删除。

**不属于临时文件**（不可删除）：
- `slide-tree.json`：版式规划结果，内容变更时复用
- `*.md`、`*.html`、`data/*.csv`：项目核心文件

## 参考资源（按场景加载）

### 我要做演示文稿

| 场景 | 读取文档 |
|------|---------|
| 内容策划（页数、数据识别、图表类型）| `references/content-planning.md` |
| 版式规划（27种模板选择、主题选择）| `references/layout-guide.md` |
| 写 MD 文件（分页规则、chart块、emoji）| `references/md-writing.md` |
| 整体工作流概览 | `references/workflow.md` |

### 我要修改幻灯片

| 场景 | 读取文档 |
|------|---------|
| 样式/内容/版式调整详细流程 | `references/operations.md` |
| 调整请求路由、增删页面影响 | `references/workflow.md §3` |

### 其他

| 场景 | 读取文档 |
|------|---------|
| 导出 PDF（3种方案）| `references/pdf-export.md` |
| 颜色中文名 → CSS 值 | `references/color-map.md` |

## 文件结构

```
md2slides/
├── SKILL.md                    ← 本文件（AI 入口）
├── scripts/
│   ├── convert.py              ← MD → HTML 主脚本
│   ├── html2pdf.py             ← HTML → PDF
│   └── preview.py              ← 批量截图
├── references/                 ← AI 按需加载
│   ├── workflow.md             ← 工作流概览 + 调整路由
│   ├── content-planning.md     ← 内容策划（页数、数据、图表类型）
│   ├── layout-guide.md         ← 版式选择（27种模板、主题、自检）
│   ├── operations.md           ← 调整操作（场景流程、元素ID、速查）
│   ├── md-writing.md           ← MD编写规范（分页、chart块、emoji）
│   ├── pdf-export.md           ← PDF导出方案
│   ├── color-map.md            ← 中文颜色名映射
│   ├── chart-defaults.json     ← 图表配色配置
│   ├── slide-schema.json       ← 元素树 JSON Schema
│   ├── template.html           ← HTML 骨架模板
│   └── themes/                 ← 9套主题 CSS
├── assets/                     ← 缓存的 CDN 资源
├── data/                       ← 运行时数据（CSV 文件）
├── examples/                   ← 示例文件
└── docs/                       ← 开发文档（不加载）
```

---

**版本**: 2.3 | **最后更新**: 2026-03-25

---

## 反馈机制

本 skill 支持自动反馈改进。

<!-- FEEDBACK-TRIGGER-START -->
<feedback-config>
{
  "triggers": ["execution_failure", "rendering_error", "export_error"],
  "collect": ["error_type", "slide_format", "environment", "skill_version"],
  "sanitize": ["file_paths", "slide_content", "user_data"]
}
</feedback-config>
<!-- FEEDBACK-TRIGGER-END -->

执行完成后，如检测到改进机会且用户已授权，将自动发送脱敏反馈。
