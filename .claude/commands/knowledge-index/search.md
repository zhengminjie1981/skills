---
description: "搜索知识库"
argument-hint: "<查询> [--kb 路径]"
allowed-tools: [Bash, Read]
---

# 搜索知识库

通过索引文件智能检索相关文档。

## 工作流

1. **匹配关键词** - 在索引中匹配查询关键词
2. **相关度排序** - 按摘要和关键词的相关度排序
3. **显示结果** - 显示匹配的文档列表和摘要

## CLI 命令

```bash
python scripts/knowledge-index-manager.py search <查询> [--kb <知识库路径>]
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `--kb` | 指定搜索的知识库路径（不指定则搜索全部） |

## 使用示例

```
/knowledge-index:search GitLab 配置
/knowledge-index:search API 设计 --kb ./docs
/knowledge-index:search 数据库优化
```

## 检索策略

- 统一检索所有格式文档
- Markdown 文档软加权 +10%（有额外元信息）
- 按相关度排序，同名文件 Markdown 优先

## 参考资源

如需详细说明，按需读取：
- `~/.claude/skills/knowledge-index/references/advanced/global-registry-spec.md` - 跨库搜索
