---
name: knowledge-index
description: |-
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

allowed-tools: [Bash, Read, Glob, Grep]
argument-hint: "<build|update|search|list> [路径] [选项]"

feedback:
  enabled: true
  version: "2.1.0"
  author: "skills-team"
---

# knowledge-index - 本地知识库智能索引

## 核心概念

### 知识库定义

**一个知识库 = 一个文件夹 + 一个索引文件**

```
知识库/
├── _index.yaml          # 知识库索引（AI 可读）
├── 文档1.md
├── 文档2.pdf
└── 子文件夹/
    └── 文档3.docx       # 子文件夹文档也属于该知识库
```

**关键原则**：
- ✅ 一个索引覆盖该文件夹及所有子文件夹的文档
- ❌ 不在子文件夹创建独立索引
- ✅ 全局注册表 `~/.knowledge-index/registry.yaml` 维护所有知识库信息

## 索引版本 2.1

**文档分类索引**：
- `markdown_documents`：Markdown 文档（含 summary、keywords、links、backlinks、tags）
- `other_documents`：其他格式（PDF、Word 等）

**检索策略**：统一检索 + 软加权
- 所有文档统一检索
- Markdown 软加权 +10%（因为有 links/tags 额外信息）
- 按相关度排序，同名文件 Markdown 优先

详细结构见：`references/core/index-spec.md`

## 6 个核心功能

| 功能 | 说明 | 触发示例 |
|------|------|---------|
| 构建索引 | 扫描文档，生成摘要，写入索引 | "为「信息化」建立索引" |
| 增量更新 | 检测变更，仅更新变化部分 | "更新「信息化」的索引" |
| 智能检索 | 通过索引定位相关文档 | "在知识库中查找 GitLab 配置" |
| 全局管理 | 列出所有知识库，跨库检索 | "查看所有知识库" |
| 层级提升 | 自动处理父子索引冲突 | 构建索引时自动执行 |
| AI 摘要 | 生成文档摘要和关键词 | 构建索引时自动执行 |

## Obsidian CLI 集成

### 概述

knowledge-index 支持 Obsidian 官方 CLI 进行原生搜索，提供更准确的检索结果。

### 工作流程

```
用户查询
    ↓
检查 Obsidian CLI 是否可用
    ├─ 可用 → obsidian search --format=json → 返回结果
    └─ 不可用 → 使用现有 _index.yaml 索引检索
    ↓
返回搜索结果
```

### 启用条件

**桌面用户**：
1. 更新 Obsidian 到最新版本（2026年2月后）
2. Settings → General → 启用 Command line interface
3. 按提示添加 CLI 到 PATH
4. **保持 Obsidian 桌面应用运行中**

**验证 CLI 可用性**：
```bash
obsidian vault
# 应显示当前 vault 信息
```

### 搜索模式

| 模式 | 参数 | 特点 |
|------|------|------|
| 自动 | 默认 | 自动检测 CLI，不可用时回退索引 |
| 优先 CLI | `--prefer-obsidian` | 优先使用 CLI |
| 仅索引 | `--no-obsidian` | 禁用 CLI，显示相关度分数 |

### CLI 限制

- 需要 Obsidian 桌面应用**正在运行**
- 搜索结果不包含相关度分数
- 路径为相对于 vault 的相对路径

## 3 步快速流程

| 操作 | 步骤 |
|------|------|
| **首次构建** | 扫描文档 → 生成摘要 → 写入 `_index.yaml` |
| **增量更新** | 检测变更 → 增量处理 → 更新索引 |
| **智能检索** | 读取索引 → 匹配文档 → 生成回答 |

## 子功能调用

| 指令 | 参数 | 说明 |
|------|------|------|
| `/knowledge-index build <路径> [--force] [--no-ai]` | 知识库路径 | 扫描文档，生成摘要，创建索引 |
| `/knowledge-index update <路径> [--no-ai]` | 知识库路径 | 检测变更，增量更新索引 |
| `/knowledge-index search <查询> [--kb 路径]` | 查询关键词 | 通过索引检索相关文档 |
| `/knowledge-index list` | 无 | 列出全局注册表中所有知识库 |

**参数说明**：

| 参数 | 适用 | 说明 |
|------|------|------|
| `--force` | build | 强制创建索引（忽略父索引） |
| `--no-ai` | build / update | 禁用 AI 摘要，使用基础摘要 |
| `--kb <路径>` | search | 指定搜索的知识库（不指定则搜索全部） |

