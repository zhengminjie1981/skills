---
description: "修改现有模块（含影响分析）"
argument-hint: "<模块名> [变更描述]"
allowed-tools: [Read, Glob, Grep, Write, Bash(git:*)]
---

# 修改现有模块

按照文档驱动开发工作流，执行迭代变更流程。

## 工作流

1. **变更发起** - 明确变更内容、原因、范围
2. **影响分析** - 列出所有受影响的文档和代码文件
3. **更新源头文档** - 优先更新系统架构设计，然后是数据结构规范或接口规范
4. **更新关联文档** - 按影响分析逐一更新受影响文档
5. **文档一致性检查** - 执行检查清单，一致性评分 ≥ 95%（编码前检查点）
6. **代码修改** - 按更新后的文档修改代码，同步更新测试文件
7. **验证与收尾** - 运行测试、更新项目计划与进展记录、更新 README

## 质量门禁

编码前检查点：
- [ ] 影响分析已完成
- [ ] 源头文档已更新
- [ ] 关联文档已同步
- [ ] 文档一致性检查通过（≥ 95%）

## 参考资源

如需详细规范，按需读取：
- `~/.claude/skills/dev-workflow/references/full-spec.md` - 完整规范（含迭代变更流程）
- `~/.claude/skills/dev-workflow/references/checklist.md` - 检查清单
- `~/.claude/skills/dev-workflow/references/decision-tree.md` - 场景决策树
