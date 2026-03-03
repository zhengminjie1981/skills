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

  # 文档读取策略
  read_strategy:
    # 读取模式: direct（直接读取）, convert（转换后读取）, hybrid（混合模式）
    mode: "direct"

    # 各格式的读取策略（仅在 mode=hybrid 时生效）
    formats:
      pdf: "direct"      # direct 或 convert
      word: "convert"    # direct（尝试）或 convert
      markdown: "direct" # 始终直接读取

    # 转换工具优先级（仅在需要转换时使用）
    conversion_tools:
      - "doc2md"    # 优先使用 doc2md skill
      - "pandoc"    # 备选：pandoc
      - "pymupdf"   # 备选：PyMuPDF（仅 PDF）

    # 转换失败时的行为
    on_conversion_failure: "fallback"  # fallback（降级到直接读取）或 skip（跳过文档）

    # PDF 特殊配置
    pdf:
      prefer_ocr: false        # 是否优先使用 OCR（适用于扫描件）
      prefer_structure: false  # 是否优先保留结构（适用于复杂表格/公式）

    # 缓存策略
    cache:
      enabled: false           # 是否缓存转换结果
      directory: ".knowledge-index/cache"  # 缓存目录
      max_age_days: 30        # 缓存过期天数
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

### read_strategy（新增）

控制 AI Agent 如何读取文档内容：

```yaml
# 模式1: 直接读取（默认，零依赖）
read_strategy:
  mode: "direct"
  # PDF 和 Markdown 都直接读取，不进行转换

# 模式2: 转换后读取（高质量）
read_strategy:
  mode: "convert"
  conversion_tools:
    - "doc2md"
    - "pandoc"
  # 所有文档都转换为 Markdown 后再读取

# 模式3: 混合模式（推荐）
read_strategy:
  mode: "hybrid"
  formats:
    pdf: "direct"      # PDF 直接读取
    word: "convert"    # Word 转换后读取
    markdown: "direct" # Markdown 直接读取
  on_conversion_failure: "fallback"
```

**读取模式对比**：

| 模式 | 依赖 | 速度 | 质量 | 适用场景 |
|------|------|------|------|---------|
| `direct` | 无 | 快 | 中 | 大部分场景 |
| `convert` | doc2md/pandoc | 慢 | 高 | 复杂文档、需要保留格式 |
| `hybrid` | 可选 | 中 | 高 | 混合格式知识库 |

**PDF 特殊配置**：

```yaml
read_strategy:
  mode: "hybrid"
  formats:
    pdf: "convert"  # PDF 转换
  pdf:
    prefer_ocr: true        # 扫描件优先 OCR
    prefer_structure: true  # 复杂表格/公式优先保留结构
  conversion_tools:
    - "doc2md"
```

**缓存策略**（提升性能）：

```yaml
read_strategy:
  mode: "convert"
  cache:
    enabled: true
    directory: ".knowledge-index/cache"
    max_age_days: 30
```

**降级策略**：

```yaml
read_strategy:
  mode: "convert"
  on_conversion_failure: "fallback"  # 转换失败时降级到直接读取
```

### conversion（已废弃）

⚠️ 此配置项已被 `read_strategy` 替代，保留仅为向后兼容。

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

### 完整配置（推荐）

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

  # 新增：文档读取策略
  read_strategy:
    mode: "hybrid"
    formats:
      pdf: "direct"      # PDF 直接读取
      word: "convert"    # Word 转换
      markdown: "direct" # Markdown 直接读取
    conversion_tools:
      - "doc2md"
      - "pandoc"
    on_conversion_failure: "fallback"
```

### 仅索引 Markdown（零依赖）

```yaml
indexing:
  file_types:
    - ".md"
  exclude:
    - "templates/"
  read_strategy:
    mode: "direct"  # 无需任何工具
```

### PDF 扫描件索引（需要 OCR）

```yaml
indexing:
  file_types:
    - ".pdf"
  read_strategy:
    mode: "convert"
    conversion_tools:
      - "doc2md"  # 使用 doc2md --tool mineru
    pdf:
      prefer_ocr: true
      prefer_structure: true
```

### 混合格式知识库（推荐配置）

```yaml
indexing:
  file_types:
    - ".md"
    - ".pdf"
    - ".docx"
    - ".doc"

  read_strategy:
    mode: "hybrid"
    formats:
      pdf: "direct"      # PDF 直接读取
      word: "convert"    # Word 转换
      markdown: "direct" # Markdown 直接读取
    conversion_tools:
      - "doc2md"
      - "pandoc"
    on_conversion_failure: "fallback"
    cache:
      enabled: true
      directory: ".knowledge-index/cache"
```
