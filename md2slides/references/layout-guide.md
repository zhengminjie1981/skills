# md2slides 版式选择指南

> 阶段二（版式规划）时参考本文档。

---

## 1. 主题选择

AI 应在版式规划前确认主题，根据场景推荐：

| 场景 | 推荐主题 |
|------|---------|
| 商务汇报、客户演示、季报 | `professional-dark` |
| 正式文档、打印版、白底需求 | `professional-light` |
| 产品发布、All-hands、对外演讲台 | `keynote-white` |
| 工程师技术分享、架构评审、代码讲解 | `tech-terminal` |
| 年会、颁奖、公司纪念日、节日祝贺 | `celebration` |
| 员工关怀、团建、OKR 回顾、企业文化 | `caring-green` |
| 企业历史、品牌故事、文化宣讲、公关 | `warm-earth` |
| AI/创新产品展示、设计评审、创意提案 | `creative-gradient` |
| 极简风格、内部分享、学术/研究汇报 | `minimal-clean` |

> 用户已指定主题时直接采用，无需再问。未指定时，根据场景主动推荐并说明理由，请用户确认。

---

## 2. 版式规划流程

```
1. 逐页读取 MD 内容，分析：
   - 页面类型（封面/目录/内容/数据/结语）
   - 元素构成（标题、列表条数、是否有图片、是否有图表）
   - 内容密度（轻量 / 中等 / 密集）

2. 为每页选择最佳版式模板，写入 slide-tree.json 的 layout 字段：
   {
     "index": 3,
     "type": "content",
     "layout": {
       "template": "image-right",
       "imageWidth": "38%",
       "rationale": "6条数据要点为主体，图片辅助视觉"
     }
   }

   ⚠️  **每一页都必须有 layout 字段，无一例外。**
   缺少 layout ≠ 继承默认，而是强制回退到单列渲染（text-default 无��题样式）。
   即使某页适合 text-default，也必须显式写出 `"template": "text-default"`。

3. 输出完整 slide-tree.json，告知用户版式摘要
```

---

## 3. 版式模板速查

| 模板 | 适用场景 |
|------|---------|
| `text-default` | 通用内容页，标题 + 正文/列表 |
| `text-hero` | 重要观点突出，大标题 + 少量副文字 |
| `text-two-column` | 4-8 条要点，两列分栏（各半） |
| `text-three-column` | 3 组并列内容，三列分栏 |
| `statement` | 单一核心陈述，全幅文字 |
| `quote-center` | 引用语居中展示，适合结语 |
| `quote-side` | 引用语 + 旁边说明文字 |
| `image-right` | 文字/列表为主，图片占右侧 |
| `image-left` | 文字/列表为主，图片占左侧 |
| `image-top` | 图片在上，说明文字在下 |
| `image-bottom` | 说明文字在上，图片在下 |
| `image-fullbleed` | 图片铺满背景，文字叠加（结语首选） |
| `image-only` | 纯图片页，无文字内容 |
| `chart-full` | 单图表全屏，趋势/数据为主角 |
| `chart-right` | 图表占右侧，左侧为文字说明 |
| `chart-left` | 图表占左侧，右侧为文字说明 |
| `chart-bottom` | 图表在下，上方为说明 |
| `stat-cards` | 3-4 个关键数字/KPI 卡片展示 |
| `timeline-vertical` | 垂直时间线，适合发展历程 |
| `timeline-horizontal` | 水平时间线，适合阶段/步骤 |
| `compare-two` | 两组方案/选项对比 |
| `compare-three` | 三组方案/选项对比 |
| `cover-image-bg` | 封面：图片铺满背景 + 文字叠加 |
| `cover-split` | 封面：左右分割，一侧文字一侧图片 |
| `card-grid` | 通用内容卡片网格；`columns` 控制列数 |
| `section-header` | 章节分隔页；≤4个章节居中大标题，≥5个章节左标题+右TOC |
| `table-full` | 数据表格全屏展示 |

---

## 4. 版式选择原则

**第一步：判断内容性质（优先于数量）**

| 内容性质 | 判断标准 | 合理版式 | 不合理版式 |
|---------|---------|---------|----------|
| 并列关系 | 两组内容左右对等、可互换顺序 | `text-two-column` / `text-three-column` | `text-default` |
| 叙事流 | 连贯段落，有前后逻辑，不可拆分 | `text-default` | `text-two-column` |
| 顺序导航 | 目录/步骤，有先后顺序不可打乱 | `text-default` | `text-two-column` |
| 多维数据 | 每条有 2+ 个维度（指标/数值/对比） | `table-full` | 列表拆两列 |
| 独立个体 | 每条是完整单元（功能、特性、场景） | `card-grid` | `text-two-column` |
| KPI 数字 | 数字是主角，说明是辅助 | `stat-cards` | `text-default` |
| 主体+注解 | 一个核心图表 + 少量文字说明 | `chart-right` / `chart-left` | 平等两列 |

**不适用 stat-cards/card-grid 的内容格式**：

| 格式 | 问题 | 推荐替代 |
|------|------|---------|
| 4条以内"关键词：说明" | 卡片视觉太弱，分割感强 | `text-default` + 列表项内 **关键词** 加粗描述 |
| 长段落描述（>30字/项） | 卡片溢出，阅读困难 | `text-default` 或 `card-grid` 配合精简文案 |

