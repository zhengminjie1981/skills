# 全局注册表规范

> **版本**: 2.1
> **最后更新**: 2026-03-04

## 概述

全局注册表维护所有知识库的元信息，支持快速发现、跨知识库检索和层级冲突检测。

## 注册表位置

### 默认路径

```bash
# Windows
C:/Users/{username}/.knowledge-index/registry.yaml

# Linux/macOS
~/.knowledge-index/registry.yaml
```

### 环境变量配置（可选）

```bash
# 自定义注册表路径
export KNOWLEDGE_INDEX_REGISTRY="/custom/path/registry.yaml"
```

---

## 注册表结构

### 完整格式

```yaml
# 全局注册表
version: "1.0"
last_updated: "2026-03-04T10:00:00Z"
registry_path: "C:/Users/zheng/.knowledge-index/registry.yaml"

# 所有知识库列表
knowledge_bases:
  # 知识库 1
  - name: "信息化知识库"
    path: "E:/知识库/信息化"                    # 知识库根目录（绝对路径）
    index_path: "E:/知识库/信息化/_index.yaml"  # 索引文件路径
    created: "2026-02-15T10:00:00Z"            # 创建时间
    last_updated: "2026-03-04T09:30:00Z"       # 最后更新时间
    last_indexed: "2026-03-04T09:30:00Z"       # 最后索引时间
    document_count: 15                         # 文档总数
    total_size_mb: 2.5                         # 总大小（MB）
    status: "active"                           # active, deleted, moved, error

    # 层级信息
    hierarchy:
      parent: null                             # 父知识库路径（如果有）
      depth: 0                                 # 层级深度（0=顶级）
      children: []                             # 子知识库路径列表

    # 统计信息
    stats:
      file_types:                              # 文件类型分布
        markdown: 10
        pdf: 3
        word: 2
      avg_document_size_kb: 166.7
      last_scan_duration_sec: 5.2

    # 配置信息
    config:
      has_custom_config: true                  # 是否有 _index_config.yaml
      read_strategy: "hybrid"                  # 读取策略
      exclude_patterns:                        # 排除规则
        - ".git"
        - "templates/"

  # 知识库 2
  - name: "项目文档"
    path: "D:/Projects/文档"
    index_path: "D:/Projects/文档/_index.yaml"
    created: "2026-01-20T14:00:00Z"
    last_updated: "2026-03-03T16:00:00Z"
    last_indexed: "2026-03-03T16:00:00Z"
    document_count: 32
    total_size_mb: 5.8
    status: "active"

    hierarchy:
      parent: null
      depth: 0
      children: []
```

### 最小格式（仅必填字段）

```yaml
version: "1.0"
last_updated: "2026-03-04T10:00:00Z"
knowledge_bases:
  - name: "信息化知识库"
    path: "E:/知识库/信息化"
    index_path: "E:/知识库/信息化/_index.yaml"
    last_updated: "2026-03-04T09:30:00Z"
    document_count: 15
```

---

## 字段说明

### 元数据字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `version` | string | ✅ | 注册表格式版本 |
| `last_updated` | datetime | ✅ | 注册表最后更新时间 |
| `registry_path` | string | ❌ | 注册表文件路径（绝对路径） |

### 知识库字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 知识库显示名称 |
| `path` | string | ✅ | 知识库根目录（绝对路径） |
| `index_path` | string | ✅ | 索引文件路径（绝对路径） |
| `created` | datetime | ✅ | 知识库创建时间 |
| `last_updated` | datetime | ✅ | 索引最后更新时间 |
| `last_indexed` | datetime | ❌ | 最后索引时间 |
| `document_count` | integer | ✅ | 文档总数 |
| `total_size_mb` | float | ✅ | 总大小（MB） |
| `status` | string | ✅ | 状态：active/deleted/moved/error |

### 层级字段（hierarchy）

