---
description: "转换文档为 Markdown"
argument-hint: "<文件> [--tool auto|pandoc|mineru|pymupdf]"
allowed-tools: [Bash, Read, Glob]
---

# 转换文档为 Markdown

将 40+ 种文档格式转换为 Markdown。

## 工作流

1. **检测类型** - 根据文件扩展名确定文档类型
2. **选择工具** - 智能选择转换工具
3. **执行转换** - 调用 converter.py 脚本
4. **报告结果** - 显示输出文件路径

## 工具选择矩阵

| 文件类型 | 推荐工具 | 说明 |
|---------|---------|------|
| Word/EPUB/HTML | pandoc | 原生支持 |
| 扫描 PDF | mineru | 需要 OCR |
| 表格 PDF | mineru | 更好的表格提取 |
| 简单 PDF | pymupdf | 快速轻量 |
| Python 3.14+ | pymupdf | 兼容性好 |

## 推荐参数

```bash
# 安全默认值
python scripts/converter.py <文件> --relative-images --skip-toc

# 复杂 PDF
python scripts/converter.py <文件> --tool mineru --relative-images

# 首次使用（自动安装 pandoc）
python scripts/converter.py <文件> --auto-install --relative-images --skip-toc
```

## 使用示例

```
/doc2md:convert report.docx
/doc2md:convert document.pdf --tool mineru
/doc2md:convert presentation.pptx --tool auto
```

## 参考资源

如需详细说明，按需读取：
- `~/.claude/skills/doc2md/references/usage.md` - 完整使用文档
- `~/.claude/skills/doc2md/references/troubleshooting.md` - 故障排除
