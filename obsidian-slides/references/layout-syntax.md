# Obsidian Slides 布局语法参考

> 本文档介绍 Slides Extended 插件的布局语法

## 核心概念

Slides Extended 基于 reveal.js，扩展了两种布局标签：

| 标签 | 用途 | 特点 |
|------|------|------|
| `<grid>` | 网格布局 | 灵活拖拽、支持背景 |
| `<split>` | 分栏布局 | 简单左右/上下分割 |

---

## Grid 布局

### 基本语法

```html
<grid drag="宽度 高度" drop="x y" bg="颜色/图片" flow="方向">
  内容
</grid>
```

### 属性说明

| 属性 | 说明 | 示例 |
|------|------|------|
| `drag` | 占用空间（宽×高，单位：格子） | `drag="50 100"` |
| `drop` | 放置位置（x y 坐标） | `drop="0 0"` |
| `bg` | 背景颜色或图片 | `bg="#1a1a1a"` 或 `bg="image.png"` |
| `flow` | 内容排列方向 | `flow="col"`（纵向）或 `flow="row"`（横向） |

### 坐标系统

- 整个幻灯片为 100×100 的网格
- 左上角为 (0, 0)
- 右下角为 (100, 100)

```
(0,0) ───────────── (100,0)
  │                    │
  │                    │
  │                    │
(0,100) ─────────── (100,100)
```

---

## 常用布局模式

### 1. 左右分栏（50/50）

```html
<grid drag="50 100" drop="0 0">
  左侧内容
</grid>

<grid drag="50 100" drop="50 0">
  右侧内容
</grid>
```

### 2. 左右分栏（60/40）

```html
<grid drag="60 100" drop="0 0">
  主要内容
</grid>

<grid drag="40 100" drop="60 0">
  次要内容
</grid>
```

### 3. 三栏等分

```html
<grid drag="33 100" drop="0 0">
  第一栏
</grid>

<grid drag="33 100" drop="33 0">
  第二栏
</grid>

<grid drag="34 100" drop="66 0">
  第三栏
</grid>
```

### 4. 图文混排（左图右文）

```html
<grid drag="45 100" drop="0 0" bg="image.png">
</grid>

<grid drag="55 100" drop="45 0" flow="col">
  ## 标题
  文字内容...
</grid>
```

### 5. 顶部标题 + 底部内容

```html
<grid drag="100 20" drop="0 0">
  ## 标题
</grid>

<grid drag="100 80" drop="0 20">
  主要内容
</grid>
```

### 6. 引用 + 正文

```html
<grid drag="30 100" drop="0 0">
  > "这是一段引用"
  > — 作者
</grid>

<grid drag="70 100" drop="30 0">
  正文内容...
</grid>
```

---

## Split 布局

### 基本语法

```html
<split even>
  <div>
    左侧内容
  </div>

  <div>
    右侧内容
  </div>
</split>
```

### 属性说明

| 属性 | 说明 | 值 |
|------|------|---|
| `even` | 等分 | 无需值 |
| `left="比例"` | 左侧占比 | `left="2"` 表示 2:1 |
| `right="比例"` | 右侧占比 | `right="2"` 表示 1:2 |

### 示例

```html
<!-- 等分 -->
<split even>
  <div>左侧</div>
  <div>右侧</div>
</split>

<!-- 2:1 分割 -->
<split left="2">
  <div>占 2/3</div>
  <div>占 1/3</div>
</split>
```

---

## Grid vs Split 选择

| 场景 | 推荐 | 原因 |
|------|------|------|
| 简单左右分栏 | `<split>` | 语法简单 |
| 需要背景图片 | `<grid>` | 支持 bg 属性 |
| 三栏及以上 | `<grid>` | 更灵活 |
| 精确位置控制 | `<grid>` | 坐标系统 |
| 快速原型 | `<split>` | 快速编写 |

---

## 深色/浅色主题适配

### 深色主题

```html
<grid drag="100 100" drop="0 0" bg="#1a1a2e">
  <span style="color: #eee">白色文字</span>
</grid>
```

### 浅色主题

```html
<grid drag="100 100" drop="0 0" bg="#f5f5f5">
  <span style="color: #333">深色文字</span>
</grid>
```

---

## 常见问题

| 问题 | 解决方案 |
|------|---------|
| 布局不生效 | 检查 drag/drop 数值是否超出 100 |
| 内容溢出 | 减小 drag 尺寸或精简内容 |
| 背景图片不显示 | 使用相对路径或确保图片在 vault 中 |
| 中文换行异常 | 添加 `flow="col"` 属性 |

---

**参考**：[Slides Extended 官方文档](https://github.com/ebullient/obsidian-slides-extended)
