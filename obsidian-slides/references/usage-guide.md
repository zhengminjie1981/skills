# Obsidian Slides 使用指南

> 本指南帮助用户快速上手 Obsidian Slides Extended 插件

## 一、安装 Slides Extended 插件

### 插件说明

**Slides Extended 与核心 Slides 插件的关系：**

| 插件 | 类型 | 渲染引擎 | 说明 |
|------|------|---------|------|
| **核心 Slides** | Obsidian 内置 | Obsidian 原生 | 基础演示，右键标签页 → "开始演示" |
| **Slides Extended** | 社区插件 | reveal.js | 高级功能（推荐用于复杂幻灯片） |

> 💡 两者**独立运行，互不冲突**，可根据需要选择使用。

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

## 三、AI 对话使用示例

> 以下示例展示如何通过与 AI 对话，让 AI 帮你完成 Slides 的创建和配置

### 示例 1：从零创建幻灯片

```
👤 用户：帮我创建一个产品介绍幻灯片，产品是一个 AI 写作助手

🤖 AI：好的，我来帮你创建产品介绍幻灯片。

请先确认几个信息：
1. 目标受众是谁？（开发者/普通用户/企业客户）
2. 演示时长大概多久？（5分钟/10分钟/20分钟）
3. 风格偏好？（深色科技风/浅色商务风）

👤 用户：面向普通用户，5分钟，浅色商务风

🤖 AI：明白了，我将使用 product-pitch 模板，浅色主题，生成 5 页幻灯片。

[生成 Markdown 文件]
```

**AI 生成的结果**：

```markdown
---
slideOptions:
  theme: white
  transition: slide
---

## AI 写作助手

**让每个人都能轻松写出好文章**

演讲者 | 日期

---

## 痛点

**写作者的困扰**

<ul>
  <li class="fragment">不知道如何开头</li>
  <li class="fragment">担心语法和措辞</li>
  <li class="fragment">效率低下，反复修改</li>
</ul>

---
...（后续页面）
```

---

### 示例 2：内容转换

```
👤 用户：把下面这段内容转成幻灯片：

# 项目周报
本周完成了用户登录模块的开发，修复了3个bug。
下周计划完成支付模块。
遇到的问题是第三方API不稳定。

🤖 AI：好的，我来将这段内容转换为 3 页幻灯片结构。

[生成结果]
```

**AI 生成的结果**：

```markdown
---
slideOptions:
  theme: league
---

## 项目周报

---

## 本周进展

**已完成**

- ✅ 用户登录模块开发
- ✅ 修复 3 个 bug

---

## 问题与计划

<split even>

<div>

**遇到的问题**
- 第三方 API 不稳定

</div>

<div>

**下周计划**
- 完成支付模块

</div>

</split>
```

---

### 示例 3：布局生成

```
👤 用户：我需要做一个左右对比的页面，左边是旧方案，右边是新方案

🤖 AI：好的，我来生成左右对比布局。
```

**AI 生成的代码**：

```markdown
## 方案对比

<split even>

<div>

### 旧方案

- ❌ 效率低
- ❌ 成本高
- ❌ 难维护

</div>

<div>

### 新方案

- ✅ 效率提升 3 倍
- ✅ 成本降低 50%
- ✅ 易于扩展

</div>

</split>
```

---

### 示例 4：主题配置

```
👤 用户：给这个幻灯片配置一个深色主题

🤖 AI：以下是可用的深色主题：

| 主题 | 风格 |
|------|------|
| `black` | 黑底白字，极简 |
| `night` | 深蓝黑底，高端科技感 |
| `moon` | 深蓝配黄，创意独特 |

你想用哪个？

👤 用户：用 night

🤖 AI：好的，生成 frontmatter 配置：
```

**AI 生成的 frontmatter**：

```markdown
---
slideOptions:
  theme: night
  transition: slide
  css: |
    .reveal h1, .reveal h2 { color: #58a6ff; }
    .reveal { color: #c9d1d9; }
    .reveal a { color: #00d9ff; }
---
```

---

### 示例 5：添加动画效果

```
👤 用户：我想让列表逐条显示，怎么做？

🤖 AI：使用 `fragment` 类即可实现。示例：

```html
<ul>
  <li class="fragment">第一条</li>
  <li class="fragment">第二条</li>
  <li class="fragment">第三条</li>
</ul>
```

更多动画效果：

| 效果 | 代码 |
|------|------|
| 从下淡入 | `class="fragment fade-up"` |
| 放大 | `class="fragment grow"` |
| 高亮红色 | `class="fragment highlight-red"` |

---

### 示例 6：特定布局需求

```
👤 用户：我需要做一个左右对比的页面，左边是旧方案，右边是新方案

🤖 AI：使用 `<split>` 标签实现左右对比布局：
```

**AI 生成的代码**：

```markdown
## 方案对比

<split even>

<div>

### 旧方案

- ❌ 效率低
- ❌ 成本高
- ❌ 难维护

</div>

<div>

### 新方案

- ✅ 效率提升 3 倍
- ✅ 成本降低 50%
- ✅ 易于扩展

</div>

</split>
```

---

### 示例 7：代码演示页

```
👤 用户：我要展示一段 Python 代码，还需要逐行讲解

🤖 AI：使用代码块 + 行号高亮实现：
```

**AI 生成的代码**：

```markdown
## 代码演示

### 完整代码

​```python
def process_data(items):
    result = []
    for item in items:
        if item.valid:
            result.append(item.value)
    return result
​```

---

### 逐行讲解

​```python [1|2-4|5-6]
def process_data(items):
    result = []
    for item in items:
        if item.valid:
            result.append(item.value)
    return result
​```

- 第 1 行：函数定义
- 第 2-4 行：遍历并筛选
- 第 5-6 行：返回结果
```

---

### 示例 8：使用转换脚本

```
👤 用户：我有一个很长的 Markdown 文档，想快速转成幻灯片

🤖 AI：可以使用 `md2slides.py` 脚本自动转换：

```bash
python scripts/md2slides.py your-doc.md -o slides.md --theme dark
```

脚本会：
- 自动按 H2 标题分页
- 添加 frontmatter 配置
- 使用指定的深色主题

---

### 示例 9：复制模板快速开始

```
👤 用户：我要做一个技术分享，有没有现成的模板？

🤖 AI：有！推荐使用 `technical.md` 模板，结构为：

1. 标题页
2. 背景（为什么重要）
3. 架构图
4. 核心代码
5. 演示
6. 总结
7. Q&A

你可以直接复制：
`assets/templates/technical.md`

然后替换 `{{技术主题}}` 等占位符即可。
```

---

### 示例 10：深浅主题切换

```
👤 用户：模板里的深色版本和浅色版本怎么用？

🤖 AI：模板文件中包含两个版本的代码：

**使用方法**：
1. 打开模板文件（如 `product-pitch.md`）
2. 找到 `<!-- 深色版本 - DARK -->` 部分 → 复制使用
3. 或找到 `<!-- 浅色版本 - LIGHT -->` 部分 → 复制使用

**快速切换**：只需修改 frontmatter 的 `theme` 值：
- 深色：`theme: night` 或 `theme: black`
- 浅色：`theme: white` 或 `theme: league`
```

---

## 四、快速参考卡

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

**参考资源**：
- [Slides Extended 插件](https://github.com/ebullient/obsidian-slides-extended)
- [reveal.js 文档](https://revealjs.com/)
- [核心 Slides 插件帮助](https://help.obsidian.md/plugins/slides)
