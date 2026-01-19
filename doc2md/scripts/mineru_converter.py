#!/usr/bin/env python3
"""
MinerU PDF to Markdown Converter

Advanced PDF parsing with OCR, table extraction, and layout recognition.
Best for scanned PDFs, complex tables, and academic papers.
"""

import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def check_mineru_installed() -> bool:
    """Check if MinerU is installed and accessible."""
    try:
        result = subprocess.run(
            ['mineru', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_mineru_python() -> bool:
    """Check if MinerU Python package is installed."""
    try:
        import importlib
        spec = importlib.util.find_spec("miner_u")
        return spec is not None
    except (ImportError, ModuleNotFoundError):
        return False


def get_output_path(input_path: str, output_dir: Optional[str] = None) -> str:
    """
    Determine output .md file path.

    Args:
        input_path: Path to input PDF
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


def convert_with_mineru_cli(
    input_path: str,
    output_path: Optional[str] = None,
    extract_images: bool = True,
    ocr_enabled: bool = True,
    formula_as_text: bool = False
) -> Tuple[Optional[str], bool]:
    """
    Convert PDF to Markdown using MinerU CLI.

    Args:
        input_path: Path to input PDF file
        output_path: Path to output .md file
        extract_images: Extract images to media folder
        ocr_enabled: Enable OCR for scanned PDFs
        formula_as_text: Convert LaTeX formulas to text

    Returns:
        Tuple of (output_path, success)
    """
    if output_path is None:
        output_path = get_output_path(input_path)

    # Determine output directory for MinerU
    output_dir = str(Path(output_path).parent)

    # Build mineru command
    # Note: Adjust command based on actual MinerU CLI interface
    cmd = [
        'mineru',
        input_path,
        '-o', output_dir,
        '--format', 'markdown'
    ]

    if extract_images:
        cmd.append('--extract-images')

    if ocr_enabled:
        cmd.append('--ocr')

    if formula_as_text:
        cmd.append('--formula-as-text')

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=300  # 5 minute timeout for PDF processing
        )

        # MinerU may output to a different filename, find the .md file
        output_files = list(Path(output_dir).glob('*.md'))

        if output_files:
            # Use the first .md file found
            generated_file = output_files[0]

            # If it's not the expected filename, rename it
            if str(generated_file) != output_path:
                generated_file.rename(output_path)

            return output_path, True
        else:
            return None, False

    except subprocess.CalledProcessError as e:
        print(f"Error: MinerU conversion failed: {e.stderr}")
        return None, False
    except subprocess.TimeoutExpired:
        print(f"Error: MinerU conversion timed out after 5 minutes")
        return None, False
    except Exception as e:
        print(f"Error: {e}")
        return None, False


def convert_with_mineru_python(
    input_path: str,
    output_path: Optional[str] = None,
    extract_images: bool = True
) -> Tuple[Optional[str], bool]:
    """
    Convert PDF to Markdown using MinerU Python API.

    This is the preferred method as it provides more control.

    Args:
        input_path: Path to input PDF file
        output_path: Path to output .md file
        extract_images: Extract images to media folder

    Returns:
        Tuple of (output_path, success)
    """
    try:
        # Try to import MinerU
        from mine_llu import extract_pdf_content

        if output_path is None:
            output_path = get_output_path(input_path)

        output_dir = str(Path(output_path).parent)

        # Extract content using MinerU
        result = extract_pdf_content(
            input_path,
            output_format='markdown',
            extract_images=extract_images,
            output_dir=output_dir
        )

        # Save the markdown content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['markdown'])

        return output_path, True

    except ImportError:
        # Fallback: try the package name variant
        try:
            from mineru import extract_pdf_content

            if output_path is None:
                output_path = get_output_path(input_path)

            output_dir = str(Path(output_path).parent)

            result = extract_pdf_content(
                input_path,
                output_format='markdown',
                extract_images=extract_images,
                output_dir=output_dir
            )

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result['markdown'])

            return output_path, True

        except ImportError as e:
            print(f"Error: MinerU Python package not installed: {e}")
            print("\nInstall with: pip install mineru")
            return None, False

    except Exception as e:
        print(f"Error during MinerU conversion: {e}")
        return None, False


def embed_images_as_base64(markdown_content: str, base_dir: str) -> str:
    """
    Embed images as Base64 in Markdown.

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

        if image_path.startswith('data:'):
            return match.group(0)

        full_path = Path(base_dir) / image_path if not Path(image_path).is_absolute() else Path(image_path)

        if not full_path.exists():
            return match.group(0)

        try:
            with open(full_path, 'rb') as img_file:
                image_data = img_file.read()
                encoded = base64.b64encode(image_data).decode('utf-8')

                ext = full_path.suffix.lower().lstrip('.')
                mime_type = {
                    'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png',
                    'gif': 'gif', 'svg': 'svg+xml'
                }.get(ext, ext)

                return f'![{alt_text}](data:image/{mime_type};base64,{encoded})'
        except Exception as e:
            print(f"Warning: Could not embed image {full_path}: {e}")
            return match.group(0)

    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    return re.sub(pattern, replace_image, markdown_content)


def remove_table_of_contents(markdown_content: str) -> str:
    """
    Remove table of contents from Markdown.

    Args:
        markdown_content: Markdown content potentially containing TOC

    Returns:
        Markdown with TOC removed
    """
    import re

    lines = markdown_content.split('\n')
    result_lines = []
    in_toc = False

    toc_headings = [
        'table of contents', 'contents', 'toc',
        '目录', '目　录', '索引',
        'table des matières', 'sommaire',
        'inhalt', 'inhaltsverzeichnis',
        'índice', 'tabla de contenidos',
    ]

    for line in lines:
        stripped = line.strip()

        # Check for TOC heading
        is_toc_heading = False
        for heading in toc_headings:
            if re.match(r'^#+\s*', stripped, re.IGNORECASE):
                heading_text = re.sub(r'^#+\s*', '', stripped, flags=re.IGNORECASE).lower().strip()
                if heading_text == heading.lower():
                    is_toc_heading = True
                    in_toc = True
                    break

        if is_toc_heading:
            continue

        # Detect end of TOC
        if in_toc:
            if re.match(r'^#+\s+', stripped) and not re.search(r'\.{2,}|\s+\d+\s*$', stripped):
                in_toc = False
                result_lines.append(line)
                continue

            if re.search(r'\.{2,}|\s+\d+\s*$', stripped):
                continue

        if not in_toc:
            result_lines.append(line)

    return '\n'.join(result_lines)


def convert_pdf(
    input_path: str,
    output_path: Optional[str] = None,
    extract_images: bool = True,
    embed_images: bool = False,
    relative_images: bool = False,
    skip_toc: bool = False,
    use_cli: bool = False,
    ocr_enabled: bool = True
) -> Tuple[Optional[str], bool]:
    """
    Convert PDF to Markdown using MinerU.

    Args:
        input_path: Path to input PDF
        output_path: Path to output .md file
        extract_images: Extract images to media folder
        embed_images: Embed images as Base64
        relative_images: Keep images as relative paths (implies extract_images)
        skip_toc: Remove table of contents
        use_cli: Use CLI instead of Python API
        ocr_enabled: Enable OCR

    Returns:
        Tuple of (output_path, success)
    """
    # Choose conversion method
    if use_cli:
        output_path, success = convert_with_mineru_cli(
            input_path, output_path, extract_images, ocr_enabled
        )
    else:
        output_path, success = convert_with_mineru_python(
            input_path, output_path, extract_images
        )

    if not success:
        return None, False

    # Post-process the Markdown
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if skip_toc:
        content = remove_table_of_contents(content)

    # Embed images only if not using relative_images
    if embed_images and extract_images and not relative_images:
        media_dir = str(Path(output_path).parent / 'media')
        if Path(media_dir).exists():
            content = embed_images_as_base64(content, media_dir)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_path, True


def print_installation_instructions():
    """Print MinerU installation instructions."""
    import platform
    system = platform.system()

    print("\n" + "="*60)
    print("MINERU NOT FOUND")
    print("="*60)
    print("\nMinerU is required for advanced PDF conversion.")
    print("\nInstallation instructions:\n")

    print("Python package (recommended):")
    print("  pip install mineru")

    print("\nOr from source:")
    print("  git clone https://github.com/opendatalab/MinerU.git")
    print("  cd MinerU")
    print("  pip install -e .")

    if system == "Windows":
        print("\nWindows requirements:")
        print("  pip install pywin32")

    print("\nAfter installation, restart your terminal and try again.")
    print("="*60 + "\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Convert PDF to Markdown using MinerU',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
MinerU provides advanced PDF parsing with:
- OCR for scanned documents
- Intelligent table extraction
- Layout recognition
- Formula parsing (LaTeX)
- Multi-language support

Examples:
  # Convert a PDF
  %(prog)s document.pdf

  # Convert with image extraction
  %(prog)s document.pdf --extract-images

  # Convert with relative image paths
  %(prog)s document.pdf --relative-images

  # Convert and embed images
  %(prog)s document.pdf --embed-images

  # Remove table of contents
  %(prog)s document.pdf --skip-toc
        """
    )

    parser.add_argument(
        'input',
        help='PDF file to convert'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output Markdown file path'
    )

    parser.add_argument(
        '--extract-images',
        action='store_true',
        default=True,
        help='Extract images to media folder (default: True)'
    )

    parser.add_argument(
        '--no-extract-images',
        action='store_false',
        dest='extract_images',
        help='Do not extract images'
    )

    parser.add_argument(
        '--embed-images',
        action='store_true',
        help='Embed images as Base64 (creates self-contained file)'
    )

    parser.add_argument(
        '--relative-images',
        action='store_true',
        help='Keep images as relative paths to media folder'
    )

    parser.add_argument(
        '--skip-toc',
        action='store_true',
        help='Remove table of contents'
    )

    parser.add_argument(
        '--use-cli',
        action='store_true',
        help='Use MinerU CLI instead of Python API'
    )

    parser.add_argument(
        '--no-ocr',
        action='store_false',
        dest='ocr_enabled',
        help='Disable OCR (only for CLI mode)'
    )

    args = parser.parse_args()

    # Check input file
    if not Path(args.input).exists():
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    # Check MinerU installation
    has_cli = check_mineru_installed()
    has_python = check_mineru_python()

    if args.use_cli and not has_cli:
        print("Error: MinerU CLI not found. Install MinerU or use Python API.")
        print_installation_instructions()
        sys.exit(1)

    if not args.use_cli and not has_python:
        print("Error: MinerU Python package not found.")
        print_installation_instructions()
        sys.exit(1)

    # Convert
    output_path, success = convert_pdf(
        args.input,
        output_path=args.output,
        extract_images=args.extract_images,
        embed_images=args.embed_images,
        relative_images=args.relative_images,
        skip_toc=args.skip_toc,
        use_cli=args.use_cli,
        ocr_enabled=args.ocr_enabled
    )

    if success:
        print(f"[OK] Converted: {args.input} -> {output_path}")
        sys.exit(0)
    else:
        print(f"[FAIL] Conversion failed: {args.input}")
        sys.exit(1)


if __name__ == '__main__':
    main()
