# Doc2Md - Troubleshooting Guide

Common issues and solutions when using Doc2Md.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Conversion Issues](#conversion-issues)
- [Image Issues](#image-issues)
- [Output Issues](#output-issues)
- [Performance Issues](#performance-issues)

## Installation Issues

### "Pandoc Not Found"

**Error:**
```
PANDOC NOT FOUND
Pandoc is required for document conversion.
```

**Causes:**
- Pandoc is not installed
- Pandoc is not in your PATH
- Terminal needs to be restarted after installation

**Solutions:**

1. Check if pandoc is installed:
   ```bash
   pandoc --version
   ```

2. If not found, install pandoc:
   - **Windows**: `choco install pandoc`
   - **macOS**: `brew install pandoc`
   - **Linux**: `sudo apt-get install pandoc`

3. Restart your terminal after installation

4. Verify pandoc is in PATH:
   ```bash
   which pandoc  # macOS/Linux
   where pandoc  # Windows
   ```

### "Python Not Found"

**Error:**
```
python: command not found
```

**Solutions:**

**Windows:**
- Install Python from https://www.python.org/downloads/
- Check "Add Python to PATH" during installation

**macOS/Linux:**
```bash
# Install Python 3
sudo apt-get install python3  # Linux
brew install python  # macOS

# Use python3 instead of python
python3 scripts/converter.py ...
```

### Permission Denied

**Error:**
```
Permission denied: 'scripts/converter.py'
```

**Solutions:**

**Linux/macOS:**
```bash
chmod +x scripts/converter.py
```

**Windows:**
- Run as Administrator if needed
- Check antivirus settings

## Conversion Issues

### Conversion Failed

**Error:**
```
Error: Pandoc conversion failed
```

**Solutions:**

1. Use verbose mode to see details:
   ```bash
   python scripts/converter.py document.docx --verbose
   ```

2. Check the file exists and is readable:
   ```bash
   ls -la document.docx
   ```

3. Verify the file format is supported:
   ```bash
   python scripts/converter.py --help
   # See supported formats
   ```

4. Try converting with pandoc directly:
   ```bash
   pandoc document.docx -o test.md
   ```

5. Check if the file is corrupted:
   - Try opening it in the original application
   - Create a new copy and try again

### Unsupported Format

**Error:**
```
Error: Unsupported file type
```

**Solutions:**

1. Check supported formats:
   - DOCX, DOC, PDF, EPUB, HTML, ODT, RTF, TXT, etc.

2. If you have an unsupported format:
   - Convert it to a supported format first
   - Use pandoc directly to check support: `pandoc --list-input-formats`

3. Check file extension is correct:
   ```bash
   mv document.doc document.docx  # If needed
   ```

### Empty Output File

**Issue:** Conversion succeeds but output .md file is empty.

**Solutions:**

1. Check the input file has content:
   ```bash
   wc -l input.docx  # Check file size
   ```

2. Try with verbose mode:
   ```bash
   python scripts/converter.py input.docx --verbose
   ```

3. Check pandoc output directly:
   ```bash
   pandoc input.docx -o test.md
   cat test.md
   ```

4. Some PDFs are image-based (scanned):
   - These require OCR (not supported)
   - Try a text-based PDF instead

### Encoding Issues

**Error:**
```
UnicodeDecodeError or encoding errors
```

**Solutions:**

1. The converter uses UTF-8 encoding by default

2. For problematic files, try converting with pandoc directly:
   ```bash
   pandoc input.docx -o output.md --wrap=none
   ```

3. Check the file encoding:
   ```bash
   file -i input.txt  # Linux/macOS
   ```

## Image Issues

### Images Not Extracting

**Issue:** Images don't appear in output or media folder.

**Solutions:**

1. Make sure to use the `--extract-media` flag:
   ```bash
   python scripts/converter.py document.docx --extract-media
   ```

2. Check if the document actually contains images

3. Verify the media folder was created:
   ```bash
   ls -la document.md.media/
   ```

4. Some formats don't support image extraction:
   - Plain text files
   - Some PDF configurations

### Images Not Embedding

**Issue:** Base64 embedding not working.

**Solutions:**

1. Use both flags together:
   ```bash
   python scripts/converter.py document.docx --extract-media --embed-images
   ```

   Note: `--embed-images` requires `--extract-media`

2. Check the output file:
   ```bash
   grep "data:image" document.md
   ```

3. Verify images were extracted first:
   ```bash
   ls document.md.media/
   ```

4. Large files may take time to embed:
   - Be patient with large documents
   - Use `--verbose` to see progress

### Broken Image Links

**Issue:** Image links in output don't work.

**Solutions:**

1. Without `--extract-media`:
   - Images are not copied
   - Links point to original locations (may not exist)

2. With `--extract-media`:
   - Images are in `filename.media/` folder
   - Keep the media folder with the .md file

3. With `--embed-images`:
   - Images are embedded as Base64
   - No external files needed

## Output Issues

### Table of Contents Still Present

**Issue:** Used `--skip-toc` but TOC is still there.

**Solutions:**

1. The TOC detection looks for specific patterns:
   - Headings like "Table of Contents", "目录"
   - Followed by page numbers and dots

2. If your TOC has a different title:
   - Check the exact heading in the source
   - The converter supports multiple languages

3. Check if it's really a TOC:
   - TOCs have page numbers
   - Regular section headings don't

4. Manually verify the detection:
   ```bash
   python scripts/converter.py document.docx --skip-toc --verbose
   ```

### Formatting Issues

**Issue:** Formatting doesn't look right.

**Solutions:**

1. Pandoc does best-effort conversion:
   - Complex layouts may not convert perfectly
   - Some manual adjustment may be needed

2. Check the original document:
   - Clean formatting converts better
   - Remove unnecessary styles

3. Try different pandoc options:
   ```bash
   pandoc input.docx -o output.md --atx-headers
   ```

4. Post-process the Markdown:
   - Clean up spacing
   - Adjust heading levels
   - Fix table formatting

### Large File Size

**Issue:** Output .md file is very large.

**Causes:**
- Using `--embed-images` (Base64 increases size)
- Large number of images
- Long documents

**Solutions:**

1. Don't use `--embed-images`:
   - Use `--extract-media` instead
   - Keeps images as separate files

2. Compress images separately:
   ```bash
   # Optimize images in media folder
   mogrify -quality 80 *.png
   ```

3. Split large documents:
   - Convert in sections
   - Use separate files

## Performance Issues

### Slow Conversion

**Issue:** Conversion takes a long time.

**Solutions:**

1. Large files naturally take longer:
   - Be patient
   - Use `--verbose` to see progress

2. Multiple files:
   - Consider parallel processing
   - Use batch conversion for efficiency

3. System resources:
   - Check CPU and memory usage
   - Close other applications if needed

4. Pandoc version:
   ```bash
   pandoc --version
   # Update to latest version if old
   ```

### Memory Issues

**Error:**
```
MemoryError or out of memory
```

**Solutions:**

1. Very large files may exceed memory:
   - Split the file into smaller sections
   - Convert each section separately

2. Close other applications:
   - Free up system memory
   - Try converting on a machine with more RAM

3. Don't use `--embed-images` for large documents:
   - Base64 encoding increases memory usage
   - Use `--extract-media` instead

## Getting Help

If you're still having issues:

1. Check the [usage guide](usage.md)
2. Review [installation instructions](installation.md)
3. Consult [pandoc documentation](https://pandoc.org/)
4. Use verbose mode for debugging:
   ```bash
   python scripts/converter.py document.docx --verbose
   ```

## Reporting Issues

When reporting an issue, include:

1. Your operating system and version
2. Pandoc version (`pandoc --version`)
3. Python version (`python --version`)
4. Exact command used
5. Error message (if any)
6. Sample file (if possible and non-confidential)
