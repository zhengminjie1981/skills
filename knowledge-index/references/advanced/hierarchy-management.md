# 索引层级管理规范

## 核心概念

### 知识库定义

**一个知识库 = 一个文件夹 + 一个索引文件**

```
知识库/
├── _index.yaml          # 知识库索引
├── 文档1.md             # 知识库包含的文档
└── 子文件夹/
    └── 文档2.md         # 子文件夹的文档也属于该知识库
```

**关键原则**：
- ✅ 一个索引文件覆盖该文件夹及其所有子文件夹的所有文档
- ❌ 不应在子文件夹中创建独立的索引文件
- ✅ 子文件夹的文档通过父级索引统一管理

### 层级提升策略

**核心原则**：始终在最高级别维护索引，避免父子文件夹重复索引

**定义**：
- **知识库**：一个文件夹及其 `_index.yaml` 索引文件的组合
- **知识库范围**：该文件夹及其所有子文件夹的所有文档
- **层级冲突**：父文件夹和子文件夹同时有 `_index.yaml` 文件

**策略**：当检测到层级冲突时，自动提升至最高级别，删除所有下级索引

---

## 场景分析与处理逻辑

### 场景矩阵

| # | 当前文件夹 | 父文件夹 | 子文件夹 | 操作 | 注册表变更 |
|---|-----------|---------|---------|------|-----------|
| 1 | 无索引 | 无索引 | - | ✅ 在当前创建索引 | +当前 |
| 2 | 有索引 | 无索引 | - | ✅ 保持当前索引 | 无变化 |
| 3 | 无索引 | 有索引 | - | ⚠️ 提示用户，建议更新父索引 | 无变化 |
| 4 | 有索引 | 有索引 | - | 🔄 删除当前索引，更新父索引 | -当前 |
| 5 | 无索引 | 无索引 | 有索引 | ✅ 在当前创建索引，删除子索引 | +当前, -子 |
| 6 | 有索引 | 无索引 | 有索引 | 🔄 删除所有子索引，更新当前索引 | -子 |
| 7 | 无索引 | 有索引 | 有索引 | 🔄 删除当前和子索引，更新父索引 | -子 |
| 8 | 有索引 | 有索引 | 有索引 | 🔄 删除当前和子索引，更新父索引 | -当前, -子 |

---

## 详细场景处理

### 场景 1：当前无索引，父无索引（标准创建）

```
知识库/
├── 文档1.md
└── 文档2.md
```

**用户请求**：为「知识库」建立索引

**处理流程**：
```
1. 检查父文件夹 → 无索引
2. 检查当前文件夹 → 无索引
3. 检查子文件夹 → 无子文件夹/无索引
4. 在当前文件夹创建索引
5. 注册到全局注册表
```

**输出**：
```
✓ 索引创建完成
  - 知识库: 知识库
  - 文档数量: 2
  - 索引文件: 知识库/_index.yaml
  - 已注册到全局目录
```

**注册表**：
```yaml
knowledge_bases:
  - name: "知识库"
    path: "E:/知识库"
    index_path: "E:/知识库/_index.yaml"
    document_count: 2
```

---

### 场景 2：当前有索引，父无索引（正常更新）

```
知识库/
├── _index.yaml      # 已存在
├── 文档1.md
└── 文档2.md
```

**用户请求**：为「知识库」建立索引

**处理流程**：
```
1. 检查父文件夹 → 无索引
2. 检查当前文件夹 → 有索引
3. 询问用户：重建 or 更新
4. 执行相应操作
5. 更新全局注册表
```

**输出**：
```
⚠️ 检测到已有索引文件（最后更新: 2 天前）
选择操作：
  1. 重建索引（删除旧索引，重新构建）
  2. 更新索引（增量更新，仅处理变更）

请选择: 2

✓ 索引更新完成
  - 新增: 0 个
  - 修改: 1 个
  - 删除: 0 个
```

---

### 场景 3：当前无索引，父有索引（建议更新父索引）

```
父知识库/
├── _index.yaml          # 父索引存在
├── 文档0.md
└── 子主题/
    └── 文档1.md         # 当前文件夹
```

**用户请求**：为「子主题」建立索引

**处理流程**：
```
1. 检查父文件夹 → 有索引
2. 检查当前文件夹 → 无索引
3. 提示用户：父索引已包含此文件夹
4. 建议更新父索引
```

**输出**：
```
⚠️ 检测到父文件夹已有索引
  - 父索引: E:/父知识库/_index.yaml
  - 已包含当前文件夹: 子主题/

建议操作：
  1. 更新父索引（推荐）
     → 更新「父知识库」的索引以包含最新变更

  2. 强制在当前文件夹创建独立索引（不推荐）
     → 将导致重复索引，父索引和当前索引都会包含「子主题/文档1.md」

请选择 (1/2): 1

✓ 已更新父索引
  - 知识库: 父知识库
  - 新增: 0 个
  - 修改: 1 个
```

