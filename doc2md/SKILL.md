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
| Standard PDFs (text-based) | PyMuPDF or Pandoc |
| Scanned PDFs / PDFs with OCR | **MinerU** |
| Complex table extraction | **MinerU** |
| Academic papers with formulas | **MinerU** |
| Python 3.14+ compatibility | **PyMuPDF** |
| Batch mixed formats | Pandoc (auto-detects) |

## Quick Start

```bash
# Install Pandoc (for 40+ formats)
choco install pandoc  # Windows
brew install pandoc   # macOS
sudo apt-get install pandoc  # Linux

# Install MinerU (for advanced PDF processing)
pip install mineru  # Python 3.10-3.12 required

# Install PyMuPDF (lightweight PDF alternative, Python 3.14+ compatible)
pip install PyMuPDF

# Convert a document with Pandoc
python scripts/converter.py document.docx

# Convert a PDF with MinerU (best for tables, OCR)
python scripts/converter.py document.pdf --tool mineru

# Convert a PDF with PyMuPDF (lightweight, Python 3.14+)
python scripts/converter.py document.pdf --tool pymupdf

# Portable mode: auto-download pandoc if not found
python scripts/converter.py document.docx --auto-install

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
| `--auto-install` | Auto-download portable pandoc to `bin/` if not found |
| `--status` | Show runtime status (pandoc, mineru availability) |
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

### PyMuPDF (Lightweight PDF)
- **Lightweight**: Fast and simple PDF parsing
- **Python 3.14+ compatible**: Works with latest Python versions
- **Text extraction**: Extracts text from text-based PDFs
- **Basic layout**: Detects headings and paragraphs
- **Image extraction**: Extracts images to media folder
- **No complex dependencies**: Simple pip install

## Workflow

1. User provides document path(s)
2. Detect file format - PDFs can use Pandoc or MinerU
3. Check tool availability (provide installation instructions if needed)
4. Run appropriate converter with options
5. Post-process: remove TOC, embed images
6. Return converted .md file(s)

## Important Notes

- **Tool requirements**: At least one tool (Pandoc, MinerU, or PyMuPDF) must be installed
  - Pandoc: Required for non-PDF formats. Can be system-installed OR use `--auto-install` for portable version
  - MinerU: Optional, for advanced PDF processing. Install with `pip install mineru` (Python 3.10-3.12)
  - PyMuPDF: Optional, for lightweight PDF processing. Install with `pip install PyMuPDF` (Python 3.14+ compatible)
- **Portable mode**: Use `--auto-install` to automatically download pandoc to `bin/` directory
  - Downloaded once, reused across sessions
  - Can be synced to cloud/storage for use across machines
  - Priority: portable bin/ > system pandoc
- **PDF handling**: For PDFs, choose the appropriate tool:
  - **MinerU**: Best for scanned documents, complex tables, formulas, Chinese/mixed-language content
  - **PyMuPDF**: Good for simple text-based PDFs, fast processing, Python 3.14+ compatibility
  - **Pandoc**: Basic PDF support, works on most systems
- **Image handling**:
  - `--relative-images`: Extracts images to media/ folder, keeps relative paths
  - `--embed-images`: Embeds images as Base64, creating self-contained but larger files
  - `--extract-media`: Extracts images (same as --relative-images)
- **TOC removal**: Recommended for Word/PDF documents with tables of contents
- **Error handling**: Continues processing batch operations even if individual files fail

## Troubleshooting

- **"Pandoc not found"**:
  - Option 1: Use `--auto-install` to download portable version automatically
  - Option 2: Install system-wide with `choco/brew/apt install pandoc`
  - Option 3: Check status with `--status`
- **"MinerU not found"**: Install with `pip install mineru` (requires Python 3.10-3.12)
- **"PyMuPDF not found"**: Install with `pip install PyMuPDF` (compatible with Python 3.14+)
- **Conversion fails**: Use `-v` flag to see detailed error messages
- **Images options**:
  - Use `--relative-images` for separate image files in media/ folder
  - Use `--embed-images` for Base64 embedded images
  - Use `--extract-media` (same as `--relative-images`)
- **TOC still present**: Ensure `--skip-toc` flag is used
- **PDF table issues**: Try `--tool mineru` for better table extraction
- **Scanned PDF blank**: Use `--tool mineru` (auto-enables OCR) or `--tool pymupdf` for text PDFs only
- **Python 3.14 compatibility**: Use `--tool pymupdf` for PDF processing with Python 3.14+

For detailed documentation, see `references/usage.md`.
