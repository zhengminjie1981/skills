---
name: dev-workflow
description: 文档驱动开发工作流规范。当且仅当涉及以下场景时触发：
  1) 创建新模块或功能（关键词：新建模块、添加功能、实现新特性、开发新组件、创建新的）
  2) 修改现有代码、数据结构或接口（关键词：修改、重构、变更、更新接口、改字段、修改数据结构）
  3) 需要编写或更新技术文档（关键词：写文档、更新设计、编写规范、补充文档）
  4) 文档一致性检查（关键词：检查一致性、验证文档）
  5) 涉及模块设计、数据结构规范、接口规范（关键词：模块设计、数据结构、接口定义）

  不触发场景：
  - 纯粹的代码阅读、问题排查（关键词：查看、阅读、分析、排查）
  - 简单的配置修改（如修改 README、.gitignore、配置文件）
  - 快速原型验证（用户明确说明是 poc/demo/spike/原型）
  - 简单的查询和解释（关键词：解释、说明、什么是）

allowed-tools: [Read, Glob, Grep, Write, Bash]
argument-hint: "<new|change|check> [模块名]"

feedback:
  enabled: true
  version: "1.5.0"
  author: "skills-team"
---

# 开发工作流规范

> **适用范围**：所有软件开发项目
> **强制约束**：所有代码实现必须有对应文档先行，不允许无文档直接编码

## 核心原则（黄金规则）

| 编号 | 原则 | 核心要求 |
|------|------|----------|
| **P-01** | **文档优先** | 任何模块或功能的实现，必须先完成技术文档，再编写代码 |
| **P-02** | **变更留档** | 任何迭代修改，必须先更新相关文档并完成影响分析，再修改代码 |
| **P-03** | **模块化边界** | 模块间通过数据结构规范和接口规范进行交互，禁止跨模块直接访问内部实现 |
| **P-04** | **一致性维护** | 文档更新后，须同步检查并更新所有引用该内容的文档 |
| **P-05** | **集中进展记录** | 所有工作计划与进展统一记录在项目计划与进展记录中，不得分散在各模块文档中 |
| **P-06** | **文档定位清晰** | 每份文档须明确自身层级、回答的问题及上下游关联 |
| **P-07** | **文档集中管理** | 所有正式文档须集中存放在统一的文档目录下，目录名称可由项目决定 |
| **P-08** | **临时文件隔离** | 临时文档、脚本和数据须放在专门的临时目录下，定期清理 |
| **P-09** | **版本可追溯** | 所有文档必须包含版本历史章节，记录变更内容、日期和影响范围 |

## 文档层级体系

| 层级 | 目录示例 | 回答的问题 | 典型特征 |
|------|---------|-----------|---------|
| **L1 系统级** | `系统设计/` | 系统做什么、整体技术路线、模块边界怎么划分 | 架构师视角；结论驱动下级文档 |
| **L2 规范级** | `技术规范/` | 跨模块数据结构与接口的权威定义 | 单一事实来源；引用而非复制 |
| **L3 模块级** | `模块设计/` | 某个模块如何实现 | 聚焦单一模块职责边界 |
| **L4 验证级** | `测试验证/` | 技术方案的验证方法、测试策略与性能评估 | 回答"如何验证" |
| **L5 报告级** | `报告/` | 某次实验或阶段工作的结果记录 | 事后产物；只读 |

**权威性层级**：系统架构设计 > 数据结构规范 / 接口规范 > 模块设计文档 > 验证方案/报告

## 强制要求

**必须存在的目录和文件**：
- ✅ **文档根目录**：名称可自定义（如 `doc/`、`docs/`），所有正式文档必须在此目录下
- ✅ **临时目录**：名称可自定义（如 `temp/`、`tmp/`），并在 `.gitignore` 中排除
- ✅ **文档导航入口**：位于文档根目录下，如 `doc/README.md`
- ✅ **项目进展记录**：位于文档根目录下，记录唯一的进展跟踪

**详细目录结构示例**：见 [full-spec.md](references/full-spec.md)

## 子功能调用

| 指令 | 说明 |
|------|------|
| `/dev-workflow new <模块名>` | 启动新模块开发（文档优先，7步流程） |
| `/dev-workflow change <模块名> [变更描述]` | 修改现有模块（含影响分析，7步流程） |
| `/dev-workflow check [模块名]` | 验证文档一致性，输出检查报告 |

## 快速参考

### 新模块开发流程（7步）

```
1. 需求明确 → 明确功能边界、输入输出数据结构
2. 系统架构更新（如需）→ 更新系统架构设计，明确模块边界和数据流
3. 数据结构更新（如需）→ 更新数据结构规范，检查接口规范
4. 编写模块技术文档 → 模块定位、输入输出规范、核心算法、接口设计、验证方案
5. 接口规范更新（如需）→ 更新接口规范，检查引用一致性
6. 文档一致性检查 → 检查系统架构、数据结构、接口、相关模块文档的一致性（编码前检查点）
7. 代码实现与测试 → 严格按文档定义实现，执行验证、补充实测结果、更新项目计划与进展记录
```

