# 集成方案

本文档说明如何将知识库索引集成到各种工作流和系统中。

## 与 doc2md skill 集成

### 集成方式

**依赖类型**: 软依赖（可选但推荐）

**集成流程**:
```
检测 doc2md skill → 可用时优先使用 → 不可用时降级处理
```

### 调用接口

在 Claude Code 环境中:

```python
def convert_with_doc2md(file_path):
    """使用 doc2md skill 转换文档"""
    # 通过 Skill tool 调用
    result = Skill(skill="doc2md", args=file_path)

    if result.success:
        return result.markdown
    else:
        raise Exception(f"doc2md 转换失败: {result.error}")
```

### 协作模式

#### 模式 1: 优先使用

```python
def smart_convert(file_path):
    """智能选择转换工具"""
    available_tools = detect_tools()

    # 优先使用 doc2md
    if 'doc2md' in available_tools:
        try:
            return convert_with_doc2md(file_path)
        except Exception:
            pass  # 降级到其他工具

    # 备选工具
    if 'pandoc' in available_tools:
        return convert_with_pandoc(file_path)

    if 'pymupdf' in available_tools:
        return convert_with_pymupdf(file_path)

    raise Exception("无可用转换工具")
```

#### 模式 2: 质量优先

```python
def quality_first_convert(file_path):
    """优先质量的转换策略"""
    # 重要文档使用 doc2md（质量最高）
    if is_important_document(file_path):
        return convert_with_doc2md(file_path)

    # 普通文档使用 pandoc（速度快）
    return convert_with_pandoc(file_path)
```

### 配置示例

```yaml
conversion:
  # 首选工具
  preferred_tool: "doc2md"

  # 降级策略
  fallback_order:
    - "doc2md"
    - "pandoc"
    - "pymupdf"
    - "direct"  # 仅 Markdown

  # 质量优先场景
  quality_first_patterns:
    - "*-重要.pdf"
    - "规范*.docx"
    - "需求*.pdf"
```

---

## 与版本控制系统集成

### Git 集成

#### 自动忽略索引文件

在 `.gitignore` 中添加:
```
# 知识库索引
_index.yaml
_index.yaml.backup
.index_cache/
```

#### 或提交索引到仓库

**优势**:
- 团队共享索引
- 版本追踪索引变更

**在 `.gitignore` 中**:
```
# 忽略备份和缓存
_index.yaml.backup
.index_cache/

# 不忽略索引文件本身
# _index.yaml
```

#### Git 钩子集成

**pre-commit 钩子**: 自动更新索引

```bash
#!/bin/bash
# .git/hooks/pre-commit

# 检查知识库文件是否变更
if git diff --cached --name-only | grep -q "知识库/"; then
    echo "检测到知识库文件变更，更新索引..."

    # 在 Claude Code 中触发更新
    # 实际实现可能需要通过 API 调用
    echo "请手动运行: 为「知识库」更新索引"
fi
```

---

## 与 CI/CD 集成

### GitHub Actions

```yaml
# .github/workflows/update-index.yml
name: Update Knowledge Base Index

on:
  push:
    paths:
      - 'knowledge-base/**'
  schedule:
    - cron: '0 2 * * 0'  # 每周日凌晨 2 点

jobs:
  update-index:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Claude Code
        run: |
          # 安装 Claude Code CLI
          # 实际实现取决于 Claude Code 的安装方式

      - name: Update Index
        run: |
          # 触发索引更新
          claude-code skill knowledge-index --action update --path knowledge-base

      - name: Commit Changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add knowledge-base/_index.yaml
          git commit -m "chore: update knowledge base index" || echo "No changes"
          git push
```

### GitLab CI

```yaml
# .gitlab-ci.yml
update-knowledge-index:
  stage: build
  script:
    - echo "Updating knowledge base index..."
    # 触发索引更新
    - claude-code skill knowledge-index --action update --path knowledge-base
  only:
    changes:
      - knowledge-base/**/*
  artifacts:
    paths:
      - knowledge-base/_index.yaml
    expire_in: 1 week
```

---

## 与文档管理系统集成

### Obsidian 集成

#### 配置

在 Obsidian vault 根目录:

```yaml
# _index_config.yaml
indexing:
  file_types:
    - ".md"

  exclude:
    - ".obsidian/"
    - ".trash/"
    - "templates/"

  summary:
    max_length: 200
```

#### 自动化脚本

```python
import os
import subprocess

def update_obsidian_index(vault_path):
    """更新 Obsidian 索引"""
    # 触发 Claude Code 更新索引
    subprocess.run([
        'claude-code', 'skill', 'knowledge-index',
        '--action', 'update',
        '--path', vault_path
    ])

    print(f"✓ Obsidian 索引已更新: {vault_path}")

# 定时任务（使用 cron 或 Windows Task Scheduler）
if __name__ == "__main__":
    vault_path = "/path/to/obsidian/vault"
    update_obsidian_index(vault_path)
```

---

### Notion 集成（导出后）

#### 导出流程

1. 从 Notion 导出为 Markdown
2. 保存到本地文件夹
3. 为该文件夹建立索引

#### 自动化脚本

