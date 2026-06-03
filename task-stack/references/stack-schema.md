# Task Stack Schema v2.1

`task-stack` v2.1 采用混合模型：执行流任务使用详情 JSON，尚未开始的待办使用 JSON Lines 轻量记录。

## 文件布局

任务数据存储在项目根目录 `.tasks/` 下：

```text
.tasks/
├── stack.json              # 执行流索引
├── backlog.jsonl           # 轻量待办，一行一个任务
├── tasks/
│   ├── T001.json           # active / suspended / blocked 任务详情
│   └── T003.json
└── archive.json            # 已完成任务摘要
```

## `.tasks/stack.json`

只保存执行流任务 id、顺序和入口信息。backlog 不放在这里。

```json
{
  "version": "2.1",
  "updated": "2026-05-31T10:00:00+08:00",
  "next_id": 4,
  "active": "T003",
  "stack": ["T003", "T001"],
  "tasks_dir": "tasks",
  "backlog_file": "backlog.jsonl"
}
```

### 字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `version` | string | 是 | 格式版本，v2.1 固定为 `"2.1"` |
| `updated` | string | 是 | ISO 8601 时间戳，最后一次修改时间 |
| `next_id` | integer | 是 | 下一个任务编号，新任务 id = `"T" + next_id` |
| `active` | string\|null | 是 | 当前活跃任务 id；无活跃任务时为 `null` |
| `stack` | array | 是 | 执行流任务 id 数组，`stack[0]` 为栈顶 |
| `tasks_dir` | string | 是 | 任务详情目录，默认 `"tasks"` |
| `backlog_file` | string | 是 | 轻量待办文件，默认 `"backlog.jsonl"` |

### 约束

- `stack` 只能包含已经进入执行流的任务 id。
- `stack` 不包含 backlog 任务。
- `active` 必须为 `null` 或存在于 `stack` 中。
- `stack[0]` 通常应等于 `active`。
- `stack` 引用的任务必须存在于 `.tasks/tasks/<id>.json`。
- backlog 任务保存在 `.tasks/backlog.jsonl`，默认不需要任务详情文件。

## `.tasks/backlog.jsonl`

一行一个尚未开始的轻量待办。每行都是独立 JSON 对象。

```jsonl
{"id":"T002","title":"补充 API 文档","priority":"medium","created":"2026-05-31T09:20:00+08:00","source":"src/api/"}
{"id":"T004","title":"优化缓存策略","priority":"low","created":"2026-05-31T09:25:00+08:00","source":"用户提到后续处理"}
```

### backlog 行字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一任务 id |
| `title` | string | 是 | 简短待办标题 |
| `priority` | string | 是 | `high` / `medium` / `low` |
| `created` | string | 是 | ISO 8601 创建时间，用于衰老提醒 |
| `source` | string\|null | 否 | 可快速恢复任务背景的文件、目录、用户上下文或来源 |
| `tags` | array | 否 | 轻量分类；只有常按标签整理时才需要 |
| `details` | string\|null | 否 | 可选任务详情文件路径；仅当 backlog 已有长上下文时使用 |

### backlog 设计原则

- backlog 不追求保存充分信息，只保存可识别、可排序、可找到来源的信息。
- 长上下文不写入 `backlog.jsonl`，应写入 `.tasks/tasks/<id>.json` 并用 `details` 指向。
- `add/later` 默认只追加 JSONL 行，不创建任务详情文件。
- `promote` 时再把 JSONL 行转换为 `.tasks/tasks/<id>.json`。

## `.tasks/tasks/<id>.json`

保存已进入执行流任务的详情、状态和恢复上下文。

```json
{
  "version": "2.1",
  "id": "T001",
  "title": "重构认证中间件",
  "status": "suspended",
  "parent": null,
  "priority": "high",
  "tags": ["refactor", "auth"],
  "created": "2026-05-31T09:30:00+08:00",
  "updated": "2026-05-31T10:00:00+08:00",
  "suspended_at": "2026-05-31T10:00:00+08:00",
  "suspend_reason": "用户要求先处理紧急任务 T003",
  "resume_hint": "继续 middleware.ts 后半部分重构，下一步补充 JWT 验证分支",
  "context": "auth/middleware.ts:80",
  "branch": "refactor/auth-middleware",
  "progress_snapshot": {
    "summary": "已完成 session 校验逻辑梳理，正在迁移 JWT 验证路径",
    "current_files": ["auth/middleware.ts"],
    "next_steps": ["补充 JWT 验证分支", "运行认证相关测试"],
    "known_decisions": ["保留旧 session fallback，避免一次性破坏兼容"]
  }
}
```

