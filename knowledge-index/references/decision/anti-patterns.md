# 反模式案例

本文档列举知识库索引的常见错误做法和最佳实践对比。

## 1. 路径处理反模式

### ❌ 反模式: 使用相对路径不明确

**错误做法**:
```
用户: 帮我建立索引
AI: （未询问路径，假设当前目录）
    为当前目录建立索引...
```

**问题**:
- 可能索引错误的目录
- 用户意图不明确

**✅ 最佳实践**:
```
用户: 帮我建立索引
AI: 请问您要为哪个知识库建立索引？
    可以提供文件夹路径或名称。
用户: 信息化
AI: ✓ 收到请求：为「信息化」建立索引
    开始构建索引...
```

---

### ❌ 反模式: Windows 路径格式错误

**错误做法**:
```python
path = "C:\Users\zheng\knowledge-base"  # \U 被解释为转义序列
```

**问题**:
- Python 字符串转义错误
- 路径无法识别

**✅ 最佳实践**:
```python
# 方式1: 使用正斜杠（推荐）
path = "C:/Users/zheng/knowledge-base"

# 方式2: 使用双反斜杠
path = "C:\\Users\\zheng\\knowledge-base"

# 方式3: 使用原始字符串
path = r"C:\Users\zheng\knowledge-base"
```

---

## 2. 工具使用反模式

### ❌ 反模式: 硬编码依赖 doc2md

**错误做法**:
```python
def convert_pdf(file_path):
    # 假设 doc2md 一定可用
    return call_doc2md(file_path)
```

**问题**:
- doc2md 不可用时索引失败
- 无法降级处理

**✅ 最佳实践**:
```python
def convert_pdf(file_path, available_tools):
    # 按优先级尝试多个工具
    for tool in ['doc2md', 'pandoc', 'pymupdf']:
        if tool in available_tools:
            try:
                return convert_with_tool(tool, file_path)
            except Exception:
                continue

    # 所有工具都失败
    return None
```

---

### ❌ 反模式: 忽略工具检测结果

**错误做法**:
```python
# 未检测工具，直接调用
markdown = call_pandoc(file_path)
```

**问题**:
- pandoc 未安装时报错
- 用户体验差

**✅ 最佳实践**:
```python
# 先检测工具
available_tools = detect_available_tools()

if 'pandoc' in available_tools:
    markdown = call_pandoc(file_path)
else:
    print("⚠️ pandoc 不可用，尝试其他工具...")
    markdown = fallback_convert(file_path)
```

---

## 3. 索引构建反模式

### ❌ 反模式: 索引覆盖整个磁盘

**错误做法**:
```
用户: 为 C:\ 建立索引
AI: （未警告）开始构建索引...
```

**问题**:
- 扫描整个磁盘，耗时极长
- 包含大量无关文件
- 可能包含系统文件

**✅ 最佳实践**:
```
用户: 为 C:\ 建立索引
AI: ⚠️ 警告: C:\ 是系统根目录，包含大量文件
    建议指定具体的知识库文件夹，如：
      - C:\Users\zheng\Documents
      - C:\Knowledge

    是否继续索引 C:\？（不推荐）
```

---

### ❌ 反模式: 不检查现有索引

**错误做法**:
```
用户: 为「信息化」建立索引
AI: （未检查）开始构建索引...
    [覆盖现有索引]
```

**问题**:
- 覆盖现有索引，可能丢失信息
- 用户可能是想更新而非重建

**✅ 最佳实践**:
```
用户: 为「信息化」建立索引
AI: ⚠️ 检测到已有索引文件（最后更新: 2 天前）
    选择操作：
      1. 重建索引（删除旧索引，重新构建）
      2. 更新索引（增量更新，仅处理变更）
```

---

### ❌ 反模式: 单个大文件处理超时

**错误做法**:
```python
def convert_document(file_path):
    # 无超时限制
    result = call_doc2md(file_path)
    return result
```

**问题**:
- 大文件（如 100MB PDF）转换可能耗时数分钟
- 阻塞整个构建流程

**✅ 最佳实践**:
```python
def convert_document(file_path, timeout=30):
    try:
        result = call_doc2md_with_timeout(file_path, timeout)
        return result
    except TimeoutError:
        print(f"⚠️ 转换超时: {file_path}")
        print("建议: 分割大文件或增加超时时间")
        return None
```

