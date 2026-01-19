---
name: doc2md
description: Convert 40+ document formats to Markdown using Pandoc and MinerU. Supports Word, PDF, EPUB, HTML, PowerPoint, LaTeX, Jupyter, CSV, and more. MinerU provides advanced PDF parsing with OCR, table extraction, and layout recognition. Ideal for documents with tables, images, complex formatting, or scanned PDFs.
---

# Doc2Md - Document to Markdown Converter

Convert documents to Markdown using two powerful tools:
- **Pandoc**: Universal document converter for 40+ formats
- **MinerU**: Advanced PDF parser with OCR and intelligent layout recognition

## Tool Selection

| Use Case | Recommended Tool |
|----------|-----------------|
| Word, EPUB, HTML, other formats | **Pandoc** |
| Standard PDFs (text-based) | Pandoc or MinerU |
| Scanned PDFs / PDFs with OCR | **MinerU** |
| Complex table extraction | **MinerU** |
| Academic papers with formulas | **MinerU** |
| Batch mixed formats | Pandoc (auto-detects) |

## Quick Start

```bash
# Install Pandoc (for 40+ formats)
choco install pandoc  # Windows
brew install pandoc   # macOS
sudo apt-get install pandoc  # Linux

# Install MinerU (for advanced PDF processing)
pip install mineru  # Python package

# Convert a document with Pandoc
python scripts/converter.py document.docx

# Convert a PDF with MinerU (better for tables, OCR)
python scripts/converter.py document.pdf --tool mineru

# Remove table of contents (recommended for Word/PDF)
python scripts/converter.py document.docx --skip-toc

# With images - extract and keep as relative paths
python scripts/converter.py document.docx --relative-images

# With images - embed as Base64 (self-contained)
python scripts/converter.py document.docx --extract-media --embed-images

# Batch convert
python scripts/converter.py "./docs/*.pdf" -o ./output/
```

## When to Use

Use this skill when:
- Converting Word documents (.docx, .doc) to Markdown
- Extracting content from PDFs (especially scanned PDFs)
- Converting EPUB e-books, HTML, or other formats
- Processing documents with complex tables, images, or formulas
- Converting academic papers with mathematical formulas
- Batch converting multiple documents

## Common Options

| Option | Description |
|--------|-------------|
| `--tool {pandoc|mineru}` | Select conversion tool (auto-detect for non-PDF) |
| `--skip-toc` | Remove table of contents (recommended - Markdown has no page numbers) |
| `--extract-media` | Extract images to media/ folder |
| `--embed-images` | Embed images as Base64 (creates self-contained Markdown) |
| `--relative-images` | Keep images as relative paths (implies --extract-media) |
| `-o DIR` | Specify output directory |
| `-v` | Verbose mode |

### MinerU-Specific Options

| Option | Description |
|--------|-------------|
| `--ocr` | Enable OCR for scanned PDFs (auto-detected by MinerU) |
| `--formula-as-text` | Convert LaTeX formulas to text/MathML |
| `--parse-tables` | Enhanced table parsing (default for MinerU) |

## Key Features

### Pandoc (40+ formats)
- **Documents**: DOCX, DOC, ODT, RTF, PDF
- **E-books**: EPUB, FB2
- **Presentations**: PPTX
- **Web**: HTML, XHTML, XML
- **Markdown**: MD, Markdown, RMarkdown, and variants
- **Academic**: LaTeX, TeX
- **Code**: RST, Textile, Org-mode, Jupyter Notebook
- **Data**: CSV, TSV, JSON
- Fast conversion for standard documents
- Preserves structure: headings, tables, lists, formatting
- Image handling: extract to folder or embed as Base64
- Batch processing with glob patterns
- TOC removal in multiple languages

### MinerU (Advanced PDF)
- **Intelligent layout recognition**: Detects document structure automatically
- **OCR support**: Processes scanned PDFs and images
- **Table extraction**: Complex table structures preserved as Markdown
- **Formula parsing**: LaTeX formulas converted to readable format
- **Multi-language**: Supports Chinese, English, and other languages
- **Image extraction**: Preserves images and figure captions

## Workflow

1. User provides document path(s)
2. Detect file format - PDFs can use Pandoc or MinerU
3. Check tool availability (provide installation instructions if needed)
4. Run appropriate converter with options
5. Post-process: remove TOC, embed images
6. Return converted .md file(s)

## Important Notes

- **Tool requirements**: At least one tool (Pandoc or MinerU) must be installed
  - Pandoc: Required for non-PDF formats
  - MinerU: Optional, for advanced PDF processing
- **PDF handling**: For PDFs, MinerU is recommended for:
  - Scanned documents
  - Complex table layouts
  - Mathematical formulas
  - Chinese/mixed-language content
- **Image handling**:
  - `--relative-images`: Extracts images to media/ folder, keeps relative paths
  - `--embed-images`: Embeds images as Base64, creating self-contained but larger files
  - `--extract-media`: Extracts images (same as --relative-images)
- **TOC removal**: Recommended for Word/PDF documents with tables of contents
- **Error handling**: Continues processing batch operations even if individual files fail

## Troubleshooting

- **"Pandoc not found"**: Install pandoc using system package manager
- **"MinerU not found"**: Install with `pip install mineru`
- **Conversion fails**: Use `-v` flag to see detailed error messages
- **Images options**:
  - Use `--relative-images` for separate image files in media/ folder
  - Use `--embed-images` for Base64 embedded images
  - Use `--extract-media` (same as `--relative-images`)
- **TOC still present**: Ensure `--skip-toc` flag is used
- **PDF table issues**: Try `--tool mineru` for better table extraction
- **Scanned PDF blank**: Use `--tool mineru` (auto-enables OCR)

For detailed documentation, see `references/usage.md`.
