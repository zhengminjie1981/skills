# 触发规则

## 反馈触发条件

自动反馈系统仅在检测到以下情况时触发。

---

## 触发级别

### 🔴 Critical（必须触发）

| 条件 | 说明 | 触发时机 |
|------|------|----------|
| `skill_execution_failure` | Skill 执行失败 | 返回错误或异常 |
| `unhandled_exception` | 未处理异常 | 捕获到未预期的异常 |
| `timeout_error` | 超时错误 | 操作超过限定时间 |

**行为**: 无论用户设置如何，都会触发反馈收集。

### 🟡 Suggested（建议触发）

| 条件 | 说明 | 判断标准 |
|------|------|----------|
| `user_retry_gt_2` | 用户重试超过2次 | 同一操作重试 ≥ 3 次 |
| `execution_time_anomaly` | 执行时间异常 | 超过平均时间 3 倍 |
| `frequent_output_modification` | 频繁修改输出 | 用户修改输出 ≥ 3 次 |
| `edge_case_detected` | 检测到边界情况 | AI 判断为非典型场景 |

**行为**: AI 根据上下文判断是否值得反馈。

---

## 触发流程

```
Skill 执行
    │
    ├─ 成功 ────────────────────────→ 检查 Suggested 条件
    │                                       │
    │                                       ├─ 满足 → 触发反馈
    │                                       │
    │                                       └─ 不满足 → 结束
    │
    └─ 失败 ──→ 检查是否 Critical 错误
                    │
                    ├─ 是 → 必须触发反馈
                    │
                    └─ 否 → 检查 Suggested 条件
```

---

## Skill 自定义触发

Skill 可以在 `FEEDBACK-TRIGGER` 块中自定义触发条件：

```json
{
  "triggers": [
    "execution_failure",
    "user_retry",
    "anomaly",
    "custom_condition"
  ],
  "collect": [
    "error_type",
    "environment",
    "skill_version"
  ],
  "sanitize": [
    "file_paths",
    "user_data",
    "code_content"
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `triggers` | string[] | 触发条件列表 |
| `collect` | string[] | 要收集的信息 |
| `sanitize` | string[] | 要脱敏的内容 |

---

## 限流机制

为避免刷屏，系统实施以下限流：

| 规则 | 值 | 说明 |
|------|-----|------|
| 每日上限 | 5 条 | 每天最多发送 5 条反馈 |
| 合并窗口 | 24 小时 | 相似反馈合并为一条 |
| 去重键 | error_type + skill_name | 相同错误不重复发送 |

---

## 排除规则

以下情况不触发反馈：

1. 系统已禁用（`enabled: false`）
2. Skill 在排除列表中（`excluded_skills`）
3. 用户未授权且拒绝协议
4. 达到每日上限
5. 重复错误（已在合并窗口内）
