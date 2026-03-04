# Knowledge Index - 开发文档

> **版本**: 2.1
> **最后更新**: 2026-03-04

## 文档索引

### 设计规范

| 文档 | 说明 |
|------|------|
| [DESIGN-SUMMARY.md](./DESIGN-SUMMARY.md) | **设计总结** - 全局注册表和层级管理的完整设计 |
| [global-registry-spec.md](./global-registry-spec.md) | **全局注册表规范** - 注册表结构、操作、配置 |
| [hierarchy-management.md](./hierarchy-management.md) | **层级管理规范** - 8 种场景的详细处理逻辑 |

### 实现指南

| 文档 | 说明 |
|------|------|
| [hierarchy-implementation.md](./hierarchy-implementation.md) | **实现指南** - 完整的伪代码和使用示例 |

---

## 快速开始

### 核心概念

**一个知识库 = 一个文件夹 + 一个索引文件**

```python
知识库/
├── _index.yaml          # 索引文件（覆盖所有子文件夹）
├── 文档1.md
└── 子文件夹/
    └── 文档2.md         # 也属于该知识库
```

### 全局注册表

**位置**: `~/.knowledge-index/registry.yaml`

维护所有知识库的元信息，支持：
- 快速发现所有知识库
- 跨知识库检索
- 层级冲突检测

### 层级提升策略

**核心原则**: 始终在最高级别维护索引

**自动提升**: 检测到父子索引冲突时，自动删除下级索引

---

## 实现优先级

### Phase 1: 核心功能（必需）

- [ ] 实现 `KnowledgeBaseManager` 类
- [ ] 实现层级检测算法
- [ ] 实现层级提升算法
- [ ] 实现全局注册表管理

### Phase 2: 增强功能（推荐）

- [ ] 跨知识库检索
- [ ] 知识库健康检查
- [ ] 注册表备份与恢复

---

## 关键算法

### 决策树

```python
def build_index(kb_path):
    parent_index = find_parent_index(kb_path)
    current_index = has_index(kb_path)
    child_indexes = find_child_indexes(kb_path)

    if parent_index:
        if current_index:
            # 场景 4, 8: 层级提升至父
            promote_to_parent(kb_path, parent_index)
        else:
            # 场景 3, 7: 建议更新父索引
            suggest_update_parent(kb_path, parent_index)
    else:
        if child_indexes:
            # 场景 5, 6: 层级提升至当前
            promote_to_current(kb_path, child_indexes)
        else:
            # 场景 1, 2: 正常创建或更新
            if current_index:
                update_index(kb_path)
            else:
                create_index(kb_path)
```

---

## 测试计划

### 单元测试

- [ ] 8 种场景的完整测试用例
- [ ] 层级检测算法测试
- [ ] 层级提升算法测试
- [ ] 注册表操作测试

### 集成测试

- [ ] 端到端索引创建流程
- [ ] 跨知识库检索功能
- [ ] 健康检查功能

---

## 相关资源

### 用户文档

- [SKILL.md](../SKILL.md) - 用户使用指南
- [references/](../references/) - 详细参考文档

### 开发文档

- [DESIGN-SUMMARY.md](./DESIGN-SUMMARY.md) - 设计总结
- [global-registry-spec.md](./global-registry-spec.md) - 注册表规范
- [hierarchy-management.md](./hierarchy-management.md) - 层级管理规范
- [hierarchy-implementation.md](./hierarchy-implementation.md) - 实现指南

---

**维护者**: AI Agent
**状态**: 开发中
