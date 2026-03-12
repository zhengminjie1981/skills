---
description: "列出所有知识库"
argument-hint: ""
allowed-tools: [Bash, Read]
---

# 列出所有知识库

查看全局注册表中所有已索引的知识库。

## 工作流

1. **读取注册表** - 读取 `~/.knowledge-index/registry.yaml`
2. **显示状态** - 列出每个知识库的路径和文档数量

## CLI 命令

```bash
python scripts/knowledge-index-manager.py list
```

## 使用示例

```
/knowledge-index:list
```

## 输出示例

```
已注册的知识库：

1. E:/知识库/信息化
   - 文档数：15
   - 最后更新：2026-03-12

2. ./docs
   - 文档数：8
   - 最后更新：2026-03-10
```

## 参考资源

如需详细说明，按需读取：
- `~/.claude/skills/knowledge-index/references/advanced/global-registry-spec.md` - 全局注册表规范
