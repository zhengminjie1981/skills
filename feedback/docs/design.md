# 自动反馈系统设计文档

## 概述

本系统为 E:/Skills 项目提供自动反馈收集和发送功能，帮助持续改进 skill 质量。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Feedback System                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌────────────────┐  │
│  │  配置层      │───→│  决策层      │───→│  发送层        │  │
│  │ config.yaml │    │ AI + 规则   │    │ gh / glab CLI │  │
│  └─────────────┘    └─────────────┘    └────────────────┘  │
│         ↑                  ↑                    ↓          │
│  ┌─────────────┐    ┌─────────────┐    ┌────────────────┐  │
│  │  授权层      │    │  收集层      │    │  目标仓库      │  │
│  │ consent.json│    │ 脱敏处理    │    │ GitHub/GitLab  │  │
│  └─────────────┘    └─────────────┘    └────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 目录结构

```
feedback/
├── SKILL.md                    # 入口文件，AI 决策逻辑
├── references/
│   ├── protocol.md             # 用户协议
│   ├── triggers.md             # 触发规则
│   ├── privacy.md              # 隐私与脱敏规范
│   └── discovery.md            # Skill 发现机制
├── scripts/
│   ├── sender.py               # 统一发送接口
│   ├── github_client.py        # GitHub CLI 封装
│   └── gitlab_client.py        # GitLab CLI 封装
├── data/
│   ├── config.yaml             # 系统配置
│   ├── registry.json           # 用户授权 + Skill 注册表
│   └── feedback_queue.json     # 发送队列（去重）
└── docs/
    └── design.md               # 本文档
```

## 核心流程

### 1. 授权流程

```
/feedback-setup
       │
       ├─ 展示协议
       │
       ├─ 选择渠道（GitHub/GitLab）
       │
       └─ 保存到 registry.json
```

### 2. 触发流程

```
Skill 执行完成
       │
       ├─ 检查 FEEDBACK-TRIGGER 块
       │
       ├─ AI 判断触发条件
       │
       ├─ 检查授权状态
       │
       ├─ 收集脱敏信息
       │
       └─ 调用 sender.py 发送
```

## 配置说明

### config.yaml

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `enabled` | 系统开关 | `true` |
| `target.github.repo` | GitHub 仓库 | `owner/repo` |
| `target.gitlab.project_id` | GitLab 项目 | `namespace/project` |
| `rate_limit.max_per_day` | 每日上限 | `5` |
| `sanitization.remove_paths` | 移除路径 | `true` |

### registry.json

```json
{
  "consent": {
    "consented": true,
    "channel": "github"
  },
  "skills": {
    "global": { ... },
    "project": { ... }
  }
}
```

## 与 Skill 集成

### 启用反馈

1. 在 `SKILL.md` 添加 front matter：
```yaml
feedback:
  enabled: true
  version: "1.0.0"
  author: "your-name"
```

2. 添加触发块：
```markdown
<!-- FEEDBACK-TRIGGER-START -->
<feedback-config>
{
  "triggers": ["execution_failure", "user_retry"],
  "collect": ["error_type", "environment"]
}
</feedback-config>
<!-- FEEDBACK-TRIGGER-END -->
```

### 禁用反馈

1. 临时：`feedback.enabled: false`
2. 完全：移除 feedback 配置和触发块
3. 用户侧：添加到 `excluded_skills`

## 下架方式

1. 软关闭：`config.yaml` → `enabled: false`
2. 完全移除：删除 `feedback/` 目录

无副作用，不影响其他 skill。

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-01 | 初始版本 |