### 任务字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `version` | string | 是 | 格式版本，v2.1 固定为 `"2.1"` |
| `id` | string | 是 | 唯一标识，格式 `T` + 数字，如 `T001` |
| `title` | string | 是 | 简短任务标题 |
| `status` | string | 是 | `active` / `suspended` / `blocked` / `completed` |
| `parent` | string\|null | 是 | 父任务 id。顶层任务为 `null` |
| `priority` | string | 是 | `high` / `medium` / `low` |
| `tags` | array | 是 | 分类标签，如 `["bug", "auth"]` |
| `created` | string | 是 | ISO 8601 创建时间 |
| `updated` | string | 是 | ISO 8601 最后更新时间 |
| `suspended_at` | string\|null | 是 | 挂起时间；非 suspended 时为 `null` |
| `suspend_reason` | string\|null | 是 | 挂起原因；非 suspended 时为 `null` |
| `resume_hint` | string | 是 | 恢复时的一句话上下文提示 |
| `context` | string\|null | 否 | 相关文件、行号、命令或问题背景 |
| `branch` | string\|null | 否 | 关联 git 分支；resume 时提示切换 |
| `progress_snapshot` | object | 是 | 中断或恢复所需的结构化进展快照 |

### `progress_snapshot`

| 字段 | 类型 | 说明 |
|------|------|------|
| `summary` | string | 当前进展摘要 |
| `current_files` | array | 当前相关文件、目录或资源 |
| `next_steps` | array | 恢复后最应执行的下一步 |
| `known_decisions` | array | 已做出的关键判断，避免恢复时重复分析 |

## status 值

| 状态 | 含义 | 何时设置 |
|------|------|---------|
| `active` | 正在处理 | push、resume、promote 后的当前任务 |
| `suspended` | 暂时挂起 | 被 push/promote 打断，或用户主动挂起 |
| `blocked` | 被阻塞 | 等待外部条件，如 CI、他人反馈、权限 |
| `completed` | 已完成 | done 后的任务文件状态或归档状态 |

backlog 任务不使用 `status` 字段；是否处于 backlog 由其存在于 `backlog.jsonl` 决定。

## `.tasks/archive.json`

保存已完成任务的轻量摘要，避免 list 时读取所有历史任务文件。

