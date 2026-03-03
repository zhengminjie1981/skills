# 性能优化

本文档提供知识库索引的性能优化策略和配置建议。

## 性能瓶颈分析

### 常见瓶颈

| 瓶颈 | 原因 | 影响 |
|------|------|------|
| 文档转换 | I/O 密集，工具速度慢 | 构建时间长 |
| AI 摘要生成 | API 调用延迟，网络限制 | 等待时间长 |
| 文件扫描 | 大量小文件，递归遍历 | 扫描时间长 |
| 索引写入 | YAML 序列化，磁盘 I/O | 写入时间长 |

### 性能指标

| 指标 | 小型（<100） | 中型（100-500） | 大型（>500） |
|------|-------------|----------------|-------------|
| 扫描速度 | < 1 秒 | 1-5 秒 | 5-30 秒 |
| 转换速度 | 5-10 秒/文档 | 10-20 秒/文档 | 20-30 秒/文档 |
| 摘要速度 | 2-5 秒/文档 | 2-5 秒/文档 | 2-5 秒/文档 |
| 总构建时间 | < 5 分钟 | 5-30 分钟 | 30 分钟-2 小时 |

---

## 优化策略

### 1. 文档转换优化

#### 1.1 选择快速工具

**工具性能对比**:

| 工具 | PDF 转换速度 | 内存占用 | 推荐场景 |
|------|-------------|---------|---------|
| doc2md | 中（5-10 秒） | 中（50-100MB） | 高质量摘要 |
| pandoc | 快（2-5 秒） | 低（20-50MB） | 通用转换 |
| PyMuPDF | 极快（1-2 秒） | 低（10-30MB） | 大规模知识库 |

**配置示例**:
```yaml
conversion:
  preferred_tool: "pymupdf"  # 使用最快的工具
```

---

#### 1.2 并行转换

**原理**: 多线程处理多个文档

**实现**:
```python
from concurrent.futures import ThreadPoolExecutor

def parallel_convert(files, max_workers=4):
    """并行转换文档"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(convert_document, f) for f in files]
        results = [f.result() for f in futures]
    return results
```

**配置**:
```yaml
performance:
  parallel_workers: 4  # 根据 CPU 核心数调整
```

**性能提升**: 2-4 倍

---

#### 1.3 转换缓存

**原理**: 缓存转换结果，避免重复转换

**实现**:
```python
import hashlib
import pickle

def convert_with_cache(file_path, cache_dir=".cache"):
    """带缓存的文档转换"""
    # 计算文件哈希
    file_hash = calculate_hash(file_path)
    cache_file = f"{cache_dir}/{file_hash}.pkl"

    # 检查缓存
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)

    # 转换文档
    markdown = convert_document(file_path)

    # 保存缓存
    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_file, 'wb') as f:
        pickle.dump(markdown, f)

    return markdown
```

**配置**:
```yaml
performance:
  enable_cache: true
  cache_dir: ".index_cache"
```

**性能提升**: 增量更新时 5-10 倍

---

### 2. AI 摘要生成优化

#### 2.1 批量 API 调用

**原理**: 一次 API 调用处理多个文档

**实现**:
```python
def batch_generate_summaries(documents, batch_size=10):
    """批量生成摘要"""
    summaries = []

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]

        # 一次 API 调用处理多个文档
        batch_summaries = ai_batch_summarize(batch)
        summaries.extend(batch_summaries)

    return summaries
```

**配置**:
```yaml
summary:
  batch_api: true
  batch_size: 10
```

**性能提升**: 2-3 倍（减少网络往返）

---

#### 2.2 摘要长度控制

**原理**: 减少摘要长度，降低 API 负载

**配置**:
```yaml
summary:
  max_length: 200  # 减少到 200 字符
```

**性能提升**: 20-30%

---

#### 2.3 超时控制

**原理**: 避免单个文档卡住整个流程

**实现**:
```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("摘要生成超时")

def generate_summary_with_timeout(content, timeout=10):
    """带超时的摘要生成"""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    try:
        summary = ai_generate_summary(content)
        signal.alarm(0)  # 取消定时器
        return summary
    except TimeoutError:
        # 降级：使用文档前 200 字符
        return content[:200] + "..."
```

**配置**:
```yaml
summary:
  timeout_seconds: 10
```

---

### 3. 文件扫描优化

#### 3.1 排除规则优化

**原理**: 减少不必要的文件扫描

**配置**:
```yaml
exclude:
  - ".git"          # 排除 Git 目录
  - ".obsidian"     # 排除 Obsidian 配置
  - "node_modules"  # 排除 Node 模块
  - "*.tmp"         # 排除临时文件
  - "drafts/"       # 排除草稿文件夹
```

**性能提升**: 10-30%（取决于目录结构）

---

#### 3.2 文件类型限制

**原理**: 仅扫描支持的文件类型

**配置**:
```yaml
indexing:
  file_types:
    - ".md"
    - ".pdf"
    - ".docx"
    # 移除不常用的格式
```

**性能提升**: 5-10%

---

### 4. 索引写入优化

#### 4.1 原子写入

**原理**: 先写临时文件，再重命名

**实现**:
```python
def atomic_write_index(index, file_path):
    """原子写入索引文件"""
    temp_path = f"{file_path}.tmp"

    # 写入临时文件
    with open(temp_path, 'w', encoding='utf-8') as f:
        yaml.dump(index, f)

    # 原子重命名
    os.rename(temp_path, file_path)
```

**优势**:
- 避免写入过程中断导致损坏
- 提高写入速度

---

#### 4.2 索引压缩

**原理**: 移除冗余字段，减小文件大小

