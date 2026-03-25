"""
html2pdf.py - HTML presentation to PDF converter
Requires: playwright, pypdf
"""
import pathlib, json, io, argparse, sys, os, subprocess


def _check_playwright() -> bool:
    """Check if playwright is importable in the current Python env."""
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        return True
    except ImportError:
        return False


def _find_browser() -> str | None:
    """
    Detect available browser in priority order: Edge → Chrome → Chromium.
    Uses executable path checks (fast, no browser launch needed).
    Returns channel name ('msedge', 'chrome', 'chromium') or None.
    """
    # Known executable paths per platform
    candidates = {
        "msedge": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/usr/bin/microsoft-edge",
        ],
        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
        ],
    }

    for channel, paths in candidates.items():
        for exe in paths:
            if pathlib.Path(exe).exists():
                print(f"  Found {channel}: {exe}")
                return channel
        print(f"  {channel}: not found")

    # Fall back to playwright-managed Chromium
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            path = pathlib.Path(p.chromium.executable_path)
            if path.exists():
                print(f"  Found chromium (playwright managed): {path}")
                return "chromium"
            print("  chromium (playwright managed): not found")
    except Exception:
        pass

    return None


def _check_pypdf() -> bool:
    try:
        import pypdf  # noqa: F401
        return True
    except ImportError:
        return False


def print_install_guide():
    """Print installation instructions when no browser is available."""
    print("""
No usable browser found. To enable PDF export, choose one option:

  Option A - Use system Edge or Chrome (recommended, no extra download):
    pip install playwright pypdf
    (Edge/Chrome will be detected automatically)

  Option B - Download playwright's Chromium (~200 MB):
    pip install playwright pypdf
    playwright install chromium

  Option C - Manual export via browser (no install needed):
    1. Open the HTML file in Chrome/Edge
    2. Press Ctrl+P -> Save as PDF
    3. Check "Background graphics"
    Note: Charts may not render correctly with this method.
""")


def merge_pdfs(pdf_bytes_list: list[bytes], output_path: pathlib.Path):
    from pypdf import PdfWriter, PdfReader
    writer = PdfWriter()
    for pdf_bytes in pdf_bytes_list:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)


def html_to_pdf(
    html_path: pathlib.Path,
    pdf_path: pathlib.Path,
    tree_path: pathlib.Path | None = None,
    wait_ms: int = 1500,
    browser_channel: str | None = None,
):
    from playwright.sync_api import sync_playwright

    html_abs = str(html_path.resolve())

    # Resolve tree file: explicit arg > same-stem-tree.json > slide-tree.json
    if tree_path is None:
        stem_tree = html_path.parent / (html_path.stem + "-tree.json")
        default_tree = html_path.parent / "slide-tree.json"
        tree_path = stem_tree if stem_tree.exists() else default_tree

    if tree_path.exists():
        tree  = json.loads(tree_path.read_text(encoding="utf-8"))
        ratio = tree["presentation"]["ratio"]
        total = tree["presentation"]["totalSlides"]
    else:
        # fallback: parse from HTML
        import re
        html_content = html_path.read_text(encoding="utf-8")
        m = re.search(r"width:\s*(\d+)px.*?height:\s*(\d+)px", html_content, re.DOTALL)
        width, height = (int(m.group(1)), int(m.group(2))) if m else (1280, 720)
        ratio = "16:9"
        total = html_content.count('class="slide"')

    width, height = (1280, 720) if ratio == "16:9" else (1024, 768)

    browser_label = browser_channel if browser_channel else "chromium (managed)"
    print(f"Converting {html_path.name} ({total} slides, {width}x{height}px) via {browser_label}...")

    pdf_pages: list[bytes] = []

    with sync_playwright() as p:
        if browser_channel in ("msedge", "chrome"):
            browser = p.chromium.launch(channel=browser_channel)
        else:
            browser = p.chromium.launch()

        page = browser.new_page(viewport={"width": width, "height": height})

        file_url = f"file:///{html_abs.replace(os.sep, '/')}"
        page.goto(file_url)
        page.wait_for_timeout(wait_ms)

        # Fix black borders: body bg is #000 for browser presentation,
        # but for PDF we need transparent body + slide filling the full page.
        # Also lock scale=1 so CSS transform doesn't leave gaps at edges.
        page.add_style_tag(content="""
            body { background: transparent !important; }
            #presentation { transform: none !important; }
            #page-counter, #progress-bar { display: none !important; }
            .slide.active {
                position: relative !important;
                width: 100% !important; height: 100% !important;
            }
        """)

        for i in range(total):
            page.evaluate(f"goTo({i})")
            page.wait_for_timeout(80)

            single_pdf = page.pdf(
                width=f"{width}px",
                height=f"{height}px",
                print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            )
            pdf_pages.append(single_pdf)
            print(f"  Page {i+1}/{total}", end="\r", flush=True)

        browser.close()

    print()
    merge_pdfs(pdf_pages, pdf_path)
    size_kb = pdf_path.stat().st_size // 1024
    print(f"PDF generated: {pdf_path}  ({total} pages, {size_kb} KB)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert HTML presentation to PDF")
    parser.add_argument("--input",   required=True, help="Input .html file")
    parser.add_argument("--output",  help="Output .pdf file (default: same name as input)")
    parser.add_argument("--tree",    help="slide-tree.json path (auto-detected if omitted)")
    parser.add_argument("--wait",    type=int, default=1500,
                        help="Wait ms for JS rendering (default: 1500)")
    parser.add_argument("--browser", choices=["msedge", "chrome", "chromium"],
                        help="Force a specific browser (default: auto-detect)")
    args = parser.parse_args()

    if not _check_playwright():
        print("Error: playwright is not installed.")
        print_install_guide()
        sys.exit(1)

    if not _check_pypdf():
        print("Error: pypdf is not installed.")
        print("Install with: pip install pypdf")
        sys.exit(1)

    # Resolve browser
    if args.browser:
        channel = args.browser
        print(f"Using browser: {channel} (forced via --browser)")
    else:
        channel = _find_browser()
        if channel is None:
            print("Error: no usable browser found (Edge, Chrome, or playwright Chromium).")
            print_install_guide()
            sys.exit(1)
        print(f"Using browser: {channel} (auto-detected)")

    inp  = pathlib.Path(args.input)
    out  = pathlib.Path(args.output) if args.output else inp.with_suffix(".pdf")
    tree = pathlib.Path(args.tree) if args.tree else None

    html_to_pdf(inp, out, tree_path=tree, wait_ms=args.wait, browser_channel=channel)
