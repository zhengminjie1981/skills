# Sample Files Directory

Place your sample document files here for testing.

## 📁 Recommended Files

### Word Documents
- `word-example.docx` - A Word document with:
  - Headings (H1, H2, H3)
  - Paragraphs
  - Lists (ordered and unordered)
  - A table
  - An image or two
  - Table of contents

### PDF Files
- `pdf-simple.pdf` - A simple text-based PDF
- `pdf-complex.pdf` - A PDF with tables, images, or complex layout
- `pdf-scanned.pdf` - A scanned document (for OCR testing)

### Other Formats
- `epub-example.epub` - An EPUB e-book
- `html-example.html` - An HTML document
- `presentation.pptx` - A PowerPoint presentation

## 🎯 How to Create Sample Files

### Option 1: Create Your Own

1. Open Microsoft Word or Google Docs
2. Create a document with various elements:
   - Title and headings
   - Regular paragraphs
   - Bullet and numbered lists
   - A table
   - An image
   - Links
3. Save as `.docx`
4. Optionally, export to PDF

### Option 2: Use Public Domain Content

Download from these sources:

- **Project Gutenberg**: https://www.gutenberg.org/ (free e-books)
- **Microsoft Templates**: https://create.microsoft.com/templates
- **Google Docs Templates**: https://docs.google.com/templates
- **Sample PDFs**: https://www.adobe.com/acrobat/resources/by-industry.html

### Option 3: Use Your Own

Use non-confidential documents from your work or personal files.

## ⚠️ Important Notes

### File Size
Keep files small (< 1 MB) for quick testing:
- Word: 1-5 pages
- PDF: 1-5 pages
- Images: Web resolution (72-150 dpi)

### Confidentiality
**Never** add confidential or sensitive documents:
- No personal information
- No proprietary content
- No copyrighted material without permission

### Content Ideas

Good sample documents include:
- ✅ User manuals
- ✅ Reports with tables
- ✅ Academic papers
- ✅ Technical documentation
- ✅ Presentations

Avoid:
- ❌ Financial statements
- ❌ Legal documents
- ❌ Personal letters
- ❌ Anything with sensitive data

## 🧪 Quick Test

Once you have a sample file:

```bash
# From the doc2md directory
cd /e/skills/doc2md

# Convert Word document
python scripts/converter.py examples/sample-files/word-example.docx \
  --relative-images \
  --skip-toc \
  -o examples/output/

# Check the result
cat examples/output/word-example.md
```

## 📋 Testing Checklist

Test with different file types:

- [ ] `.docx` - Word document
- [ ] `.pdf` (simple) - Text-based PDF
- [ ] `.pdf` (complex) - PDF with tables
- [ ] `.pdf` (scanned) - Scanned document
- [ ] `.epub` - E-book
- [ ] `.html` - Web page
- [ ] `.pptx` - Presentation
- [ ] Batch conversion - Multiple files

## 🤝 Contributing

If you create good sample files:

1. Ensure they're non-confidential
2. Keep them small
3. Add to this directory
4. Update the README
5. Submit a pull request

---

**Remember:** Keep sample files small, non-confidential, and representative of real-world usage.
