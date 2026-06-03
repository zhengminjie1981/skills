---
name: task-stack
description: |-
  任务堆栈管理 - 跟踪主线任务和分支任务，跨会话持久化，支持待办、临时插入任务和自动整理。

  **触发场景**（包含以下关键词）：
  - 任务管理：创建任务、任务列表、查看任务、任务堆栈、我的任务、待办
  - 任务操作：完成任务、挂起任务、继续任务、回到主线、任务完成
  - 任务分支：分支任务、子任务、先处理、暂时搁置、主线任务、临时插入
  - 任务初始化：初始化任务、分析项目、项目任务
  - 任务整理：整理任务、合并任务、任务优先级、重新组织
  - 任务迁移：迁移任务栈、升级任务栈、v1 转 v2.1

  **不触发场景**：
  - 简单的单步操作
  - 纯代码编写（无任务上下文）
  - 信息查询类问题

argument-hint: "<init|push|add|done|list|suspend|resume|promote|organize|archive|migrate> [描述]"

feedback:
  enabled: true
  version: "1.0.0"
  author: "skills-team"
---

# Task Stack - 任务堆栈管理

> 栈式任务管理：记录轻量待办，跟踪执行流任务，临时插入任务前自动保存恢复上下文，跨会话持久化。

## 栈数据

任务数据存储在项目根目录 `.tasks/` 下（已 gitignored，个人数据不进仓库）：

```text
.tasks/
├── stack.json              # 执行流索引：active、stack、next_id
├── backlog.jsonl           # 轻量待办：一行一个尚未开始的任务
├── tasks/
│   ├── T001.json           # active / suspended / blocked 任务详情
│   └── T003.json
└── archive.json            # 已完成任务归档摘要
```

详细格式见 [stack-schema.md](references/stack-schema.md)。

**快速理解**：
- `.tasks/stack.json` 只保存执行流任务 id 顺序和入口索引，不保存 backlog
- `stack` 数组有序，index 0 是栈顶，`active` 指向当前活跃任务 id
- `.tasks/backlog.jsonl` 一行一个轻量待办，适合追加和列表展示
- backlog 任务默认不创建 `.tasks/tasks/<id>.json`
- 任务进入执行流（active/suspended/blocked）或需要保存恢复上下文时，才创建任务详情 JSON
- 任务可选关联 `branch` 字段，resume 时提示切换分支

## 核心操作

| 操作 | 触发方式 | 行为 |
|------|---------|------|
| **init** | 初始化 / 分析项目 | 生成初始执行流任务和轻量 backlog |
| **add** / **later** | 追加后续任务 | 向 `backlog.jsonl` 追加一行或多行，不影响当前 active |
| **push** / **interrupt** | 新任务 / 分支任务 / 临时插入 | 先保存当前进展快照并 suspend，再将新任务放到栈顶 |
| **promote** | 待办升级 | 先保存并挂起当前任务，再把 backlog 行转为任务详情并移入栈顶 |
| **done** | 栈顶任务完成 | 归档当前任务，恢复其 parent 或下一个栈顶任务 |
| **suspend** | 用户要求搁置 | 创建/更新任务详情，记录原因、resume_hint 和进展快照 |
| **resume** | 用户说继续 / 选择恢复 | 标记 active，呈现 resume_hint、progress_snapshot 和 context |
| **list** | 查看任务 | 展示 stack + backlog，按层级缩进，标注状态 |
| **organize** | 整理任务 | 分析相关任务，建议合并和优先级调整 |
| **migrate** | 迁移任务栈 | 按提示词将 v1 大 JSON 转为 v2.1 混合结构 |
| **archive** | 清理归档 | 清理 `archive.json` 中的旧条目 |

## 操作细节

### add / later 记录后续任务

用于“先记下来，后面再做”的场景，不打断当前任务。

1. 从用户输入中拆出一个或多个后续任务
2. 为每个任务分配 id
3. 向 `.tasks/backlog.jsonl` 追加一行轻量记录：`id`、`title`、`priority`、`created`、可选 `source` / `tags`
4. 递增 `.tasks/stack.json.next_id`，更新 `updated`
5. 不创建任务详情 JSON，除非用户提供了大量必须保存的上下文
6. 不修改 `active`，不修改当前任务状态，不打断当前上下文

### push / interrupt 临时插入新任务

用于“先处理这个”“把当前任务延后”的场景。

