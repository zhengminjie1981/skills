---
description: "生成幻灯片布局"
argument-hint: "<类型> [选项]"
allowed-tools: [Read, Write]
---

# 生成幻灯片布局

生成 Obsidian Slides Extended 的 grid/split 布局代码。

## 工作流

1. **解析类型** - 确定布局类型和参数
2. **生成代码** - 生成对应的布局代码
3. **提供示例** - 展示使用示例

## 支持的布局类型

| 类型 | 语法 | 适用场景 |
|------|------|---------|
| split | `<split even>` | 左右分栏 |
| split-left | `<split left="60">` | 左侧为主 |
| split-right | `<split right="60">` | 右侧为主 |
| grid | `<grid drag="100 100" drop="33 33 33">` | 多栏网格 |

## 使用示例

```
/obsidian-slides:layout split
/obsidian-slides:layout split-left 70
/obsidian-slides:layout grid 3
```

## 输出示例

### split 布局

```html
<split even>

<!-- 左侧内容 -->

--

<!-- 右侧内容 -->

</split>
```

### grid 布局

```html
<grid drag="100 100" drop="33 33 33">

<!-- 第一栏 -->

<!-- 第二栏 -->

<!-- 第三栏 -->

</grid>
```

## 参考资源

如需详细语法，按需读取：
- `~/.claude/skills/obsidian-slides/references/layout-syntax.md` - 完整布局语法
