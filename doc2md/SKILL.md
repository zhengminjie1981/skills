---
name: doc2md
description: |
  Convert 40+ document formats to Markdown.

  WHEN TO USE: User needs to convert DOCX, PDF, EPUB, HTML, PPTX to Markdown
  TRIGGERS: "convert document", "to markdown", "extract from PDF", "Word to MD"
  CAPABILITIES: OCR, table extraction, image handling, batch processing

allowed-tools: [Bash, Read, Glob]
argument-hint: "<convert|batch> <文件或模式> [选项]"

feedback:
  enabled: true
  version: "1.0.0"
  author: "skills-team"
---

# Doc2Md - Document to Markdown Converter

## 🎯 One-Line Summary
Convert any document to clean Markdown with intelligent tool selection.

## 子功能调用

| 指令 | 说明 |
|------|------|
| `/doc2md convert <文件> [--tool auto\|pandoc\|mineru\|pymupdf]` | 转换单个文档为 Markdown |
| `/doc2md batch <模式> [-o 输出目录]` | 批量转换多个文档 |

**convert 示例**：
```
/doc2md convert report.docx
/doc2md convert document.pdf --tool mineru
```

**batch 示例**：
```
/doc2md batch "./docs/*.docx"
/doc2md batch "./files/*.pdf" -o ./markdown/
```

## 🤖 AI Agent Quick Reference

### Decision Tree (3 steps)
```
Is it a PDF?
├─ YES → Does it have tables/formulas/scanned content?
│         ├─ YES → Use --tool mineru
│         └─ NO  → Use --tool pymupdf (or pandoc)
└─ NO  → Use --tool pandoc (default)
```

### Most Common Commands

```bash
# Pattern 1: Standard Word Document (80% of cases)
python scripts/converter.py document.docx --relative-images --skip-toc

# Pattern 2: Complex PDF (tables/OCR/formulas)
python scripts/converter.py document.pdf --tool mineru --relative-images

# Pattern 3: Simple PDF (fast)
python scripts/converter.py document.pdf --tool pymupdf --relative-images

# Pattern 4: Batch Convert
python scripts/converter.py "./docs/*.docx" -o ./output/ --relative-images --skip-toc
```

## 📋 Tool Selection Matrix

| File Type | Tool | Command Flag | Why |
|-----------|------|-------------|-----|
| Word/EPUB/HTML | `pandoc` | (default) | Native support |
| Scanned PDF | `mineru` | `--tool mineru` | OCR required |
| PDF with tables | `mineru` | `--tool mineru` | Better extraction |
| Simple PDF | `pymupdf` | `--tool pymupdf` | Fast & light |
| Python 3.14+ | `pymupdf` | `--tool pymupdf` | Compatibility |

## ⚡ Quick Start

### Step 1: Check Environment
```bash
python scripts/converter.py --status
```

### Step 2: Convert (with auto-setup)
```bash
# If pandoc missing, add --auto-install
python scripts/converter.py document.docx --auto-install --relative-images --skip-toc
```

## 🚨 Common Issues & Quick Fixes

| Issue | Solution | Command |
|-------|----------|---------|
| "Pandoc not found" | Auto-install | Add `--auto-install` |
| "MinerU not found" | Install package | `pip install mineru` (Python 3.10-3.12) |
| "PyMuPDF not found" | Install package | `pip install PyMuPDF` |
| Images missing | Extract images | Add `--relative-images` |
| TOC still present | Remove TOC | Add `--skip-toc` |
| PDF blank output | Use OCR tool | Add `--tool mineru` |
| Conversion slow | Use fast tool | Add `--tool pymupdf` |

## 💡 AI Agent Notes

### Safe Defaults (Always Use)
- `--relative-images` - Extract images to media/ folder (editable)
- `--skip-toc` - Remove TOC for Word/PDF (Markdown has no pages)
- `--tool auto` - Auto-select for mixed batches

### Typical Workflow
```
1. Check status: python scripts/converter.py --status
2. If pandoc missing: add --auto-install
3. Convert with safe defaults: --relative-images --skip-toc
4. For PDFs: specify tool (mineru or pymupdf)
5. If fails: use -v flag and check error
```

### Red Flags (Special Handling)
- User mentions "scanned", "OCR", "tables" → use `--tool mineru`
- User wants "single file" → use `--embed-images`
- User needs "portable" → use `--auto-install`
- Python 3.14+ environment → use `--tool pymupdf` for PDF

## 🔍 When to Load Detailed Docs

Load these **ONLY when needed** (avoid context pollution):

- **Installation issues?** → `references/installation.md`
- **Need more examples?** → `references/scenarios.md`
- **Conversion failed?** → `references/troubleshooting.md`
- **Portable mode?** → `references/portable.md`
- **AI quick ref?** → `references/ai-quick-reference.md`

## 📦 Options Reference

