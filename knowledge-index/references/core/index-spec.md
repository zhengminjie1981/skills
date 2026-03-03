# 索引完整规范

本文档详细定义知识库索引文件的完整格式规范。

## 索引文件位置

- **文件名**: `_index.yaml`
- **位置**: 知识库根目录
- **编码**: UTF-8
- **格式**: YAML

## 完整格式规范

```yaml
# ===== 索引元数据 =====
version: "1.0"
knowledge_base:
  name: "知识库名称"
  path: "相对路径"
  created: "2026-03-03T10:00:00Z"      # ISO 8601 格式
  last_updated: "2026-03-03T15:30:00Z"
  total_documents: 15
  total_size_mb: 2.5

# ===== 文档索引 =====
documents:
  - path: "相对路径/文档名.md"
    filename: "文档名.md"
    type: "markdown"                   # markdown, pdf, word
    modified: "2026-02-28T10:30:00Z"
    size: 15234                        # 字节数
    hash: "a1b2c3d4"                   # 可选：用于精确变更检测
    summary: |
      文档摘要内容
      支持多行文本
    keywords: ["关键词1", "关键词2"]    # 5-10个
    topics: ["主题1", "主题2"]          # 3-5个主题标签

# ===== 检索增强（可选） =====
clusters:
  - name: "聚类名称"
    documents: ["文档1.md", "文档2.pdf"]
```

## 字段说明

### 元数据字段（必填）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `version` | string | 索引格式版本 | `"1.0"` |
| `knowledge_base.name` | string | 知识库显示名称 | `"信息化知识库"` |
| `knowledge_base.path` | string | 知识库相对路径 | `"信息化"` |
| `knowledge_base.created` | datetime | 索引创建时间 | `"2026-03-03T10:00:00Z"` |
| `knowledge_base.last_updated` | datetime | 最后更新时间 | `"2026-03-03T15:30:00Z"` |
| `knowledge_base.total_documents` | integer | 文档总数 | `15` |
| `knowledge_base.total_size_mb` | float | 总大小（MB） | `2.5` |

### 文档字段（必填）

| 字段 | 类型 | 说明 | 必填 |
|------|------|------|------|
| `path` | string | 文档相对路径 | ✅ |
| `filename` | string | 文件名（含扩展名） | ✅ |
| `type` | string | 文档类型 | ✅ |
| `modified` | datetime | 最后修改时间 | ✅ |
| `size` | integer | 文件大小（字节） | ✅ |
| `hash` | string | 文件内容哈希 | ❌ |
| `summary` | string | AI 生成的摘要 | ✅ |
| `keywords` | array | 关键词列表 | ✅ |
| `topics` | array | 主题标签列表 | ✅ |

### 检索增强字段（可选）

| 字段 | 类型 | 说明 |
|------|------|------|
| `clusters` | array | 主题聚类列表 |
| `clusters[].name` | string | 聚类名称 |
| `clusters[].documents` | array | 属于该聚类的文档路径列表 |

## 摘要质量要求

### 结构化摘要（推荐）

```yaml
summary: |
  本文档介绍 XXX 的完整流程：
  1. 功能模块A：详细说明
  2. 功能模块B：详细说明
  3. 功能模块C：详细说明
```

### 摘要长度

- **推荐**: 100-300 字符
- **最小**: 50 字符
- **最大**: 500 字符（可在配置中调整）

### 关键词要求

- **数量**: 5-10 个
- **特性**: 具有检索价值，避免通用词
- **示例**: ✅ `["GitLab", "CI/CD", "流水线"]` ❌ `["文档", "说明", "介绍"]`

### 主题标签要求

- **数量**: 3-5 个
- **特性**: 反映文档类别和所属领域
- **示例**: `["配置管理", "协作开发", "持续集成"]`

## 索引更新规则

### 文档新增

1. 扫描到新文档时，添加到 `documents` 列表末尾
2. 生成摘要、关键词、主题标签
3. 更新 `total_documents` 和 `total_size_mb`
4. 更新 `last_updated`

### 文档修改

1. 检测到修改（mtime 或 hash）
2. 重新生成摘要和元数据
3. 保持 `path` 不变，更新其他字段
4. 更新 `last_updated`

### 文档删除

1. 检测到文件不存在
2. 从 `documents` 列表中移除
3. 更新 `total_documents` 和 `total_size_mb`
4. 更新 `last_updated`

## 主题聚类维护

### 自动生成规则

- AI 分析所有文档的 `topics` 字段
- 识别高频主题（出现 ≥ 2 次）
- 将相关文档归入同一聚类

### 聚类命名

- 使用简洁的主题名称
- 避免过长的聚类名称
- 示例：✅ `"开发工具"` ❌ `"软件开发和协作工具集合"`

## 编码和格式

### YAML 格式要求

- 使用 2 空格缩进
- 字符串优先使用双引号
- 多行文本使用 `|` 或 `>`

### 时间格式

- 标准：ISO 8601
- 格式：`YYYY-MM-DDTHH:MM:SSZ`
- 示例：`"2026-03-03T10:00:00Z"`

### 路径格式

- 使用正斜杠 `/`（跨平台兼容）
- 相对于知识库根目录
- 示例：`"子文件夹/文档名.md"`

## 验证清单

构建或更新索引后，应验证：

- [ ] 所有必填字段已填写
- [ ] 时间格式符合 ISO 8601
- [ ] 路径使用正斜杠
- [ ] 摘要长度在合理范围
- [ ] 关键词数量适中（5-10个）
- [ ] YAML 语法正确
- [ ] 文件编码为 UTF-8

## 示例索引

完整的示例索引见 `references/execution/templates.md`。
