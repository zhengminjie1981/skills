---
description: "创建演示文稿"
argument-hint: "[主题] [--template 类型]"
allowed-tools: [Read, Write, Glob]
---

# 创建演示文稿

创建 Obsidian Slides Extended（reveal.js）演示文稿。

## 工作流

1. **选择模板** - 根据用途选择合适的模板
2. **收集内容** - 通过对话收集幻灯片内容
3. **生成 Markdown** - 生成完整的幻灯片 Markdown
4. **保存文件** - 保存到指定位置

## 可用模板

| 模板 | 适用场景 |
|------|---------|
| product-pitch | 产品介绍 |
| technical | 技术分享 |
| report | 工作汇报 |
| tutorial | 教程/教学 |
| generic | 通用演示 |

## 使用示例

```
/obsidian-slides:new
/obsidian-slides:new AI 助手产品介绍
/obsidian-slides:new 技术分享 --template technical
```

## 前置要求

需要安装 **Obsidian Slides Extended** 插件：
- 设置 → 第三方插件 → 浏览 → 搜索 "Slides Extended"
- 安装并启用

## 参考资源

如需详细说明，按需读取：
- `~/.claude/skills/obsidian-slides/references/usage-guide.md` - 使用教程
- `~/.claude/skills/obsidian-slides/references/templates.md` - 模板详细说明