1. 读取当前 `active` 任务并加载其任务文件
2. 如果当前任务尚无详情文件，但已有较多上下文，先创建 `.tasks/tasks/<id>.json`
3. 利用 Agent 当前上下文生成进展快照：已完成事项、关键判断、相关文件/命令/错误、下一步、打断原因
4. 更新被打断任务的 `resume_hint`、`context`、`progress_snapshot`、`suspend_reason`、`suspended_at`，并设为 `suspended`
5. 创建新任务详情文件，`status = "active"`，必要时 `parent` 指向被打断任务
6. 将新任务 id 插入 `stack[0]`，设置 `active` 为新任务 id
7. 递增 `next_id`，更新 `updated`
8. 简短告知用户：原任务已保存进度并挂起，新任务已开始

如果当前上下文不足以生成有效快照，只问最小必要澄清问题，不要求用户完整复述进展。

### promote 待办升级

1. 先按 `push` 规则保存并挂起当前 active 任务
2. 从 `.tasks/backlog.jsonl` 移除目标任务行
3. 用该行轻量信息创建 `.tasks/tasks/<id>.json`，补充 `status = "active"`、`resume_hint` 和 `progress_snapshot`
4. 插入 `stack[0]` 并设置 `active`

### done 完成任务

1. 将当前 active 任务从 `stack` 移除
2. 将完成摘要追加到 `.tasks/archive.json`
3. 可将任务文件标记为 `completed` 或按归档策略移动
4. 如果 parent 仍在 `stack` 中，恢复 parent 为 `active`
5. 否则设置 `active` 为新的 `stack[0]` 或 `null`
6. 只更新受影响的任务文件和轻量索引

### init 初始化

1. 分析项目信息来源：`git log`、`git status`、当前分支、CLAUDE.md / README.md、TODO/FIXME/HACK
2. 根据分析结果生成任务建议：进行中任务放入 `stack` 并创建详情，未开始任务写入 `backlog.jsonl`
3. 先展示给用户确认，再写入文件

### migrate 迁移

v1 `.tasks/stack.json` 是完整对象数组，v2.1 是 `stack.json` + `backlog.jsonl` + 执行流任务详情。迁移采用提示词驱动，不新增脚本。

1. 只有用户明确要求迁移，或执行需要写入 v2.1 的任务栈操作时才提示迁移
2. 迁移前保留原始 `.tasks/stack.json` 内容，必要时写入 `.tasks/stack.v1.backup.json`
3. 将 v1 `stack[]` 中的任务对象写入 `.tasks/tasks/<id>.json`
4. 将 v1 `backlog[]` 中的任务对象转换为 `.tasks/backlog.jsonl` 的轻量行
5. 新 `.tasks/stack.json` 只保留 `version`、`updated`、`next_id`、`active`、`stack`、`tasks_dir`、`backlog_file`
6. 不覆盖已存在任务文件；如冲突，先询问用户

## 主动行为规则

### 1. 分支任务或临时插入 → 先快照再 push

工作中发现需要分支任务，或用户要求先处理另一个任务时：

1. 先用 Agent 当前上下文总结当前任务进展和关键信息
2. 写入当前任务的 `resume_hint` 和 `progress_snapshot`
3. 挂起当前任务并 push 新任务到栈顶
4. 告知用户："已保存 [原任务] 的进度并挂起，现在开始 [新任务]。"

### 2. 后续任务 → add，不打断

用户说“后续还要做”“先记一下”“待办”时，默认执行 `add`：

1. 可一次记录多个任务
2. 只追加到 `backlog.jsonl`
3. 不改变 `active` 和 `stack`
4. 简短确认新增的待办数量和标题

### 3. 任务完成 → 自动 pop

栈顶任务完成时：

1. 归档完成任务
2. 恢复 parent 或下一个栈顶任务
3. 提醒用户："[完成的任务] 已完成。[恢复的任务] 可以继续了——上次做到 [resume_hint]。"

### 4. 话题切换 → 简短提醒

用户突然切换到不相关话题时，一句话提醒：

"当前有未完成的任务 [X]，要挂起还是稍后继续？"

不要阻止用户。用户选择继续新话题时，先保存当前任务快照，再挂起。

### 5. resume_hint 实时更新

工作过程中保持当前任务的 `resume_hint` 为最新状态。关键步骤后、切换文件时、用户暂停时、每次 git commit 后，都应更新当前任务文件。

### 6. 衰老和堆积提醒

- suspended 任务：`suspended_at` 超过 7 天 → 标记 stale
- backlog 任务：`created` 超过 14 天且 priority = low → 建议归档
- stack 深度 > 5 → 提醒建议整理
- backlog 数量 > 10 → 提醒建议整理或归档

## 会话生命周期

### 启动时

如果 `.tasks/stack.json` 存在且有任务：

1. 读取执行流索引
2. 加载 active 任务文件
3. 按需读取 suspended 任务详情和 `backlog.jsonl` 摘要
4. 简要提示当前活跃/挂起任务