| 字段 | 类型 | 说明 |
|------|------|------|
| `parent` | string | 父知识库路径（null 表示顶级） |
| `depth` | integer | 层级深度（0=顶级，1=一级子，2=二级子...） |
| `children` | array | 子知识库路径列表 |

### 统计字段（stats）

| 字段 | 类型 | 说明 |
|------|------|------|
| `file_types` | object | 文件类型分布 |
| `avg_document_size_kb` | float | 平均文档大小 |
| `last_scan_duration_sec` | float | 最后扫描耗时 |

### 配置字段（config）

| 字段 | 类型 | 说明 |
|------|------|------|
| `has_custom_config` | boolean | 是否有自定义配置 |
| `read_strategy` | string | 读取策略 |
| `exclude_patterns` | array | 排除规则 |

---

## 注册表操作

### 1. 注册知识库

**触发时机**：创建新索引时

**操作**：
```python
def register_knowledge_base(kb_path, index_path, metadata):
    """注册知识库到全局注册表"""

    # 1. 检查是否已注册
    if find_in_registry(kb_path):
        return update_registry_entry(kb_path, metadata)

    # 2. 检测父知识库
    parent_kb = find_parent_knowledge_base(kb_path)

    # 3. 检测子知识库
    child_kbs = find_child_knowledge_bases(kb_path)

    # 4. 创建注册条目
    entry = {
        "name": metadata.get("name", os.path.basename(kb_path)),
        "path": kb_path,
        "index_path": index_path,
        "created": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "document_count": metadata.get("document_count", 0),
        "total_size_mb": metadata.get("total_size_mb", 0),
        "status": "active",
        "hierarchy": {
            "parent": parent_kb["path"] if parent_kb else None,
            "depth": calculate_depth(kb_path, parent_kb),
            "children": [child["path"] for child in child_kbs]
        }
    }

    # 5. 添加到注册表
    registry["knowledge_bases"].append(entry)
    registry["last_updated"] = datetime.now().isoformat()

    # 6. 保存注册表
    save_registry()

    # 7. 如果有子知识库，标记为需要合并
    if child_kbs:
        mark_for_promotion(kb_path, child_kbs)
```

**示例输出**：
```
✓ 已注册到全局目录
  - 知识库: 信息化知识库
  - 路径: E:/知识库/信息化
  - 文档: 15 个
```

---

### 2. 更新注册信息

**触发时机**：更新索引时

**操作**：
```python
def update_registry_entry(kb_path, updates):
    """更新注册表中的知识库信息"""

    # 1. 查找条目
    entry = find_in_registry(kb_path)
    if not entry:
        raise Exception(f"知识库未注册: {kb_path}")

    # 2. 更新字段
    entry.update(updates)
    entry["last_updated"] = datetime.now().isoformat()

    # 3. 保存注册表
    save_registry()
```

---

### 3. 注销知识库

**触发时机**：删除索引或层级提升时

**操作**：
```python
def unregister_knowledge_base(kb_path):
    """从注册表移除知识库"""

    # 1. 查找并移除条目
    registry["knowledge_bases"] = [
        kb for kb in registry["knowledge_bases"]
        if kb["path"] != kb_path
    ]

    # 2. 更新时间戳
    registry["last_updated"] = datetime.now().isoformat()

    # 3. 保存注册表
    save_registry()
```

---

### 4. 查询知识库

**列出所有知识库**：
```python
def list_knowledge_bases():
    """列出所有注册的知识库"""

    return [
        {
            "name": kb["name"],
            "path": kb["path"],
            "document_count": kb["document_count"],
            "last_updated": kb["last_updated"],
            "status": kb["status"]
        }
        for kb in registry["knowledge_bases"]
        if kb["status"] == "active"
    ]
```

**查找特定知识库**：
```python
def find_knowledge_base(kb_path):
    """查找知识库"""

    for kb in registry["knowledge_bases"]:
        if kb["path"] == kb_path:
            return kb
    return None
```

