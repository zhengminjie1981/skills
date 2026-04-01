# 隐私与脱敏规范

## 数据处理原则

1. **最小化收集**: 只收集改进 skill 必需的信息
2. **自动脱敏**: 发送前自动移除敏感信息
3. **透明可控**: 用户可随时查看和禁用

---

## 脱敏规则

### 1. 路径处理

| 原始 | 脱敏后 |
|------|--------|
| `E:/Users/john/project/src/main.py` | `<PATH>/src/main.py` |
| `/home/user/.config/app/settings.json` | `<PATH>/.config/app/settings.json` |
| `C:\Users\Alice\Documents\work\` | `<PATH>/` |

**规则**: 移除用户目录和盘符，保留相对结构。

### 2. 文件名哈希

```python
# 原始
"secret-database-config.json"

# 脱敏后
"file_a3f2b1c8"
```

**规则**: 保留扩展名语义，文件名替换为哈希值。

### 3. 敏感值过滤

**自动移除的模式**:

```
password=xxx
password: xxx
api_key=xxx
api-key: xxx
token=xxx
secret=xxx
```

**正则表达式**:
```regex
(password|api[_-]?key|token|secret)\s*[=:]\s*\S+
```

**替换为**: `[REDACTED]`

### 4. 用户信息移除

| 数据 | 处理方式 |
|------|----------|
| 用户名 | 移除 |
| 邮箱 | 移除 |
| IP 地址 | 移除 |
| 主机名 | 替换为 `<HOST>` |

---

## 收集的信息

### 错误反馈

```json
{
  "skill_name": "db-mcp",
  "skill_version": "1.2.0",
  "error_type": "UnicodeDecodeError",
  "error_message": "'utf-8' codec can't decode byte 0xff",
  "stack_trace": "... (已脱敏) ...",
  "environment": {
    "os": "Windows 11",
    "python_version": "3.11.0"
  },
  "timestamp": "2026-04-01T10:30:00Z",
  "trigger": "execution_failure"
}
```

### 性能反馈

```json
{
  "skill_name": "knowledge-index",
  "skill_version": "2.0.0",
  "execution_time_ms": 15234,
  "anomaly_type": "slow_execution",
  "environment": {
    "os": "Windows 11",
    "cpu_cores": 8,
    "memory_gb": 16
  },
  "timestamp": "2026-04-01T10:30:00Z"
}
```

---

## 不收集的信息

### 绝对不收集

| 类型 | 原因 |
|------|------|
| 代码内容 | 可能包含商业机密 |
| 配置文件内容 | 可能包含凭证 |
| 数据库连接字符串 | 安全风险 |
| 用户输入的文本 | 隐私保护 |
| 文件内容 | 隐私保护 |

### 需要用户确认才收集

| 类型 | 说明 |
|------|------|
| 部分堆栈信息 | 用于调试，会先脱敏 |
| 操作上下文 | 帮助复现问题 |

---

## 配置选项

用户可以在 `config.yaml` 中调整：

```yaml
sanitization:
  # 移除文件路径
  remove_paths: true

  # 移除用户信息
  remove_user_info: true

  # 哈希文件名
  hash_filenames: true

  # 自定义脱敏模式（正则）
  redact_patterns:
    - "password\\s*[=:]\\s*\\S+"
    - "api[_-]?key\\s*[=:]\\s*\\S+"
```

---

## 合规说明

- 本系统不收集个人身份信息 (PII)
- 不跨用户追踪行为
- 数据仅用于改进 skill 质量
- 用户可随时撤回授权
