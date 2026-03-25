# md2slides 调整操作指南

> 收到用户调整请求时参考本文档。

---

## 1. 调整类型判断

| 操作 | 路径 | 修改 MD | 修改 tree |
|------|------|---------|----------|
| 修改标题/要点/段落文字 | 内容变更 | 是 | 否 |
| 增删列表条目 | 内容变更 | 是 | 否 |
| 增加/删除/移动页面 | 内容变更 | 是 | 否 |
| 修改图表类型、数据源、字段 | 内容变更 | 是 | 否 |
| 修改字体大小/颜色/粗细 | 样式调整 | 否 | 自动（从 HTML 反向同步）|
| 修改间距/对齐/背景色 | 样式调整 | 否 | 自动（从 HTML 反向同步）|
| 修改图表位置/宽高百分比 | 样式调整 | 否 | 自动（从 HTML 反向同步）|
| **换版式/换布局** | **版式切换** | **否** | **是（layout 字段）** |

**快速判断**：
- 修改文字/要点/标题文本 → 内容变更
- 增加/删除/移动页面 → 内容变更
- 修改图表类型/数据源/字段 → 内容变更
- 修改字体大小/颜色/粗细 → 样式调整
- 修改间距/对齐/背景色 → 样式调整
- 修改图表位置/宽高百分比 → 样式调整

---

## 2. 场景流程

### 场景 A：从原始材料生成演示文稿

```
用户: 帮我把下面这份产品季报做成演示文稿：[材料]

AI 步骤：
1. 分析材料，识别可视化数据段落
2. 规划页面结构（封面/目录/内容页/数据页/结语）
3. 提取数据 → 创建 data/{名称}-s{N}-{描述}.csv
4. 生成 MD 文件，含 <!-- chart --> 块
5. 展示摘要（页数 + 每页标题）并确认

AI: 已完成内容策划，共 8 页：
    1 封面 / 2 目录 / 3-6 内容页 / 7 数据页（含折线图）/ 8 结语
    涉及数据文件：data/report-s7-users.csv（已创建）
    请确认内容，或告知需要调整的地方。

用户: 好的，继续

AI: 请选择宽高比：A. 16:9（推荐） B. 4:3
用户: 16:9

AI: 根据商务汇报风格，建议 professional-dark 主题。是否采用？
用户: 好的

AI 执行：python scripts/convert.py --input report.md --output report.html --tree slide-tree.json
AI: HTML 已生成：report.html（8 页）
```

### 场景 B：样式调整

```
用户: 把第3页的标题改成黄色，字大一点

AI 步骤：
1. 读取 slide-tree.json，定位 s3-title1
2. 修改 HTML 中 id="s3-title1" 元素的 style：
   color → #FFD700；fontSize 1.9em → 2.3em

AI: 已更新 s3-title1：
    fontSize: 1.9em → 2.3em
    color: → #FFD700
    HTML 文件已保存。（下次重新生成时 tree 自动同步）
```

### 场景 C：内容变更

```
用户: 第4页加一条要点："Q4 净利润首次转正"

AI 步骤：
1. 判断为内容变更（增加列表条目）
2. 定位 MD 第4页（<!-- Slide 4 -->）
3. 在列表末尾添加该条目
4. 运行 convert.py --preserve-styles
5. 汇报结果

AI: 已更新第4页列表（+1条）。重新生成完成，已有样式全部保留。
```

### 场景 D：含图表的内容变更

```
用户: 第5页的柱状图改成折线图

AI 步骤：
1. 判断为内容变更（修改图表类型）
2. 定位 MD 第5页的 <!-- chart --> 块
3. 修改 type: bar → type: line
4. 运行 convert.py --preserve-styles
5. 汇报（图表 position/width/height 样式已保留）
```

### 场景 E：版式切换

```
用户: 把第7页换成双栏布局

AI 步骤：
1. 读取 slide-tree.json，找到 index=7 的 slide 节点
2. 修改 layout.template：原值 -> "text-two-column"
3. 如需调整辅助参数（如 imageWidth），同步修改 layout 其他字段
4. 运行 convert.py（无需 --preserve-styles）：
   python scripts/convert.py --input demo.md --output demo.html --tree slide-tree.json
5. 告知修改结果
```

