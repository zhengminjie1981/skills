#!/usr/bin/env python3
"""
Document to Markdown Converter

Converts documents to Markdown using:
- Pandoc: 40+ formats (Word, EPUB, HTML, etc.)
- MinerU: Advanced PDF parsing with OCR and table extraction
"""

import argparse
import base64
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Dict, Literal

# Pandoc supported formats
SUPPORTED_FORMATS = {
    # Word processing
    '.docx': 'docx',
    '.doc': 'doc',
    '.odt': 'odt',
    '.rtf': 'rtf',
    '.epub': 'epub',

    # PDF
    '.pdf': 'pdf',

    # Presentations (via pandoc filters)
    '.pptx': 'pptx',

    # Web/Markup
    '.html': 'html',
    '.htm': 'html',
    '.xhtml': 'xhtml',
    '.xml': 'xml',

    # Markdown variants
    '.md': 'markdown',
    '.markdown': 'markdown',
    '.mdown': 'markdown',
    '.mkd': 'markdown',
    '.mkdn': 'markdown',
    '.mdwn': 'markdown',
    '.mdtext': 'markdown',
    '.text': 'markdown',
    '.rmarkdown': 'markdown',

    # Text formats
    '.txt': 'plain',
    '.text': 'plain',

    # LaTeX/Scientific
    '.tex': 'latex',
    '.latex': 'latex',
    '.ltx': 'latex',

    # reStructuredText
    '.rst': 'rst',

    # Jupyter Notebook
    '.ipynb': 'ipynb',

    # Other markup
    '.opml': 'opml',
    '.org': 'org',
    '.textile': 'textile',
    '.wiki': 'mediawiki',
    '.mediawiki': 'mediawiki',

    # E-books
    '.fb2': 'fb2',

    # Data
    '.csv': 'csv',
    '.tsv': 'tsv',
    '.json': 'json',
}

# Map extensions to pandoc input formats
INPUT_FORMATS = {
    # Word processing
    '.docx': 'docx',
    '.doc': 'doc',
    '.odt': 'odt',
    '.rtf': 'rtf',
    '.epub': 'epub',

    # PDF
    '.pdf': 'pdf',

    # Presentations
    '.pptx': 'pptx',

    # Web/Markup
    '.html': 'html',
    '.htm': 'html',
    '.xhtml': 'xhtml',
    '.xml': 'xml',

    # Markdown variants
    '.md': 'markdown',
    '.markdown': 'markdown',
    '.mdown': 'markdown',
    '.mkd': 'markdown',
    '.mkdn': 'markdown',
    '.mdwn': 'markdown',
    '.mdtext': 'markdown',
    '.text': 'markdown',
    '.rmarkdown': 'markdown',

    # Text
    '.txt': 'plain',

    # LaTeX
    '.tex': 'latex',
    '.latex': 'latex',
    '.ltx': 'latex',

    # reStructuredText
    '.rst': 'rst',

    # Jupyter
    '.ipynb': 'ipynb',

    # Other
    '.opml': 'opml',
    '.org': 'org',
    '.textile': 'textile',
    '.wiki': 'mediawiki',
    '.mediawiki': 'mediawiki',
    '.fb2': 'fb2',
    '.csv': 'csv',
    '.tsv': 'tsv',
    '.json': 'json',
}


