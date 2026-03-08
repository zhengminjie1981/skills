# Obsidian Slides 使用指南

> 本指南帮助用户快速上手 Obsidian Slides Extended 插件

## 一、安装 Slides Extended 插件

### 步骤 1：开启第三方插件

1. 打开 Obsidian
2. 进入 **设置** → **第三方插件**
3. 关闭 **安全模式**

### 步骤 2：安装插件

1. 点击 **浏览** 按钮
2. 搜索 **Slides Extended**
3. 点击 **安装**
4. 安装完成后点击 **启用**

### 步骤 3：配置插件（可选）

进入 **设置** → **Slides Extended**，可配置：

| 选项 | 说明 | 建议值 |
|------|------|--------|
| Default Theme | 默认主题 | 按需选择 |
| Transition | 切换动画 | slide |
| Slide Number | 显示页码 | 开启 |
| Controls | 显示导航 | 开启 |

---

## 二、基本使用方法

### 创建幻灯片

1. 在 Obsidian 中新建一个 Markdown 文件
2. 添加 frontmatter 配置
3. 使用 `---` 分隔不同页面
4. 点击右侧的 **幻灯片图标** 或使用快捷键预览

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl/Cmd + P` → "Slides: Start" | 开始演示 |
| `→` / `Space` | 下一页 |
| `←` | 上一页 |
| `↑` / `↓` | 垂直导航 |
| `F` | 全屏模式 |
| `O` | 概览模式 |
| `S` | 演讲者视图 |
| `Esc` | 退出演示 |

### 导出功能

**Slides Extended 自带导出功能**：

1. 打开幻灯片预览
2. 点击右下角的 **导出按钮**（或右键菜单）
3. 选择导出格式：
   - **PDF** - 直接导出为 PDF 文件
   - **HTML** - 导出为独立网页文件

> 💡 提示：PDF 导出会保留当前主题样式，动画会展开为多个页面。

---

## 三、使用示例

### 示例 1：最简单的幻灯片

```markdown
---
slideOptions:
  theme: white
---

## 欢迎使用 Obsidian Slides

这是一个简单的演示文稿

---

## 第二页

更多内容...
```

### 示例 2：带列表和动画

```markdown
---
slideOptions:
  theme: night
---

## 项目进展

**本周完成**

<ul>
  <li class="fragment">完成了用户认证模块</li>
  <li class="fragment">优化了数据库查询</li>
  <li class="fragment">修复了 3 个 bug</li>
</ul>
```

### 示例 3：左右分栏布局

```markdown
---
slideOptions:
  theme: league
---

## 产品介绍

<split even>

<div>

**核心功能**

- 功能一
- 功能二
- 功能三

</div>

<div>

**用户价值**

- 价值一
- 价值二
- 价值三

</div>

</split>
```

### 示例 4：三栏卡片布局

```markdown
---
slideOptions:
  theme: white
---

## 方案对比

<div style="display: flex; gap: 20px;">
  <div style="flex: 1; background: #f5f5f5; padding: 20px; border-radius: 8px;">
    <h4>方案 A</h4>
    <ul>
      <li>优点一</li>
      <li>优点二</li>
    </ul>
  </div>
  <div style="flex: 1; background: #e8f5e9; padding: 20px; border-radius: 8px;">
    <h4>方案 B</h4>
    <ul>
      <li>优点一</li>
      <li>优点二</li>
    </ul>
  </div>
  <div style="flex: 1; background: #e3f2fd; padding: 20px; border-radius: 8px;">
    <h4>方案 C</h4>
    <ul>
      <li>优点一</li>
      <li>优点二</li>
    </ul>
  </div>
</div>
```

### 示例 5：代码演示

```markdown
---
slideOptions:
  theme: black
  highlightTheme: monokai
---

## 代码示例

**Python 快速排序**

```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + [pivot] + quicksort(right)
​```

---

## 逐行解释

```python [1-2|3-4|5-6|7]
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + [pivot] + quicksort(right)
​```
```

### 示例 6：带背景图片

```markdown
---
slideOptions:
  theme: night
---

<section data-background="cover.jpg" data-background-opacity="0.3">

## 年度总结

**2025 年回顾**

<p style="font-size: 24px;">
  感谢团队的努力付出
</p>

</section>
```

### 示例 7：引用和强调

```markdown
---
slideOptions:
  theme: white
---

## 设计理念

<grid drag="30 100" drop="0 0">

> "简单是复杂的终极形式。"
>
> — 达·芬奇

</grid>

<grid drag="70 100" drop="30 0" flow="col">

**核心原则**

1. **简洁**：去除多余元素
2. **清晰**：信息传达明确
3. **一致**：风格统一

</grid>
```

### 示例 8：数据展示

```markdown
---
slideOptions:
  theme: league
---

## 季度数据

<div style="display: flex; gap: 24px; margin-top: 30px;">
  <div style="flex: 1; text-align: center;">
    <div style="font-size: 48px; font-weight: bold; color: #4CAF50;">+25%</div>
    <p>用户增长</p>
  </div>
  <div style="flex: 1; text-align: center;">
    <div style="font-size: 48px; font-weight: bold; color: #2196F3;">1.2M</div>
    <p>活跃用户</p>
  </div>
  <div style="flex: 1; text-align: center;">
    <div style="font-size: 48px; font-weight: bold; color: #FF9800;">98%</div>
    <p>满意度</p>
  </div>
  <div style="flex: 1; text-align: center;">
    <div style="font-size: 48px; font-weight: bold; color: #9C27B0;">50+</div>
    <p>新功能</p>
  </div>
