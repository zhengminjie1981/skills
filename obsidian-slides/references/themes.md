# Obsidian Slides 主题和样式参考

> 本文档介绍 Slides Extended 的主题配置和自定义样式方法

## AI 使用说明

> ⚠️ **AI 边界**：AI 无法看到幻灯片渲染效果，无法判断配色是否好看。
>
> **正确用法**：AI 列出主题/配色选项，由用户选择后生成配置代码。
> **错误用法**：让 AI "推荐好看的配色" 或 "优化样式"。

---

## 内置主题

reveal.js 提供 10 个内置主题，可直接在 frontmatter 中配置：

### 主题一览

| 主题 | 风格 | 适用场景 | 深浅 |
|------|------|---------|------|
| `black` | 黑底白字 | 科技、极简 | 深色 |
| `white` | 白底黑字 | 商务、学术 | 浅色 |
| `league` | 灰色背景 | 通用 | 浅灰 |
| `beige` | 米色背景 | 温和、文艺 | 浅色 |
| `sky` | 蓝色渐变 | 企业、清新 | 浅色 |
| `night` | 深蓝黑底 | 高端、科技 | 深色 |
| `serif` | 衬线字体 | 学术、传统 | 浅色 |
| `simple` | 极简白底 | 简洁、通用 | 浅色 |
| `solarized` | Solarized 配色 | 开发者 | 浅色 |
| `moon` | 深蓝配黄 | 创意、独特 | 深色 |

### 主题选择指南

```
演示场景？
├─ 学术报告 → serif / white
├─ 产品发布 → black / night
├─ 技术分享 → solarized / black
├─ 商务汇报 → league / sky
├─ 教程演示 → simple / white
└─ 创意展示 → moon / beige
```

---

## Frontmatter 配置

### 基本配置

```yaml
---
slideOptions:
  theme: white
  transition: slide
  backgroundTransition: fade
---
```

### 完整配置示例

```yaml
---
slideOptions:
  theme: night
  transition: slide
  backgroundTransition: fade
  slideNumber: true
  overview: true
  controls: true
  progress: true
  hash: true
  keyboard: true
  width: 1280
  height: 720
  margin: 0.1
  minScale: 0.2
  maxScale: 2.0
---
```

### 配置项说明

| 配置 | 说明 | 默认值 |
|------|------|--------|
| `theme` | 主题名称 | `black` |
| `transition` | 页面切换动画 | `slide` |
| `backgroundTransition` | 背景切换动画 | `fade` |
| `slideNumber` | 显示页码 | `false` |
| `controls` | 显示导航箭头 | `true` |
| `progress` | 显示进度条 | `true` |
| `width/height` | 幻灯片尺寸 | `1280x720` |

---

## 深浅主题适配

### 方案1: 使用内置主题

| 需求 | 推荐主题 |
|------|---------|
| 深色主题 | `black`, `night`, `moon` |
| 浅色主题 | `white`, `simple`, `beige`, `sky`, `serif` |
| 中性 | `league`, `solarized` |

### 方案2: 自定义 CSS

在 frontmatter 中注入自定义样式：

**深色主题模板：**

```yaml
---
slideOptions:
  theme: black
  css: |
    :root {
      --bg-color: #1a1a2e;
      --text-color: #eee;
      --accent-color: #00d9ff;
      --heading-color: #fff;
    }
    .reveal {
      background: var(--bg-color);
      color: var(--text-color);
    }
    .reveal h1, .reveal h2, .reveal h3 {
      color: var(--heading-color);
    }
    .reveal a {
      color: var(--accent-color);
    }
    .reveal code {
      background: #2d2d44;
      color: #ff79c6;
    }
---
```

**浅色主题模板：**

```yaml
---
slideOptions:
  theme: white
  css: |
    :root {
      --bg-color: #ffffff;
      --text-color: #333;
      --accent-color: #0066cc;
      --heading-color: #111;
    }
    .reveal {
      background: var(--bg-color);
      color: var(--text-color);
    }
    .reveal h1, .reveal h2, .reveal h3 {
      color: var(--heading-color);
    }
    .reveal a {
      color: var(--accent-color);
    }
    .reveal code {
      background: #f5f5f5;
      color: #d63384;
    }
---
```

---

## 常用样式片段

### 标题渐变色

```css
.reveal h1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

### 卡片样式

```css
.card {
  background: rgba(255,255,255,0.1);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
```

### 高亮文本

```css
.highlight {
  background: linear-gradient(120deg, #f6d365 0%, #fda085 100%);
  padding: 2px 8px;
  border-radius: 4px;
}
```

### 代码块美化

```css
.reveal pre {
  background: #1e1e2e;
  border-radius: 8px;
  padding: 16px;
}
.reveal code {
  font-family: 'JetBrains Mono', monospace;
}
```

---

## 配色方案推荐

### 科技感（深色）

| 元素 | 颜色 |
|------|------|
| 背景 | `#0d1117` |
| 主文字 | `#c9d1d9` |
| 标题 | `#58a6ff` |
| 强调 | `#238636` |
| 代码 | `#ff7b72` |

### 商务风（浅色）

| 元素 | 颜色 |
|------|------|
| 背景 | `#ffffff` |
| 主文字 | `#24292f` |
| 标题 | `#0969da` |
| 强调 | `#cf222e` |
| 代码 | `#8250df` |

### 清新绿（浅色）

| 元素 | 颜色 |
|------|------|
| 背景 | `#f0fff4` |
| 主文字 | `#1a202c` |
| 标题 | `#276749` |
| 强调 | `#38a169` |
| 代码 | `#2d3748` |

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| CSS 不生效 | 检查缩进，使用 `css: \|` 多行语法 |
| 字体显示异常 | 使用 Web 安全字体或导入 Google Fonts |
| 颜色对比度不够 | 使用 [对比度检查工具](https://webaim.org/resources/contrastchecker/) |
| 打印时样式丢失 | 这是正常现象，建议导出 HTML |

---

**参考**：[reveal.js 主题](https://revealjs.com/themes/)
