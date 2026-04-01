---
name: feedback
description: |
  自动反馈系统 - 收集 skill 使用反馈，帮助持续改进质量。

  **触发场景**（使用以下命令）：
  - 设置授权：/feedback-setup、配置反馈、启用反馈
  - 查看状态：/feedback-status、反馈状态
  - 注册技能：/feedback-register、注册反馈
  - 移除注册：/feedback-unregister、取消反馈
  - 发送反馈：/feedback-send、提交反馈
  - 禁用系统：/feedback-disable、关闭反馈
  - 启用系统：/feedback-enable、开启反馈
  - 查看队列：/feedback-queue、反馈队列
  - 验证配置：/feedback-verify、验证反馈

  **不触发场景**：
  - 系统禁用时（enabled: false）

argument-hint: "[command] [options]"
---

# 自动反馈系统

## 快速开始

### 首次使用

```
用户: /feedback-setup
```

AI 将引导你完成：
1. 阅读用户协议
2. 选择反馈渠道（GitHub / GitLab）
3. 确认授权

### 检查状态

```
用户: /feedback-status
```

显示当前授权状态、已注册的 skill、发送统计。

---

## 命令参考

| 命令 | 功能 | 参数 |
|------|------|------|
| `/feedback-setup` | 首次设置授权 | 无 |
| `/feedback-status` | 查看状态 | 无 |
| `/feedback-register` | 注册支持反馈的 skill | `--skill=<name>` `--path=<path>` |
| `/feedback-unregister` | 移除 skill 注册 | `--skill=<name>` |
| `/feedback-send` | 手动发送反馈 | `--skill=<name>` `--type=<type>` |
| `/feedback-disable` | 禁用反馈系统 | 无 |
| `/feedback-enable` | 启用反馈系统 | 无 |
| `/feedback-queue` | 查看发送队列 | `--pending` `--sent` |
| `/feedback-verify` | 验证 skill 配置 | `--skill=<name>` |

---

## 决策树

### 用户调用命令时

```
用户输入命令
    │
    ├─ /feedback-setup
    │       │
    │       ├─ 已授权？ ──是──→ 显示当前状态
    │       │       │
    │       │       否
    │       │       ↓
    │       │   展示协议 → 选择渠道 → 保存授权
    │       │
    │       └─ 更新 registry.json
    │
    ├─ /feedback-status
    │       │
    │       └─ 读取 registry.json → 显示状态
    │
    ├─ /feedback-register
    │       │
    │       ├─ 检查 skill 是否存在
    │       │
    │       ├─ 读取 skill 的 SKILL.md
    │       │
    │       ├─ 验证 feedback.enabled = true
    │       │
    │       └─ 添加到 registry.json
    │
    ├─ /feedback-send
    │       │
    │       ├─ 检查是否已授权
    │       │       │
    │       │       否 → 提示执行 /feedback-setup
    │       │       │
    │       │       是
    │       │       ↓
    │       ├─ 收集反馈信息（脱敏）
    │       │
    │       ├─ 检查限流和去重
    │       │
    │       └─ 调用发送脚本
    │
    └─ /feedback-disable
            │
            └─ 更新 config.yaml → enabled: false
```

### 自动触发反馈时

```
Skill 执行完成
    │
    ├─ 检查 SKILL.md 是否包含 FEEDBACK-TRIGGER 块
    │       │
    │       无 → 结束
    │       │
    │       有
    │       ↓
    ├─ AI 判断是否满足触发条件
    │       │
    │       不满足 → 结束
    │       │
    │       满足
    │       ↓
    ├─ 检查 registry.json 是否已授权
    │       │
    │       未授权 → 弹出协议确认
    │       │
    │       已授权
    │       ↓
    ├─ 收集反馈信息
    │       │
    │       ├─ 错误类型
    │       ├─ 环境（OS、版本）
    │       ├─ Skill 版本
    │       └─ 脱敏处理
    │
    ├─ 检查限流和去重
    │       │
    │       超限 → 合并或丢弃
    │       │
    │       通过
    │       ↓
    └─ 自动发送（调用 gh/glab CLI）
```

---

## 配置文件位置

| 文件 | 路径 | 用途 |
|------|------|------|
| 系统配置 | `feedback/data/config.yaml` | 开关、限流、脱敏规则 |
| 用户授权 | `feedback/data/registry.json` | 授权状态、已注册 skill |
| 发送队列 | `feedback/data/feedback_queue.json` | 去重、历史记录 |

