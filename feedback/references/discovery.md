# Skill 发现机制

## 概述

自动反馈系统需要发现哪些 skill 支持反馈功能。本文档说明发现和注册机制。

---

## 发现策略

### 扫描路径

| 范围 | 路径 | 说明 |
|------|------|------|
| 全局 | `E:/Skills/` | 本项目下的所有 skill |
| 全局 | `~/.claude/skills/` | Claude Code 全局 skills |
| 项目 | `./.claude/skills/` | 当前项目的 skills |
| 项目 | `./skills/` | 项目自定义目录 |

### 发现条件

Skill 被识别为"支持反馈"的条件：

1. 存在 `SKILL.md` 文件
2. Front matter 包含 `feedback` 字段
3. `feedback.enabled` 为 `true`

---

## Front Matter 规范

```yaml
---
name: skill-name
description: |
  Skill 描述...

  **触发场景**：...

feedback:
  enabled: true                    # 必需：启用反馈
  version: "1.0.0"                 # 必需：语义化版本
  author: "author-name"            # 必需：作者标识
  repository: "owner/repo"         # 可选：自定义反馈仓库
---
```

### 字段说明

| 字段 | 必须 | 类型 | 说明 |
|------|------|------|------|
| `feedback.enabled` | ✅ | boolean | 必须为 `true` |
| `feedback.version` | ✅ | string | 语义化版本号 (semver) |
| `feedback.author` | ✅ | string | 作者或组织标识 |
| `feedback.repository` | ❌ | string | 自定义反馈目标仓库 |

---

## FEEDBACK-TRIGGER 块

支持反馈的 skill 应在 `SKILL.md` 末尾包含触发配置：

```markdown
<!-- FEEDBACK-TRIGGER-START -->
<feedback-config>
{
  "triggers": ["execution_failure", "user_retry", "anomaly"],
  "collect": ["error_type", "environment", "skill_version"],
  "sanitize": ["file_paths", "user_data", "code_content"]
}
</feedback-config>
<!-- FEEDBACK-TRIGGER-END -->
```

### 解析规则

1. 查找 `<!-- FEEDBACK-TRIGGER-START -->` 标记
2. 提取 `<feedback-config>` 标签内的 JSON
3. 解析为配置对象
4. 如无此块，使用默认配置

---

## 注册表结构

`registry.json` 存储已发现的 skill：

```json
{
  "version": "1.0",
  "consent": {
    "consented": true,
    "channel": "github",
    "timestamp": "2026-04-01T10:00:00Z"
  },
  "skills": {
    "global": {
      "db-mcp": {
        "path": "E:/Skills/db-mcp",
        "version": "1.2.0",
        "author": "skill-author",
        "registered_at": "2026-04-01T10:00:00Z"
      }
    },
    "project": {
      "custom-skill": {
        "path": "./skills/custom-skill",
        "version": "0.1.0",
        "author": "local-dev",
        "project": "my-project"
      }
    }
  }
}
```

---

## 发现流程

```
系统启动 / 用户调用命令
        │
        ├─ 扫描配置的路径
        │       │
        │       ├─ 检查每个目录的 SKILL.md
        │       │
        │       └─ 解析 front matter
        │
        ├─ 筛选 feedback.enabled = true
        │
        ├─ 与 registry.json 对比
        │       │
        │       ├─ 新增 → 自动注册
        │       │
        │       ├─ 更新 → 更新版本信息
        │       │
        │       └─ 移除 → 从注册表删除
        │
        └─ 返回已注册 skill 列表
```

---

## 手动操作

### 注册 skill

```bash
/feedback-register --skill=db-mcp --path=E:/Skills/db-mcp
```

### 移除注册

```bash
/feedback-unregister --skill=db-mcp
```

### 验证配置

```bash
/feedback-verify --skill=db-mcp
```

检查项：
- [ ] SKILL.md 存在
- [ ] front matter 格式正确
- [ ] feedback.enabled = true
- [ ] feedback.version 格式正确
- [ ] feedback.author 已填写
- [ ] FEEDBACK-TRIGGER 块存在（可选）
