# 模板库

本文档提供知识库索引相关的各种模板，包括索引文件模板、配置模板和 AI 提示词模板。

## 1. 索引文件模板

### 1.1 最小索引模板

```yaml
version: "1.0"
knowledge_base:
  name: "知识库名称"
  path: "相对路径"
  created: "2026-03-03T10:00:00Z"
  last_updated: "2026-03-03T10:00:00Z"
  total_documents: 0
  total_size_mb: 0

documents: []
```

### 1.2 完整索引模板

```yaml
version: "1.0"
knowledge_base:
  name: "信息化知识库"
  path: "信息化"
  description: "企业信息化建设相关文档"
  created: "2026-03-03T10:00:00Z"
  last_updated: "2026-03-03T15:30:00Z"
  total_documents: 15
  total_size_mb: 2.5
  maintainer: "IT部门"

documents:
  # Markdown 文档示例
  - path: "GitLab 完整指南.md"
    filename: "GitLab 完整指南 - 从配置管理到协作开发.md"
    type: "markdown"
    modified: "2026-02-28T10:30:00Z"
    size: 15234
    hash: "a1b2c3d4"
    summary: |
      本文档详细介绍 GitLab 的完整使用流程：
      1. 配置管理：SSH密钥、项目设置
      2. 协作开发：分支策略、Merge Request
      3. CI/CD：流水线配置、自动化部署
    keywords: ["GitLab", "CI/CD", "版本控制", "DevOps"]
    topics: ["配置管理", "协作开发", "持续集成"]

  # PDF 文档示例
  - path: "迅蚁无人机对接需求.pdf"
    filename: "迅蚁无人机对接需求.pdf"
    type: "pdf"
    modified: "2026-01-15T09:00:00Z"
    size: 245678
    hash: "e5f6g7h8"
    summary: |
      迅蚁无人机系统对接需求文档，包含：
      - API接口规范
      - 数据交换格式
      - 安全认证机制
    keywords: ["无人机", "API", "对接", "迅蚁"]
    topics: ["接口规范", "数据交换"]

  # Word 文档示例
  - path: "ERP现状-戴鸿.docx"
    filename: "ERP现状-戴鸿.docx"
    type: "word"
    modified: "2026-01-20T14:00:00Z"
    size: 87654
    hash: "i9j0k1l2"
    summary: |
      ERP系统现状分析报告：
      - 系统架构和模块
      - 使用情况和问题
      - 改进建议
    keywords: ["ERP", "系统分析", "企业管理"]
    topics: ["业务系统", "信息化现状"]

# 主题聚类（可选）
clusters:
  - name: "开发工具"
    description: "软件开发和协作工具"
    documents:
      - "GitLab 完整指南.md"
      - "AI辅助文档编写指南.md"
  - name: "业务系统"
    description: "企业业务系统文档"
    documents:
      - "ERP现状-戴鸿.docx"
      - "前台信息化系统情况-小雄.md"
```

### 1.3 文档条目模板

```yaml
# 单个文档条目
- path: "相对路径/文档名.扩展名"
  filename: "文档名.扩展名"
  type: "markdown"  # markdown, pdf, word
  modified: "2026-03-03T10:00:00Z"
  size: 12345
  hash: "可选-内容哈希"
  summary: |
    文档摘要内容
    支持多行文本
  keywords: ["关键词1", "关键词2", "关键词3"]
  topics: ["主题1", "主题2"]
```

## 2. 配置文件模板

### 2.1 默认配置模板（零依赖）

```yaml
# 索引配置
indexing:
  # 包含的文件类型
  file_types:
    - ".md"
    - ".pdf"
    - ".docx"
    - ".doc"

  # 排除的文件/文件夹
  exclude:
    - "_index.yaml"
    - "_index_config.yaml"
    - ".git"
    - "*.tmp"
    - "drafts/"

  # 摘要配置
  summary:
    max_length: 500        # 最大字符数
    include_keywords: true
    include_topics: true
    keywords_count: 5

  # 更新检测
  update_detection:
    method: "mtime"        # mtime 或 hash
    auto_check: true

  # 读取策略（默认：直接读取，零依赖）
  read_strategy:
    mode: "direct"  # PDF 和 Markdown 都直接读取，无需任何工具
```

### 2.2 高级配置模板（混合模式）

