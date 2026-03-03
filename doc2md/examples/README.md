# Examples

This directory contains example documents and expected outputs to help you understand how to use Doc2Md.

## 📁 Directory Structure

```
examples/
├── README.md              # This file
├── expected-outputs/      # Expected conversion results
│   ├── word-example.md    # Expected output from Word document
│   └── pdf-example.md     # Expected output from PDF
└── sample-files/          # Place your sample files here
    ├── README.txt         # Instructions for sample files
    └── (add your files)
```

## 🎯 Getting Sample Files

### Option 1: Create Your Own

Create a simple Word document with:
- Headings (H1, H2, H3)
- Paragraphs
- Lists (ordered and unordered)
- A table
- An image

### Option 2: Download Example Files

Download sample files from:
- Microsoft Office templates: https://create.microsoft.com/templates
- Public domain PDFs: https://www.gutenberg.org/

### Option 3: Use Your Own Documents

Use documents from your own work (non-confidential).

## 📝 Example 1: Word Document Conversion

### Input File
Place a `.docx` file in `sample-files/` directory, e.g., `word-example.docx`

### Command
```bash
cd /e/skills/doc2md
python scripts/converter.py examples/sample-files/word-example.docx \
  --relative-images \
  --skip-toc \
  -o examples/output/
```

### Expected Output
See `expected-outputs/word-example.md` for what the output should look like.

### Key Features to Check
- [ ] Headings preserved (# ## ###)
- [ ] Paragraphs separated correctly
- [ ] Lists formatted properly (- or 1.)
- [ ] Tables converted to Markdown syntax
- [ ] Images extracted to media/ folder
- [ ] TOC removed (--skip-toc flag)

## 📝 Example 2: PDF Conversion (Simple)

### Input File
Place a text-based `.pdf` file in `sample-files/`

### Command
```bash
python scripts/converter.py examples/sample-files/simple.pdf \
  --tool pymupdf \
  --relative-images \
  -o examples/output/
```

### Expected Output
See `expected-outputs/pdf-simple.md`

### Key Features to Check
- [ ] Text extracted correctly
- [ ] Headings recognized
- [ ] Paragraphs formatted
- [ ] Images extracted

## 📝 Example 3: PDF Conversion (Complex)

### Input File
Place a PDF with tables or scanned content in `sample-files/`

### Command
```bash
python scripts/converter.py examples/sample-files/complex.pdf \
  --tool mineru \
  --relative-images \
  -o examples/output/
```

### Expected Output
See `expected-outputs/pdf-complex.md`

### Key Features to Check
- [ ] Tables extracted correctly
- [ ] OCR text recognized (if scanned)
- [ ] Complex layout preserved
- [ ] Images extracted

## 📝 Example 4: Batch Conversion

### Command
```bash
python scripts/converter.py "examples/sample-files/*.docx" \
  -o examples/output/ \
  --relative-images \
  --skip-toc
```

### Expected Output
Multiple `.md` files in `examples/output/` directory.

## 🧪 Testing Your Setup

### Quick Test
```bash
# 1. Check status
python scripts/converter.py --status

# 2. Auto-install if needed
python scripts/converter.py --auto-install

# 3. Convert test file (create a simple .txt file first)
echo "# Test\n\nThis is a test." > test.txt
python scripts/converter.py test.txt
cat test.md
```

## ✅ Verification Checklist

After conversion, verify:

- [ ] Output file created (`.md` extension)
- [ ] File size reasonable (not empty, not too large)
- [ ] Headings converted to `#` syntax
- [ ] Lists formatted correctly
- [ ] Tables use Markdown syntax (`|` separators)
- [ ] Images extracted (if using `--relative-images`)
- [ ] No broken image links
- [ ] TOC removed (if using `--skip-toc`)

## 🐛 Troubleshooting

### Common Issues

**Issue:** "File not found"
**Solution:** Check file path and ensure you're in the correct directory

**Issue:** "Pandoc not found"
**Solution:** Add `--auto-install` flag or install pandoc

**Issue:** "Images not extracted"
**Solution:** Add `--relative-images` flag

**Issue:** "Output is empty"
**Solution:**
- For PDFs: Try `--tool mineru`
- Check if file is corrupted
- Use `-v` flag for details

## 📚 Next Steps

1. Try converting your own documents
2. Experiment with different options
3. Check the quality of output
4. Read `references/scenarios.md` for more examples

## 🤝 Contributing Examples

If you have good example files (non-confidential), consider contributing:

1. Place files in `sample-files/`
2. Add expected output in `expected-outputs/`
3. Update this README with the example
4. Submit a pull request

---

**Note:** Keep sample files small (< 1MB) and non-confidential.
