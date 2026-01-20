# Doc2Md - Document to Markdown Converter

Convert 40+ document formats to Markdown using Pandoc, MinerU, and PyMuPDF.

## Features

### Pandoc (Universal Converter)
- **Formats**: DOCX, DOC, ODT, RTF, EPUB, PDF, HTML, PPTX, LaTeX, and 30+ more
- **Fast** conversion for standard documents
- **Preserves** structure: headings, tables, lists, formatting
- **Batch processing** with glob patterns

### MinerU (Advanced PDF Parser)
- **OCR support** for scanned PDFs
- **Intelligent table extraction** - complex table structures preserved
- **Formula parsing** - LaTeX formulas converted to readable format
- **Layout recognition** - detects document structure automatically
- **Multi-language** support (Chinese, English, and more)

### PyMuPDF (Lightweight PDF Parser)
- **Lightweight** and fast PDF conversion
- **Python 3.14+ compatible** - works with latest Python versions
- **Text extraction** from text-based PDFs
- **Basic layout detection** - headings and paragraphs
- **Image extraction** support

## Image Handling Options

| Option | Description | Use Case |
|--------|-------------|----------|
| `--relative-images` | Extract images to `media/` folder with relative paths | Default option - keeps file size small, images editable |
| `--embed-images` | Embed images as Base64 in Markdown | Self-contained files, no external dependencies |
| `--extract-media` | Same as `--relative-images` | Legacy alias |

### Comparison

```bash
# Relative paths (recommended)
python scripts/converter.py document.docx --relative-images
# Result: document.md + media/image1.png, media/image2.png
# Pros: Small .md file, images can be edited separately

# Base64 embedded
python scripts/converter.py document.docx --embed-images
# Result: document.md (with images encoded inside)
# Pros: Single self-contained file, easy to share
# Cons: Larger file size, images harder to extract
```

## Installation

### Pandoc (Required for non-PDF formats)
```bash
# Windows
choco install pandoc

# macOS
brew install pandoc

# Linux
sudo apt-get install pandoc  # Debian/Ubuntu
sudo yum install pandoc      # RHEL/CentOS
```

### MinerU (Optional, for advanced PDF processing)
```bash
pip install mineru
# Requires Python 3.10-3.12
```

### PyMuPDF (Optional, for lightweight PDF processing)
```bash
pip install PyMuPDF
# Compatible with Python 3.14+
```

## Quick Start

```bash
# Basic conversion
python scripts/converter.py document.docx

# Convert with relative image paths
python scripts/converter.py document.docx --relative-images

# Convert with embedded images (self-contained)
python scripts/converter.py document.docx --embed-images

# Remove table of contents (recommended)
python scripts/converter.py document.docx --skip-toc --relative-images

# Convert PDF with MinerU (best for tables/OCR)
python scripts/converter.py document.pdf --tool mineru --relative-images

# Convert PDF with PyMuPDF (lightweight, Python 3.14+)
python scripts/converter.py document.pdf --tool pymupdf --relative-images

# Batch convert
python scripts/converter.py "./docs/*.pdf" -o ./output/ --relative-images
```

## Tool Selection

| Use Case | Recommended Tool |
|----------|-----------------|
| Word, EPUB, HTML, other formats | **Pandoc** |
| Standard PDFs (text-based) | PyMuPDF or Pandoc |
| Scanned PDFs / PDFs with OCR | **MinerU** |
| Complex table extraction | **MinerU** |
| Academic papers with formulas | **MinerU** |
| Python 3.14+ compatibility | **PyMuPDF** |

## Command-Line Options

```
positional arguments:
  inputs                Files or directories to convert

optional arguments:
  -h, --help            Show help message
  -o DIR, --output DIR  Output directory
  --tool {auto,pandoc,mineru,pymupdf}
                        Conversion tool (default: auto)
  -v, --verbose         Enable detailed output
  --skip-toc            Remove table of contents
  --extract-media       Extract images to media folder (alias for --relative-images)
  --relative-images     Keep images as relative paths (recommended)
  --embed-images        Embed images as Base64 (self-contained)
```

## Examples

### Word Documents
```bash
# Convert with relative image paths
python scripts/converter.py report.docx --relative-images --skip-toc

# Convert with embedded images
python scripts/converter.py report.docx --embed-images --skip-toc
```

### PDF Documents
```bash
# Standard PDF with Pandoc
python scripts/converter.py document.pdf --relative-images

# Scanned PDF with MinerU (OCR)
python scripts/converter.py scanned.pdf --tool mineru --relative-images

# Simple PDF with PyMuPDF (fast, lightweight)
python scripts/converter.py document.pdf --tool pymupdf --relative-images

# Academic paper with formulas
python scripts/converter.py paper.pdf --tool mineru --embed-images
```

### Presentations
```bash
# PowerPoint with images
python scripts/converter.py presentation.pptx --relative-images
```

### Batch Processing
```bash
# Convert all documents in a directory
python scripts/converter.py "./documents/*.docx" -o ./output/ --relative-images

# Convert mixed formats
python scripts/converter.py docs/* -o ./markdown/ --relative-images --skip-toc
```

## Output Structure

### Using --relative-images
```
output/
├── document.md          # Markdown with ![alt](media/image1.png)
└── media/
    ├── image1.png
    └── image2.png
```

### Using --embed-images
```
output/
└── document.md          # Markdown with ![alt](data:image/png;base64,...)
```

## Troubleshooting

### Images not appearing
- **Missing images**: Add `--relative-images` or `--extract-media` flag
- **Check media folder**: Ensure images were extracted to `media/` directory
- **Path issues**: Verify relative paths are correct

### Conversion fails
- **"Pandoc not found"**: Install Pandoc using package manager
- **"MinerU not found"**: Run `pip install mineru` (requires Python 3.10-3.12)
- **"PyMuPDF not found"**: Run `pip install PyMuPDF` (compatible with Python 3.14+)
- **Use verbose mode**: Add `-v` flag for detailed error messages

### PDF issues
- **Blank output**: Use `--tool mineru` for scanned PDFs or `--tool pymupdf` for text PDFs
- **Table issues**: Try `--tool mineru` for better table extraction
- **Chinese content**: Use `--tool mineru` for better multi-language support
- **Python 3.14 compatibility**: Use `--tool pymupdf` for PDF processing

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