```yaml
# 高级索引配置
indexing:
  file_types:
    - ".md"
    - ".pdf"
    - ".docx"
    - ".doc"
    - ".txt"

  exclude:
    - "_index.yaml"
    - ".git"
    - ".obsidian"
    - "*.tmp"
    - "*.bak"
    - "drafts/"
    - "archive/"

  summary:
    max_length: 300
    min_length: 50
    include_keywords: true
    include_topics: true
    keywords_count: 8
    topics_count: 3
    language: "zh"

  update_detection:
    method: "hash"
    algorithm: "md5"
    auto_check: true
    check_interval_hours: 24

  # 读取策略（混合模式，推荐）
  read_strategy:
    mode: "hybrid"
    formats:
      pdf: "direct"      # PDF 直接读取
      word: "convert"    # Word 转换后读取
      markdown: "direct" # Markdown 直接读取
    conversion_tools:
      - "doc2md"         # 优先使用 doc2md
      - "pandoc"         # 备选 pandoc
    on_conversion_failure: "fallback"  # 转换失败时降级到直接读取
    pdf:
      prefer_ocr: false           # PDF 不优先 OCR
      prefer_structure: false     # PDF 不优先保留结构
    cache:
      enabled: true               # 启用转换缓存
      directory: ".knowledge-index/cache"
      max_age_days: 30

  performance:
    batch_size: 50
    parallel_workers: 4
    enable_cache: true

  advanced:
    generate_clusters: true
    cluster_min_documents: 2
    validate_after_build: true
```

### 2.3 场景配置模板

#### 仅索引 Markdown（零依赖）

```yaml
indexing:
  file_types:
    - ".md"
  exclude:
    - "templates/"
    - "drafts/"
  summary:
    max_length: 200
  read_strategy:
    mode: "direct"  # 无需任何工具
```

#### PDF 扫描件索引（需要 OCR）

```yaml
indexing:
  file_types:
    - ".pdf"
  read_strategy:
    mode: "convert"
    conversion_tools:
      - "doc2md"  # 使用 doc2md --tool mineru
    pdf:
      prefer_ocr: true        # 优先 OCR
      prefer_structure: true  # 保留结构
```

#### 混合格式知识库（推荐配置）

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

#### 大规模知识库优化

```yaml
indexing:
  file_types:
    - ".md"
    - ".pdf"

  summary:
    max_length: 200
    keywords_count: 3

  update_detection:
    method: "mtime"

  read_strategy:
    mode: "direct"  # 直接读取，速度最快

  performance:
    batch_size: 100
    parallel_workers: 8
    enable_cache: true
```

#### 高精度更新检测

```yaml
indexing:
  update_detection:
    method: "hash"
    algorithm: "sha256"

  summary:
    max_length: 500
    include_keywords: true
```

## 3. AI 摘要提示词模板

### 3.1 标准摘要提示词

```
请为以下文档生成一个简洁的摘要（100-300 字符）：

【文档内容】
{document_content}

【要求】
1. 提取文档的核心观点和结构
2. 使用简洁的语言
3. 保持客观，不添加评价
4. 如果文档有明确结构，按要点列出
5. 摘要长度控制在 100-300 字符

【输出格式】
摘要内容...
```

### 3.2 关键词提取提示词

```
请从以下文档中提取 5-10 个关键词：

【文档内容】
{document_content}

【要求】
1. 关键词应具有检索价值
2. 避免通用词（如"文档"、"说明"、"介绍"）
3. 优先选择专业术语和核心概念
4. 每个关键词 2-10 字符

【输出格式】
["关键词1", "关键词2", "关键词3", ...]
```

### 3.3 主题标签提取提示词

```
请为以下文档生成 3-5 个主题标签：

【文档内容】
{document_content}

【要求】
1. 主题标签反映文档的类别和所属领域
2. 使用简洁的短语（2-6 字符）
3. 涵盖文档的主要方面
4. 避免过于宽泛的标签

【输出格式】
["主题1", "主题2", "主题3", ...]
```

### 3.4 综合摘要提示词

```
请为以下文档生成完整的索引信息：

【文档内容】
{document_content}

【任务】
1. 生成摘要（100-300 字符）
2. 提取关键词（5-10 个）
3. 提取主题标签（3-5 个）

【输出格式】
摘要: |
  [摘要内容]
关键词: ["关键词1", "关键词2", ...]
主题: ["主题1", "主题2", ...]
```

### 3.5 文档匹配提示词

