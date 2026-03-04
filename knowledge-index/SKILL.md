---
name: knowledge-index
description: |
  本地知识库智能索引技能。自动扫描文档、生成AI摘要、维护增量索引，支持AI智能检索。

  **触发场景**（包含以下关键词）：
  - 构建索引：建立索引、创建索引、为...建立索引、构建知识库、帮我索引、生成索引
  - 更新索引：更新索引、同步索引、刷新索引、检查更新、同步知识库
  - 智能检索：在知识库中查找、参考知识库、根据知识库、基于...写、在索引中搜索
  - 状态查询：查看索引状态、检查哪些知识库、索引信息、知识库状态

  **不触发场景**：
  - 纯粹的文件操作（复制、移动、删除文件）
  - 单个文档编辑或查看
  - 与知识库无关的查询
  - 代码编写或调试
  - 系统配置或设置
---

# knowledge-index - 本地知识库智能索引

## 核心概念

### 知识库定义

**一个知识库 = 一个文件夹 + 一个索引文件**

```
知识库/
├── _index.yaml          # 知识库索引
├── 文档1.md             # 知识库包含的文档
└── 子文件夹/
    └── 文档2.md         # 子文件夹的文档也属于该知识库
```

**关键原则**：
- ✅ 一个索引文件覆盖该文件夹及其所有子文件夹的所有文档
- ❌ 不应在子文件夹中创建独立的索引文件
- ✅ 子文件夹的文档通过父级索引统一管理

### 全局注册表

**位置**: `~/.knowledge-index/registry.yaml`

维护所有知识库的元信息，支持：
- 快速发现所有知识库
- 跨知识库检索
- 层级冲突检测
- 知识库健康检查

**注册表结构**：
```yaml
version: "1.0"
knowledge_bases:
  - name: "信息化知识库"
    path: "E:/知识库/信息化"
    index_path: "E:/知识库/信息化/_index.yaml"
    document_count: 15
    last_updated: "2026-03-04T09:30:00Z"
    status: "active"
```

**详细规范**: `references/advanced/global-registry-spec.md`

### 层级管理策略

**核心原则**: 始终在最高级别维护索引，避免父子文件夹重复索引

**自动层级提升**: 检测到父子索引冲突时，自动删除下级索引，保留最高级别索引

**8 种场景处理**:
1. 当前无索引，父无索引 → ✅ 正常创建索引
2. 当前有索引，父无索引 → ✅ 正常更新索引
3. 当前无索引，父有索引 → ⚠️ 建议更新父索引
4. 当前有索引，父有索引 → 🔄 自动提升至父级别
5. 当前无索引，父无索引，子有索引 → 🔄 自动提升至当前级别
6. 当前有索引，父无索引，子有索引 → 🔄 自动合并子索引
7. 当前无索引，父有索引，子有索引 → 🔄 完全提升至父级别
8. 当前有索引，父有索引，子有索引 → 🔄 完全提升至父级别

**详细说明**: `references/advanced/hierarchy-management.md`

## 核心功能

| 功能 | 说明 | 触发示例 |
|------|------|---------|
| 构建索引 | 扫描文档，生成结构化索引 | "为「信息化」建立索引" |
| AI摘要生成 | 自动提取核心内容，生成简洁摘要 | 构建索引时自动执行 |
| 增量更新 | 检测文件变更，仅更新变化部分 | "更新「信息化」的索引" |
| 智能检索 | AI根据需求，通过索引定位相关文档 | "在知识库中查找 GitLab 配置" |
| 全局管理 | 列出所有知识库，跨知识库检索 | "查看所有知识库" |
| 层级提升 | 自动处理父子文件夹索引冲突 | 构建索引时自动执行 |

## 核心原则

| # | 原则 | 核心要求 |
|---|------|---------|
| 1 | 零依赖优先 | 默认直接读取文档，无需安装额外工具 |
| 2 | 用户可控 | 通过配置文件控制是否转换、如何转换 |
| 3 | 智能降级 | 工具不可用时自动降级到直接读取 |
| 4 | 质量保证 | 三层验证（结构、语义、完整性） |
| 5 | 用户友好 | 提供清晰的进度反馈和错误提示 |
| 6 | 性能优化 | 批量处理、并行转换、智能缓存 |
| 7 | 容错设计 | 单个文档失败不影响整体流程 |

## 索引文件结构

```
知识库文件夹/
├── _index.yaml          # 索引文件（AI可读）
├── _index_config.yaml   # 配置文件（可选）
├── 文档1.md
├── 文档2.pdf
└── 子文件夹/
    └── 文档3.docx
```

**索引文件格式**: 详见 `references/core/index-spec.md`

## 快速流程

| 操作 | 步骤 |
|------|------|
| 首次构建 | 扫描 → 检测工具 → 转换&摘要 → 写入索引 → 验证 |
| 增量更新 | 读取索引 → 检测变更 → 增量处理 → 验证 |
| 智能检索 | 读取索引 → 匹配文档 → 读取内容 → 生成输出 |

**完整工作流程**: 详见 `references/core/workflow-spec.md`

## 质量门禁

- **构建前**: 路径有效、文档存在、工具可用
- **构建中**: 转换成功率 > 90%、摘要长度合理（50-500字符）、关键词有效（5-10个）
- **构建后**: YAML语法正确、字段完整、统计准确

