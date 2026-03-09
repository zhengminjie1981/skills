# Obsidian Slides 配置生成 Skill 设计文档

## 概述

本 Skill 帮助用户生成 Obsidian Slides Extended（reveal.js）演示文稿的布局代码、主题配置和动画语法。

## 目标用户

- Obsidian 用户
- 需要制作演示文稿的人
- 希望快速生成专业幻灯片的用户

## 核心功能

1. **幻灯片生成**：新建幻灯片 / 内容转换
2. **布局生成**：生成 grid/split 布局代码
3. **主题配置**：生成 frontmatter 主题设置（含 transition）
4. **动画语法**：生成 fragment 类名

## 技术栈

- Obsidian Slides Extended 插件
- reveal.js 框架
- Markdown + HTML 混合语法

## 文件结构

```
obsidian-slides/
├── SKILL.md                    # 入口文件
├── references/                 # AI 参考文档
│   ├── layout-syntax.md        # 布局语法参考
│   ├── themes.md               # 主题和样式参考
│   ├── templates.md            # 模板说明
│   └── snippets.md             # 代码片段库
├── scripts/                    # 可执行脚本
│   └── md2slides.py            # Markdown 转 Slides 脚本
├── assets/templates/           # 模板文件
│   ├── product-pitch.md        # 产品介绍
│   ├── meeting-report.md       # 会议汇报
│   ├── tutorial.md             # 教程演示
│   ├── technical.md            # 技术分享
│   └── announcement.md         # 公告通知
└── docs/
    └── design.md               # 本文档
```

## 模板设计原则

1. **简单干净**：避免过度设计
2. **深浅适配**：每个模板提供 dark/light 两个版本
3. **可定制**：使用 `{{占位符}}` 标记需要替换的内容
4. **结构清晰**：每页有明确的目的

## 触发场景设计

**触发关键词**：
- 幻灯片生成：创建幻灯片、新建 slides、转成幻灯片、Markdown 转 slides
- 布局生成：幻灯片布局、grid 布局、分栏布局
- 主题配置：幻灯片主题、换主题、深色主题
- 动画效果：逐条显示、fragment、动画

**不触发场景**：
- 纯 PowerPoint/Keynote 相关
- 纯 Markdown 格式问题

## 变更日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-03-09 | 2.0 | 功能定位调整：移除"美化"，聚焦配置生成 |
| 2026-03-08 | 1.0 | 初始版本 |

---

*创建日期：2026-03-08*