### 场景 F：多个调整请求（HTML 优先迭代）

**适用场景**：用户连续提出多个调整请求（样式+内容混合）

```
用户: 第3页标题改大一点
AI: 1. 直接改 HTML（style="font-size: 2.5em"）
    2. 记录到"待同步清单"

用户: 再大一点，第5页加一条要点
AI: 1. 直接改 HTML（style="font-size: 3em"）
    2. 直接改 MD（新增列表项）
    3. 更新清单

用户: 好了，就这样
AI: 1. 运行 convert.py --preserve-styles（样式 → tree.json）
    2. 验证重新生成的 HTML 与修改后的一致
    3. 输出最终变更报告
```

**AI 待同步清单示例**（会话内维护）：
```
样式变更 → tree.json（--preserve-styles 自动同步）
  - s3-title1: font-size: 3em
  - s7-chart1: width: 70%

内容变更 → MD（已直接修改）
  - s5-list1: 新增条目 "数据安全增强"

版式变更 → tree.json（需手动，无法从 HTML 逆向）
  - s4: text-default → image-right
```

**例外**：版式变更（换 template）无法从 HTML 逆向推断，仍需改 tree.json。

---

## 3. 增删页面的影响告知

增加或删除页面时，后续页码会整体后移/前移：

```
示例：在第5页后插入新页
  原第6页 -> 现第7页（ID: s6-* -> s7-*）
  原第6页的手工样式将丢失

在执行前，AI 应先告知：
  "此操作会导致第6页及之后共 N 页的手工样式重置，是否继续？"
```

---

## 4. 元素 ID 命名规则

```
格式：  s{N}-{type}{seq}
示例：  s3-title1    第3页第1个标题
         s3-subtitle1 第3页副标题
         s3-list1     第3页第1个列表
         s3-p1        第3页第1个段落
         s3-img1      第3页第1张图片
         s4-chart1    第4页第1个图表

type 枚举： title / subtitle / h3 / list / p / img / code / table / quote / chart
```

---

## 5. 常见边界情况

| 情况 | 处理方式 |
|------|----------|
| 用户描述不清晰是内容还是样式 | 明确询问用户意图 |
| 用户要求换版式 | 版式切换路径：修改 tree JSON -> 重新生成（见 §2 场景E） |
| 图表类型修改（bar -> line） | 内容变更（需更新 MD 中 chart 块） |
| 图表位置/宽高修改 | 样式调整（直接修改 HTML，下次重新生成自动同步 tree） |
| 多个元素同类型（如两个列表） | 请用户指明是第几个，在 tree JSON 中区分 |
| CSV 数据有误 | 让用户编辑 data/ 目录下对应 CSV，再重新生成 |
| 元素 ID 不匹配（页面结构变化） | 该元素样式重置，告知用户哪些丢失 |
| 图片路径不正确 | 确认图片路径相对于 MD 文件所在目录 |

---

## 6. 调整操作速查

### 常见样式 → 元素 ID 定位

| 用户说法 | 定位方法 |
|---------|---------|
| "第N页标题" | slide-tree.json 中 index=N 的 h1 元素，通常为 sN-title1 |
| "第N页副标题" | sN-subtitle1 |
| "第N页列表/要点" | sN-list1（多个列表则为 list1, list2...） |
| "第N页图表" | sN-chart1 |
| "第N页背景" | HTML 中 id="slide-N" 的 .slide 元素 |

### 调整幅度参考

| 用户说法 | 推荐调整量 |
|---------|---------|
| "大一点" / "小一点" | ±0.3em ~ 0.5em |
| "大很多" / "小很多" | ±0.8em ~ 1.2em |
| "加粗" | fontWeight: bold |
| "细一点" | fontWeight: 300 |
| "间距大一点" | margin/padding +0.3em ~ 0.5em |

### 效率原则

优先用 JSON 定位，避免全量读 HTML：
```
1. 读 slide-tree.json → 找到目标 ID（如 s3-title1）
2. Grep HTML 文件中该 ID → 精确定位行号
3. Edit 修改对应 style 属性
```

*版本: 1.1 | 最后更新: 2026-03-25*