### 目标仓库（当前配置）

| 渠道 | 仓库 | 说明 |
|------|------|------|
| **GitHub** | `zhengminjie1981/skills` | 反馈发送到此仓库的 Issues |
| **GitLab** | `Antbook/AI/skills` | 备选渠道 |

> 用户可在 `/feedback-setup` 时选择使用 GitHub 或 GitLab。

---

## 为 Skill 添加/移除反馈支持

### 添加反馈支持（3 步）

**Step 1**: 在 `SKILL.md` 的 front matter 添加 `feedback` 字段

```yaml
---
name: your-skill
description: |
  技能描述...

feedback:
  enabled: true                    # 必须：启用反馈
  version: "1.0.0"                 # 必须：skill 版本
  author: "your-name"              # 必须：作者标识
---
```

**Step 2**: 在 `SKILL.md` 末尾添加 `FEEDBACK-TRIGGER` 块

```markdown
## 反馈机制

本 skill 支持自动反馈改进。

<!-- FEEDBACK-TRIGGER-START -->
<feedback-config>
{
  "triggers": ["execution_failure", "user_retry", "anomaly"],
  "collect": ["error_type", "environment", "skill_version"],
  "sanitize": ["file_paths", "user_data", "code_content"]
}
</feedback-config>
<!-- FEEDBACK-TRIGGER-END -->

执行完成后，如检测到改进机会且用户已授权，将自动发送脱敏反馈。
```

**Step 3**: 注册到反馈系统

```
/feedback-register --skill=your-skill
```

---

### 移除反馈支持（3 种方式）

#### 方式 1: 临时禁用（保留配置，可恢复）

修改 `SKILL.md` front matter：

```yaml
feedback:
  enabled: false    # 改为 false
```

#### 方式 2: 完全移除（删除所有反馈相关配置）

1. 删除 front matter 中的 `feedback` 字段
2. 删除 `<!-- FEEDBACK-TRIGGER-START -->` 到 `<!-- FEEDBACK-TRIGGER-END -->` 之间的内容
3. 从注册表移除：
   ```
   /feedback-unregister --skill=your-skill
   ```

#### 方式 3: 用户侧禁用（不影响 skill 本身）

用户可以在 `feedback/data/config.yaml` 中排除特定 skill：

```yaml
excluded_skills:
  - your-skill
```

---

### 无 Feedback Skill 时的行为

**重要原则**：如果本地不存在 `feedback` skill，则**自动忽略**所有 skill 中的反馈相关配置。

具体行为：

| 场景 | 行为 |
|------|------|
| skill 有 `feedback` 字段，但无 feedback skill | 忽略，正常执行 skill |
| skill 有 `FEEDBACK-TRIGGER` 块，但无 feedback skill | 忽略，不触发任何反馈 |
| 用户调用 `/feedback-*` 命令 | 提示"feedback skill 未安装" |

**实现方式**：AI 在执行 skill 时，先检查 `feedback/` 目录是否存在：
- 存在 → 按正常流程处理反馈
- 不存在 → 完全跳过反馈逻辑

这确保了：
1. 反馈系统是**可选的**，不影响 skill 的核心功能
2. 删除 `feedback/` 目录即可完全移除反馈功能
3. Skill 中的反馈配置是**声明式的**，无副作用

---

## 详细参考

执行任务时，按需阅读以下参考文档：

| 文档 | 用途 |
|------|------|
| `references/protocol.md` | 用户协议详情 |
| `references/triggers.md` | 触发规则详解 |
| `references/privacy.md` | 隐私与脱敏规范 |
| `references/discovery.md` | Skill 发现机制 |

---

## 常见问题

### Q: 如何完全禁用反馈？

```bash
/feedback-disable
```

或修改 `config.yaml`:
```yaml
enabled: false
```

### Q: 如何排除特定 skill？

修改 `config.yaml`:
```yaml
excluded_skills:
  - skill-name-1
```

### Q: 反馈发送到哪里？

根据用户选择的渠道：
- **GitHub**: 发送到配置的 GitHub 仓库 Issue
- **GitLab**: 发送到配置的 GitLab 项目 Issue

### Q: 发送前可以预览吗？

可以，修改 `registry.json` 中的 `preferences.preview_before_send: true`。