**查找父知识库**：
```python
def find_parent_knowledge_base(kb_path):
    """查找父知识库（向上递归查找）"""

    current_path = os.path.dirname(kb_path)

    while current_path and current_path != os.path.dirname(current_path):
        # 检查当前路径是否有索引
        parent_index = os.path.join(current_path, "_index.yaml")
        if os.path.exists(parent_index):
            # 查找注册表中的父知识库
            parent_kb = find_knowledge_base(current_path)
            if parent_kb:
                return parent_kb

        # 向上一级
        current_path = os.path.dirname(current_path)

    return None
```

**查找子知识库**：
```python
def find_child_knowledge_bases(kb_path):
    """查找子知识库（向下递归查找）"""

    child_kbs = []

    for kb in registry["knowledge_bases"]:
        # 检查是否是子路径
        if kb["path"].startswith(kb_path + os.sep):
            child_kbs.append(kb)

    return child_kbs
```

---

### 5. 健康检查

**检查知识库状态**：
```python
def check_knowledge_base_health():
    """检查所有知识库的健康状态"""

    issues = []

    for kb in registry["knowledge_bases"]:
        # 检查路径是否存在
        if not os.path.exists(kb["path"]):
            kb["status"] = "deleted"
            issues.append({
                "type": "path_not_found",
                "kb": kb["name"],
                "path": kb["path"]
            })
            continue

        # 检查索引文件是否存在
        if not os.path.exists(kb["index_path"]):
            kb["status"] = "error"
            issues.append({
                "type": "index_not_found",
                "kb": kb["name"],
                "path": kb["index_path"]
            })
            continue

        # 检查索引文件是否损坏
        try:
            with open(kb["index_path"], encoding='utf-8') as f:
                yaml.safe_load(f)
        except Exception as e:
            kb["status"] = "error"
            issues.append({
                "type": "index_corrupted",
                "kb": kb["name"],
                "error": str(e)
            })
            continue

        # 检查是否需要更新
        if is_index_stale(kb):
            issues.append({
                "type": "index_stale",
                "kb": kb["name"],
                "last_updated": kb["last_updated"]
            })

    # 保存状态更新
    save_registry()

    return issues
```

**输出示例**：
```yaml
健康检查完成：
  ✓ 正常: 3 个知识库
  ⚠️ 需要更新: 1 个知识库
  ❌ 路径不存在: 0 个知识库
  ❌ 索引损坏: 0 个知识库

建议：
  - 更新「项目文档」的索引（最后更新: 7 天前）
```

---

## 层级管理

### 检测层级冲突

```python
def detect_hierarchy_conflicts():
    """检测所有层级冲突"""

    conflicts = []

    for kb in registry["knowledge_bases"]:
        # 检查父知识库
        parent = find_parent_knowledge_base(kb["path"])
        if parent:
            conflicts.append({
                "type": "parent_child_conflict",
                "parent": parent,
                "child": kb,
                "suggestion": "promote_to_parent"
            })

        # 检查子知识库
        children = find_child_knowledge_bases(kb["path"])
        if children:
            conflicts.append({
                "type": "has_child_indexes",
                "parent": kb,
                "children": children,
                "suggestion": "promote_to_parent"
            })

    return conflicts
```

### 自动层级提升

```python
def auto_promote_hierarchy():
    """自动执行层级提升"""

    conflicts = detect_hierarchy_conflicts()

    for conflict in conflicts:
        if conflict["type"] == "has_child_indexes":
            # 父索引存在，删除子索引
            parent = conflict["parent"]
            children = conflict["children"]

            print(f"检测到层级冲突: {parent['name']}")
            print(f"  子知识库: {len(children)} 个")

            # 删除所有子索引
            for child in children:
                print(f"  删除子索引: {child['name']}")
                delete_index(child["index_path"])
                unregister_knowledge_base(child["path"])

            # 更新父索引
            print(f"  更新父索引: {parent['name']}")
            update_index(parent["path"])
```

