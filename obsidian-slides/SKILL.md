---
name: obsidian-slides
description: |
  帮助用户创建、排版和美化 Obsidian Slides Extended（reveal.js）演示文稿。

  **触发场景**（包含以下关键词）：
  - 创建幻灯片：创建 Obsidian 幻灯片、新建 slides、制作演示文稿、生成幻灯片
  - 排版布局：幻灯片排版、slides 布局、grid 布局、分栏、重新排版
  - 美化样式：美化幻灯片、幻灯片主题、slides 样式、换主题
  - 内容转换：转成幻灯片、文字转 slides、Markdown 转 slides

  **不触发场景**：
  - 纯 PowerPoint/Keynote 相关（非 Obsidian）
  - 纯 Markdown 格式问题（非幻灯片）
  - 其他 Obsidian 插件问题
---

# Obsidian Slides 排版美化

## 一行总结

> 帮助用户创建、排版和美化 Obsidian Slides Extended（reveal.js）演示文稿

## 快速开始

### 创建新幻灯片

```
用户: 帮我创建一个产品介绍幻灯片
AI: 询问主题/风格 → 选择模板 → 生成完整 Markdown
```

### 排版优化

```
用户: 这个幻灯片内容太挤，帮我重新排版
AI: 分析内容结构 → 推荐 grid/split 布局 → 重新组织
```

### 批量转换

```bash
# 将普通 Markdown 转换为 Slides 骨架
python scripts/md2slides.py input.md --theme dark
```

## 核心功能

| 功能 | 说明 | 触发示例 |
|------|------|---------|
| 布局生成 | 生成 grid/split 布局代码 | "帮我做一个左右分栏" |
| 主题配置 | 推荐 frontmatter 主题设置 | "换个专业风格" |
| 模板生成 | 基于预制模板快速创建 | "生成一个学术报告模板" |
| 内容转换 | Markdown 自动分页布局 | "把这段文字转成 3 页幻灯片" |
| 样式美化 | CSS 自定义样式建议 | "给标题加个渐变色" |

## 决策树

```
用户需求？
├─ 新建幻灯片
│   ├─ 知道模板类型？ → 使用对应模板
│   └─ 不确定？ → 询问：产品/会议/教程/技术/公告
│
├─ 排版优化
│   ├─ 内容多且挤？ → 推荐 grid 分栏布局
│   ├─ 图文混排？ → 推荐 split 左右布局
│   └─ 单页简单内容？ → 居中布局
│
├─ 美化样式
│   ├─ 快速换风格？ → 推荐 10 个内置主题
│   ├─ 需要自定义？ → 读取 themes.md 提供 CSS 方案
│   └─ 深色/浅色？ → 提供两种配色方案
│
└─ 内容转换
    ├─ 有现成 Markdown？ → 使用 md2slides.py
    └─ 口述内容？ → 自动分段 + 应用布局
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

### 场景2: 排版优化

```
用户: 这个幻灯片内容太多了，帮我重新排版
AI:
  1. 分析内容结构
  2. 读取 references/layout-syntax.md
  3. 推荐布局方案：
     - 使用 <grid> 分栏
     - 拆分为多页
     - 使用 fragment 逐步展示
```

### 场景3: 主题美化

```
用户: 给这个幻灯片换个专业风格
AI:
  1. 读取 references/themes.md
  2. 推荐：black/white/league 主题
  3. 生成 frontmatter 配置
  4. 可选：提供自定义 CSS 片段
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
| `references/themes.md` | 主题配置和自定义 CSS | 需要样式美化时 |
| `references/templates.md` | 5 个模板详细说明 | 需要了解模板结构时 |
| `references/snippets.md` | fragment、background 等片段 | 需要特效功能时 |

---

**版本**: 1.1 | **最后更新**: 2026-03-08
