# AI Agent Quick Reference

> This file is optimized for AI agents. Keep it minimal and actionable.

## 🎯 Purpose

Convert documents (DOCX, PDF, EPUB, HTML, etc.) to Markdown format.

## 🤖 Decision Flow

```
User says: "convert [document]"
    ↓
Check file type
    ├─ .pdf → Has complex content (tables/OCR/formulas)?
    │         ├─ YES → Use --tool mineru
    │         └─ NO  → Use --tool pymupdf
    ├─ .docx, .epub, .html → Use default (pandoc)
    └─ Other → Check SUPPORTED_FORMATS in converter.py

Always add:
    --relative-images  (unless user wants single file)
    --skip-toc         (for Word/PDF with TOC)
```

## ⚡ Common Commands

### Before Starting
```bash
# Check environment
python scripts/converter.py --status

# Auto-setup if needed
python scripts/converter.py --auto-install
```

### Standard Conversions
```bash
# Word document
python scripts/converter.py report.docx --relative-images --skip-toc

# PDF (simple)
python scripts/converter.py document.pdf --tool pymupdf --relative-images

# PDF (complex - tables/OCR)
python scripts/converter.py scan.pdf --tool mineru --relative-images

# Batch
python scripts/converter.py "./docs/*.docx" -o ./output/ --relative-images --skip-toc
```

## 🚨 Error Handling

| Error | Fix |
|-------|-----|
| Pandoc not found | Add `--auto-install` |
| MinerU not found | `pip install mineru` (Python 3.10-3.12) |
| PyMuPDF not found | `pip install PyMuPDF` |
| Images not extracted | Add `--relative-images` |
| TOC still present | Add `--skip-toc` |
| PDF output empty | Try `--tool mineru` |
| Conversion slow | Use `--tool pymupdf` for simple PDFs |

## 📊 Tool Selection Cheat Sheet

| File Type | Recommended Tool | Reason |
|-----------|-----------------|--------|
| `.docx`, `.doc`, `.odt`, `.rtf` | `pandoc` (default) | Native support |
| `.epub`, `.html`, `.pptx` | `pandoc` (default) | Native support |
| `.pdf` (scanned) | `mineru` | OCR support |
| `.pdf` (tables) | `mineru` | Better extraction |
| `.pdf` (formulas) | `mineru` | LaTeX parsing |
| `.pdf` (simple text) | `pymupdf` | Fast & light |
| Mixed batch | `auto` | Auto-detect |

## 💡 AI-Specific Tips

### When to Ask User
- If PDF and unsure about complexity → "Does the PDF have tables, formulas, or is it scanned?"
- If user wants single file → "Do you want images embedded (single file) or separate (editable)?"

### Safe Defaults
- Always use `--relative-images` (best for editing)
- Always use `--skip-toc` for Word/PDF (Markdown has no pages)
- Use `--tool auto` when in doubt

### Performance Considerations
- MinerU: Slower but more accurate (good for complex PDFs)
- PyMuPDF: Fast and lightweight (good for simple PDFs)
- Pandoc: Fast for non-PDF formats

### Verbose Mode
If conversion fails, re-run with `-v` flag to get detailed error:
```bash
python scripts/converter.py document.docx -v --relative-images --skip-toc
```

## 📚 Documentation Map

Load these ONLY when needed:

- `references/installation.md` - If setup/installation issues
- `references/usage.md` - If user needs advanced options
- `references/troubleshooting.md` - If conversion fails
- `references/portable.md` - If user needs portable/cross-machine setup

## 🔄 Typical Agent Workflow

```python
# 1. Check environment
run("python scripts/converter.py --status")

# 2. If pandoc missing
if "not found" in status:
    run("python scripts/converter.py --auto-install")

# 3. Determine tool
tool = "auto"  # default
if file.endswith('.pdf'):
    if user_mentions(['scanned', 'ocr', 'tables', 'formulas']):
        tool = "mineru"
    else:
        tool = "pymupdf"  # or pandoc

# 4. Build command
cmd = f"python scripts/converter.py {file} --tool {tool} --relative-images --skip-toc"

# 5. Execute
result = run(cmd)

# 6. If failed, check error and retry
if result.failed:
    if "MinerU not found" in result.error:
        inform_user("Installing MinerU...")
        run("pip install mineru")
        run(cmd)  # retry
```

## 🎓 Supported Formats (40+)

**Common:** `.docx`, `.doc`, `.pdf`, `.epub`, `.html`, `.pptx`, `.txt`
**Academic:** `.tex`, `.latex`, `.rst`, `.ipynb`
**Data:** `.csv`, `.tsv`, `.json`, `.xml`
**Others:** `.odt`, `.rtf`, `.fb2`, `.org`, `.wiki`

Full list in `scripts/converter.py` → `SUPPORTED_FORMATS`

## ✅ Pre-Flight Checklist

Before conversion, ensure:

- [ ] Pandoc available (or use `--auto-install`)
- [ ] For PDF with MinerU: `pip install mineru` (Python 3.10-3.12)
- [ ] For PDF with PyMuPDF: `pip install PyMuPDF` (Python 3.14+)
- [ ] Input file exists and is readable
- [ ] Output directory exists (or will be created)

## 🚀 Quick Examples

```bash
# Example 1: Simple Word document
python scripts/converter.py report.docx --relative-images --skip-toc

# Example 2: Scanned PDF
python scripts/converter.py old-scan.pdf --tool mineru --relative-images

# Example 3: Complex PDF with tables
python scripts/converter.py financial-report.pdf --tool mineru --relative-images --skip-toc

# Example 4: Batch convert docs
python scripts/converter.py "./documents/*.docx" -o ./markdown/ --relative-images --skip-toc

# Example 5: Create single file with embedded images
python scripts/converter.py presentation.pptx --embed-images --skip-toc
```

---
**Remember:** Start simple, add complexity only when needed.
