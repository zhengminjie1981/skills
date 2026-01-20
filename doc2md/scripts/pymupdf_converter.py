#!/usr/bin/env python3
"""
PyMuPDF PDF to Markdown Converter

Lightweight PDF parsing using PyMuPDF (fitz).
Best for simple text-based PDFs. Compatible with Python 3.14+.

Limitations:
- No OCR support (text-based PDFs only)
- Basic table extraction (not as advanced as MinerU)
- No formula parsing
"""

import base64
import re
from pathlib import Path
from typing import List, Optional, Tuple


def check_pymupdf_installed() -> bool:
    """Check if PyMuPDF is installed."""
    try:
        import importlib.util
        spec = importlib.util.find_spec("PyMuPDF") or importlib.util.find_spec("fitz")
        return spec is not None
    except Exception:
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


def detect_heading_level(text: str, font_size: float, base_size: float = 12.0) -> Optional[int]:
    """
    Detect heading level based on font size.

    Args:
        text: Text content
        font_size: Font size in points
        base_size: Base font size for comparison

    Returns:
        Heading level (1-6) or None
    """
    # Skip empty lines
    if not text.strip():
        return None

    # Size ratios for heading detection
    if font_size >= base_size * 1.8:
        return 1
    elif font_size >= base_size * 1.5:
        return 2
    elif font_size >= base_size * 1.3:
        return 3
    elif font_size >= base_size * 1.15:
        return 4
    elif font_size >= base_size * 1.05:
        return 5
    elif font_size > base_size:
        return 6

    return None


def extract_images_from_page(page, page_num: int, media_dir: Path) -> List[str]:
    """
    Extract images from a PDF page.

    Args:
        page: PyMuPDF page object
        page_num: Page number (0-based)
        media_dir: Directory to save images

    Returns:
        List of extracted image paths
    """
    image_list = page.get_images()
    extracted_paths = []

    for img_index, img in enumerate(image_list):
        try:
            xref = img[0]
            base_image = page.parent.extract_image(xref)

            if base_image:
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # Save image
                image_filename = f"page{page_num + 1}_img{img_index + 1}.{image_ext}"
                image_path = media_dir / image_filename

                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                extracted_paths.append(str(image_path))
        except Exception as e:
            print(f"Warning: Could not extract image {img_index} from page {page_num + 1}: {e}")
            continue

    return extracted_paths


def convert_pdf(
    input_path: str,
    output_path: Optional[str] = None,
    extract_images: bool = True,
    embed_images: bool = False,
    relative_images: bool = False,
    skip_toc: bool = False,
    **kwargs
) -> Tuple[Optional[str], bool]:
    """
    Convert PDF to Markdown using PyMuPDF.

    Args:
        input_path: Path to input PDF
        output_path: Path to output .md file
        extract_images: Extract images to media folder
        embed_images: Embed images as Base64
        relative_images: Keep images as relative paths (implies extract_images)
        skip_toc: Remove table of contents
        **kwargs: Additional arguments (unused)

    Returns:
        Tuple of (output_path, success)
    """
    # Check PyMuPDF availability
    if not check_pymupdf_installed():
        print("Error: PyMuPDF is not installed.")
        print("Install with: pip install PyMuPDF")
        return None, False

    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("Error: Could not import PyMuPDF (fitz).")
        print("Install with: pip install PyMuPDF")
        return None, False

    # Determine output path
    if output_path is None:
        output_path = get_output_path(input_path)

    output_path_obj = Path(output_path)
    media_dir = output_path_obj.parent / 'media'

    # Create media directory if extracting images
    if extract_images:
        media_dir.mkdir(parents=True, exist_ok=True)

    # Open PDF
    try:
        doc = fitz.open(input_path)
    except Exception as e:
        print(f"Error: Could not open PDF: {e}")
        return None, False

    # Track extracted images
    image_counter = 0
    image_map = {}  # Map page positions to image paths

    # Extract images first (if requested)
    if extract_images:
        for page_num in range(len(doc)):
            page = doc[page_num]
            images = extract_images_from_page(page, page_num, media_dir)
            for img_path in images:
                image_map[(page_num, image_counter)] = img_path
                image_counter += 1

    # Convert pages to Markdown
    markdown_lines = []
    prev_font_size = None
    base_font_size = 12.0

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block["type"] == 0:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        font_size = span["size"]

                        # Skip empty text
                        if not text.strip():
                            markdown_lines.append("")
                            continue

                        # Detect headings
                        heading_level = detect_heading_level(text, font_size, base_font_size)

                        if heading_level:
                            # Remove extra whitespace
                            text = text.strip()
                            markdown_lines.append(f"{'#' * heading_level} {text}")
                        else:
                            # Regular paragraph
                            # Check if it looks like a list item
                            if re.match(r'^\s*[\-\*\+•]\s', text):
                                markdown_lines.append(text)
                            elif re.match(r'^\s*\d+\.\s', text):
                                markdown_lines.append(text)
                            else:
                                markdown_lines.append(text)

            elif block["type"] == 1 and extract_images:  # Image block
                # Add image reference
                img_key = (page_num, image_counter)
                if img_key in image_map:
                    img_path = image_map[img_key]

                    if relative_images or embed_images:
                        # Use relative path
                        relative_path = f"media/{Path(img_path).name}"
                        markdown_lines.append(f"![Image]({relative_path})")
                    else:
                        # Use absolute path
                        markdown_lines.append(f"![Image]({img_path})")

                    image_counter += 1

    doc.close()

    # Join lines and clean up
    markdown_content = "\n".join(markdown_lines)

    # Remove table of contents if requested
    if skip_toc:
        markdown_content = remove_table_of_contents(markdown_content)

    # Embed images if requested (skip when using relative_images)
    if embed_images and extract_images and not relative_images:
        markdown_content = embed_images_as_base64(markdown_content, str(media_dir))

    # Write output file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    except Exception as e:
        print(f"Error: Could not write output file: {e}")
        return None, False

    return output_path, True


def embed_images_as_base64(markdown_content: str, base_dir: str) -> str:
    """
    Embed images as Base64 in Markdown.

    Args:
        markdown_content: Markdown content with image references
        base_dir: Base directory for resolving relative image paths

    Returns:
        Markdown with Base64 embedded images
    """
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


def print_installation_instructions():
    """Print PyMuPDF installation instructions."""
    print("\n" + "="*60)
    print("PYMUPDF NOT FOUND")
    print("="*60)
    print("\nPyMuPDF is required for PDF conversion.")
    print("\nInstallation instructions:\n")
    print("  pip install PyMuPDF")
    print("\nAfter installation, restart your terminal and try again.")
    print("="*60 + "\n")


def main():
    """Main CLI entry point."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description='Convert PDF to Markdown using PyMuPDF',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
PyMuPDF provides lightweight PDF parsing with:
- Text extraction from PDFs
- Basic layout recognition
- Image extraction
- Compatible with Python 3.14+

Limitations:
- No OCR support (text-based PDFs only)
- Basic table extraction
- No formula parsing

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

    args = parser.parse_args()

    # Check input file
    if not Path(args.input).exists():
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    # Convert
    output_path, success = convert_pdf(
        args.input,
        output_path=args.output,
        extract_images=args.extract_images,
        embed_images=args.embed_images,
        relative_images=args.relative_images,
        skip_toc=args.skip_toc
    )

    if success:
        print(f"[OK] Converted: {args.input} -> {output_path}")
        sys.exit(0)
    else:
        print(f"[FAIL] Conversion failed: {args.input}")
        sys.exit(1)


if __name__ == '__main__':
    main()
