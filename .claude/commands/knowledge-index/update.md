---
description: "增量更新索引"
argument-hint: "<路径> [--no-ai]"
allowed-tools: [Bash, Read, Glob, Grep]
---

# 增量更新索引

检测知识库变更，增量更新索引文件。

## 工作流

1. **检测变更** - 对比文件哈希，识别新增、修改、删除的文档
2. **增量处理** - 仅处理变更的文档
3. **更新索引** - 更新 `_index.yaml` 索引文件
4. **报告变更** - 显示变更统计

## CLI 命令

```bash
python scripts/knowledge-index-manager.py update <知识库路径> [--no-ai]
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `--no-ai` | 禁用 AI 摘要，使用基础摘要 |

## 使用示例

```
/knowledge-index:update E:/知识库/信息化
/knowledge-index:update ./docs --no-ai
```

## 变更检测

- 基于文件内容的 SHA256 哈希
- 仅处理有变化的文档
- 自动清理已删除文档的索引条目

## 参考资源

如需详细说明，按需读取：
- `~/.claude/skills/knowledge-index/references/advanced/incremental-update.md` - 增量更新算法
