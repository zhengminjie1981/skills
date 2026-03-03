# 索引配置说明

在知识库根目录创建 `_index_config.yaml` 文件以自定义索引行为。

## 默认配置

```yaml
# 索引配置
indexing:
  # 包含的文件类型
  file_types:
    - ".md"
    - ".pdf"
    - ".docx"
    - ".doc"
    - ".txt"

  # 排除的文件/文件夹
  exclude:
    - "_index.yaml"
    - "_index_config.yaml"
    - ".git"
    - ".obsidian"
    - "*.tmp"
    - "*.bak"
    - "~$*"
    - "drafts/"
    - "archive/"

  # 摘要配置
  summary:
    max_length: 500        # 摘要最大字符数
    include_keywords: true # 是否生成关键词
    include_topics: true   # 是否生成主题标签
    keywords_count: 5      # 关键词数量

  # 更新检测方法
  update_detection:
    method: "mtime"        # mtime (修改时间) 或 hash (内容哈希)
    auto_check: true       # 是否自动检测变更

  # 文档转换
  conversion:
    pdf_engine: "mineru"   # mineru 或 pymupdf
    ocr_enabled: true      # PDF OCR 支持
```

## 配置项详解

### file_types

支持的文件类型列表。可添加或移除类型：

```yaml
file_types:
  - ".md"      # Markdown
  - ".pdf"     # PDF
  - ".docx"    # Word 2007+
  - ".doc"     # Word 旧版
  - ".txt"     # 纯文本
  - ".epub"    # 电子书
  - ".html"    # 网页
```

### exclude

排除规则支持：
- 精确文件名: `_index.yaml`
- 通配符: `*.tmp`
- 文件夹: `drafts/`

```yaml
exclude:
  - "_index.yaml"      # 排除索引文件自身
  - "README.md"        # 排除特定文件
  - "*.bak"            # 排除备份文件
  - "drafts/"          # 排除草稿文件夹
  - ".*/"              # 排除隐藏文件夹
```

### summary

控制 AI 摘要生成：

```yaml
summary:
  max_length: 500        # 摘要长度限制
  include_keywords: true # 提取关键词
  include_topics: true   # 提取主题
  keywords_count: 5      # 关键词数量上限
  language: "zh"         # 摘要语言
```

### update_detection

变更检测策略：

```yaml
# 方式1: 基于修改时间（快速）
update_detection:
  method: "mtime"
  tolerance_seconds: 1  # 时间容差

# 方式2: 基于内容哈希（准确但较慢）
update_detection:
  method: "hash"
  algorithm: "md5"      # md5 或 sha256
```

## 示例配置

### 最小配置

```yaml
indexing:
  file_types:
    - ".md"
    - ".pdf"
```

### 完整配置

```yaml
indexing:
  file_types:
    - ".md"
    - ".pdf"
    - ".docx"

  exclude:
    - "_index.yaml"
    - ".git"
    - "archive/"

  summary:
    max_length: 300
    include_keywords: true
    keywords_count: 3

  update_detection:
    method: "mtime"

  conversion:
    pdf_engine: "mineru"
    ocr_enabled: true
```

### 仅索引 Markdown

```yaml
indexing:
  file_types:
    - ".md"
  exclude:
    - "templates/"
```
