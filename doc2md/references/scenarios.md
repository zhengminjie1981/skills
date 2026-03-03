# Doc2Md 场景指南

> 按使用场景组织，快速找到解决方案

## 📋 场景索引

| 场景 | 跳转 |
|------|------|
| Word 文档转 Markdown | [→ 场景 1](#场景-1-word-文档转换) |
| PDF 转换（简单） | [→ 场景 2](#场景-2-简单-pdf-转换) |
| PDF 转换（复杂表格） | [→ 场景 3](#场景-3-pdf-复杂表格提取) |
| 扫描版 PDF | [→ 场景 4](#场景-4-扫描版-pdfocr-识别) |
| 批量转换 | [→ 场景 5](#场景-5-批量转换文档) |
| 便携模式（跨机器） | [→ 场景 6](#场景-6-便携模式) |
| 单文件（嵌入图片） | [→ 场景 7](#场景-7-创建单文件分享) |
| 学术论文 | [→ 场景 8](#场景-8-学术论文转换) |
| 混合格式批量 | [→ 场景 9](#场景-9-混合格式批量转换) |

---

## 场景 1: Word 文档转换

**典型需求**: 将 .docx 报告转换为 Markdown 用于文档网站

### 快速命令
```bash
python scripts/converter.py report.docx --relative-images --skip-toc
```

### 详细步骤

1. **检查环境**
```bash
python scripts/converter.py --status
```

2. **如果 pandoc 缺失**
```bash
python scripts/converter.py report.docx --auto-install --relative-images --skip-toc
```

3. **输出结果**
```
report.md          # Markdown 文件
media/
├── image1.png     # 提取的图片
└── image2.png
```

### 关键选项
- `--relative-images`: 提取图片到 media/ 文件夹（推荐）
- `--skip-toc`: 移除目录（Markdown 无页码）
- `--auto-install`: 自动安装 pandoc

### 常见问题

**Q: 图片没有提取？**
A: 添加 `--relative-images` 标志

**Q: 目录还在？**
A: 添加 `--skip-toc` 标志

**Q: 转换失败？**
A: 使用 `-v` 查看详细错误：`python scripts/converter.py report.docx -v --relative-images --skip-toc`

---

## 场景 2: 简单 PDF 转换

**典型需求**: 文本型 PDF 转 Markdown

### 快速命令
```bash
python scripts/converter.py document.pdf --tool pymupdf --relative-images
```

### 工具选择

| 工具 | 何时使用 |
|------|---------|
| `pymupdf` | 简单文本 PDF（推荐，快速） |
| `pandoc` | 基础 PDF 支持 |
| `mineru` | 复杂 PDF（表格/OCR） |

### 详细步骤

1. **判断 PDF 类型**
   - 简单文本 → `--tool pymupdf`
   - 有表格/公式 → `--tool mineru`
   - 扫描版 → `--tool mineru`

2. **转换命令**
```bash
# 简单 PDF（快速）
python scripts/converter.py document.pdf --tool pymupdf --relative-images

# 如果不确定，使用自动检测
python scripts/converter.py document.pdf --tool auto --relative-images
```

3. **验证输出**
```bash
# 检查转换质量
head -n 50 document.md
```

### 关键选项
- `--tool pymupdf`: 轻量级 PDF 工具（快）
- `--tool mineru`: 高级 PDF 工具（准确）
- `--tool auto`: 自动选择

---

## 场景 3: PDF 复杂表格提取

**典型需求**: 从财务报告提取复杂表格

### 快速命令
```bash
python scripts/converter.py financial-report.pdf --tool mineru --relative-images
```

### 为什么用 MinerU？
- ✅ 复杂表格结构识别
- ✅ 合并单元格处理
- ✅ 嵌套表格支持
- ✅ 表头识别

### 详细步骤

1. **安装 MinerU**
```bash
# 需要 Python 3.10-3.12
pip install mineru
```

2. **转换**
```bash
python scripts/converter.py financial-report.pdf --tool mineru --relative-images --skip-toc
```

3. **验证表格**
```bash
# 查看表格是否正确转换
grep -A 5 "^|" financial-report.md
```

### 表格质量检查

如果表格不完整：
```bash
# 尝试增加详细输出
python scripts/converter.py financial-report.pdf --tool mineru -v --relative-images
```

### 关键选项
- `--tool mineru`: 必须使用 MinerU
- `--skip-toc`: 移除目录
- `-v`: 详细模式（调试）

---

## 场景 4: 扫描版 PDF（OCR 识别）

**典型需求**: 老旧扫描文档转可编辑 Markdown

### 快速命令
```bash
python scripts/converter.py old-scan.pdf --tool mineru --relative-images
```

### MinerU OCR 特性
- 自动检测扫描内容
- 多语言支持（中英文）
- 保留文档布局

### 详细步骤

1. **确认是扫描版**
```bash
# 如果 PDF 打开后是图片，就是扫描版
file old-scan.pdf
```

2. **安装 MinerU**
```bash
pip install mineru  # Python 3.10-3.12
```

3. **转换**
```bash
python scripts/converter.py old-scan.pdf --tool mineru --relative-images
```

4. **验证 OCR 质量**
```bash
# 检查识别的文本
cat old-scan.md | head -n 50
```

### OCR 优化提示

**中文文档**:
```bash
# MinerU 自动支持中文 OCR
python scripts/converter.py chinese-scan.pdf --tool mineru --relative-images
```

**低质量扫描**:
- MinerU 会自动增强图像
- 如果效果不好，考虑先用图像处理工具增强

### 关键选项
- `--tool mineru`: OCR 必需
- `--relative-images`: 保留原始图像

---

## 场景 5: 批量转换文档

**典型需求**: 转换整个文档目录

### 快速命令
```bash
python scripts/converter.py "./docs/*.docx" -o ./markdown/ --relative-images --skip-toc
```

### 批量模式

| 需求 | 命令 |
|------|------|
| 单一格式 | `"./docs/*.docx"` |
| 多种格式 | `"./docs/*"` |
| 递归目录 | 使用 `**/*.docx` (需要 shell 支持) |

### 详细步骤

1. **查看要转换的文件**
```bash
# 列出匹配的文件
ls docs/*.docx
```

2. **批量转换**
```bash
python scripts/converter.py "./docs/*.docx" -o ./markdown/ --relative-images --skip-toc
```

3. **检查结果**
```bash
# 查看转换统计
ls -l markdown/*.md | wc -l
```

### 批量转换报告

转换完成后会显示：
```
============================================================
Conversion Summary
============================================================
[OK] Success: 15
[FAIL] Failed:  2
[SKIP] Skipped: 0

Failed files:
  - docs/bad-file.docx: Conversion failed
```

### 处理失败文件

```bash
# 重新转换失败文件，使用详细模式
python scripts/converter.py docs/bad-file.docx -v --relative-images --skip-toc
```

### 关键选项
- Glob 模式: `"./docs/*.docx"`
- 输出目录: `-o ./markdown/`
- 失败继续: 默认跳过失败文件

---

## 场景 6: 便携模式

**典型需求**: 在不同电脑间同步使用，无需重复安装

### 快速命令
```bash
# 首次使用，自动下载 pandoc
python scripts/converter.py document.docx --auto-install --relative-images

# 之后使用，直接转换
python scripts/converter.py document.docx --relative-images
```

### 便携模式原理

```
doc2md/
├── bin/
│   └── pandoc/          # ← 自动下载到这里
│       └── pandoc.exe
├── scripts/
└── ...
```

优先级：
1. 便携版 `bin/pandoc/` （优先）
2. 系统 pandoc （降级）

### 详细步骤

1. **首次使用 - 自动安装**
```bash
python scripts/converter.py --status
python scripts/converter.py document.docx --auto-install --relative-images
```

2. **同步到其他机器**
```bash
# 将整个 doc2md/ 目录复制到新机器
# bin/pandoc/ 会一并复制，无需重新安装
```

3. **在新机器使用**
```bash
python scripts/converter.py another.docx --relative-images
```

### 云同步

将以下目录加入云同步：
```
doc2md/
├── bin/        # ← 便携工具
├── scripts/    # ← 脚本
└── .venv/      # ← 虚拟环境（可选）
```

### 检查便携状态
```bash
python scripts/converter.py --status
```

输出：
```
=== Doc2Md Runtime Status ===
Pandoc: ✓ E:\skills\doc2md\bin\pandoc\pandoc.exe
  Version: pandoc 3.1.11
```

### 关键选项
- `--auto-install`: 自动下载便携版
- `--status`: 查看运行时状态

---

## 场景 7: 创建单文件分享

**典型需求**: 转换后需要单文件分享（图片嵌入）

### 快速命令
```bash
python scripts/converter.py presentation.pptx --embed-images --skip-toc
```

### 图片处理对比

| 方式 | 命令 | 结果 | 适用场景 |
|------|------|------|---------|
| 相对路径 | `--relative-images` | `.md` + `media/` 文件夹 | 需要编辑图片 |
| Base64 嵌入 | `--embed-images` | 单个 `.md` 文件 | 分享、存档 |

### 详细步骤

1. **转换并嵌入图片**
```bash
python scripts/converter.py presentation.pptx --embed-images --skip-toc
```

2. **验证嵌入**
```bash
# 检查是否有 data:image
grep "data:image" presentation.md
```

3. **文件大小对比**
```bash
# 相对路径模式
ls -lh presentation.md         # 小
du -sh media/                  # 图片单独存储

# 嵌入模式
ls -lh presentation.md         # 大（包含图片）
```

### 注意事项

**优点**:
- ✅ 单文件，易分享
- ✅ 无外部依赖

**缺点**:
- ❌ 文件较大
- ❌ 图片难编辑
- ❌ Git 不友好

### 推荐使用场景

- ✅ 发送邮件附件
- ✅ 上传到文档系统
- ✅ 存档单个文件

**不推荐**:
- ❌ 版本控制（Git）
- ❌ 需要编辑图片
- ❌ 文档网站

### 关键选项
- `--embed-images`: 嵌入图片
- `--skip-toc`: 移除目录

---

## 场景 8: 学术论文转换

**典型需求**: PDF 论文转 Markdown，保留公式和引用

### 快速命令
```bash
python scripts/converter.py paper.pdf --tool mineru --relative-images --skip-toc
```

### 为什么用 MinerU？

- ✅ LaTeX 公式识别
- ✅ 参考文献格式保留
- ✅ 复杂表格处理
- ✅ 图表标题识别

### 详细步骤

1. **安装 MinerU**
```bash
pip install mineru  # Python 3.10-3.12
```

2. **转换论文**
```bash
python scripts/converter.py paper.pdf --tool mineru --relative-images --skip-toc
```

3. **检查公式**
```bash
# 查看公式是否正确转换
grep -E "\$.*\$" paper.md
```

### 质量检查清单

- [ ] 标题和作者信息
- [ ] 摘要完整
- [ ] 公式可读
- [ ] 表格结构
- [ ] 参考文献列表
- [ ] 图表清晰

### 处理特殊内容

**公式识别失败**:
```bash
# 尝试增加详细输出
python scripts/converter.py paper.pdf --tool mineru -v --relative-images
```

**图表质量差**:
- MinerU 会提取原始图像
- 检查 `media/` 文件夹中的图片

### 关键选项
- `--tool mineru`: 学术论文必需
- `--skip-toc`: 移除目录
- `--relative-images`: 保留图表

---

## 场景 9: 混合格式批量转换

**典型需求**: 目录中有 DOCX、PDF、EPUB 等多种格式

### 快速命令
```bash
python scripts/converter.py "./mixed-docs/*" -o ./markdown/ --tool auto --relative-images --skip-toc
```

### 工具自动选择

`--tool auto` 会根据文件类型自动选择：
- PDF → MinerU（如果可用）或 PyMuPDF 或 Pandoc
- DOCX/EPUB/HTML → Pandoc
- 其他 → Pandoc

### 详细步骤

1. **查看混合文件**
```bash
ls mixed-docs/
# document.docx  report.pdf  book.epub  slides.pptx
```

2. **批量转换（自动工具选择）**
```bash
python scripts/converter.py "./mixed-docs/*" -o ./markdown/ --tool auto --relative-images --skip-toc
```

3. **查看转换结果**
```bash
ls markdown/
# document.md  report.md  book.md  slides.md
```

### 转换报告

```
============================================================
Conversion Summary
============================================================
[OK] Success: 4
[FAIL] Failed:  0
[SKIP] Skipped: 0
```

### 性能考虑

混合格式批量转换：
- Pandoc 处理非 PDF（快）
- MinerU/PyMuPDF 处理 PDF（较慢）
- 总体时间取决于 PDF 数量和复杂度

### 优化建议

**如果 PDF 很多**:
```bash
# 先转换非 PDF（快）
python scripts/converter.py "./mixed-docs/*.{docx,epub,html}" -o ./markdown/ --relative-images --skip-toc

# 再转换 PDF（慢）
python scripts/converter.py "./mixed-docs/*.pdf" -o ./markdown/ --tool auto --relative-images --skip-toc
```

### 关键选项
- `"./mixed-docs/*"`: 匹配所有文件
- `--tool auto`: 自动选择工具
- `-o ./markdown/`: 统一输出目录

---

## 🎯 快速决策表

| 你的需求 | 使用命令 |
|---------|---------|
| Word 文档 | `python scripts/converter.py file.docx --relative-images --skip-toc` |
| 简单 PDF | `python scripts/converter.py file.pdf --tool pymupdf --relative-images` |
| 复杂 PDF（表格/OCR） | `python scripts/converter.py file.pdf --tool mineru --relative-images` |
| 批量转换 | `python scripts/converter.py "./docs/*" -o ./output/ --relative-images --skip-toc` |
| 单文件分享 | `python scripts/converter.py file.docx --embed-images --skip-toc` |
| 首次使用 | `python scripts/converter.py file.docx --auto-install --relative-images --skip-toc` |

---

## 📚 相关文档

- **详细用法**: `references/usage.md`
- **安装指南**: `references/installation.md`
- **故障排查**: `references/troubleshooting.md`
- **便携模式**: `references/portable.md`
- **AI 快速参考**: `references/ai-quick-reference.md`