**第二步：数量作为辅助参考（内容性质已确定为并列时）**

```
并列内容 + 2 组 -> text-two-column
并列内容 + 3 组 -> text-three-column
并列内容 + 4-6 项独立单元 -> card-grid（columns:2 或 3）
```

**按页面类型的完整路径**：

```
封面（cover）
  有图片 -> cover-image-bg / cover-split
  无图片 -> text-hero

目录（toc）
  -> text-default（标题 + 列表）
  ★ 禁止用多列：目录是顺序导航，不是并列关系；多列会破坏阅读顺序

章节页（section）
  -> section-header（脚本自动按章节数切换子变体）
  ★ ≤4 个章节：居中大标题 + 底部进度点
  ★ ≥5 个章节：左侧标题 + 右侧 TOC 列表，当前章节高亮

**内容量判断原则**：

| `<li>` 数量 | 推荐版式 | 理由 |
|-----------|---------|------|
| 1-4 条 | text-default | 单列完整展示，无空白 |
| 5-8 条 | text-two-column | 双列均衡，视觉舒适 |
| 9+ 条 | text-three-column | 三列紧凑，信息密集 |

**例外**：
- 叙事流/步骤（有前后逻辑）→ text-default（无论多少条）
- 独立完整单元（功能、特性）→ card-grid（4-6 条）
- KPI 数字（3-6 个）→ stat-cards

内容页（content）
  有图片 + 4条以内要点 -> image-right / image-left
  有图片 + 6条要点     -> image-right（imageWidth: 35%）
  无图片，内容性质优先：
    叙事流（连续段落/有前后逻辑）    -> text-default（无论多少条）
    顺序导航（步骤/目录）            -> text-default（禁止多列）
    多维数据（每条有指标/值/对比）   -> table-full（条目数 > 6 时同样适用）
    并列关系（2组）                  -> text-two-column
    并列关系（3组）                  -> text-three-column
    独立个体（4-6项，每项是完整单元）-> card-grid
    KPI 数字（3-6个）                -> stat-cards
    时间线/历程                      -> timeline-vertical / timeline-horizontal
    对比（2-3方案）                  -> compare-two / compare-three
  ★ 多组「标题+列表」结构分列：加 splitMode=group
    columns 参数（stat-cards/card-grid）：
      3项 -> 默认（单行）
      4项 -> columns:2（2×2）
      5项 -> columns:3（2+3）
      6项 -> columns:3（2×3）

数据页（data）
  单图表               -> chart-full
  图表 + 文字说明      -> chart-right / chart-left
  ★ 图表尺寸/位置可在 layout 中覆盖（见 §5）

结语页（outro）
  有图片               -> image-fullbleed
  有引用语             -> quote-center
  无图片               -> text-hero
```

---

## 5. Layout 参数速查

以下参数可在 slide-tree.json 的 `layout` 字段中设置：

**图表参数**：

| 参数 | 作用 | 示例 |
|------|------|------|
| `chartWidth` | 图表宽度 | `"90%"` |
| `chartHeight` | 图表高度 | `"80%"` |
| `chartPosition` | 图表位置 | `"right"` / `"left"` / `"bottom"` / `"full"` |

**标题参数**：

| 参数 | 作用 | 示例 |
|------|------|------|
| `titleSize` | 标题字体大小 | `"2.5em"` / `"36px"` |
| `titleColor` | 标题颜色 | `"#FFD700"` / `"gold"` |

**分列参数**：

| 参数 | 作用 | 适用版式 |
|------|------|---------|
| `splitMode` | 分列模式（`item` / `group`）| text-two-column, text-three-column |
| `columns` | 卡片列数 | stat-cards, card-grid |
| `customCss` | 页面级自定义 CSS | 所有版式 |

**示例**：

```json
{
  "index": 5,
  "layout": {
    "template": "chart-right",
    "chartWidth": "70%",
    "chartHeight": "75%",
    "titleSize": "1.8em"
  }
}
```

---

## 6. 版式规划自检（规划完成后执行）

**第 0 步：完整性校验（写入前必须通过）**

```
Q1：统计 MD 文件中 --- 分页符的数量，得出总页数 N
Q2：slide-tree.json 中是否有 N 个 slide 节点，且每个节点都有 layout 字段？
    如果否 → 补全缺失页面的 layout 后再写入，不允许跳过任何页
```

对每个 text-two-column / text-three-column 页面执行：

```
1. 内容性质检查
   Q：两列内容是「并列/对比关系」吗？可以互换顺序而不破坏语义吗？
   如果否 → 降级为 text-default
   特别检查：目录/步骤类内容 → 必须降级（顺序导航禁用多列）

2. 多维数据检查
   Q：每个列表项是否有 2+ 个维度（如：指标名 + 数值 + 同比）？
   如果是 → 改用 table-full

3. 列均衡检查
   Q：估算左右两列字数比，是否 ≥ 0.5？
   如果否 → 降级为 text-default，或改用 :::col 手动调整分列点

4. 条目数量检查（card-grid 适用性）
   Q：列表项是否为独立完整单元（每条都能单独成立）？
   如果是 → 优先 card-grid，而非强行分列
```

检查通过后才写入 slide-tree.json。如有降级，在版式摘要中注明原因。

*版本: 1.3 | 最后更新: 2026-03-25*
