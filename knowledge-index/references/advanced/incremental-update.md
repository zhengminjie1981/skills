# 增量更新优化

本文档详细说明知识库索引的增量更新机制和优化策略。

## 增量更新原理

### 核心思想

```
只处理变更的文档，避免全量重建
```

### 优势

- **时间节省**: 仅处理变更部分，大幅减少处理时间
- **资源节约**: 减少 AI API 调用和计算资源消耗
- **数据保留**: 保留未变更文档的摘要和元数据

## 变更检测算法

### 1. mtime 方法（修改时间）

**原理**: 对比文件修改时间

**伪代码**:
```python
def detect_changes_mtime(kb_path, old_index):
    current_files = scan_directory(kb_path)
    changes = {'added': [], 'modified': [], 'deleted': []}

    # 检测新增和修改
    for file in current_files:
        if file.path not in old_index:
            changes['added'].append(file)
        elif file.mtime > old_index[file.path].modified:
            changes['modified'].append(file)

    # 检测删除
    for indexed_file in old_index:
        if indexed_file not in current_files:
            changes['deleted'].append(indexed_file)

    return changes
```

**优点**:
- 速度快（O(n)）
- 无需读取文件内容

**缺点**:
- 可能误判（文件复制、移动会改变 mtime）
- 精度受文件系统限制（通常 1-2 秒）

**适用场景**:
- 大型知识库（>100 文档）
- 频繁更新
- 对精确性要求不高

---

### 2. hash 方法（内容哈希）

**原理**: 计算文件内容哈希值对比

**伪代码**:
```python
import hashlib

def detect_changes_hash(kb_path, old_index):
    current_files = scan_directory(kb_path)
    changes = {'added': [], 'modified': [], 'deleted': []}

    # 检测新增和修改
    for file in current_files:
        current_hash = calculate_hash(file.path)

        if file.path not in old_index:
            changes['added'].append(file)
        elif current_hash != old_index[file.path].hash:
            changes['modified'].append(file)

    # 检测删除
    for indexed_file in old_index:
        if indexed_file not in current_files:
            changes['deleted'].append(indexed_file)

    return changes

def calculate_hash(file_path, algorithm='md5'):
    """计算文件哈希"""
    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()
```

**优点**:
- 精确（检测内容变更）
- 不受文件系统操作影响

**缺点**:
- 速度慢（需读取所有文件）
- 计算开销大

**适用场景**:
- 小型知识库（<100 文档）
- 需要精确检测
- 重要知识库

---

### 3. 混合方法（推荐）

**原理**: mtime 初筛 + hash 精确验证

**伪代码**:
```python
def detect_changes_hybrid(kb_path, old_index):
    current_files = scan_directory(kb_path)
    changes = {'added': [], 'modified': [], 'deleted': []}

    # Step 1: mtime 初筛
    potential_changes = []
    for file in current_files:
        if file.path not in old_index:
            changes['added'].append(file)
        elif file.mtime > old_index[file.path].modified + 2:  # 2秒容差
            potential_changes.append(file)

    # Step 2: hash 精确验证
    for file in potential_changes:
        current_hash = calculate_hash(file.path)
        if current_hash != old_index[file.path].hash:
            changes['modified'].append(file)

    # 检测删除
    for indexed_file in old_index:
        if indexed_file not in current_files:
            changes['deleted'].append(indexed_file)

    return changes
```

**优点**:
- 平衡速度和精度
- 减少不必要的 hash 计算

**适用场景**:
- 中型知识库（50-500 文档）
- 需要平衡性能和精度

---

## 算法选择指南

| 知识库规模 | 更新频率 | 精度要求 | 推荐算法 |
|-----------|---------|---------|---------|
| 小（<50） | 低 | 高 | hash |
| 小（<50） | 高 | 中 | mtime |
| 中（50-200） | 低 | 高 | 混合 |
| 中（50-200） | 高 | 中 | mtime |
| 大（>200） | 低 | 高 | 混合 |
| 大（>200） | 高 | 低 | mtime |

**配置示例**:
```yaml
update_detection:
  method: "hybrid"  # mtime, hash, hybrid
  tolerance_seconds: 2
  hash_algorithm: "md5"  # md5, sha256
```

---

## 索引合并算法

### 基本合并流程

```python
def merge_index(old_index, changes):
    """合并新旧索引"""
    new_index = old_index.copy()

    # 处理删除
    for deleted_file in changes['deleted']:
        new_index['documents'].remove(deleted_file)

    # 处理修改
    for modified_file in changes['modified']:
        # 重新生成摘要
        summary = generate_summary(modified_file)
        # 更新索引条目
        update_document_in_index(new_index, modified_file, summary)

    # 处理新增
    for added_file in changes['added']:
        # 生成摘要
        summary = generate_summary(added_file)
        # 添加到索引
        add_document_to_index(new_index, added_file, summary)

    # 更新元数据
    new_index['knowledge_base']['last_updated'] = current_time()
    new_index['knowledge_base']['total_documents'] = len(new_index['documents'])

    return new_index
```

### 保留字段策略

```python
def update_document_in_index(index, file_path, new_summary):
    """更新文档索引，保留部分字段"""
    for doc in index['documents']:
        if doc['path'] == file_path:
            # 更新字段
            doc['modified'] = get_file_mtime(file_path)
            doc['size'] = get_file_size(file_path)
            doc['hash'] = calculate_hash(file_path)
            doc['summary'] = new_summary['summary']
            doc['keywords'] = new_summary['keywords']
            doc['topics'] = new_summary['topics']

            # 保留字段（如用户手动编辑的）
            # doc['custom_field'] 保持不变
            break
```

---

## 性能优化

