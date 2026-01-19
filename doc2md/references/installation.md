# Installation Guide

How to install and set up Doc2Md - Document to Markdown Converter.

## Prerequisites

The converter requires at least one conversion tool:
- **Pandoc** (required for non-PDF formats)
- **MinerU** (optional, for advanced PDF processing)

### Pandoc vs MinerU

| Feature | Pandoc | MinerU |
|---------|--------|--------|
| Formats | 40+ (Word, EPUB, HTML, PDF, etc.) | PDF only |
| OCR | No | Yes |
| Table Extraction | Basic | Advanced |
| Formula Parsing | Basic | LaTeX support |
| Speed | Fast | Slower (more accurate) |

**Recommendation**: Install both tools for maximum flexibility.

## Install Pandoc (Required)

Pandoc is the industry-standard document converter and supports 40+ formats.

### What is Pandoc?

Pandoc is a universal document converter:
- Developed since 2006
- Widely used in academia and industry
- Converts between Markdown, Word, PDF, HTML, EPUB, and more
- Cross-platform (Windows, macOS, Linux)

## Pandoc Installation

### Windows

#### Option 1: Using Chocolatey (Recommended)

```powershell
choco install pandoc
```

#### Option 2: Using Installer

1. Download from: https://pandoc.org/installing.html
2. Run the installer
3. Restart your terminal

#### Option 3: Using Scoop

```powershell
scoop install pandoc
```

### macOS

#### Using Homebrew (Recommended)

```bash
brew install pandoc
```

#### Using MacPorts

```bash
sudo port install pandoc
```

### Linux

#### Debian/Ubuntu

```bash
sudo apt-get update
sudo apt-get install pandoc
```

#### RHEL/CentOS/Fedora

```bash
sudo yum install pandoc
```

#### Arch Linux

```bash
sudo pacman -S pandoc
```

## Verify Installation

After installing pandoc, verify it's working:

```bash
pandoc --version
```

You should see output like:

```
pandoc 2.19.2
Compiled with use of pandoc-types 1.22.1...
```

## Install MinerU (Optional)

MinerU provides advanced PDF parsing with OCR, table extraction, and layout recognition.

### What is MinerU?

MinerU is a PDF parsing library:
- Intelligent layout recognition
- OCR support for scanned documents
- Advanced table extraction
- LaTeX formula parsing
- Multi-language support

### Installation

MinerU is distributed as a Python package:

```bash
pip install mineru
```

Or from source:

```bash
git clone https://github.com/opendatalab/MinerU.git
cd MinerU
pip install -e .
```

### Dependencies

MinerU requires several dependencies. They are usually installed automatically:

- PyMuPDF (PDF parsing)
- Pillow (image processing)
- PyTorch (for ML models)
- EasyOCR (for OCR functionality)

### Windows-Specific Requirements

On Windows, you may need:

```bash
pip install pywin32
```

### Verify MinerU Installation

Test MinerU is working:

```bash
python -c "import importlib.util; print('MinerU available' if importlib.util.find_spec('mineru') else 'Not found')"
```

## Python Requirements

**Minimum for Pandoc only:**
- No Python packages required

**For MinerU:**
- Python 3.8+
- mineru package
- Dependencies installed automatically

### Python Version

- Minimum: Python 3.7+ (Pandoc)
- Recommended: Python 3.8+ (MinerU)

## Setup the Skill

### Clone or Download

If you haven't already, get the skill:

```bash
# Clone the repository
git clone <repository-url>
cd doc2md
```

### Verify the Structure

Ensure you have the following structure:

```
doc2md/
├── SKILL.md
├── scripts/
│   └── converter.py
├── references/
│   ├── installation.md
│   ├── usage.md
│   └── troubleshooting.md
└── requirements.txt
```

## Test the Installation

Test that everything is working:

```bash
# Test pandoc
pandoc --version

# Test MinerU (if installed)
python -c "import importlib.util; print('MinerU:', 'Available' if importlib.util.find_spec('mineru') else 'Not installed')"

# Test the converter
python scripts/converter.py --help
```

You should see the help message with all available options, including the `--tool` option.

## Quick Test

Convert a test document to verify everything works:

```bash
# Create a simple test file (if you don't have one)
echo "# Test Document

This is a test paragraph." > test.md

# Convert it back and forth
python scripts/converter.py test.md
```

## Troubleshooting Installation

### Pandoc Not Found

If you get "Pandoc not found" error:

1. Verify pandoc is installed:
   ```bash
   pandoc --version
   ```

2. If not found, reinstall using the instructions above

3. Restart your terminal after installation

4. Check that pandoc is in your PATH:
   ```bash
   which pandoc  # macOS/Linux
   where pandoc  # Windows
   ```

### Permission Denied

If you get permission errors:

**Linux/macOS:**
```bash
chmod +x scripts/converter.py
```

**Windows:**
Make sure Python has permission to execute scripts.

### Python Not Found

If Python is not found:

**Windows:**
- Install Python from: https://www.python.org/downloads/
- Check "Add Python to PATH" during installation

**macOS:**
```bash
brew install python
```

**Linux:**
```bash
sudo apt-get install python3
```

### MinerU Not Found

If you get "MinerU not found" or "MinerU module not found":

1. Verify MinerU is installed:
   ```bash
   python -c "import importlib.util; print('Available' if importlib.util.find_spec('mineru') else 'Not found')"
   ```

2. If not found, install MinerU:
   ```bash
   pip install mineru
   ```

3. Check Python version (requires 3.8+):
   ```bash
   python --version
   ```

4. If dependencies fail, try:
   ```bash
   pip install --upgrade pip
   pip install mineru --no-cache-dir
   ```

### MinerU OCR Errors

If OCR doesn't work on scanned PDFs:

1. Ensure EasyOCR is installed:
   ```bash
   pip install easyocr
   ```

2. For Windows, install Visual C++ redistributable

3. For Linux, install system dependencies:
   ```bash
   sudo apt-get install libgomp1
   ```

## Update Pandoc

To update pandoc to the latest version:

**Windows (Chocolatey):**
```powershell
choco upgrade pandoc
```

**macOS (Homebrew):**
```bash
brew upgrade pandoc
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get upgrade pandoc
```

## Uninstall

To remove the converter:

```bash
# Just delete the directory
rm -rf doc2md
```

To remove pandoc:

**Windows (Chocolatey):**
```powershell
choco uninstall pandoc
```

**macOS (Homebrew):**
```bash
brew uninstall pandoc
```

**Linux:**
```bash
sudo apt-get remove pandoc
```

## Next Steps

After installation:
1. Read [usage.md](usage.md) for detailed usage instructions
2. Try converting a document
3. Explore the available options

For help with issues, see [troubleshooting.md](troubleshooting.md).
