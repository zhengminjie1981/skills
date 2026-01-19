# Doc2Md - Usage Guide

Complete guide for converting documents to Markdown using Pandoc and MinerU.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Tool Selection](#tool-selection)
- [Supported Formats](#supported-formats)
- [Command-Line Options](#command-line-options)
- [Advanced Usage](#advanced-usage)
- [MinerU-Specific Features](#mineru-specific-features)
- [Examples](#examples)
- [Output Format](#output-format)

## Basic Usage

### Convert a Single File

The simplest usage - convert a document in the current directory:

```bash
python scripts/converter.py document.docx
```

Output: `document.md` in the same directory.

### Specify Output Directory

Save converted files to a specific directory:

```bash
python scripts/converter.py document.pdf -o ./markdown/
```

Output: `./markdown/document.md`

### Choose Conversion Tool

Select which tool to use for conversion:

```bash
# Auto-detect (MinerU for PDFs if available, Pandoc otherwise)
python scripts/converter.py document.pdf --tool auto

# Use Pandoc for all files
python scripts/converter.py document.pdf --tool pandoc

# Use MinerU for PDFs (Pandoc for other formats)
python scripts/converter.py document.pdf --tool mineru
```

## Tool Selection

### When to Use Each Tool

| Scenario | Recommended Tool | Why |
|----------|-----------------|-----|
| Word, EPUB, HTML documents | Pandoc | Native format support |
| Standard text-based PDFs | Pandoc or MinerU | Both work well |
| Scanned PDFs | MinerU | OCR support |
| PDFs with complex tables | MinerU | Better table extraction |
| Academic papers with formulas | MinerU | LaTeX formula parsing |
| Chinese/mixed-language PDFs | MinerU | Better multi-language support |
| Batch conversion (mixed formats) | Pandoc | Faster for simple docs |

### Tool Comparison

| Feature | Pandoc | MinerU |
|---------|--------|--------|
| Speed | Fast | Slower |
| Formats | 40+ | PDF only |
| OCR | No | Yes |
| Table extraction | Basic | Advanced |
| Formula parsing | Basic | LaTeX |
| Scanned PDF support | No | Yes |

## Supported Formats

### Word Processing
| Format | Extensions | Notes |
|--------|------------|-------|
| Word | `.docx`, `.doc` | Best format support |
| OpenDocument | `.odt` | OpenOffice/LibreOffice |
| Rich Text | `.rtf` | Basic formatting |

### PDF & E-books
| Format | Extensions | Notes |
|--------|------------|-------|
| PDF | `.pdf` | Pandoc: text extraction / MinerU: OCR + tables |
| EPUB | `.epub` | E-book format |
| FictionBook 2 | `.fb2` | E-book format |

### Presentations
| Format | Extensions | Notes |
|--------|------------|-------|
| PowerPoint | `.pptx` | Via pandoc filters |

### Web & Markup
| Format | Extensions | Notes |
|--------|------------|-------|
| HTML | `.html`, `.htm`, `.xhtml` | Web pages |
| XML | `.xml` | Structured markup |
| Wiki | `.wiki`, `.mediawiki` | Mediawiki format |
| OPML | `.opml` | Outline processor |

### Markdown Variants
| Format | Extensions | Notes |
|--------|------------|-------|
| Markdown | `.md`, `.markdown`, `.mdown`, `.mkd`, `.mkdn`, `.mdwn`, `.mdtext` | Various extensions |
| R Markdown | `.rmarkdown` | R document format |

### Text & Code
| Format | Extensions | Notes |
|--------|------------|-------|
| Plain Text | `.txt`, `.text` | Simple conversion |
| LaTeX | `.tex`, `.latex`, `.ltx` | Academic/Scientific |
| reStructuredText | `.rst` | Python documentation |
| Textile | `.textile` | Markup language |
| Org-mode | `.org` | Emacs organizer |

### Data & Notebooks
| Format | Extensions | Notes |
|--------|------------|-------|
| CSV | `.csv` | Tabular data |
| TSV | `.tsv` | Tab-separated values |
| JSON | `.json` | Structured data |
| Jupyter Notebook | `.ipynb` | Python notebooks |

**Total: 40+ formats supported by Pandoc**

## Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `inputs` | Files or directories to convert (required) | `document.docx` |
| `--tool {auto,pandoc,mineru}` | Conversion tool to use | `--tool mineru` |
| `-o, --output DIR` | Output directory | `-o ./output/` |
| `-v, --verbose` | Enable detailed output | `--verbose` |
| `--extract-media` | Extract images to media folder | `--extract-media` |
| `--embed-images` | Embed images as Base64 | `--embed-images` |
| `--skip-toc` | Remove table of contents | `--skip-toc` |

## Advanced Usage

### Remove Table of Contents

Word and PDF documents often contain tables of contents with page numbers. Since Markdown doesn't have page numbers, these should be removed:

```bash
python scripts/converter.py document.docx --skip-toc
```

The `--skip-toc` option automatically detects and removes TOCs in multiple languages:
- English: "Table of Contents", "Contents"
- Chinese: "目录", "索引"
- French: "Table des matières"
- German: "Inhalt"
- Spanish: "Índice"
- And more...

### Extract Images

Extract images from documents to a `media/` folder:

```bash
python scripts/converter.py presentation.pptx --extract-media
```

Output:
- `presentation.md` (Markdown file)
- `presentation.media/` (Extracted images)

### Embed Images as Base64

Create self-contained Markdown files with embedded images:

```bash
python scripts/converter.py document.docx --extract-media --embed-images
```

Images are converted to Base64 data URIs and embedded directly in the Markdown:

```markdown
![Image](data:image/png;base64,iVBORw0KGgo...)
```

**Pros**: Single file, easy to share
**Cons**: Larger file size, harder to edit

### Batch Convert Multiple Files

Convert multiple files at once:

```bash
python scripts/converter.py file1.docx file2.pdf file3.epub
```

Each file is converted to `.md` in its original directory.

### Batch Convert Directory

Convert all documents in a directory using glob patterns:

```bash
python scripts/converter.py "./documents/*.docx" -o ./converted/
```

All `.docx` files are converted to `./converted/` directory.

### Combined Options

Multiple options can be combined:

```bash
python scripts/converter.py document.docx --skip-toc --extract-media -o ./output/
```

This will:
1. Remove the table of contents
2. Extract images to `output/media/`
3. Save to `output/document.md`

## MinerU-Specific Features

### OCR for Scanned PDFs

MinerU automatically detects and processes scanned PDFs using OCR:

```bash
python scripts/converter.py scanned.pdf --tool mineru
```

MinerU will:
- Automatically detect if the PDF is scanned
- Enable OCR when needed
- Extract text from images
- Preserve document layout

### Advanced Table Extraction

For PDFs with complex or nested tables:

```bash
python scripts/converter.py financial-report.pdf --tool mineru
```

MinerU provides:
- Complex table structure detection
- Merged cell handling
- Nested table support
- Header row recognition

### Formula Parsing

Academic papers with mathematical formulas:

```bash
python scripts/converter.py research-paper.pdf --tool mineru
```

Formulas are handled intelligently:
- LaTeX formulas preserved or converted
- Math expressions recognized
- Scientific notation supported

### Multi-Language Documents

For documents with mixed languages (e.g., Chinese and English):

```bash
python scripts/converter.py bilingual-doc.pdf --tool mineru
```

MinerU excels at:
- Chinese character recognition
- Mixed language layout handling
- Proper text segmentation

## Examples

### Example 1: Convert Word Document

**Scenario**: Convert a Word document to Markdown for documentation

```bash
python scripts/converter.py user-guide.docx
```

**Output**: `user-guide.md` with:
- Headings preserved
- Tables converted to Markdown
- Bold/italic text preserved
- Lists maintained

### Example 2: Convert PDF with TOC Removal

**Scenario**: Convert a PDF report that has a table of contents

```bash
python scripts/converter.py report.pdf --skip-toc
```

**Output**: Clean `report.md` without the TOC section

### Example 3: Convert Presentation with Images

**Scenario**: Convert a PowerPoint presentation

```bash
python scripts/converter.py presentation.pptx --extract-media
```

**Output**:
- `presentation.md` (slides as Markdown)
- `presentation.media/` (extracted images)

### Example 4: Batch Convert Documentation

**Scenario**: Convert entire documentation folder

```bash
python scripts/converter.py "./docs/*.docx" -o ./markdown-docs/ --skip-toc
```

**Output**: All Word documents converted to `./markdown-docs/` without TOCs

### Example 5: Create Self-Contained Document

**Scenario**: Create a single Markdown file with embedded images for sharing

```bash
python scripts/converter.py document.docx --skip-toc --extract-media --embed-images
```

**Output**: Single `document.md` file with all images embedded as Base64

### Example 6: Convert Scanned PDF with OCR

**Scenario**: Extract text from a scanned PDF document

```bash
python scripts/converter.py scanned-document.pdf --tool mineru
```

**Output**: `scanned-document.md` with:
- OCR-extracted text
- Preserved layout structure
- Recognized headings and paragraphs

### Example 7: Convert Academic Paper with Formulas

**Scenario**: Convert a research paper with mathematical formulas

```bash
python scripts/converter.py research-paper.pdf --tool mineru --skip-toc
```

**Output**: `research-paper.md` with:
- LaTeX formulas preserved
- Table structures maintained
- References formatted properly
- TOC removed

### Example 8: Convert Financial Report with Complex Tables

**Scenario**: Extract data from a financial report with complex tables

```bash
python scripts/converter.py financial-report.pdf --tool mineru -o ./output/
```

**Output**: `./output/financial-report.md` with:
- Complex table structures
- Merged cells handled
- Numeric data preserved
- Proper column alignment

### Example 9: Batch Convert PDFs with MinerU

**Scenario**: Convert multiple PDFs using MinerU for better extraction

```bash
python scripts/converter.py "./reports/*.pdf" --tool mineru -o ./markdown/ --skip-toc
```

**Output**: All PDFs converted to `./markdown/` with:
- OCR applied where needed
- Tables properly extracted
- TOCs removed

### Example 10: Mixed Language Document

**Scenario**: Convert a Chinese-English bilingual document

```bash
python scripts/converter.py bilingual-doc.pdf --tool mineru
```

**Output**: `bilingual-doc.md` with:
- Chinese characters correctly recognized
- English text properly extracted
- Layout preserved for both languages

## Output Format

Generated Markdown follows standard format:

### Headings
```markdown
# Heading 1
## Heading 2
### Heading 3
```

### Tables
```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

### Images
```markdown
![Alt text](path/to/image.png)
```

Or with Base64:
```markdown
![Alt text](data:image/png;base64,iVBORw0KGgo...)
```

### Lists
```markdown
- Unordered item 1
- Unordered item 2

1. Ordered item 1
2. Ordered item 2
```

### Text Formatting
```markdown
**bold text**
*italic text*
***bold and italic***
```

## Tips

### General Tips

1. **Always use `--skip-toc`** for Word/PDF documents with tables of contents
2. **Use `--extract-media`** when you need editable images
3. **Use `--embed-images`** when creating standalone files to share
4. **Use `-v` flag** for debugging conversion issues
5. **Use glob patterns** (`*.docx`) for batch operations

### MinerU-Specific Tips

6. **Use `--tool mineru`** for scanned PDFs (auto-enables OCR)
7. **Use `--tool mineru`** for PDFs with complex tables or nested structures
8. **Use `--tool mineru`** for academic papers with mathematical formulas
9. **Use `--tool mineru`** for Chinese or mixed-language documents
10. **Use `--tool pandoc`** when speed is important and PDFs are simple text-based

### Tool Selection Guide

- **Quick conversion of simple documents**: Pandoc (faster)
- **Scanned or image-based PDFs**: MinerU (required)
- **Complex table structures**: MinerU (better accuracy)
- **Mixed format batch**: Use `--tool auto` for automatic selection
- **Maximum quality**: MinerU for PDFs, Pandoc for others

## Python API

You can also use the converter as a Python module:

```python
import sys
sys.path.append('scripts')

from converter import convert, batch_convert

# Single file with auto tool selection
output_path, success = convert(
    'document.pdf',
    'output.md',
    tool='auto',  # Auto-detect: MinerU for PDF, Pandoc for others
    skip_toc=True,
    extract_media=True
)

# Single file with specific tool
output_path, success = convert(
    'scanned.pdf',
    'output.md',
    tool='mineru',  # Force MinerU for OCR
    skip_toc=True
)

# Batch processing with tool selection
results = batch_convert(
    ['file1.docx', 'file2.pdf', 'file3.pdf'],
    output_dir='./output/',
    tool='auto',  # MinerU for PDFs, Pandoc for DOCX
    skip_toc=True
)

print(f"Converted {len(results['success'])} files")
```
