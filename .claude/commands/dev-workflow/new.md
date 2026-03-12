---
description: "启动新模块开发（文档优先）"
argument-hint: "<模块名>"
allowed-tools: [Read, Glob, Grep, Write, Bash(git:*)]
---

# 启动新模块开发

按照文档驱动开发工作流，启动一个新模块的开发流程。

## 工作流

1. **需求明确** - 询问用户明确功能边界、输入输出数据结构
2. **系统架构更新** - 如需，更新系统架构设计，明确模块边界和数据流
3. **数据结构更新** - 如需，更新数据结构规范，检查接口规范
4. **编写模块技术文档** - 模块定位、输入输出规范、核心算法、接口设计、验证方案
5. **接口规范更新** - 如需，更新接口规范，检查引用一致性
6. **文档一致性检查** - 检查系统架构、数据结构、接口、相关模块文档的一致性（编码前检查点）
7. **代码实现与测试** - 严格按文档定义实现，执行验证、补充实测结果、更新项目计划与进展记录

## 质量门禁

编码前检查点：
- [ ] 系统架构设计已完成（如需）
- [ ] 数据结构规范已更新（如需）
- [ ] 接口规范已更新（如需）
- [ ] 模块设计文档已完成
- [ ] 文档一致性检查通过（≥ 95%）

## 参考资源

如需详细规范，按需读取：
- `~/.claude/skills/dev-workflow/references/full-spec.md` - 完整规范
- `~/.claude/skills/dev-workflow/references/templates.md` - 文档模板
- `~/.claude/skills/dev-workflow/references/checklist.md` - 检查清单
- `~/.claude/skills/dev-workflow/references/quality-gates.md` - 质量门禁