```
请评估以下文档与用户查询的相关性：

【用户查询】
{user_query}

【文档摘要】
{document_summary}

【要求】
1. 评分范围：0-5（0=不相关，5=高度相关）
2. 简要说明评分理由

【输出格式】
评分: [0-5]
理由: [一句话说明]
```

## 4. 验证脚本模板

### 4.1 YAML 语法验证

```python
import yaml

def validate_yaml_syntax(file_path):
    """验证 YAML 文件语法"""
    try:
        with open(file_path, encoding='utf-8') as f:
            yaml.safe_load(f)
        return {'valid': True, 'message': 'YAML 语法正确'}
    except yaml.YAMLError as e:
        return {'valid': False, 'error': str(e)}
```

### 4.2 字段完整性验证

```python
import yaml

def validate_index_completeness(index_path):
    """验证索引字段完整性"""
    with open(index_path, encoding='utf-8') as f:
        index = yaml.safe_load(f)

    errors = []

    # 检查元数据
    required_meta = ['version', 'knowledge_base']
    for field in required_meta:
        if field not in index:
            errors.append(f"缺少必填字段: {field}")

    # 检查文档
    required_doc_fields = ['path', 'filename', 'type', 'summary', 'keywords']
    for i, doc in enumerate(index.get('documents', [])):
        for field in required_doc_fields:
            if field not in doc:
                errors.append(f"文档 {i} 缺少字段: {field}")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'document_count': len(index.get('documents', []))
    }
```

## 5. 报告模板

### 5.1 构建报告模板

```yaml
知识库索引构建报告
==================

基本信息:
  - 知识库名称: {name}
  - 路径: {path}
  - 构建时间: {timestamp}

文档统计:
  - 总数: {total}
  - Markdown: {md_count}
  - PDF: {pdf_count}
  - Word: {word_count}
  - 转换失败: {failed_count}

索引文件:
  - 位置: {index_path}
  - 大小: {size_kb} KB

质量指标:
  - 转换成功率: {success_rate}%
  - 平均摘要长度: {avg_summary_length} 字符
  - 平均关键词数量: {avg_keywords} 个

处理详情:
  成功文档:
    - {doc1}
    - {doc2}

  失败文档:
    - {failed_doc1}: {reason}
    - {failed_doc2}: {reason}

建议:
  - {suggestion1}
  - {suggestion2}
```

### 5.2 更新报告模板

```yaml
知识库索引更新报告
==================

知识库: {name}

变更统计:
  - 新增: {added_count} 个文档
  - 修改: {modified_count} 个文档
  - 删除: {deleted_count} 个文档
  - 当前总数: {total_count} 个文档

处理详情:
  新增文档:
    - {new_doc1}
    - {new_doc2}

  修改文档:
    - {modified_doc1}
    - {modified_doc2}

  删除文档:
    - {deleted_doc1}

索引文件:
  - 最后更新: {last_updated}
  - 文件大小: {size_kb} KB

建议:
  - {suggestion}
```

## 6. 使用示例

### 6.1 创建新索引

```bash
# 1. 准备配置文件（可选）
cp templates/config-advanced.yaml 知识库/_index_config.yaml

# 2. 触发索引构建
用户: 为「知识库」建立索引

# 3. 查看构建报告
AI 输出构建报告...
```

### 6.2 自定义摘要长度

```yaml
# 在 _index_config.yaml 中配置
summary:
  max_length: 200
  min_length: 50
```

### 6.3 自定义排除规则

```yaml
# 在 _index_config.yaml 中配置
exclude:
  - "*.bak"
  - "temp/"
  - "obsolete/"
```

## 7. 最佳实践

### 7.1 配置文件管理

- 小型知识库（<100 文档）：使用默认配置
- 中型知识库（100-500 文档）：使用高级配置，调整批处理大小
- 大型知识库（>500 文档）：使用优化配置，启用缓存和并行处理

### 7.2 摘要质量优化

- 技术文档：max_length = 300，包含代码示例
- 业务文档：max_length = 200，强调关键指标
- 学术文档：max_length = 500，包含研究方法和结论

### 7.3 关键词优化

- 通用知识库：keywords_count = 5
- 专业领域：keywords_count = 8-10
- 多主题文档：keywords_count = 10

## 8. 相关资源

- 索引完整规范: `references/core/index-spec.md`
- 配置选项详解: `references/execution/config-options.md`（原 config-options.md）
- 质量门禁: `references/core/quality-gates.md`
- 检查清单: `references/execution/checklist.md`