**如果用户选择强制创建**：
```
⚠️ 警告：将在子级别创建独立索引
  这将导致文档重复索引，不推荐此操作

是否继续？(y/N): y

✓ 已在「子主题」创建索引
  ⚠️ 注意：文档可能同时存在于父索引和当前索引中

建议：在父索引的 _index_config.yaml 中排除「子主题/」
```

---

### 场景 4：当前有索引，父有索引（层级提升）

```
父知识库/
├── _index.yaml          # 父索引
├── 文档0.md
└── 子主题/
    ├── _index.yaml      # 当前索引（将被删除）
    └── 文档1.md
```

**用户请求**：为「子主题」建立索引

**处理流程**：
```
1. 检查父文件夹 → 有索引
2. 检查当前文件夹 → 有索引
3. 检测到层级冲突
4. 自动执行层级提升：
   - 删除当前索引
   - 更新父索引
   - 从注册表移除当前索引
```

**输出**：
```
⚠️ 检测到父子索引冲突
  - 父索引: E:/父知识库/_index.yaml
  - 当前索引: E:/父知识库/子主题/_index.yaml

执行层级提升：
  [1/3] 备份当前索引...
  [2/3] 删除当前索引: 子主题/_index.yaml
  [3/3] 更新父索引以包含所有文档...

✓ 层级提升完成
  - 已删除: 子主题/_index.yaml
  - 已更新: 父知识库/_index.yaml
  - 文档总数: 2 个（父知识库）

建议：从 .gitignore 中移除「子主题/_index.yaml」（如适用）
```

---

### 场景 5：当前无索引，父无索引，子有索引（层级提升）

```
知识库/
├── 文档0.md
├── 子主题A/
│   ├── _index.yaml      # 子索引（将被删除）
│   └── 文档1.md
└── 子主题B/
    ├── _index.yaml      # 子索引（将被删除）
    └── 文档2.md
```

**用户请求**：为「知识库」建立索引

**处理流程**：
```
1. 检查父文件夹 → 无索引
2. 检查当前文件夹 → 无索引
3. 检查子文件夹 → 发现 2 个子索引
4. 自动执行层级提升：
   - 创建父索引（包含所有文档）
   - 删除所有子索引
   - 更新注册表
```

**输出**：
```
⚠️ 检测到子文件夹已有索引
  - 子主题A/_index.yaml
  - 子主题B/_index.yaml

执行层级提升：
  [1/4] 扫描所有文档...
  [2/4] 创建父索引...
  [3/4] 删除子索引...
    - 删除: 子主题A/_index.yaml
    - 删除: 子主题B/_index.yaml
  [4/4] 更新注册表...

✓ 层级提升完成
  - 已创建: 知识库/_index.yaml
  - 已删除: 2 个子索引
  - 文档总数: 3 个
  - 已注册到全局目录

层级结构已优化为单一索引
```

---

### 场景 6：当前有索引，父无索引，子有索引（合并子索引）

```
知识库/
├── _index.yaml          # 当前索引
├── 文档0.md
└── 子主题/
    ├── _index.yaml      # 子索引（将被删除）
    └── 文档1.md
```

**用户请求**：为「知识库」建立索引

**处理流程**：
```
1. 检查父文件夹 → 无索引
2. 检查当前文件夹 → 有索引
3. 检查子文件夹 → 发现子索引
4. 询问用户：更新并合并 or 重建
5. 删除子索引，更新当前索引
```

**输出**：
```
⚠️ 检测到子文件夹有索引
  - 子主题/_index.yaml

选择操作：
  1. 更新并合并（推荐）
     → 删除子索引，更新当前索引包含所有文档
  2. 重建索引
     → 删除所有索引，重新构建

请选择: 1

执行索引合并：
  [1/3] 删除子索引: 子主题/_index.yaml
  [2/3] 扫描所有文档...
  [3/3] 更新当前索引...

✓ 索引合并完成
  - 已删除: 1 个子索引
  - 更新: 知识库/_index.yaml
  - 文档总数: 2 个
```

---

### 场景 7：当前无索引，父有索引，子有索引（层级提升）

```
父知识库/
├── _index.yaml          # 父索引
├── 文档0.md
└── 子主题A/
    ├── _index.yaml      # 子索引（将被删除）
    └── 子主题B/
        └── 文档1.md     # 当前文件夹（无索引）
```

