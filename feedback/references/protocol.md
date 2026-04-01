# 用户协议

## 自动反馈系统用户协议

**版本**: 1.0.0
**生效日期**: 2026-04-01

---

## 概述

本协议说明自动反馈系统如何收集、处理和发送用户使用数据。使用支持反馈的 skill 即表示您同意本协议。

---

## 数据收集范围

### ✅ 我们收集

| 数据类型 | 用途 | 示例 |
|----------|------|------|
| 错误类型 | 诊断问题 | `UnicodeDecodeError` |
| 操作系统 | 环境复现 | `Windows 11` |
| Skill 版本 | 版本追踪 | `1.2.0` |
| 执行时长 | 性能分析 | `2.5s` |
| 错误堆栈 | 问题定位 | 已脱敏的堆栈信息 |

### ❌ 我们不收集

| 数据类型 | 原因 |
|----------|------|
| 代码内容 | 隐私保护 |
| 文件路径 | 已脱敏处理 |
| 用户名/邮箱 | 个人信息 |
| API Key/密码 | 安全考虑 |
| 项目名称 | 商业机密 |

---

## 脱敏处理

所有数据发送前会经过以下脱敏处理：

1. **路径替换**: `E:/Users/xxx/project/file.txt` → `<PATH>/file.txt`
2. **文件名哈希**: `secret-config.json` → `file_a3f2b1`
3. **敏感词过滤**: 移除 password、token、api_key 等敏感值
4. **用户信息移除**: 不包含任何个人身份信息

---

## 数据发送

### 发送渠道

您可以选择：
- **GitHub**: 发送到指定的 GitHub 仓库 Issue
- **GitLab**: 发送到指定的 GitLab 项目 Issue

### 发送内容示例

```markdown
## [自动反馈] Skill 执行异常

**Skill**: db-mcp v1.2.0
**类型**: execution_failure
**时间**: 2026-04-01T10:30:00Z
**环境**: Windows 11, Python 3.11

### 错误信息
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff
```

### 堆栈（已脱敏）
```
File "<PATH>/parser.py", line 42, in parse_file
    content = file.read()
```

---
*此反馈由自动反馈系统生成，不包含用户个人信息。*
```

---

## 用户权利

### 您可以随时

- **查看状态**: `/feedback-status`
- **禁用系统**: `/feedback-disable`
- **重新启用**: `/feedback-enable`
- **排除特定 skill**: 修改 `config.yaml` 的 `excluded_skills`

### 数据保留

- 反馈数据存储在您选择的目标仓库
- 本地仅保留发送记录用于去重
- 您可以删除 `feedback_queue.json` 清除本地记录

---

## 协议更新

协议更新时，系统会提示您重新确认。继续使用即表示接受更新后的协议。

---

## 联系方式

如有疑问，请在目标仓库提交 Issue。