**实现**:
```python
def compress_index(index):
    """压缩索引文件"""
    for doc in index['documents']:
        # 移除空字段
        if not doc.get('hash'):
            del doc['hash']

        # 缩短摘要
        if len(doc['summary']) > 300:
            doc['summary'] = doc['summary'][:300]

        # 限制关键词
        doc['keywords'] = doc['keywords'][:5]

    return index
```

**性能提升**: 写入速度 10-20%，文件大小减小 20-30%

---

## 大规模知识库优化

### 1. 分批处理

**配置**:
```yaml
performance:
  batch_size: 100  # 每批处理 100 个文档
  batch_delay_seconds: 5  # 批次间延迟 5 秒
```

**实现**:
```python
def batch_build_index(files, batch_size=100):
    """分批构建索引"""
    index = create_empty_index()

    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]

        # 处理批次
        batch_results = process_batch(batch)
        index['documents'].extend(batch_results)

        # 进度报告
        print(f"进度: {min(i+batch_size, len(files))}/{len(files)}")

        # 批次间延迟（避免过载）
        time.sleep(5)

    return index
```

**性能提升**: 避免内存溢出，稳定处理大规模知识库

---

### 2. 并行处理

**配置**:
```yaml
performance:
  parallel_workers: 8  # 8 个并行工作线程
  parallel_batch_size: 50  # 每个线程处理 50 个文档
```

**实现**:
```python
from concurrent.futures import ProcessPoolExecutor

def parallel_build_index(files, max_workers=8, batch_size=50):
    """并行构建索引"""
    # 分割文件列表
    batches = [files[i:i+batch_size] for i in range(0, len(files), batch_size)]

    # 并行处理
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(process_batch, batches)

    # 合并结果
    index = create_empty_index()
    for batch_result in results:
        index['documents'].extend(batch_result['documents'])

    return index
```

**性能提升**: 4-8 倍（取决于 CPU 核心数）

---

### 3. 内存优化

**问题**: 大规模知识库索引构建内存占用高

**解决方案**:

#### 3.1 流式处理

```python
def stream_build_index(files):
    """流式构建索引（避免内存堆积）"""
    index_path = "_index.yaml"

    # 写入索引头部
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("version: '1.0'\n")
        f.write("knowledge_base:\n")
        f.write("  name: '知识库'\n")
        f.write("documents:\n")

    # 逐个处理文档，流式追加
    for file in files:
        doc_entry = process_document(file)

        with open(index_path, 'a', encoding='utf-8') as f:
            yaml.dump([doc_entry], f)

    # 写入索引尾部（统计信息）
    finalize_index(index_path)
```

**内存节省**: 50-80%

---

#### 3.2 增量保存

```python
def incremental_save(index, file_path, interval=50):
    """每处理 N 个文档保存一次"""
    for i, file in enumerate(files):
        process_document(file)

        # 每处理 50 个文档保存一次
        if (i + 1) % interval == 0:
            save_index(index, file_path)
            print(f"已保存: {i+1}/{len(files)}")
```

**优势**:
- 避免进程中断导致进度丢失
- 减少内存占用

---

## 配置优化指南

### 小型知识库（<100 文档）

```yaml
indexing:
  file_types:
    - ".md"
    - ".pdf"
    - ".docx"

  summary:
    max_length: 300
    include_keywords: true

  update_detection:
    method: "hash"  # 精确检测

performance:
  batch_size: 50
  parallel_workers: 2
  enable_cache: false  # 小型知识库无需缓存
```

**预期性能**: 构建时间 < 5 分钟

---

### 中型知识库（100-500 文档）

```yaml
indexing:
  file_types:
    - ".md"
    - ".pdf"
    - ".docx"

  summary:
    max_length: 200
    include_keywords: true

  update_detection:
    method: "hybrid"  # 平衡速度和精度

performance:
  batch_size: 100
  parallel_workers: 4
  enable_cache: true
```

**预期性能**: 构建时间 5-30 分钟

---

### 大型知识库（>500 文档）

```yaml
indexing:
  file_types:
    - ".md"
    - ".pdf"

  summary:
    max_length: 150  # 减少摘要长度
    include_keywords: true
    keywords_count: 3  # 减少关键词数量

  update_detection:
    method: "mtime"  # 快速检测

conversion:
  preferred_tool: "pymupdf"  # 使用最快的工具

performance:
  batch_size: 200
  parallel_workers: 8
  enable_cache: true
```

**预期性能**: 构建时间 30 分钟-2 小时

---

## 性能监控

### 监控指标

```python
import time

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.metrics = {}

    def record(self, stage, duration):
        """记录阶段耗时"""
        if stage not in self.metrics:
            self.metrics[stage] = []
        self.metrics[stage].append(duration)

    def report(self):
        """生成性能报告"""
        total_time = time.time() - self.start_time

        print("性能报告:")
        print(f"  总耗时: {total_time:.2f} 秒")

        for stage, durations in self.metrics.items():
            avg_time = sum(durations) / len(durations)
            total_stage_time = sum(durations)
            print(f"  {stage}:")
            print(f"    - 总耗时: {total_stage_time:.2f} 秒")
            print(f"    - 平均: {avg_time:.2f} 秒/次")
            print(f"    - 次数: {len(durations)}")
```

### 使用示例

```python
monitor = PerformanceMonitor()

# 记录转换时间
start = time.time()
markdown = convert_document(file)
monitor.record('conversion', time.time() - start)

# 记录摘要生成时间
start = time.time()
summary = generate_summary(markdown)
monitor.record('summary', time.time() - start)

# 生成报告
monitor.report()
```

---

## 相关资源

- 增量更新优化: `references/advanced/incremental-update.md`
- 工具支持: `references/execution/tools.md`
- 故障排除: `references/execution/troubleshooting.md`
