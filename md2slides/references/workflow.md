# md2slides 工作流

> 该文档供 AI 处理边界情况时参考。详细内容见各专项文档。

---

## 0. 三阶段总览

```
阶段一：内容策划（AI 对话）
  输入：用户材料 / 原始文字
  输出：demo.md（分页内容提纲，含 chart 块）
  详见：references/content-planning.md

阶段二：版式规划（AI 对话）
  输入：demo.md（读取各页面内容）
  输出：slide-tree.json（含 layout 字段，写入版式规划结果）
  详见：references/layout-guide.md

阶段三：HTML 生成（脚本）
  输入：demo.md + slide-tree.json
  命令：python scripts/convert.py --input demo.md --output demo.html --tree slide-tree.json
  输出：demo.html（可在浏览器中演示）
```

> **重要**：MD 文件仅是内容提纲，视觉效果完全由 slide-tree.json 版式 + convert.py 决定。

---

## 3. 调整请求路由

### 3.1 范围划分

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

### 3.2 版式切换路径

```
用户说：把第7页换成双栏布局

AI 步骤：
1. 读取 slide-tree.json，找到 index=7 的 slide 节点
2. 修改 layout.template：原值 -> "text-two-column"
3. 如需调整辅助参数（如 imageWidth），同步修改 layout 其他字段
4. 运行 convert.py（无需 --preserve-styles，版式在 tree 中）：
   python scripts/convert.py --input demo.md --output demo.html --tree slide-tree.json
5. 告知修改结果
```

### 3.3 增删页面的影响告知

增加或删除页面时，后续页码会整体后移/前移：

```
示例：在第5页后插入新页
  原第6页 -> 现第7页（ID: s6-* -> s7-*）
  原第6页的手工样式将丢失

在执行前，AI 应先告知：
  "此操作会导致第6页及之后共 N 页的手工样式重置，是否继续？"
```

### 3.4 元素 ID 命名规则

```
格式：  s{N}-{type}{seq}
示例：  s3-title1    第3页第1个标题
         s3-list1     第3页第1个列表
         s4-chart1    第4页第1个图表

type 枚举： title / subtitle / h3 / list / p / img / code / table / quote / chart
```

---

## 4. 常见边界情况

| 情况 | 处理方式 |
|------|----------|
| 用户描述不清晰是内容还是样式 | 明确询问用户意图 |
| 用户要求换版式 | 版式切换路径：修改 tree JSON -> 重新生成（见 3.2） |
| 图表类型修改（bar -> line） | 内容变更（需更新 MD 中 chart 块） |
| 图表位置/宽高修改 | 样式调整（直接修改 HTML，下次重新生成自动同步 tree） |
| 多个元素同类型（如两个列表） | 请用户指明是第几个，在 tree JSON 中区分 |
| CSV 数据有误 | 让用户编辑 data/ 目录下对应 CSV，再重新生成 |
| 元素 ID 不匹配（页面结构变化） | 该元素样式重置，告知用户哪些丢失 |
| 图片路径不正确 | 确认图片路径相对于 MD 文件所在目录 |

*版本: 3.0 | 最后更新: 2026-03-25*
