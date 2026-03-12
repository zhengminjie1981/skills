---
description: "构建知识索引"
argument-hint: "<路径> [--force] [--no-ai]"
allowed-tools: [Bash, Read, Glob, Grep]
---

# 构建知识索引

扫描知识库文档，生成 AI 摘要，创建索引文件。

## 工作流

1. **扫描文档** - 扫描指定路径及子文件夹的所有文档
2. **生成摘要** - 为每个文档生成 AI 摘要（需 API Key）或基础摘要
3. **创建索引** - 写入 `_index.yaml` 索引文件
4. **注册全局** - 添加到全局注册表 `~/.knowledge-index/registry.yaml`

## CLI 命令

```bash
python scripts/knowledge-index-manager.py build <知识库路径> [--force] [--no-ai]
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `--force` | 强制创建索引（忽略父索引） |
| `--no-ai` | 禁用 AI 摘要，使用基础摘要 |

## 使用示例

```
/knowledge-index:build E:/知识库/信息化
/knowledge-index:build ./docs --force
/knowledge-index:build ./papers --no-ai
```

## 参考资源

如需详细规范，按需读取：
- `~/.claude/skills/knowledge-index/references/core/workflow-spec.md` - 完整构建流程
- `~/.claude/skills/knowledge-index/references/core/index-spec.md` - 索引文件规范
