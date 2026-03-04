# Knowledge Index - 开发文档

> **版本**: 2.1
> **最后更新**: 2026-03-04

## 文档索引

| 文档 | 说明 |
|------|------|
| [UPDATE-NOTES.md](./UPDATE-NOTES.md) | **更新说明** - 版本变更记录和迁移指南 |
| [DESIGN-SUMMARY.md](./DESIGN-SUMMARY.md) | **设计总结** - 全局注册表和层级管理的完整设计 |

## 目录结构

```
knowledge-index/
├── SKILL.md              # 入口文件（AI 友好，按需加载）
├── docs/                 # 开发文档（设计、更新记录）
│   ├── README.md
│   ├── UPDATE-NOTES.md   # 版本更新说明
│   └── DESIGN-SUMMARY.md # 设计总结
├── references/           # AI 参考文档（按需加载）
│   ├── core/             # 核心规范
│   ├── execution/        # 执行支持
│   ├── decision/         # 决策支持
│   └── advanced/         # 高级主题
├── scripts/              # 工具脚本
└── tests/                # 测试用例
```

## 详细规范位置

详细的设计规范和实现指南已移至 `references/advanced/` 目录：

| 规范 | 位置 |
|------|------|
| 全局注册表规范 | [references/advanced/global-registry-spec.md](../references/advanced/global-registry-spec.md) |
| 层级管理规范 | [references/advanced/hierarchy-management.md](../references/advanced/hierarchy-management.md) |
| 实现指南 | [references/advanced/hierarchy-implementation.md](../references/advanced/hierarchy-implementation.md) |

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

**维护者**: AI Agent
**状态**: 开发中
