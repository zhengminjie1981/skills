# 索引模板

首次构建索引时，使用此模板生成 `_index.yaml` 文件。

## 最小索引模板

```yaml
version: "1.0"
knowledge_base:
  name: "知识库名称"
  path: "相对路径"
  created: "2026-03-03T10:00:00"
  last_updated: "2026-03-03T10:00:00"
  total_documents: 0
  total_size_mb: 0

documents: []
```

## 完整索引模板

```yaml
version: "1.0"
knowledge_base:
  name: "知识库名称"
  path: "相对路径"
  description: "知识库简要描述"
  created: "2026-03-03T10:00:00"
  last_updated: "2026-03-03T10:00:00"
  total_documents: 0
  total_size_mb: 0
  maintainer: "维护者"

documents:
  # Markdown 文档示例
  - path: "文件夹/文档.md"
    filename: "文档.md"
    type: "markdown"
    modified: "2026-03-03T10:00:00"
    size: 12345
    hash: ""
    summary: |
      文档摘要内容...
    keywords: ["关键词1", "关键词2"]
    topics: ["主题1", "主题2"]

  # PDF 文档示例
  - path: "文件夹/文档.pdf"
    filename: "文档.pdf"
    type: "pdf"
    modified: "2026-03-03T10:00:00"
    size: 123456
    hash: ""
    summary: |
      PDF文档摘要...
    keywords: ["关键词"]
    topics: ["主题"]

  # Word 文档示例
  - path: "文件夹/文档.docx"
    filename: "文档.docx"
    type: "docx"
    modified: "2026-03-03T10:00:00"
    size: 45678
    hash: ""
    summary: |
      Word文档摘要...
    keywords: ["关键词"]
    topics: ["主题"]

# 主题聚类（可选）
clusters:
  - name: "聚类名称"
    description: "聚类描述"
    documents:
      - "文档1.md"
      - "文档2.pdf"
```

## 字段说明

### knowledge_base 字段

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| name | string | ✓ | 知识库显示名称 |
| path | string | ✓ | 知识库相对路径 |
| description | string | | 知识库描述 |
| created | datetime | ✓ | 创建时间 (ISO 8601) |
| last_updated | datetime | ✓ | 最后更新时间 |
| total_documents | integer | ✓ | 文档总数 |
| total_size_mb | float | ✓ | 总大小 (MB) |
| maintainer | string | | 维护者 |

### documents 字段

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| path | string | ✓ | 文件相对路径 |
| filename | string | ✓ | 文件名 |
| type | string | ✓ | 文件类型 (markdown/pdf/docx/doc) |
| modified | datetime | ✓ | 修改时间 |
| size | integer | ✓ | 文件大小 (bytes) |
| hash | string | | 文件内容哈希 (可选) |
| summary | string | ✓ | AI 生成的摘要 |
| keywords | array | | 关键词列表 |
| topics | array | | 主题标签 |

### clusters 字段

| 字段 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| name | string | ✓ | 聚类名称 |
| description | string | | 聚类描述 |
| documents | array | ✓ | 包含的文档列表 |