### 1. 批量处理

**问题**: 大量变更时逐个处理效率低

**解决方案**: 批量处理变更

```python
def batch_process_changes(changes, batch_size=50):
    """批量处理变更"""
    results = []

    # 分批处理
    for i in range(0, len(changes), batch_size):
        batch = changes[i:i+batch_size]

        # 并行处理批次
        batch_results = parallel_process(batch)
        results.extend(batch_results)

        # 进度报告
        print(f"进度: {min(i+batch_size, len(changes))}/{len(changes)}")

    return results
```

**配置**:
```yaml
performance:
  batch_size: 50
  parallel_workers: 4
```

---

### 2. 并行转换

**问题**: 文档转换是 I/O 密集型操作

**解决方案**: 多线程并行转换

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_convert(files, max_workers=4):
    """并行转换文档"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(convert_document, f) for f in files]
        results = [f.result() for f in futures]
    return results
```

---

### 3. 增量摘要生成

**问题**: AI API 调用成本高

**解决方案**: 仅对变更文档生成摘要

```python
def incremental_summary(changes):
    """增量摘要生成"""
    # 仅处理新增和修改的文档
    docs_need_summary = changes['added'] + changes['modified']

    summaries = []
    for doc in docs_need_summary:
        summary = ai_generate_summary(doc)
        summaries.append(summary)

    return summaries
```

**优化**:
- 使用缓存避免重复生成
- 批量 API 调用
- 设置超时控制

---

### 4. 索引压缩

**问题**: 大型索引文件占用空间

**解决方案**: 压缩冗余字段

```python
def compress_index(index):
    """压缩索引文件"""
    for doc in index['documents']:
        # 移除可选字段（如果为空）
        if not doc.get('hash'):
            del doc['hash']

        # 缩短摘要（如果过长）
        if len(doc['summary']) > 500:
            doc['summary'] = doc['summary'][:500]

        # 限制关键词数量
        if len(doc['keywords']) > 10:
            doc['keywords'] = doc['keywords'][:10]

    return index
```

---

## 备份和恢复

### 自动备份机制

```python
def backup_index(kb_path):
    """备份索引文件"""
    index_path = f"{kb_path}/_index.yaml"
    backup_path = f"{kb_path}/_index.yaml.backup"

    # 创建备份
    shutil.copy2(index_path, backup_path)

    # 保留最近 3 个备份
    manage_backups(kb_path, keep=3)

def manage_backups(kb_path, keep=3):
    """管理备份文件"""
    backup_dir = f"{kb_path}/backups"
    backups = sorted(os.listdir(backup_dir))

    # 删除旧备份
    while len(backups) > keep:
        old_backup = backups.pop(0)
        os.remove(f"{backup_dir}/{old_backup}")
```

### 恢复机制

```python
def restore_index(kb_path):
    """从备份恢复索引"""
    backup_path = f"{kb_path}/_index.yaml.backup"
    index_path = f"{kb_path}/_index.yaml"

    if os.path.exists(backup_path):
        shutil.copy2(backup_path, index_path)
        print("✓ 索引已从备份恢复")
    else:
        print("✗ 备份文件不存在")
```

---

## 增量更新流程图

```
开始增量更新
    │
    ├─ Step 1: 备份现有索引
    │
    ├─ Step 2: 选择变更检测算法
    │   ├─ 小型知识库 → hash
    │   ├─ 大型知识库 → mtime
    │   └─ 中型知识库 → hybrid
    │
    ├─ Step 3: 检测变更
    │   ├─ 扫描当前文件
    │   ├─ 对比索引
    │   └─ 生成变更列表
    │
    ├─ Step 4: 批量处理变更
    │   ├─ 处理新增文档
    │   │   ├─ 转换
    │   │   ├─ 生成摘要
    │   │   └─ 添加到索引
    │   │
    │   ├─ 处理修改文档
    │   │   ├─ 重新转换
    │   │   ├─ 重新生成摘要
    │   │   └─ 更新索引
    │   │
    │   └─ 处理删除文档
    │       └─ 从索引中移除
    │
    ├─ Step 5: 合并索引
    │   ├─ 更新元数据
    │   └─ 重新计算统计
    │
    ├─ Step 6: 验证索引
    │   ├─ YAML 语法
    │   ├─ 字段完整性
    │   └─ 统计一致性
    │
    ├─ Step 7: 写入索引文件
    │   └─ 原子写入（先临时文件，再重命名）
    │
    └─ Step 8: 生成报告
        └─ 输出更新统计
```

---

## 最佳实践

### 1. 定期更新

```yaml
# 在 _index_config.yaml 中配置
update_detection:
  auto_check: true
  check_interval_hours: 168  # 每周检查一次
```

### 2. 大批量变更

当有大量变更（如新增 >50 个文档）时:
- 分批更新
- 监控内存使用
- 考虑重建索引

### 3. 重要知识库

对于重要知识库:
- 使用 hash 方法（精确）
- 每次更新前备份
- 验证索引完整性

### 4. 性能监控

```python
def monitor_update_performance(start_time, changes):
    """监控更新性能"""
    elapsed = time.time() - start_time
    total_changes = len(changes['added']) + len(changes['modified']) + len(changes['deleted'])

    print(f"更新耗时: {elapsed:.2f} 秒")
    print(f"处理文档: {total_changes} 个")
    print(f"平均速度: {elapsed/total_changes:.2f} 秒/文档")
```

---

## 相关资源

- 工作流程: `references/core/workflow-spec.md`
- 性能优化: `references/advanced/performance-tuning.md`
- 故障排除: `references/execution/troubleshooting.md`
- 质量门禁: `references/core/quality-gates.md`