---

## 跨知识库检索

### 搜索所有知识库

```python
def search_all_knowledge_bases(query):
    """在所有知识库中搜索"""

    results = []

    for kb in registry["knowledge_bases"]:
        if kb["status"] != "active":
            continue

        # 读取索引
        index = load_index(kb["index_path"])

        # 匹配文档
        matched_docs = match_documents(query, index)

        if matched_docs:
            results.append({
                "knowledge_base": kb["name"],
                "matches": matched_docs
            })

    return results
```

**输出示例**：
```
在 3 个知识库中搜索: "GitLab 配置"

找到 5 个相关文档：

来自「信息化知识库」:
  1. GitLab 完整指南.md (相关度: 5/5)
  2. CI/CD 配置.pdf (相关度: 4/5)

来自「项目文档」:
  3. DevOps 实践.docx (相关度: 3/5)
  4. GitLab 流水线.md (相关度: 3/5)
  5. 部署文档.pdf (相关度: 2/5)
```

---

## 配置选项

### 全局配置

```yaml
# ~/.knowledge-index/config.yaml
registry:
  # 自动注册
  auto_register: true

  # 健康检查
  auto_health_check: true
  health_check_interval_days: 7

  # 层级管理
  auto_promote_hierarchy: true
  backup_before_promote: true

  # 备份
  max_backup_count: 5

  # 性能
  lazy_load: false
  cache_ttl_seconds: 300
```

---

## 备份与恢复

### 备份注册表

```python
def backup_registry():
    """备份注册表"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"~/.knowledge-index/backups/registry_{timestamp}.yaml"

    shutil.copy(registry_path, backup_path)

    # 保留最近 N 个备份
    clean_old_backups(max_count=5)
```

### 恢复注册表

```python
def restore_registry(backup_path):
    """从备份恢复注册表"""

    # 验证备份文件
    with open(backup_path, encoding='utf-8') as f:
        backup_data = yaml.safe_load(f)

    # 恢复
    shutil.copy(backup_path, registry_path)

    print(f"✓ 已从备份恢复注册表: {backup_path}")
```

---

## 错误处理

### 注册表损坏

```python
def repair_registry():
    """修复损坏的注册表"""

    try:
        # 尝试加载注册表
        registry = load_registry()
    except Exception as e:
        print(f"❌ 注册表损坏: {e}")

        # 从备份恢复
        latest_backup = find_latest_backup()
        if latest_backup:
            print(f"从备份恢复: {latest_backup}")
            restore_registry(latest_backup)
        else:
            print("无可用备份，重建注册表")
            rebuild_registry()
```

### 重建注册表

```python
def rebuild_registry():
    """重建注册表（扫描所有索引文件）"""

    print("开始重建注册表...")

    # 扫描所有索引文件
    index_files = find_all_index_files()

    # 重新注册
    registry = {"version": "1.0", "knowledge_bases": []}

    for index_file in index_files:
        kb_path = os.path.dirname(index_file)
        index_data = load_index(index_file)

        register_knowledge_base(kb_path, index_file, {
            "name": index_data["knowledge_base"]["name"],
            "document_count": index_data["knowledge_base"]["total_documents"],
            "total_size_mb": index_data["knowledge_base"]["total_size_mb"]
        })

    save_registry()
    print(f"✓ 注册表重建完成，共 {len(registry['knowledge_bases'])} 个知识库")
```

---

## 相关资源

- 层级管理规范：`references/advanced/hierarchy-management.md`
- 索引文件规范：`references/core/index-spec.md`
- 工作流程：`references/core/workflow-spec.md`
- 配置选项：`references/execution/config-options.md`

---

**版本**: 2.1
**最后更新**: 2026-03-04
**状态**: 规范已定义，待实现