**用户请求**：为「子主题B」建立索引

**处理流程**：
```
1. 检查父文件夹 → 有索引（子主题A）
2. 检查当前文件夹 → 无索引
3. 检查子文件夹 → 无子文件夹
4. 检测到中间层索引（子主题A）
5. 提升至最高级别（父知识库）
6. 删除子主题A索引，更新父知识库索引
```

**输出**：
```
⚠️ 检测到多层级索引
  - 父索引: 父知识库/_index.yaml
  - 中间索引: 子主题A/_index.yaml

执行层级提升至最高级别：
  [1/3] 删除中间索引: 子主题A/_index.yaml
  [2/3] 更新父索引...
  [3/3] 更新注册表...

✓ 层级提升完成
  - 已删除: 子主题A/_index.yaml
  - 已更新: 父知识库/_index.yaml
  - 当前文件夹已包含在父索引中

建议：直接更新「父知识库」的索引
```

---

### 场景 8：当前有索引，父有索引，子有索引（完全提升）

```
父知识库/
├── _index.yaml          # 父索引
├── 文档0.md
└── 子主题A/
    ├── _index.yaml      # 当前索引（将被删除）
    ├── 文档1.md
    └── 子主题B/
        ├── _index.yaml  # 子索引（将被删除）
        └── 文档2.md
```

**用户请求**：为「子主题A」建立索引

**处理流程**：
```
1. 检查父文件夹 → 有索引
2. 检查当前文件夹 → 有索引
3. 检查子文件夹 → 有索引
4. 检测到多层级冲突
5. 提升至最高级别：
   - 删除当前和子索引
   - 更新父索引
   - 更新注册表
```

**输出**：
```
⚠️ 检测到多层级索引冲突
  - 父索引: 父知识库/_index.yaml
  - 当前索引: 子主题A/_index.yaml
  - 子索引: 子主题A/子主题B/_index.yaml

执行完全层级提升：
  [1/4] 备份索引...
  [2/4] 删除下级索引...
    - 删除: 子主题A/_index.yaml
    - 删除: 子主题A/子主题B/_index.yaml
  [3/4] 更新父索引...
  [4/4] 更新注册表...

✓ 完全层级提升完成
  - 已删除: 2 个下级索引
  - 已更新: 父知识库/_index.yaml
  - 文档总数: 3 个

索引层级已优化为单一顶级索引
```

---

## 层级提升算法

### 伪代码

```python
def build_index(target_path):
    """构建索引，自动处理层级提升"""

    # Step 1: 检测索引层级
    parent_index = find_parent_index(target_path)
    current_index = has_index(target_path)
    child_indexes = find_child_indexes(target_path)

    # Step 2: 决策树
    if parent_index:
        # 场景 3, 4, 7, 8: 父文件夹有索引
        if current_index:
            # 场景 4, 8: 当前也有索引 → 层级提升
            return promote_to_parent(target_path, parent_index)
        else:
            # 场景 3, 7: 当前无索引 → 建议更新父索引
            return suggest_update_parent(parent_index)
    else:
        # 场景 1, 2, 5, 6: 父文件夹无索引
        if child_indexes:
            # 场景 5, 6: 子文件夹有索引 → 删除子索引，提升至当前
            return promote_to_current(target_path, child_indexes)
        else:
            # 场景 1, 2: 正常创建或更新
            if current_index:
                return update_index(target_path)  # 场景 2
            else:
                return create_index(target_path)  # 场景 1


def promote_to_parent(current_path, parent_index_path):
    """提升至父级别索引"""
    print(f"检测到父索引: {parent_index_path}")
    print("执行层级提升...")

    # 1. 删除当前索引
    if has_index(current_path):
        delete_index(current_path)

    # 2. 删除所有子索引
    child_indexes = find_child_indexes(current_path)
    for child_index in child_indexes:
        delete_index(child_index)

    # 3. 更新父索引
    update_index(get_parent_path(current_path))

    # 4. 更新注册表
    unregister_from_registry(current_path)
    for child_index in child_indexes:
        unregister_from_registry(child_index)

    print("✓ 层级提升完成")


def promote_to_current(current_path, child_indexes):
    """提升至当前级别，删除子索引"""
    print(f"检测到 {len(child_indexes)} 个子索引")
    print("执行层级提升...")

    # 1. 创建或更新当前索引（包含所有文档）
    if has_index(current_path):
        update_index(current_path)
    else:
        create_index(current_path)

    # 2. 删除所有子索引
    for child_index in child_indexes:
        delete_index(child_index)
        unregister_from_registry(child_index)

    # 3. 注册到全局注册表
    register_to_registry(current_path)

    print("✓ 层级提升完成")


def suggest_update_parent(parent_index_path):
    """建议用户更新父索引"""
    print(f"⚠️ 检测到父文件夹已有索引: {parent_index_path}")
    print("建议更新父索引以包含最新变更")

    choice = input("选择操作: (1) 更新父索引 [推荐]  (2) 强制创建子索引 [不推荐]: ")

    if choice == "1":
        update_index(get_parent_path(parent_index_path))
    else:
        print("⚠️ 警告: 将创建子级别索引，可能导致重复")
        create_index(current_path)
```