```python
def sync_notion_to_index(notion_export_path, index_path):
    """同步 Notion 导出到索引"""
    # 1. 检查导出文件
    if not os.path.exists(notion_export_path):
        raise Exception("Notion 导出文件不存在")

    # 2. 更新索引
    subprocess.run([
        'claude-code', 'skill', 'knowledge-index',
        '--action', 'update',
        '--path', notion_export_path
    ])

    print("✓ Notion 导出已同步到索引")
```

---

## 与搜索引擎集成

### Elasticsearch 集成

#### 同步索引到 Elasticsearch

```python
from elasticsearch import Elasticsearch
import yaml

def sync_to_elasticsearch(index_path, es_host='localhost'):
    """同步知识库索引到 Elasticsearch"""
    # 读取索引
    with open(index_path, encoding='utf-8') as f:
        index = yaml.safe_load(f)

    # 连接 Elasticsearch
    es = Elasticsearch([es_host])

    # 创建索引（如果不存在）
    index_name = "knowledge-base"
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)

    # 同步文档
    for doc in index['documents']:
        es.index(
            index=index_name,
            id=doc['path'],
            body={
                'path': doc['path'],
                'filename': doc['filename'],
                'summary': doc['summary'],
                'keywords': doc['keywords'],
                'topics': doc['topics'],
                'modified': doc['modified']
            }
        )

    print(f"✓ 已同步 {len(index['documents'])} 个文档到 Elasticsearch")
```

---

### Algolia 集成

```python
from algoliasearch.search_client import SearchClient
import yaml

def sync_to_algolia(index_path, app_id, api_key):
    """同步知识库索引到 Algolia"""
    # 读取索引
    with open(index_path, encoding='utf-8') as f:
        index = yaml.safe_load(f)

    # 连接 Algolia
    client = SearchClient.create(app_id, api_key)
    algolia_index = client.init_index('knowledge-base')

    # 准备数据
    records = []
    for doc in index['documents']:
        records.append({
            'objectID': doc['path'],
            'filename': doc['filename'],
            'summary': doc['summary'],
            'keywords': doc['keywords'],
            'topics': doc['topics'],
            'modified': doc['modified']
        })

    # 批量上传
    algolia_index.save_objects(records)

    print(f"✓ 已同步 {len(records)} 个文档到 Algolia")
```

---

## 与自动化工具集成

### 定时更新（cron）

```bash
# crontab -e

# 每天凌晨 3 点更新索引
0 3 * * * /usr/bin/claude-code skill knowledge-index --action update --path /path/to/kb >> /var/log/kb-index.log 2>&1

# 每周日凌晨 2 点重建索引
0 2 * * 0 /usr/bin/claude-code skill knowledge-index --action rebuild --path /path/to/kb >> /var/log/kb-index.log 2>&1
```

### Windows Task Scheduler

```powershell
# 创建计划任务
$Action = New-ScheduledTaskAction -Execute "claude-code" -Argument "skill knowledge-index --action update --path C:\Knowledge"
$Trigger = New-ScheduledTaskTrigger -Daily -At 3am
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable

Register-ScheduledTask -TaskName "Update Knowledge Base Index" -Action $Action -Trigger $Trigger -Settings $Settings
```

---

## API 集成

### REST API 包装

```python
from flask import Flask, jsonify, request
import yaml

app = Flask(__name__)

@app.route('/api/index/build', methods=['POST'])
def build_index():
    """构建索引 API"""
    data = request.json
    kb_path = data.get('path')

    # 触发构建
    result = build_knowledge_index(kb_path)

    return jsonify({
        'success': True,
        'index_path': f"{kb_path}/_index.yaml",
        'document_count': result['count']
    })

@app.route('/api/index/search', methods=['GET'])
def search_index():
    """搜索索引 API"""
    kb_path = request.args.get('path')
    query = request.args.get('query')

    # 读取索引并搜索
    results = search_knowledge_base(kb_path, query)

    return jsonify({
        'success': True,
        'results': results
    })

if __name__ == '__main__':
    app.run(debug=True)
```

### GraphQL API

```python
from graphene import ObjectType, String, List, Schema
import yaml

class Document(ObjectType):
    path = String()
    filename = String()
    summary = String()
    keywords = List(String)

class Query(ObjectType):
    documents = List(Document, path=String(required=True))
    search = List(Document, path=String(required=True), query=String(required=True))

    def resolve_documents(self, info, path):
        # 读取索引
        with open(f"{path}/_index.yaml", encoding='utf-8') as f:
            index = yaml.safe_load(f)

        return [Document(**doc) for doc in index['documents']]

    def resolve_search(self, info, path, query):
        # 搜索文档
        results = search_knowledge_base(path, query)
        return [Document(**doc) for doc in results]

schema = Schema(query=Query)
```

---

## 最佳实践

### 1. 索引文件管理

- **小型团队**: 提交索引到版本控制
- **大型团队**: 忽略索引，各自维护
- **CI/CD**: 自动更新索引

### 2. 更新策略

- **频繁更新**: 每日自动更新
- **中等更新**: 每周自动更新
- **偶尔更新**: 手动更新

### 3. 备份策略

- 每次更新前自动备份
- 保留最近 3-5 个备份
- 重要知识库额外备份到云存储

### 4. 性能优化

- 大型知识库使用增量更新
- 定期重建索引（如每月）
- 监控索引构建性能

---

## 相关资源

- 工具支持: `references/execution/tools.md`
- 性能优化: `references/advanced/performance-tuning.md`
- 故障排除: `references/execution/troubleshooting.md`