def check_pandoc_installed() -> bool:
    """Check if pandoc is installed and accessible."""
    try:
        result = subprocess.run(
            ['pandoc', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def get_pandoc_version() -> Optional[str]:
    """Get pandoc version string."""
    try:
        result = subprocess.run(
            ['pandoc', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.split('\n')[0]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None


def check_mineru_available() -> bool:
    """Check if MinerU is available."""
    try:
        import importlib.util
        spec = importlib.util.find_spec("mineru") or importlib.util.find_spec("mine_llu")
        return spec is not None
    except Exception:
        return False


def get_mineru_converter():
    """Import MinerU converter module."""
    try:
        # Try to import from same directory
        import mineru_converter
        return mineru_converter
    except ImportError:
        return None


def detect_input_format(file_path: str) -> Optional[str]:
    """Detect pandoc input format from file extension."""
    ext = Path(file_path).suffix.lower()
    return INPUT_FORMATS.get(ext)


def get_output_path(input_path: str, output_dir: Optional[str] = None) -> str:
    """
    Determine output .md file path.

    Args:
        input_path: Path to input document
        output_dir: Optional output directory

    Returns:
        Path to output Markdown file
    """
    input_path_obj = Path(input_path)

    if output_dir:
        output_dir_obj = Path(output_dir)
        output_dir_obj.mkdir(parents=True, exist_ok=True)
    else:
        output_dir_obj = input_path_obj.parent

    output_filename = input_path_obj.stem + '.md'
    return str(output_dir_obj / output_filename)


def remove_table_of_contents(markdown_content: str) -> str:
    """
    Remove table of contents from Markdown.

    Detects and removes TOC sections since Markdown doesn't have page numbers.
    Handles common TOC patterns in multiple languages.

    Args:
        markdown_content: Markdown content potentially containing TOC

    Returns:
        Markdown with TOC removed
    """
    import re

    lines = markdown_content.split('\n')
    result_lines = []
    in_toc = False
    toc_start_patterns = []
    toc_end_detected = False

    # Common TOC heading patterns (multilingual)
    toc_headings = [
        'table of contents', 'contents', 'toc',
        '目录', '目　录',
        '目录', '索引',
        'table des matières', 'sommaire',  # French
        'inhalt', 'inhaltsverzeichnis',     # German
        'índice', 'tabla de contenidos',    # Spanish
        'indice', 'indice analitico',       # Italian
        'содержание',                       # Russian
    ]

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check if this line is a TOC heading
        is_toc_heading = False
        for heading in toc_headings:
            # Match headings like "# Table of Contents" or "## Table of Contents"
            if re.match(r'^#+\s*', stripped, re.IGNORECASE):
                heading_text = re.sub(r'^#+\s*', '', stripped, flags=re.IGNORECASE).lower().strip()
                if heading_text == heading.lower():
                    is_toc_heading = True
                    toc_start_patterns.append(i)
                    in_toc = True
                    toc_end_detected = False
                    break

        if is_toc_heading:
            continue  # Skip the TOC heading itself

        # Detect end of TOC
        if in_toc:
            # End if we hit another major heading
            if re.match(r'^#+\s+', stripped) and not toc_end_detected:
                # Check if it's not part of the TOC
                # TOC entries usually have dots, page numbers, or are indented
                if not re.search(r'\.{3,}|\.{2}\s+\d+|\s+\d+\s*$', stripped):
                    in_toc = False
                    result_lines.append(line)
                    continue

            # Skip TOC content
            # TOC lines typically contain:
            # - Dots with page numbers: "Chapter 1 ...... 5"
            # - Just page numbers: "5"
            # - Multiple dots: "......"
            if re.search(r'\.{2,}|\s+\d+\s*$', stripped):
                continue

            # Skip lines that look like TOC entries
            # (indented, have dots, or are just numbers)
            if stripped and not stripped.startswith('#'):
                if re.match(r'^\s+\d+\s*$', stripped):  # Just page number
                    continue
                if re.search(r'\.{3,}', stripped):  # Lots of dots
                    continue

        # Add non-TOC lines
        if not in_toc:
            result_lines.append(line)

    return '\n'.join(result_lines)


def embed_images_as_base64(markdown_content: str, base_dir: str) -> str:
    """
    Embed images as Base64 in Markdown.

    Finds image references like ![alt](path/to/image.png)
    and replaces them with Base64 data URIs.

    Args:
        markdown_content: Markdown content with image references
        base_dir: Base directory for resolving relative image paths

    Returns:
        Markdown with Base64 embedded images
    """
    import re

    def replace_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)

        # Skip if already a data URI
        if image_path.startswith('data:'):
            return match.group(0)

        # Resolve full path
        full_path = Path(base_dir) / image_path if not Path(image_path).is_absolute() else Path(image_path)

        if not full_path.exists():
            return match.group(0)  # Keep original if file not found

        try:
            with open(full_path, 'rb') as img_file:
                image_data = img_file.read()
                encoded = base64.b64encode(image_data).decode('utf-8')

                # Detect format
                ext = full_path.suffix.lower().lstrip('.')
                if ext in ['jpg', 'jpeg']:
                    mime_type = 'jpeg'
                elif ext == 'png':
                    mime_type = 'png'
                elif ext == 'gif':
                    mime_type = 'gif'
                elif ext == 'svg':
                    mime_type = 'svg+xml'
                else:
                    mime_type = ext

                return f'![{alt_text}](data:image/{mime_type};base64,{encoded})'
        except Exception as e:
            print(f"Warning: Could not embed image {full_path}: {e}")
            return match.group(0)

    # Match Markdown image syntax
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    return re.sub(pattern, replace_image, markdown_content)


def convert_with_pandoc(
    input_path: str,
    output_path: Optional[str] = None,
    extract_media: bool = False,
    embed_images: bool = False,
    relative_images: bool = False,
    skip_toc: bool = False,
    standalone: bool = True,
    extra_args: Optional[List[str]] = None
) -> tuple[str, bool]:
    """
    Convert document using pandoc.

    Args:
        input_path: Path to input file
        output_path: Path to output .md file
        extract_media: Extract images to media folder
        embed_images: Embed images as Base64 (after extraction)
        relative_images: Keep images as relative paths (implies extract_media)
        skip_toc: Remove table of contents (since Markdown has no page numbers)
        standalone: Produce standalone output with metadata
        extra_args: Additional pandoc arguments

    Returns:
        Tuple of (output_path, success)
    """
    input_format = detect_input_format(input_path)
    if not input_format:
        return None, False

    if output_path is None:
        output_path = get_output_path(input_path)

    # Build pandoc command
    cmd = [
        'pandoc',
        '-f', input_format,
        '-t', 'markdown',
        input_path,
        '-o', output_path
    ]

    # Add options
    if standalone:
        cmd.extend(['-s', '--wrap=none'])

    # Handle image options
    # relative_images implies extract_media
    if relative_images:
        extract_media = True

    if extract_media:
        media_dir = str(Path(output_path).parent / 'media')
        cmd.extend(['--extract-media', media_dir])

    if extra_args:
        cmd.extend(extra_args)

    try:
        # Run pandoc
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # Post-process the Markdown
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove table of contents if requested
        if skip_toc:
            content = remove_table_of_contents(content)

        # Embed images if requested (skip when using relative_images)
        if embed_images and extract_media and not relative_images:
            media_dir = str(Path(output_path).parent / 'media')
            content = embed_images_as_base64(content, media_dir)

        # Write the processed content back
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_path, True

    except subprocess.CalledProcessError as e:
        print(f"Error: Pandoc conversion failed: {e.stderr}")
        return None, False
    except Exception as e:
        print(f"Error: {e}")
        return None, False


def convert(
    input_path: str,
    output_path: Optional[str] = None,
    tool: Literal['auto', 'pandoc', 'mineru'] = 'auto',
    extract_media: bool = False,
    embed_images: bool = False,
    relative_images: bool = False,
    skip_toc: bool = False,
    standalone: bool = True,
    extra_args: Optional[List[str]] = None
) -> tuple[Optional[str], bool]:
    """
    Convert document to Markdown using the appropriate tool.

    Args:
        input_path: Path to input file
        output_path: Path to output .md file
        tool: Conversion tool ('auto', 'pandoc', 'mineru')
        extract_media: Extract images to media folder
        embed_images: Embed images as Base64
        relative_images: Keep images as relative paths (implies extract_media)
        skip_toc: Remove table of contents
        standalone: Produce standalone output (Pandoc only)
        extra_args: Additional arguments for the tool

    Returns:
        Tuple of (output_path, success)
    """
    input_ext = Path(input_path).suffix.lower()
    is_pdf = input_ext == '.pdf'

    # Auto-detect tool
    if tool == 'auto':
        if is_pdf and check_mineru_available():
            # Use MinerU for PDFs when available
            tool = 'mineru'
        else:
            # Use Pandoc for everything else
            tool = 'pandoc'

    # Route to appropriate converter
    if tool == 'mineru':
        if not is_pdf:
            print(f"Warning: MinerU only supports PDF files. Using Pandoc instead.")
            tool = 'pandoc'
        else:
            mineru_conv = get_mineru_converter()
            if mineru_conv:
                return mineru_conv.convert_pdf(
                    input_path,
                    output_path=output_path,
                    extract_images=extract_media,
                    embed_images=embed_images,
                    relative_images=relative_images,
                    skip_toc=skip_toc,
                    use_cli=False
                )
            else:
                print("Error: MinerU module not found.")
                return None, False

    if tool == 'pandoc':
        if not check_pandoc_installed():
            print("Error: Pandoc is not installed.")
            return None, False
        return convert_with_pandoc(
            input_path,
            output_path,
            extract_media=extract_media,
            embed_images=embed_images,
            relative_images=relative_images,
            skip_toc=skip_toc,
            standalone=standalone,
            extra_args=extra_args
        )

    return None, False


def get_supported_files(paths: List[str]) -> List[str]:
    """
    Filter and expand paths to get list of supported document files.

    Args:
        paths: List of file/directory paths or glob patterns

    Returns:
        List of supported document file paths
    """
    import glob

    supported_files = []

    for path in paths:
        path_obj = Path(path)

        # Handle glob patterns
        if '*' in path or '?' in path:
            matched_files = glob.glob(path)
            supported_files.extend(matched_files)
            continue

        # Handle directories
        if path_obj.is_dir():
            for ext in SUPPORTED_FORMATS.keys():
                pattern = str(path_obj / f'*{ext}')
                supported_files.extend(glob.glob(pattern))
            continue

        # Handle individual files
        if path_obj.is_file():
            if path_obj.suffix.lower() in SUPPORTED_FORMATS:
                supported_files.append(str(path_obj))

    return sorted(set(supported_files))


def batch_convert(
    inputs: List[str],
    output_dir: Optional[str] = None,
    tool: Literal['auto', 'pandoc', 'mineru'] = 'auto',
    extract_media: bool = False,
    embed_images: bool = False,
    relative_images: bool = False,
    skip_toc: bool = False,
    verbose: bool = False
) -> Dict:
    """
    Convert multiple documents to Markdown.

    Args:
        inputs: List of file/directory paths
        output_dir: Optional output directory
        tool: Conversion tool ('auto', 'pandoc', 'mineru')
        extract_media: Extract images
        embed_images: Embed images as Base64
        relative_images: Keep images as relative paths
        skip_toc: Remove table of contents
        verbose: Enable verbose output

    Returns:
        Dictionary with results
    """
    files = get_supported_files(inputs)

    if not files:
        return {
            'success': [],
            'failed': [],
            'skipped': inputs
        }

    results = {
        'success': [],
        'failed': [],
        'skipped': []
    }

    for file_path in files:
        try:
            if verbose:
                print(f"Converting: {file_path}")

            output_path = get_output_path(file_path, output_dir)
            _, success = convert(
                file_path,
                output_path,
                tool=tool,
                extract_media=extract_media,
                embed_images=embed_images,
                relative_images=relative_images,
                skip_toc=skip_toc
            )

            if success:
                results['success'].append((file_path, output_path))
                print(f"[OK] Converted: {file_path} -> {output_path}")
            else:
                results['failed'].append((file_path, "Conversion failed"))

        except Exception as e:
            results['failed'].append((file_path, str(e)))

    return results


def print_installation_instructions():
    """Print pandoc installation instructions."""
    import platform
    system = platform.system()

    print("\n" + "="*60)
    print("PANDOC NOT FOUND")
    print("="*60)
    print("\nPandoc is required for document conversion.")
    print("\nInstallation instructions:\n")

    if system == "Windows":
        print("Windows:")
        print("  1. Using Chocolatey:")
        print("     choco install pandoc")
        print("  2. Or download installer:")
        print("     https://pandoc.org/installing.html")
    elif system == "Darwin":  # macOS
        print("macOS:")
        print("  brew install pandoc")
    else:  # Linux
        print("Linux:")
        print("  sudo apt-get install pandoc   # Debian/Ubuntu")
        print("  sudo yum install pandoc       # RHEL/CentOS")

    print("\nAfter installation, restart your terminal and try again.")
    print("="*60 + "\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Convert documents to Markdown using Pandoc and MinerU',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Supported formats:
  Pandoc: DOCX, DOC, ODT, RTF, EPUB, PDF, HTML, TXT, and 30+ more
  MinerU: PDF (advanced parsing with OCR and table extraction)

Tool Selection:
  --tool auto    Auto-detect (MinerU for PDFs if available, Pandoc otherwise)
  --tool pandoc  Use Pandoc for all files
  --tool mineru  Use MinerU for PDFs (Pandoc for other formats)

Examples:
  # Convert a Word document
  %(prog)s document.docx

  # Convert a PDF with MinerU (better tables/OCR)
  %(prog)s document.pdf --tool mineru

  # Convert to specific output directory
  %(prog)s document.pdf -o ./markdown/

  # Convert with image extraction (relative paths)
  %(prog)s presentation.pptx --relative-images

  # Convert with Base64 embedded images
  %(prog)s document.docx --embed-images

  # Convert and remove table of contents (recommended)
  %(prog)s document.docx --skip-toc

  # Convert all documents in a directory
  %(prog)s "./documents/*.docx" -o ./output/
        """
    )

    parser.add_argument(
        'inputs',
        nargs='+',
        help='Files or directories to convert'
    )

    parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        help='Output directory for converted files'
    )

    parser.add_argument(
        '--tool',
        choices=['auto', 'pandoc', 'mineru'],
        default='auto',
        help='Conversion tool to use (default: auto)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable detailed output'
    )

    parser.add_argument(
        '--extract-media',
        action='store_true',
        help='Extract images to media folder'
    )

    parser.add_argument(
        '--embed-images',
        action='store_true',
        help='Embed images as Base64 (use with --extract-media)'
    )

    parser.add_argument(
        '--relative-images',
        action='store_true',
        help='Keep images as relative paths to media folder (implies --extract-media)'
    )

    parser.add_argument(
        '--skip-toc',
        action='store_true',
        help='Remove table of contents (Markdown has no page numbers)'
    )

    args = parser.parse_args()

    # Determine required tools
    needs_pandoc = args.tool in ['auto', 'pandoc']
    needs_mineru = args.tool == 'mineru' or (args.tool == 'auto' and check_mineru_available())

    # Check tool availability
    pandoc_ok = check_pandoc_installed()
    mineru_ok = check_mineru_available()

    if needs_pandoc and not pandoc_ok:
        print_installation_instructions()
        sys.exit(1)

    # Show version info if verbose
    if args.verbose:
        if args.tool in ['auto', 'pandoc'] and pandoc_ok:
            version = get_pandoc_version()
            print(f"Pandoc: {version}")
        if args.tool in ['auto', 'mineru'] and mineru_ok:
            print("MinerU: Available")
        print()

    # Convert files
    results = batch_convert(
        args.inputs,
        output_dir=args.output_dir,
        tool=args.tool,
        extract_media=args.extract_media,
        embed_images=args.embed_images,
        relative_images=args.relative_images,
        skip_toc=args.skip_toc,
        verbose=args.verbose
    )

    # Print summary
    print("\n" + "="*60)
    print("Conversion Summary")
    print("="*60)
    print(f"[OK] Success: {len(results['success'])}")
    print(f"[FAIL] Failed:  {len(results['failed'])}")
    print(f"[SKIP] Skipped: {len(results['skipped'])}")

    if results['failed']:
        print("\nFailed files:")
        for file_path, error in results['failed']:
            print(f"  - {file_path}: {error}")

    sys.exit(0 if not results['failed'] else 1)


if __name__ == '__main__':
    main()