```text
你有 2 个任务在栈中。
当前活跃：T003 修复 token 刷新逻辑
挂起的：T001 重构认证中间件
要继续活跃任务吗？
```

如果检测到 v1 完整对象格式，只提示可迁移，不在启动检查中自动迁移。

### 工作中

- 后续任务 → add 到 `backlog.jsonl`，不打断
- 临时插入 / 分支任务 → 先快照，再 push
- 完成任务 → pop 并恢复主线
- 保持 `resume_hint` 和 `progress_snapshot` 更新

### 结束前

确保所有 active/suspended 任务的 `resume_hint` 反映最新进度。

## 展示格式

```text
任务栈（2 个任务）

▸ T003 修复 token 刷新逻辑          [active] #bug #auth  branch: fix/token-refresh
  └─ T001 重构认证中间件            [suspended] 暂停原因: 发现 token bug

待办（3 项）

  T005 补充 API 文档               [medium] source: src/api/
  T006 重构日志模块                 [low] ⚠ 15天未处理
  T007 升级依赖到最新版本           [low]

⚠ 1 项待办超期未处理，建议整理或归档
```

- `▸` 标记当前 active 任务
- 缩进表示 parent-child 关系
- suspended 任务显示暂停原因
- 括号内为优先级：`high` / `medium` / `low`
- `source:` 显示轻量待办来源
- `branch:` 显示关联的 git 分支
- `⚠` 标记衰老任务

## 典型场景

### 场景 1：记录后续任务，不打断当前任务

```text
用户: 后续还要补 API 文档和优化缓存策略
AI:   [向 backlog.jsonl 追加 T005, T006]
      已记录 2 项后续任务：T005 补 API 文档、T006 优化缓存策略。当前任务 T001 不变。
```

### 场景 2：临时插入任务

```text
用户: 先停一下，马上修 token 刷新 bug
AI:   [保存 T001 progress_snapshot]
      [T001 → suspended, push T002 active]
      已保存 T001 的进度：middleware.ts 后半部分重构，下一步补 JWT 验证。现在开始 T002 修 token 刷新 bug。
```

### 场景 3：跨会话恢复

```text
AI:   你有 1 个任务在栈中。
      挂起的：T001 重构认证中间件
      上次做到：middleware.ts 的后半部分，需要添加 JWT 验证。

用户: 继续
AI:   [resume T001]
      继续。上次在 middleware.ts:80，接下来添加 JWT 验证逻辑。
```

## 边界情况

| 情况 | 处理 |
|------|------|
| 栈为空时用户说"完成任务" | 提示"当前没有活跃任务" |
| add 时已有 active 任务 | 只追加 `backlog.jsonl`，不改变 active |
| add 时上下文很长 | 可将长上下文写入任务详情，并在 backlog 行中记录 `details` |
| push 时已有 active 任务 | 先保存快照并挂起，再插入新任务 |
| push 时无 active 任务 | 直接创建新 active 任务 |
| promote 时目标不在 backlog | 提示可用 backlog 任务 |
| promote 的 backlog 行没有详情 | 根据轻量行创建任务详情 |
| 多个 suspended 任务 | list 全部展示，resume 默认恢复栈顶或用户指定任务 |
| v1 stack.json | 提示可执行 migrate，不在普通读取时自动迁移 |
| stack 引用的任务文件缺失 | 提示数据不一致，建议修复或迁移 |
| backlog.jsonl 行格式错误 | 跳过坏行并提示修复，不静默丢弃 |
| `.tasks/` 目录不存在 | 首次 push/init/add 时创建 |
| organize 时信息不足 | 读取必要任务详情；backlog 只按轻量字段初筛 |
| resume 时分支不存在 | 提示分支已删除，让用户决定是否在当前分支继续 |

## 参考资源

| 文档 | 内容 | 何时读取 |
|------|------|---------|
| [stack-schema.md](references/stack-schema.md) | v2.1 文件结构、字段、迁移提示词和校验清单 | 需要了解数据格式细节时 |

<!-- 开发文档放在 docs/ 目录，不会被 AI 加载 -->

---

## 反馈机制

本 skill 支持自动反馈改进。

<!-- FEEDBACK-TRIGGER-START -->
<feedback-config>
{
  "triggers": ["execution_failure", "data_corruption"],
  "collect": ["error_type", "environment", "skill_version"],
  "sanitize": ["file_paths", "user_data"]
}
</feedback-config>
<!-- FEEDBACK-TRIGGER-END -->

执行完成后，如检测到改进机会且用户已授权，将自动发送脱敏反馈。

---

**版本**: 2.1 | **最后更新**: 2026-05-31