**详细流程和示例**：见 [full-spec.md](references/full-spec.md)

### 迭代变更流程（7步）

```
1. 变更发起 → 明确变更内容、原因、范围
2. 影响分析 → 列出所有受影响的文档和代码文件
3. 更新源头文档 → 优先更新系统架构设计，然后是数据结构规范或接口规范
4. 更新关联文档 → 按影响分析逐一更新受影响文档
5. 文档一致性检查 → 执行检查清单，一致性评分 ≥ 95%（编码前检查点）
6. 代码修改 → 按更新后的文档修改代码，同步更新测试文件
7. 验证与收尾 → 运行测试、更新项目计划与进展记录、更新README
```

**详细流程和影响分析**：见 [full-spec.md](references/full-spec.md)

## 质量门禁

**编码前检查点**：
- [ ] 系统架构设计已完成（如需）
- [ ] 数据结构规范已更新（如需）
- [ ] 接口规范已更新（如需）
- [ ] 模块设计文档已完成
- [ ] 文档一致性检查通过（≥ 95%）

**代码提交检查点**：
- [ ] 代码与文档一致
- [ ] 单元测试通过
- [ ] 测试用例与文档定义一致

**详细质量门禁规范**：见 [quality-gates.md](references/quality-gates.md)

## 禁止行为清单

- ❌ 直接编写代码而未创建或更新对应技术文档
- ❌ 修改数据结构字段而未同步更新数据结构规范
- ❌ 修改接口签名而未同步更新接口规范
- ❌ 在模块间使用裸字典/元组代替规范数据结构传递数据
- ❌ 跳过影响分析直接修改代码
- ❌ 文档与代码不一致超过24小时
- ❌ 将临时文件混入正式文档或代码目录
- ❌ 文档缺少版本历史或版本历史不完整

**完整禁止清单和反模式**：见 [full-spec.md](references/full-spec.md)

## 参考资源

### 核心文档
- **完整规范**：[full-spec.md](references/full-spec.md) - 详细示例、反模式、流程图、AI 执行流程
- **检查清单**：[checklist.md](references/checklist.md) - 新模块开发、迭代变更检查清单
- **质量门禁**：[quality-gates.md](references/quality-gates.md) - 各阶段质量标准

### 决策与参考
- **场景决策树**：[decision-tree.md](references/decision-tree.md) - 常见场景的决策流程
- **快速参考**：[quick-reference.md](references/quick-reference.md) - 速查表和决策流程图
- **反模式案例**：[anti-patterns.md](references/anti-patterns.md) - 反面教材与正确做法对比
- **示例对话**：[conversation-examples.md](references/conversation-examples.md) - AI 与用户的交互示例

### 工具和模板
- **文档模板**：[templates.md](references/templates.md) - 模块设计、系统架构、数据结构等模板
- **结构化模板**：[templates/schemas/](references/templates/schemas/) - JSON Schema 格式的模板定义
- **运维指南**：[operational-guide.md](references/operational-guide.md) - 临时文件管理、归档、导航维护
- **自动化工具**：[tools.md](references/tools.md) - 文档维护脚本和工具

### AI 辅助
- **AI 快速检查**：[ai-checklist.md](references/ai-checklist.md) - AI 执行前的快速检查点
- **Git 工作流**：[git-integration.md](references/git-integration.md) - 与 Git 提交的集成
- **文档生成辅助**：[doc-generation-guide.md](references/doc-generation-guide.md) - 从代码/需求生成文档

### 快速开始

**创建新模块**：
1. 参考 [templates.md](references/templates.md) 选择对应模板
2. 按照 [checklist.md](references/checklist.md) 执行检查清单
3. 通过 [quality-gates.md](references/quality-gates.md) 的质量门禁

**修改现有代码**：
1. 按照 [full-spec.md](references/full-spec.md) 的迭代变更流程执行
2. 执行影响分析和一致性检查
3. 更新版本历史

**维护文档**：
1. 参考 [operational-guide.md](references/operational-guide.md)
2. 定期清理临时文件和归档文档
3. 使用 [tools.md](references/tools.md) 中的自动化脚本

---

**文档版本**：v1.5
**最后更新**：2026-03-03

---

## 反馈机制

本 skill 支持自动反馈改进。

<!-- FEEDBACK-TRIGGER-START -->
<feedback-config>
{
  "triggers": ["execution_failure", "document_conflict", "validation_error"],
  "collect": ["error_type", "workflow_phase", "environment", "skill_version"],
  "sanitize": ["file_paths", "code_content", "user_data"]
}
</feedback-config>
<!-- FEEDBACK-TRIGGER-END -->

执行完成后，如检测到改进机会且用户已授权，将自动发送脱敏反馈。