---

## 4. 增量更新反模式

### ❌ 反模式: 全量重建代替增量更新

**错误做法**:
```python
def update_index(kb_path):
    # 删除旧索引，重新构建
    os.remove(f"{kb_path}/_index.yaml")
    build_index(kb_path)
```

**问题**:
- 浪费时间处理未变更的文档
- 大型知识库更新耗时极长

**✅ 最佳实践**:
```python
def update_index(kb_path):
    # 读取现有索引
    old_index = load_index(kb_path)

    # 检测变更
    changes = detect_changes(kb_path, old_index)

    # 增量处理
    for new_file in changes['added']:
        add_to_index(new_file)

    for modified_file in changes['modified']:
        update_in_index(modified_file)

    for deleted_file in changes['deleted']:
        remove_from_index(deleted_file)
```

---

### ❌ 反模式: 使用 mtime 检测但忽略时间精度

**错误做法**:
```python
def is_modified(file_path, index_time):
    # 直接比较，不考虑时间精度
    return os.path.getmtime(file_path) > index_time
```

**问题**:
- 文件系统时间精度可能只有 1-2 秒
- 快速操作可能误判

**✅ 最佳实践**:
```python
def is_modified(file_path, index_time, tolerance=2):
    mtime = os.path.getmtime(file_path)
    # 增加时间容差
    return mtime > (index_time + tolerance)
```

---

### ❌ 反模式: 更新失败后不回滚

**错误做法**:
```python
def update_index(kb_path):
    # 直接覆盖索引文件
    new_index = build_new_index(kb_path)
    save_index(new_index, kb_path)  # 失败时旧索引丢失
```

**问题**:
- 更新失败导致索引损坏
- 无法恢复

**✅ 最佳实践**:
```python
def update_index(kb_path):
    # 备份旧索引
    backup_index(kb_path)

    try:
        new_index = build_new_index(kb_path)
        save_index(new_index, kb_path)
    except Exception as e:
        # 回滚到旧索引
        restore_backup(kb_path)
        raise e
```

---

## 5. AI 摘要生成反模式

### ❌ 反模式: 摘要过长或过短

**错误做法**:
```yaml
summary: |
  这是一份非常详细的文档，包含了所有的细节内容...
  [摘要长达 2000 字符]
```

**问题**:
- 失去摘要的简洁性
- 检索时难以快速判断相关性

**✅ 最佳实践**:
```yaml
summary: |
  本文档介绍 GitLab 的完整使用流程：
  1. 配置管理：SSH密钥、项目设置
  2. 协作开发：分支策略、Merge Request
  3. CI/CD：流水线配置、自动化部署
# 摘要长度: 120 字符（适中）
```

---

### ❌ 反模式: 关键词过于通用

**错误做法**:
```yaml
keywords: ["文档", "说明", "介绍", "指南", "手册"]
```

**问题**:
- 无检索价值
- 无法区分文档

**✅ 最佳实践**:
```yaml
keywords: ["GitLab", "CI/CD", "版本控制", "DevOps", "流水线"]
```

---

### ❌ 反模式: 摘要失败后不降级

**错误做法**:
```python
def generate_summary(content):
    summary = ai_generate_summary(content)
    if not summary:
        raise Exception("摘要生成失败")
```

**问题**:
- 整个构建流程中断
- 用户无法获得索引

**✅ 最佳实践**:
```python
def generate_summary(content):
    try:
        summary = ai_generate_summary(content)
        return summary
    except Exception:
        # 降级：使用文档前 200 字符
        return content[:200] + "..."
```

---

## 6. 智能检索反模式

### ❌ 反模式: 索引过期但不警告

**错误做法**:
```python
def search(query, kb_path):
    index = load_index(kb_path)
    return match_documents(query, index)
```

**问题**:
- 用户不知道索引已过期
- 检索结果可能不准确

**✅ 最佳实践**:
```python
def search(query, kb_path):
    index = load_index(kb_path)

    # 检查索引新鲜度
    if is_index_stale(index):
        print("⚠️ 警告: 索引已过期（最后更新: 30 天前）")
        print("建议运行「更新索引」以获得最新结果")

    return match_documents(query, index)
```