---

## 全局注册表更新规则

### 注册表结构

```yaml
# ~/.knowledge-index/registry.yaml
version: "1.0"
last_updated: "2026-03-03T16:00:00Z"
knowledge_bases:
  - name: "知识库名称"
    path: "E:/知识库"                    # 绝对路径
    index_path: "E:/知识库/_index.yaml"  # 索引文件路径
    last_updated: "2026-03-03T15:30:00Z"
    document_count: 15
    total_size_mb: 2.5
    parent: null                         # 父知识库路径（如果有）
```

### 更新规则

| 操作 | 注册表变更 |
|------|-----------|
| 创建索引（场景1） | `+ 当前知识库` |
| 更新索引（场景2） | `更新当前知识库信息` |
| 建议更新父索引（场景3） | `无变化` |
| 层级提升-删除当前（场景4） | `- 当前知识库` |
| 层级提升-创建父索引（场景5） | `+ 当前知识库, - 所有子知识库` |
| 合并子索引（场景6） | `- 所有子知识库` |
| 多层级提升（场景7, 8） | `- 当前知识库, - 所有子知识库` |

---

## AI Agent 决策流程

```
用户请求建立索引
    │
    ├─ 扫描父文件夹
    │   ├─ 无索引 → 继续
    │   └─ 有索引 → 标记 parent_index
    │
    ├─ 扫描当前文件夹
    │   ├─ 无索引 → 继续
    │   └─ 有索引 → 标记 current_index
    │
    ├─ 扫描子文件夹
    │   ├─ 无索引 → 继续
    │   └─ 有索引 → 标记 child_indexes[]
    │
    ├─ 决策
    │   ├─ parent_index = true
    │   │   ├─ current_index = true → 场景4,8: 层级提升
    │   │   └─ current_index = false → 场景3,7: 建议更新父索引
    │   │
    │   └─ parent_index = false
    │       ├─ child_indexes.length > 0
    │       │   ├─ current_index = true → 场景6: 合并子索引
    │       │   └─ current_index = false → 场景5: 层级提升
    │       │
    │       └─ child_indexes.length = 0
    │           ├─ current_index = true → 场景2: 更新索引
    │           └─ current_index = false → 场景1: 创建索引
    │
    └─ 执行操作
        ├─ 创建/更新索引
        ├─ 删除下级索引
        └─ 更新注册表
```

---

## 输出消息模板

### 层级提升提示

```
⚠️ 检测到索引层级冲突

现有索引：
  - 父索引: {parent_path}/_index.yaml
  - 当前索引: {current_path}/_index.yaml
  - 子索引: {child_count} 个

执行层级提升策略：
  → 保留最高级别索引（父索引）
  → 删除下级索引（当前和子索引）
  → 所有文档合并至父索引

是否继续？(Y/n)
```

### 完成确认

```
✓ 层级提升完成

已删除索引：
  - {deleted_index_1}
  - {deleted_index_2}

已更新索引：
  - {parent_index}
  - 文档总数: {total_count} 个

注册表已更新：
  - 已移除: {removed_count} 个条目
  - 当前注册知识库: {total_knowledge_bases} 个

建议：
  - 更新 .gitignore（如适用）
  - 提交变更到版本控制
```

---

## 配置选项

### 允许用户配置层级提升行为

```yaml
# ~/.knowledge-index/config.yaml
hierarchy:
  # 层级提升策略
  promotion_strategy: "auto"  # auto, manual, disabled

  # auto: 自动执行层级提升（推荐）
  # manual: 检测到冲突时询问用户
  # disabled: 允许多层级索引（不推荐）

  # 是否在创建索引前检测父索引
  check_parent: true

  # 是否自动删除子索引
  auto_delete_child: true

  # 是否在删除前备份索引
  backup_before_delete: true
```

---

## 相关资源

- 全局注册表规范：`references/advanced/global-registry-spec.md`
- 索引文件规范：`references/core/index-spec.md`
- 工作流程：`references/core/workflow-spec.md`
- 决策树：`references/decision/decision-tree.md`

---

**版本**: 2.1
**最后更新**: 2026-03-11
**状态**: 已实现