```json
{
  "version": "2.1",
  "items": [
    {
      "id": "T003",
      "title": "修复 token 刷新逻辑",
      "parent": "T001",
      "completed_at": "2026-05-31T15:00:00+08:00",
      "summary": "添加了 catch fallback 并验证 token 刷新失败路径"
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 原任务 id |
| `title` | string | 原任务标题 |
| `parent` | string\|null | 原父任务 id |
| `completed_at` | string | ISO 8601 完成时间 |
| `summary` | string | 一句话完成摘要 |

## 操作示例

### 初始状态

`.tasks/stack.json`:

```json
{
  "version": "2.1",
  "updated": "2026-05-31T09:00:00+08:00",
  "next_id": 1,
  "active": null,
  "stack": [],
  "tasks_dir": "tasks",
  "backlog_file": "backlog.jsonl"
}
```

`.tasks/backlog.jsonl` 可以不存在或为空。

### push 第一个任务

`.tasks/stack.json`:

```json
{
  "version": "2.1",
  "updated": "2026-05-31T09:10:00+08:00",
  "next_id": 2,
  "active": "T001",
  "stack": ["T001"],
  "tasks_dir": "tasks",
  "backlog_file": "backlog.jsonl"
}
```

`.tasks/tasks/T001.json`:

```json
{
  "version": "2.1",
  "id": "T001",
  "title": "重构认证中间件",
  "status": "active",
  "parent": null,
  "priority": "high",
  "tags": ["refactor", "auth"],
  "created": "2026-05-31T09:10:00+08:00",
  "updated": "2026-05-31T09:10:00+08:00",
  "suspended_at": null,
  "suspend_reason": null,
  "resume_hint": "开始重构 auth/middleware.ts，将 session 校验迁移到 JWT 验证路径",
  "context": "auth/middleware.ts",
  "branch": "refactor/auth-middleware",
  "progress_snapshot": {
    "summary": "刚开始任务，尚未修改代码",
    "current_files": ["auth/middleware.ts"],
    "next_steps": ["梳理现有 session 校验逻辑"],
    "known_decisions": []
  }
}
```

### add 记录多个后续任务

用户说：“后续还要补 API 文档和优化缓存策略”。

`.tasks/stack.json` 只更新 `next_id` 和 `updated`，`active` 与 `stack` 不变：

```json
{
  "version": "2.1",
  "updated": "2026-05-31T09:20:00+08:00",
  "next_id": 4,
  "active": "T001",
  "stack": ["T001"],
  "tasks_dir": "tasks",
  "backlog_file": "backlog.jsonl"
}
```

`.tasks/backlog.jsonl` 追加：

```jsonl
{"id":"T002","title":"补充 API 文档","priority":"medium","created":"2026-05-31T09:20:00+08:00","source":"src/api/"}
{"id":"T003","title":"优化缓存策略","priority":"low","created":"2026-05-31T09:20:00+08:00","source":"用户提到后续处理"}
```

不创建 `T002.json` 或 `T003.json`。`T001` 仍为 active，`stack` 不变。

### push 临时插入任务

用户说：“先停一下，马上修 token 刷新 bug”。

先更新被打断任务 `.tasks/tasks/T001.json`：

```json
{
  "version": "2.1",
  "id": "T001",
  "title": "重构认证中间件",
  "status": "suspended",
  "parent": null,
  "priority": "high",
  "tags": ["refactor", "auth"],
  "created": "2026-05-31T09:10:00+08:00",
  "updated": "2026-05-31T09:30:00+08:00",
  "suspended_at": "2026-05-31T09:30:00+08:00",
  "suspend_reason": "用户要求先处理 T004 token 刷新 bug",
  "resume_hint": "继续 middleware.ts 后半部分重构，下一步补充 JWT 验证分支",
  "context": "auth/middleware.ts:80",
  "branch": "refactor/auth-middleware",
  "progress_snapshot": {
    "summary": "已梳理 session 校验路径，正在迁移 JWT 验证逻辑",
    "current_files": ["auth/middleware.ts"],
    "next_steps": ["补充 JWT 验证分支", "运行认证相关测试"],
    "known_decisions": ["保留旧 session fallback"]
  }
}
```

再创建 `.tasks/tasks/T004.json` 并更新索引：

```json
{
  "version": "2.1",
  "updated": "2026-05-31T09:30:00+08:00",
  "next_id": 5,
  "active": "T004",
  "stack": ["T004", "T001"],
  "tasks_dir": "tasks",
  "backlog_file": "backlog.jsonl"
}
```

### promote 待办升级

promote 等同于从 `backlog.jsonl` 取一行转换为执行流任务：

1. 对当前 active 任务写入 `progress_snapshot` 并设为 `suspended`
2. 从 `backlog.jsonl` 删除目标行
3. 用目标行创建 `.tasks/tasks/<id>.json`
4. 将目标任务设为 `active`
5. 插入 `stack[0]`
6. 更新 `active`

### done 完成任务

完成 `T004` 后：

`.tasks/stack.json`:

```json
{
  "version": "2.1",
  "updated": "2026-05-31T10:00:00+08:00",
  "next_id": 5,
  "active": "T001",
  "stack": ["T001"],
  "tasks_dir": "tasks",
  "backlog_file": "backlog.jsonl"
}
```

`.tasks/archive.json` 追加：

```json
{
  "id": "T004",
  "title": "修复 token 刷新 bug",
  "parent": "T001",
  "completed_at": "2026-05-31T10:00:00+08:00",
  "summary": "修复 token 刷新失败路径并验证回归"
}
```

`T001` 恢复为 active，并保留之前的 `resume_hint` 作为继续入口。

## v1 到 v2.1 迁移

### 检测

v1：

- `.tasks/stack.json.version === 1`
- `stack` 是完整任务对象数组
- `backlog` 是完整任务对象数组

v2.1：

- `.tasks/stack.json.version === "2.1"`
- `stack` 是执行流任务 id 字符串数组
- backlog 位于 `.tasks/backlog.jsonl`
- 执行流任务详情位于 `.tasks/tasks/`

### 迁移提示词

```text
将当前项目的 task-stack 从 v1 迁移到 v2.1：
- 先读取 .tasks/stack.json
- 如果 version=1 且 stack/backlog 是任务对象数组，则执行迁移
- 迁移前保留原始内容，必要时写入 .tasks/stack.v1.backup.json
- 将 stack[] 中的每个任务对象写入 .tasks/tasks/<id>.json
- 将 backlog[] 中的每个任务对象转换为 .tasks/backlog.jsonl 的一行
- backlog 行保留 id、title、priority、created、source/tags 等轻量字段
- 如果 backlog 对象含有大量 context/resume_hint，则可创建 .tasks/tasks/<id>.json 并在 backlog 行中写 details
- 新 stack.json 只保留 version、updated、next_id、active、stack、tasks_dir、backlog_file
- stack 字段只保存执行流任务 id 数组
- 不覆盖已存在的任务文件；如冲突，先询问用户
- 完成后报告迁移了多少个 stack 任务和 backlog 任务
```

### 字段映射

| v1 来源 | v2.1 目标 |
|---------|-----------|
| `stack[]` 任务对象 | `.tasks/tasks/<id>.json` |
| `backlog[]` 轻量任务 | `.tasks/backlog.jsonl` 一行 |
| `backlog[]` 长上下文任务 | `.tasks/backlog.jsonl` + 可选 `.tasks/tasks/<id>.json` |
| `next_id` | `.tasks/stack.json.next_id` |
| `updated` | `.tasks/stack.json.updated` |
| `stack[].id` | `.tasks/stack.json.stack[]` |
| 第一个 active 任务 | `.tasks/stack.json.active` |

### 默认值

迁移执行流任务时缺失字段按以下规则补齐：

- `version`: `"2.1"`
- 缺失 `parent`: `null`
- 缺失 `updated`: 使用原顶层 `updated` 或任务 `created`
- 缺失 `suspended_at` / `suspend_reason`: `null`
- 缺失 `resume_hint`: 使用 `context` 或 `"尚未开始"`
- 缺失 `progress_snapshot.summary`: 使用 `resume_hint`
- 缺失 `progress_snapshot.current_files`: 能从 `context` 明确提取则填写，否则 `[]`
- 缺失 `progress_snapshot.next_steps`: `[]`
- 缺失 `progress_snapshot.known_decisions`: `[]`

迁移 backlog 行时缺失字段按以下规则补齐：

- `priority`: `"medium"`
- `created`: 使用任务 `created`、顶层 `updated` 或当前时间
- `source`: 使用原 `context` 的短摘要；无来源时为 `null`

### 安全规则

- 不在普通 list/read/启动检查中自动迁移。
- 迁移前保留原始内容。
- 不覆盖已存在任务文件；有冲突先询问用户。
- 不混用 v1 完整对象数组和 v2.1 执行流索引。

## 文档化校验清单

暂不提供 JSON schema 校验脚本。需要检查任务栈一致性时，Agent 按以下清单执行：

- `.tasks/stack.json.version` 是否为 `"2.1"`。
- `stack` 是否是任务 id 数组。
- `active` 是否为 `null` 或存在于 `stack` 中。
- `stack[0]` 是否通常等于 `active`。
- `stack` 引用的任务文件是否存在。
- 每个执行流任务文件的 `id` 是否与文件名一致。
- 每个执行流任务文件是否包含必需字段。
- 每个执行流任务的 `status` 是否为合法值。
- active 任务状态是否为 `active`。
- suspended 任务是否有 `suspended_at` 和 `resume_hint`。
- `backlog.jsonl` 是否每行都是合法 JSON 对象。
- backlog 行是否包含 `id`、`title`、`priority`、`created`。
- backlog 行中的 `details` 如存在，是否指向存在的任务文件。
- 是否存在同一个 id 同时出现在 `stack` 和 `backlog.jsonl`。
- 是否存在未被 `stack` / `backlog.jsonl` / `archive` 引用的孤儿任务文件。