**完整质量门禁**: 详见 `references/core/quality-gates.md`

## 工具支持

本 skill 优先使用 Claude Code 原生读取能力，用户可通过配置选择是否转换：

### 读取策略（用户可控）

| 策略 | PDF | Word | Markdown | 依赖 | 推荐场景 |
|------|-----|------|---------|------|---------|
| **direct**（默认） | 直接读取 | 尝试读取 | 直接读取 | 无 | 大部分场景 |
| **convert** | 转换后读取 | 转换后读取 | 直接读取 | doc2md/pandoc | 复杂文档 |
| **hybrid**（推荐） | 直接读取 | 转换后读取 | 直接读取 | doc2md（可选） | 混合格式 |

### 配置方式

```yaml
# _index_config.yaml
read_strategy:
  mode: "hybrid"  # direct, convert, hybrid
  formats:
    pdf: "direct"      # PDF 直接读取
    word: "convert"    # Word 转换
    markdown: "direct" # Markdown 直接读取
  conversion_tools:
    - "doc2md"    # 优先使用
    - "pandoc"    # 备选
```

### 降级策略

```
1. 尝试用户配置的读取方式
2. 如果转换失败 → 降级到直接读取
3. 如果工具不可用 → 自动跳过转换
4. 始终保证索引生成完成
```

**工具检测和选择策略**: 详见 `references/execution/tools.md`

## 快速使用示例

```
# 构建索引
用户: 为「信息化」建立索引
AI: ✓ 扫描 15 个文档 → 转换 → 生成摘要 → 写入 _index.yaml
    ✓ 已注册到全局目录

# 智能检索
用户: 在知识库中查找 GitLab 配置
AI: ✓ 读取索引 → 匹配 2 个相关文档 → 生成答案

# 增量更新
用户: 更新「信息化」的索引
AI: ✓ 检测变更（新增 2，修改 1）→ 增量处理 → 更新索引

# 列出所有知识库
用户: 查看所有知识库
AI: ✓ 读取全局注册表 → 列出 3 个知识库

# 跨知识库检索
用户: 在所有知识库中查找 CI/CD 相关内容
AI: ✓ 读取全局注册表 → 并行查询 3 个知识库 → 合并结果
```

## 层级提升示例

### 场景：父子索引冲突

```
用户: 为「知识库/子主题」建立索引

AI: ⚠️ 检测到父子索引冲突
      - 父索引: 知识库/_index.yaml
      - 当前索引: 知识库/子主题/_index.yaml

    执行层级提升：
      [1/4] 备份索引...
      [2/4] 删除下级索引...
      [3/4] 更新父索引...
      [4/4] 验证索引...

    ✓ 层级提升完成
      - 已删除: 知识库/子主题/_index.yaml
      - 已更新: 知识库/_index.yaml
      - 文档总数: 15 个
```

## 配置选项

```yaml
# _index_config.yaml（可选）
indexing:
  file_types: [".md", ".pdf", ".docx"]
  exclude: ["_index.yaml", ".git", "drafts/"]
  summary: {max_length: 300, include_keywords: true}
  update_detection: {method: "mtime"}
```

**完整配置和模板**: 详见 `references/execution/templates.md`

## 故障排除

### 常见问题

| 问题 | 解决方案 |
|------|---------|
| 路径不存在 | 检查路径拼写，使用绝对路径 |
| 工具不可用 | 安装 doc2md/pandoc/PyMuPDF |
| 转换失败 | 跳过该文档，继续处理 |
| 索引损坏 | 重建索引 |
| 检索无结果 | 更新索引，优化关键词 |

**完整故障排除指南**: 详见 `references/execution/troubleshooting.md`

## 参考资源

### 核心规范
- `references/core/index-spec.md` - 索引完整规范
- `references/core/workflow-spec.md` - 完整工作流程
- `references/core/quality-gates.md` - 质量门禁

### 决策支持
- `references/decision/decision-tree.md` - 场景决策树
- `references/decision/quick-reference.md` - 快速参考表
- `references/decision/anti-patterns.md` - 反模式案例

### 执行支持
- `references/execution/tools.md` - 工具支持（关键）
- `references/execution/checklist.md` - 检查清单
- `references/execution/templates.md` - 模板库
- `references/execution/troubleshooting.md` - 故障排除

### 高级主题
- `references/advanced/incremental-update.md` - 增量更新优化
- `references/advanced/performance-tuning.md` - 性能优化
- `references/advanced/integration.md` - 集成方案
- `references/advanced/hierarchy-management.md` - 层级管理规范 ⭐
- `references/advanced/global-registry-spec.md` - 全局注册表规范 ⭐
- `references/advanced/hierarchy-implementation.md` - 层级管理实现指南 ⭐

## 典型场景

| 场景 | 用户请求 | AI 操作 |
|------|---------|---------|
| 新建知识库 | "我有一个文件夹，里面有各种文档，帮我建立索引" | 扫描 → 转换 → 生成 _index.yaml |
| 基于知识库写作 | "参考知识库，帮我写一份文档" | 读取索引 → 匹配文档 → 生成新文档 |
| 定期维护 | "检查哪些知识库需要更新" | 扫描索引 → 对比时间 → 报告 |

**详细决策流程**: 详见 `references/decision/decision-tree.md`

---

**版本**: 1.0 | **最后更新**: 2026-03-03
