---
description: "批量转换文档"
argument-hint: "<模式> [-o 输出目录]"
allowed-tools: [Bash, Read, Glob]
---

# 批量转换文档

批量转换多个文档为 Markdown。

## 工作流

1. **展开文件** - 使用 glob 模式匹配文件
2. **逐个转换** - 对每个文件执行转换
3. **汇总报告** - 显示转换结果统计

## 推荐参数

```bash
# 批量转换
python scripts/converter.py "./docs/*.docx" -o ./output/ --relative-images --skip-toc

# 混合格式
python scripts/converter.py "./files/*.{docx,pdf}" -o ./markdown/ --tool auto
```

## 使用示例

```
/doc2md:batch "./docs/*.docx"
/doc2md:batch "./files/*.pdf" -o ./markdown/
/doc2md:batch "./papers/*.docx" -o ./output/
```

## 支持的格式

常见：`.docx`, `.doc`, `.pdf`, `.epub`, `.html`, `.pptx`, `.txt`
学术：`.tex`, `.latex`, `.rst`, `.ipynb`
数据：`.csv`, `.tsv`, `.json`, `.xml`

## 参考资源

如需详细说明，按需读取：
- `~/.claude/skills/doc2md/references/scenarios.md` - 使用场景
- `~/.claude/skills/doc2md/references/usage.md` - 完整使用文档