### Essential Options (Most Used)
```
--relative-images          Extract images to media/ (recommended)
--skip-toc                 Remove table of contents
--tool {auto|pandoc|mineru|pymupdf}  Select converter
-o DIR                     Output directory
```

### Convenience Options
```
--auto-install             Auto-download pandoc if missing
--status                   Check runtime status
-v                         Verbose mode (debugging)
```

### Advanced Options
```
--embed-images             Embed as Base64 (single file)
```

## 📚 Supported Formats (40+)

**Common:** `.docx`, `.doc`, `.pdf`, `.epub`, `.html`, `.pptx`, `.txt`
**Academic:** `.tex`, `.latex`, `.rst`, `.ipynb`
**Data:** `.csv`, `.tsv`, `.json`, `.xml`

Full list: see `scripts/converter.py` → `SUPPORTED_FORMATS`

## 🎓 Examples by Scenario

### Scenario 1: Word Document
```bash
python scripts/converter.py report.docx --relative-images --skip-toc
```
**Output:** `report.md` + `media/` folder with images

### Scenario 2: Complex PDF (tables/OCR)
```bash
python scripts/converter.py financial-report.pdf --tool mineru --relative-images
```
**Why mineru:** Better table extraction and OCR support

### Scenario 3: Simple PDF (fast)
```bash
python scripts/converter.py document.pdf --tool pymupdf --relative-images
```
**Why pymupdf:** Fast and lightweight for text-based PDFs

### Scenario 4: Batch Convert
```bash
python scripts/converter.py "./docs/*.docx" -o ./markdown/ --relative-images --skip-toc
```
**Result:** All .docx files converted to ./markdown/

### Scenario 5: Single File (embedded images)
```bash
python scripts/converter.py presentation.pptx --embed-images --skip-toc
```
**Result:** Single .md file with Base64 images (easy to share)

### Scenario 6: First Time Setup
```bash
# Check what's available
python scripts/converter.py --status

# Auto-install pandoc
python scripts/converter.py document.docx --auto-install --relative-images --skip-toc
```

## 📊 Performance Guide

| Tool | Speed | Best For |
|------|-------|----------|
| `pandoc` | Fast | Non-PDF formats |
| `pymupdf` | Fast | Simple PDFs |
| `mineru` | Slow | Complex PDFs (OCR, tables, formulas) |

**Tip:** When in doubt, use `--tool auto` for automatic selection.

## 🔄 Typical Agent Workflow

```python
# Pseudocode for AI agents

def convert_document(file_path, user_requirements):
    # 1. Check environment
    status = run("python scripts/converter.py --status")

    # 2. Determine tool
    if file_path.endswith('.pdf'):
        if has_requirements(['scanned', 'ocr', 'tables', 'formulas']):
            tool = 'mineru'
        else:
            tool = 'pymupdf'
    else:
        tool = 'pandoc'  # default

    # 3. Build command
    cmd = f"python scripts/converter.py {file_path}"
    cmd += f" --tool {tool}"
    cmd += " --relative-images --skip-toc"

    if not has_pandoc(status):
        cmd += " --auto-install"

    # 4. Execute
    result = run(cmd)

    # 5. Handle errors
    if result.failed:
        if "not found" in result.error:
            return install_and_retry(tool, cmd)
        return debug_with_verbose(file_path, tool)

    return result
```

## ✅ Pre-Flight Checklist

Before conversion, ensure:

- [ ] Pandoc available (check with `--status` or use `--auto-install`)
- [ ] For PDF with MinerU: `pip install mineru` (Python 3.10-3.12)
- [ ] For PDF with PyMuPDF: `pip install PyMuPDF` (Python 3.14+)
- [ ] Input file exists
- [ ] Output directory specified (or will use same directory)

---

## 📖 Full Documentation

For comprehensive guides, see the `references/` directory:

- **`ai-quick-reference.md`** - AI agent optimized guide
- **`scenarios.md`** - Usage scenarios with examples
- **`usage.md`** - Complete usage documentation
- **`installation.md`** - Installation guide
- **`troubleshooting.md`** - Problem solving
- **`portable.md`** - Portable mode guide

---

**Remember:**
1. Start with safe defaults: `--relative-images --skip-toc`
2. Use `--tool mineru` for complex PDFs
3. Use `--status` to check environment
4. Use `--auto-install` for automatic setup

---

## 反馈机制

本 skill 支持自动反馈改进。

<!-- FEEDBACK-TRIGGER-START -->
<feedback-config>
{
  "triggers": ["execution_failure", "conversion_error", "ocr_failure"],
  "collect": ["error_type", "document_format", "environment", "skill_version"],
  "sanitize": ["file_paths", "document_content", "user_data"]
}
</feedback-config>
<!-- FEEDBACK-TRIGGER-END -->

执行完成后，如检测到改进机会且用户已授权，将自动发送脱敏反馈。
