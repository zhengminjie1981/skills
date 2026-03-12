---
description: "配置主题样式"
argument-hint: "[主题] [--dark|--light]"
allowed-tools: [Read, Write]
---

# 配置主题样式

为 Obsidian Slides Extended 配置主题样式。

## 工作流

1. **列出主题** - 列出可用的内置主题
2. **生成配置** - 生成 frontmatter 主题配置
3. **应用到文件** - 将配置添加到幻灯片文件

## 内置主题

### 深色主题
- `black` - 经典黑色
- `night` - 夜间模式
- `moon` - 月光主题
- `dracula` - Dracula 配色
- `hacker` - 黑客风格

### 浅色主题
- `white` - 经典白色
- `beige` - 米色主题
- `sky` - 天空蓝
- `solarized` - Solarized 配色
- `serif` - 衬线字体

## 使用示例

```
/obsidian-slides:theme
/obsidian-slides:theme --dark
/obsidian-slides:theme dracula
/obsidian-slides:theme --light
```

## 输出示例

```yaml
---
theme: dracula
transition: slide
---

# 幻灯片标题
...
```

## 参考资源

如需详细配置，按需读取：
- `~/.claude/skills/obsidian-slides/references/themes.md` - 主题配置和 CSS 选项
