---
name: obsidian-slides
description: |
  帮助用户生成 Obsidian Slides Extended（reveal.js）演示文稿的布局代码、主题配置和动画语法。

  **核心能力**（AI 可靠执行）：
  - 幻灯片生成：新建幻灯片 / 内容转换
  - 布局生成：grid/split 布局代码
  - 主题配置：frontmatter 主题设置（含 transition）
  - 动画语法：fragment 类名

  **触发场景**：
  - 幻灯片生成：创建幻灯片、新建 slides、转成幻灯片、Markdown 转 slides
  - 布局生成：幻灯片布局、grid 布局、分栏布局
  - 主题配置：幻灯片主题、换主题、深色主题
  - 动画效果：逐条显示、fragment、动画

  **不触发场景**：
  - 纯 PowerPoint/Keynote 相关
  - 纯 Markdown 格式问题
---

# Obsidian Slides 配置生成

## 一行总结

> 帮助用户生成 Obsidian Slides Extended（reveal.js）的布局代码、主题配置和动画语法

## 快速开始

### 创建新幻灯片

```
用户: 帮我创建一个产品介绍幻灯片
AI: 询问主题/风格 → 选择模板 → 生成完整 Markdown
```

### 布局生成

```
用户: 帮我做一个左右分栏布局，左边放文字，右边放图片
AI: 询问比例 → 生成 split 代码
```

## 核心功能

| 功能 | 说明 | 触发示例 |
|------|------|---------|
| 幻灯片生成 | 新建或转换幻灯片 | "帮我创建一个产品介绍幻灯片" |
| 布局生成 | 生成 grid/split 布局代码 | "做一个左右分栏" |
| 主题配置 | 生成 frontmatter 主题设置 | "配置深色主题" |
| 动画语法 | 生成 fragment 类名 | "让列表逐条显示" |

## 决策树

```
用户需求？
├─ 幻灯片生成
│   ├─ 有现成内容？ → 转换格式（md2slides 或手动分段）
│   └─ 从零开始？ → 询问用途 → 选择模板 → 填充占位符
│
├─ 布局生成
│   ├─ 左右分栏？ → 询问比例 → 生成 split 代码
│   ├─ 多栏网格？ → 询问栏数和比例 → 生成 grid 代码
│   └─ 图文混排？ → 生成 split 代码
│
├─ 主题配置
│   ├─ 快速换风格？ → 列出 10 个内置主题 → 用户选择 → 生成 frontmatter
│   └─ 深色/浅色？ → 列出对应主题 → 用户选择
│
└─ 动画效果
    ├─ 逐条显示？ → 生成 fragment 类名
    └─ 其他效果？ → 列出可用效果 → 用户选择 → 生成代码
```

## 前置要求

用户需要安装 **Obsidian Slides Extended** 插件：
- 设置 → 第三方插件 → 浏览 → 搜索 "Slides Extended"
- 安装并启用

## 典型场景

### 场景1: 创建产品介绍幻灯片

```
用户: 帮我创建一个产品介绍幻灯片，主题是 AI 助手
AI:
  1. 询问：目标受众？演示时长？
  2. 读取 assets/templates/product-pitch.md
  3. 生成完整 Markdown，包含：
     - 标题页
     - 痛点页
     - 方案页
     - 优势页
     - CTA 页
```

### 场景2: 布局生成

```
用户: 帮我做一个左右对比的布局
AI:
  1. 询问：左右比例？（50/50 或 60/40）
  2. 生成 split 布局代码
```

### 场景3: 主题配置

```
用户: 给这个幻灯片配置一个深色主题
AI:
  1. 列出深色主题选项：black / night / moon
  2. 用户选择后，生成 frontmatter 配置
```

## 常用布局速查

| 布局 | 语法 | 适用场景 |
|------|------|---------|
| 左右分栏 | `<split even>` | 图文混排 |
| 三栏等分 | `<grid drag="100 100" drop="33 33 33">` | 对比展示 |
| 单栏居中 | 默认 | 标题、强调 |
| 引用+正文 | `<grid>` + blockquote | 证言、引用 |

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 布局不生效 | 确保安装了 Slides Extended 插件 |
| 分页位置不对 | 使用 `---` 分隔，不要用 `***` |
| 中文显示异常 | 在 frontmatter 添加字体配置 |
| 主题没有变化 | 检查 frontmatter 的 theme 字段拼写 |

## 参考资源

按需加载的详细文档（仅 .md 文件）：

| 文档 | 内容 | 何时读取 |
|------|------|---------|
| `references/usage-guide.md` | **安装教程、使用示例、导出 PDF** | 首次使用或需要示例时 |
| `references/layout-syntax.md` | grid/split 完整语法 | 需要复杂布局时 |
| `references/themes.md` | 主题配置和 CSS 选项 | 需要配置主题时 |
| `references/templates.md` | 5 个模板详细说明 | 需要了解模板结构时 |
| `references/snippets.md` | fragment、background 等片段 | 需要动画效果时 |

---

**版本**: 2.0 | **最后更新**: 2026-03-09
