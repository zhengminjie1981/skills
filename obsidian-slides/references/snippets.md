# Obsidian Slides 代码片段参考

> 常用代码片段，可直接复制使用

## Fragment 动画

### 逐条显示

```html
<ul>
  <li class="fragment">第一条</li>
  <li class="fragment">第二条</li>
  <li class="fragment">第三条</li>
</ul>
```

### 动画类型

| 类名 | 效果 |
|------|------|
| `fragment` | 默认淡入 |
| `fragment fade-up` | 从下淡入 |
| `fragment fade-down` | 从上淡入 |
| `fragment fade-left` | 从右淡入 |
| `fragment fade-right` | 从左淡入 |
| `fragment grow` | 放大 |
| `fragment shrink` | 缩小 |
| `fragment highlight-red` | 变红 |
| `fragment highlight-green` | 变绿 |
| `fragment highlight-blue` | 变蓝 |

### 示例：列表动画

```html
<ol>
  <li class="fragment fade-up">第一步</li>
  <li class="fragment fade-up">第二步</li>
  <li class="fragment fade-up">第三步</li>
</ol>
```

---

## 背景设置

### 颜色背景

```html
<!-- 单页背景色 -->
<section data-background="#1a1a2e">
  内容
</section>
```

### 渐变背景

```html
<section data-background-gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)">
  内容
</section>
```

### 图片背景

```html
<section data-background="image.png">
  内容
</section>

<!-- 带透明度 -->
<section data-background="image.png" data-background-opacity="0.5">
  内容
</section>
```

### 视频背景

```html
<section data-background-video="video.mp4" data-background-video-loop>
  内容
</section>
```

### iframe 背景

```html
<section data-background-iframe="https://example.com">
  <div style="position: absolute; bottom: 20px;">
    叠加内容
  </div>
</section>
```

---

## 代码高亮

### 基本语法

```markdown
​```python
def hello():
    print("Hello, World!")
​```
```

### 行号高亮

```markdown
​```python [1-2|3|4]
def hello():
    name = "World"
    print(f"Hello, {name}!")
    return True
​```
```

- `[1-2]` 高亮第 1-2 行
- `[1-2|3|4]` 分步高亮（配合 fragment）

### 代码块主题

在 frontmatter 中设置：

```yaml
---
slideOptions:
  highlightTheme: monokai
---
```

**常用主题**：
- `monokai` - 深色
- `github` - 浅色
- `atom-one-dark` - 深色
- `atom-one-light` - 浅色

---

## 嵌入内容

### 嵌入 Obsidian 笔记

```markdown
![[其他笔记]]
```

### 嵌入网页

```html
<iframe src="https://example.com" width="100%" height="400"></iframe>
```

### 嵌入 PDF

```html
<iframe src="document.pdf" width="100%" height="500"></iframe>
```

---

## Speaker Notes

### 添加备注

```markdown
---

## 幻灯片标题

内容...

Note:
这是演讲者备注，只在演示者视图中显示。
可以写多行。
```

### 开启演示者视图

演示时按 `S` 键。

---

## 列布局

### 多列文本

```html
<div style="display: flex; gap: 20px;">
  <div style="flex: 1;">
    第一列内容
  </div>
  <div style="flex: 1;">
    第二列内容
  </div>
</div>
```

### 三列等分

```html
<div style="display: flex; gap: 16px;">
  <div style="flex: 1; text-align: center;">
    📊 数据
  </div>
  <div style="flex: 1; text-align: center;">
    📈 图表
  </div>
  <div style="flex: 1; text-align: center;">
    📝 总结
  </div>
</div>
```

---

## 特殊元素

### 引用块

```markdown
> "创新区分领导者和追随者。"
> — 史蒂夫·乔布斯
```

### 徽章/标签

```html
<span style="background: #38a169; color: white; padding: 4px 12px; border-radius: 16px; font-size: 14px;">
  新功能
</span>
```

### 分隔线

```markdown
---
```

用于分隔幻灯片页面。

### 图标（Emoji）

```markdown
✅ 完成
❌ 未完成
⏳ 进行中
🚀 发布
💡 提示
⚠️ 警告
```

---

## 导航控制

### 禁用某页的导航

```html
<section data-autoslide="5000">
  5 秒后自动跳转
</section>
```

### 垂直幻灯片

```markdown
---

## 水平幻灯片 1

内容

----

### 垂直幻灯片（向下滚动）

内容

----

### 继续垂直

内容

---

## 水平幻灯片 2
```

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| Fragment 不工作 | 确保在预览模式下查看 |
| 背景图片不显示 | 使用相对路径或确保图片在 vault 中 |
| 代码高亮不生效 | 检查语言标识符是否正确 |
| iframe 被阻止 | 某些网站禁止嵌入 |

---

**参考**：[reveal.js 文档](https://revealjs.com/)
