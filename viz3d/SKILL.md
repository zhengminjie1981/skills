---
name: viz3d
description: |
  通过自然语言生成3D场景HTML文件。

  **触发场景**：
  - 三维可视化、3D场景、画点位、空间布局
  - 场景创建、修改、调整

  **不触发场景**：
  - 2D图表、统计图表、地图可视化

allowed-tools: [Write, Edit]
argument-hint: "<项目名称>"
feedback:
  enabled: true
  version: "2.0.0"
  author: "viz3d-team"
---

# Viz3D - 3D场景生成器

> 我生成配置文件和HTML文件。你修改配置后刷新或重新生成HTML即可。

## 技术选择决策

### 首次创建
```
点位数量？
├─ < 10个 → 直接写JSON坐标
├─ 10-100个且规则分布 → JS distribution（推荐）
└─ 复杂筛选逻辑 → Python生成完整JSON
```

### 后续修改
```
修改类型？
├─ 参数修改 → 直接改JSON数值
├─ 结构调整 → 重新生成HTML
└─ 复杂计算 → Python生成新配置
```

### 生成方式
```
用户需求？
├─ 要单文件（易分享） → 配置注入HTML
└─ 要实时刷新 → 配置分离 + HTTP服务器
```

## 必须遵守的约束

### ❌ 禁止做的事
- **禁止用Python计算简单几何**（圆形、网格等）
- **禁止生成完全展开的坐标列表**（使用distribution）
- **禁止每次修改都重新生成整个HTML**（优先改配置）
- **禁止向用户展示代码**

### ✅ 必须做的事
- **规则分布使用distribution配置**
- **复杂逻辑用Python一次生成**
- **修改配置后告诉用户刷新或重新生成**
- **只给用户HTML文件位置**

## 配置格式

### 单个点
```json
{
  "id": "ga",
  "position": [-2.5, 0, 0],
  "style": {"color": "#ff4444", "size": 0.8}
}
```

### 多个点（使用distribution）
```json
{
  "id": "e1",
  "distribution": {
    "type": "circle",
    "count": 48,
    "radius": 25,
    "center": [0, 60, 0],
    "offset": 3.75
  }
}
```

**支持的分布类型**：

| 类型 | 参数 | 适用场景 |
|------|------|----------|
| circle | count, radius, center, offset | 圆形分布 |
| grid | rows, cols, spacing, center | 网格分布 |
| line | count, spacing, axis, center | 线性分布 |
| layers | layers: [{radius, count, height}] | 多层圆环 |

### 连线配置
```json
{
  "from": "e1",      // 可引用distribution组
  "to": "e0a",
  "style": {"color": "#4488ff", "opacity": 0.4}
}
```

## 问题排查优先级

连线不显示？
1. 检查 from/to 的ID是否存在
2. 检查是否引用了distribution组
3. 检查 opacity 是否太低（< 0.1）
4. 检查浏览器控制台警告

## 典型对话

```
用户: 创建起降场场景
AI: ✓ 已生成 scene.json 和 preview.html

用户: 添加48个e1点，圆形分布，半径25米
AI: ✓ 已添加 distribution 配置
    刷新浏览器查看

用户: 把半径改成30米
AI: ✓ 已修改 radius: 30
    刷新浏览器查看

用户: 禁用前后各8个点
AI: [复杂筛选，用Python计算]
    ✓ 已生成完整配置
```

## 文件结构

```
~/.claude/skills/viz3d/projects/{项目名}/
├── scene.json      ← 配置文件（简单修改编辑这个）
└── preview.html    ← 预览文件（打开这个查看）
```

## 数据验证规则

配置会自动验证以下内容：
- radius/spacing/count 必须为正数
- count 建议范围：1-1000
- opacity 建议范围：0-1
- color 格式：#rrggbb 或 0xrrggbb

**验证失败时**：浏览器控制台显示错误信息

---

**版本**: 2.0 | **核心原则**: 简化配置，按需选择技术