---

### ❌ 反模式: 返回过多结果

**错误做法**:
```python
def search(query, index):
    # 返回所有匹配的文档（可能 50+ 个）
    return all_matched_documents
```

**问题**:
- 用户信息过载
- 难以找到最相关的文档

**✅ 最佳实践**:
```python
def search(query, index):
    matched = match_documents(query, index)
    # 按相关度排序，返回前 5 个
    top_results = sorted(matched, key=relevance, reverse=True)[:5]
    return top_results
```

---

### ❌ 反模式: 不显示相关度评分

**错误做法**:
```
找到相关文档:
  - 文档1.pdf
  - 文档2.md
  - 文档3.docx
```

**问题**:
- 用户不知道哪些文档最相关
- 无法判断优先级

**✅ 最佳实践**:
```
找到相关文档:
  - 文档1.pdf (相关度: 5/5)
  - 文档2.md (相关度: 4/5)
  - 文档3.docx (相关度: 2/5)
```

---

## 7. 配置反模式

### ❌ 反模式: 过于严格的排除规则

**错误做法**:
```yaml
exclude:
  - "*.md"  # 排除所有 Markdown
```

**问题**:
- 可能排除所有文档
- 索引为空

**✅ 最佳实践**:
```yaml
exclude:
  - "README.md"  # 只排除特定文件
  - "templates/"  # 排除特定文件夹
```

---

### ❌ 反模式: 不验证配置文件

**错误做法**:
```python
config = yaml.load(config_file)
# 直接使用配置，不验证
```

**问题**:
- 配置错误导致构建失败
- 难以定位问题

**✅ 最佳实践**:
```python
config = yaml.safe_load(config_file)
validate_config(config)

def validate_config(config):
    if 'indexing' not in config:
        raise ValueError("配置缺少 'indexing' 字段")

    if config['indexing'].get('file_types'):
        for ext in config['indexing']['file_types']:
            if not ext.startswith('.'):
                raise ValueError(f"文件扩展名应以点开头: {ext}")
```

---

## 8. 错误处理反模式

### ❌ 反模式: 错误信息不明确

**错误做法**:
```
错误: 构建失败
```

**问题**:
- 用户不知道失败原因
- 无法自行修复

**✅ 最佳实践**:
```
错误: 文档转换失败
文件: large-document.pdf
原因: 转换超时（超过 30 秒）

建议:
  1. 分割大文件
  2. 在配置中增加超时时间
  3. 使用更快的转换工具
```

---

### ❌ 反模式: 单个文档失败中断整个流程

**错误做法**:
```python
for doc in documents:
    convert(doc)  # 一个失败，全部中断
    add_to_index(doc)
```

**问题**:
- 一个文档失败导致整个索引失败
- 浪费已处理的工作

**✅ 最佳实践**:
```python
errors = []
for doc in documents:
    try:
        convert(doc)
        add_to_index(doc)
    except Exception as e:
        errors.append((doc, e))
        continue  # 继续处理其他文档

# 最后报告错误
if errors:
    print(f"⚠️ {len(errors)} 个文档处理失败:")
    for doc, error in errors:
        print(f"  - {doc}: {error}")
```

---

## 反模式检查清单

在构建或更新索引时，避免以下反模式:

- [ ] 使用不明确的路径
- [ ] 硬编码依赖特定工具
- [ ] 忽略工具检测结果
- [ ] 索引覆盖整个磁盘或系统目录
- [ ] 不检查现有索引就覆盖
- [ ] 处理大文件无超时限制
- [ ] 全量重建代替增量更新
- [ ] 忽略时间精度问题
- [ ] 更新失败不回滚
- [ ] 摘要过长或关键词过于通用
- [ ] 摘要失败不降级处理
- [ ] 索引过期不警告
- [ ] 返回过多检索结果
- [ ] 不显示相关度评分
- [ ] 配置过于严格或不验证
- [ ] 错误信息不明确
- [ ] 单个文档失败中断整个流程

---

## 相关资源

- 决策树: `references/decision/decision-tree.md`
- 快速参考: `references/decision/quick-reference.md`
- 故障排除: `references/execution/troubleshooting.md`
- 质量门禁: `references/core/quality-gates.md`