</div>
```

### 示例 9：时间线

```markdown
---
slideOptions:
  theme: white
---

## 项目时间线

| 阶段 | 时间 | 交付物 |
|------|------|--------|
| 需求分析 | 1-2 周 | 需求文档 |
| 设计 | 2-3 周 | 设计稿 |
| 开发 | 4-6 周 | 功能模块 |
| 测试 | 2 周 | 测试报告 |
| 上线 | 1 周 | 正式发布 |
```

### 示例 10：深色主题完整示例

```markdown
---
slideOptions:
  theme: night
  transition: slide
  slideNumber: true
  css: |
    .reveal h1, .reveal h2 { color: #58a6ff; }
    .reveal { color: #c9d1d9; }
---

## 深色主题演示

适合科技、极简风格

---

## 功能亮点

<div style="display: flex; gap: 24px;">
  <div style="flex: 1; background: rgba(255,255,255,0.05); padding: 24px; border-radius: 12px;">
    <h4>⚡ 快速</h4>
    <p style="color: #888;">毫秒级响应</p>
  </div>
  <div style="flex: 1; background: rgba(255,255,255,0.05); padding: 24px; border-radius: 12px;">
    <h4>🔒 安全</h4>
    <p style="color: #888;">企业级加密</p>
  </div>
  <div style="flex: 1; background: rgba(255,255,255,0.05); padding: 24px; border-radius: 12px;">
    <h4>💡 智能</h4>
    <p style="color: #888;">AI 驱动</p>
  </div>
</div>

---

## 联系我们

<div style="text-align: center;">

**开始使用**

<p style="margin-top: 30px;">
  <a href="#" style="background: #58a6ff; color: white; padding: 12px 32px; border-radius: 8px; text-decoration: none;">
    立即体验
  </a>
</p>

</div>
```

---

## 四、常见使用场景

### 场景 1：周报汇报

```
用户: 帮我创建一个周报幻灯片
AI:
  1. 读取 assets/templates/meeting-report.md
  2. 生成包含：标题页、进展、数据、问题、计划的幻灯片
  3. 询问是否需要深色/浅色主题
```

### 场景 2：产品演示

```
用户: 我需要给客户演示我们的新产品
AI:
  1. 询问产品名称和核心卖点
  2. 使用 product-pitch 模板
  3. 生成：痛点 → 方案 → 优势 → 演示 → CTA 结构
```

### 场景 3：技术分享

```
用户: 帮我做一个技术分享的幻灯片，主题是 Docker
AI:
  1. 使用 technical 模板
  2. 生成：背景 → 架构 → 代码 → 演示 → 总结
  3. 添加代码高亮配置
```

### 场景 4：从文档转换

```
用户: 把这篇笔记转成幻灯片
AI:
  1. 分析文档结构
  2. 按 H2 标题分页
  3. 应用默认主题
  4. 或使用命令：python scripts/md2slides.py input.md -o slides.md
```

---

## 五、常见问题

### Q1: 幻灯片不显示？

**检查项**：
- [ ] 已安装并启用 Slides Extended 插件
- [ ] frontmatter 格式正确（`---` 包围）
- [ ] 使用 `---` 分隔页面（不是 `***`）

### Q2: 布局不生效？

**检查项**：
- [ ] `<grid>` 和 `<split>` 标签正确闭合
- [ ] drag/drop 数值不超过 100
- [ ] 在预览模式下查看（编辑模式不渲染）

### Q3: 中文显示异常？

**解决方案**：在 frontmatter 添加字体配置

```yaml
slideOptions:
  css: |
    .reveal { font-family: "Microsoft YaHei", sans-serif; }
```

### Q4: 导出的 PDF 样式不对？

**解决方案**：
1. 先在 Slides Extended 中预览，确认样式正确
2. 使用插件自带的导出功能（不是浏览器打印）
3. 动画会展开为多页，这是正常行为

### Q5: 如何嵌入视频？

```markdown
<!-- 视频 -->
<video src="demo.mp4" controls width="100%"></video>

<!-- 背景视频 -->
<section data-background-video="demo.mp4" data-background-video-loop>
  内容
</section>
```

---

## 六、快速参考卡

### 分页

```markdown
---
```

### Fragment 动画

```html
<li class="fragment">逐条显示</li>
<li class="fragment fade-up">从下淡入</li>
```

### 左右分栏

```html
<split even>
  <div>左</div>
  <div>右</div>
</split>
```

### 背景

```html
<section data-background="#1a1a2e">深色背景</section>
<section data-background="image.jpg">图片背景</section>
```

### 代码高亮

```markdown
​```python [1-2|3-4]
代码
​```
```

---

**参考资源**：
- [Slides Extended 插件](https://github.com/ebullient/obsidian-slides-extended)
- [reveal.js 文档](https://revealjs.com/)