**CLI 命令**（脚本直接调用）：

```bash
python scripts/knowledge-index-manager.py build <路径> [--force] [--no-ai]
python scripts/knowledge-index-manager.py update <路径> [--no-ai]
python scripts/knowledge-index-manager.py search <查询> [--kb <路径>]
python scripts/knowledge-index-manager.py list
```

## 按需加载指南

**根据任务类型，读取对应的详细文档：**

| 任务 / 场景 | 读取文档 | 关键内容 |
|------------|---------|---------|
| 首次构建索引 | `references/core/workflow-spec.md` | 完整构建流程 |
| 增量更新 | `references/advanced/incremental-update.md` | 变更检测算法 |
| 检测到父子冲突 | `references/advanced/hierarchy-management.md` | 8 种场景处理 |
| 查看所有知识库 | `references/advanced/global-registry-spec.md` | 注册表操作 |
| 跨知识库检索 | `references/advanced/global-registry-spec.md` | 跨库搜索 |
| **配置读取策略** | `references/execution/tools.md` | **本地优先、隐私保护** |
| 排查错误 | `references/execution/troubleshooting.md` | 常见问题解决 |
| 配置选项 | `references/execution/config-options.md` | 完整配置说明 |

## 快速示例

```
# 构建索引
用户: 为「E:/知识库/信息化」建立索引
AI: ✓ 扫描 15 个文档 → 生成摘要 → 写入 _index.yaml
    ✓ 已注册到全局目录

# 智能检索
用户: 在知识库中查找 GitLab 配置
AI: ✓ 读取索引 → 匹配 2 个相关文档 → 生成答案

# 增量更新
用户: 更新「信息化」的索引
AI: ✓ 检测变更（新增 2，修改 1）→ 增量处理 → 更新索引

# 全局管理
用户: 查看所有知识库
AI: ✓ 读取全局注册表 → 列出 3 个知识库
```

## 层级管理（自动处理）

当检测到父子索引冲突时，自动执行：
1. 备份下级索引
2. 删除下级索引
3. 更新父级索引

**详细场景和算法**：`references/advanced/hierarchy-management.md`

## 核心原则

| # | 原则 | 说明 |
|---|------|------|
| 1 | **本地优先** | 优先使用本地工具提取文本，避免上传完整文档 |
| 2 | 零依赖可用 | 无需安装工具也可使用（降级模式） |
| 3 | 用户可控 | 通过配置控制读取策略和隐私级别 |
| 4 | 智能降级 | 工具不可用时自动回退 |
| 5 | 容错设计 | 单个文档失败不影响整体 |

## AI 摘要说明

### 启用 AI 摘要

设置环境变量 `ANTHROPIC_API_KEY` 后，构建索引时会自动调用 Claude API 生成：
- 文档摘要（50-100字）
- 关键词（5-10个）
- 主题标签（3-5个）

### 缓存机制

摘要结果会缓存到 `~/.knowledge-index/cache/`，避免重复调用 API。

### 降级模式

无 API 或禁用时，会使用基础摘要：
- 提取文档前 200 字符
- 匹配常见技术关键词

## 参考资源

### 核心规范
- `references/core/index-spec.md` - 索引文件完整规范
- `references/core/workflow-spec.md` - 完整工作流程
- `references/core/quality-gates.md` - 质量门禁

### 执行支持
- `references/execution/tools.md` - 工具支持（读取策略）
- `references/execution/checklist.md` - 检查清单
- `references/execution/troubleshooting.md` - 故障排除

### 高级主题
- `references/advanced/hierarchy-management.md` - 层级管理
- `references/advanced/global-registry-spec.md` - 全局注册表
- `references/advanced/incremental-update.md` - 增量更新

---

**版本**: 2.1 | **最后更新**: 2026-03-15

---

## 反馈机制

本 skill 支持自动反馈改进。

<!-- FEEDBACK-TRIGGER-START -->
<feedback-config>
{
  "triggers": ["execution_failure", "index_corruption", "search_error"],
  "collect": ["error_type", "knowledge_base_type", "environment", "skill_version"],
  "sanitize": ["file_paths", "document_content", "user_queries"]
}
</feedback-config>
<!-- FEEDBACK-TRIGGER-END -->

执行完成后，如检测到改进机会且用户已授权，将自动发送脱敏反馈。
