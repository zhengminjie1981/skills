"""
preview.py - Generate thumbnail screenshots for all slides in an HTML presentation.
Requires: playwright

Usage:
    # Persistent preview (kept in preview/ next to HTML)
    python scripts/preview.py --input demo.html

    # Temporary preview (system temp dir, print paths, auto-clean on --clean)
    python scripts/preview.py --input demo.html --temp

    # Clean up temp previews for a given HTML file
    python scripts/preview.py --input demo.html --clean
"""
import pathlib, json, argparse, sys, os, tempfile, shutil

# Reuse browser detection from html2pdf
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from html2pdf import _check_playwright, _find_browser, print_install_guide

# Inject same CSS as PDF export: transparent body, no scaling, hide UI chrome
_PREVIEW_CSS = """
    body { background: transparent !important; }
    #presentation { transform: none !important; }
    #page-counter, #progress-bar { display: none !important; }
    .slide.active {
        position: relative !important;
        width: 100% !important; height: 100% !important;
    }
"""

# Registry file: maps html absolute path -> temp dir, so --clean knows where to look
_REGISTRY = pathlib.Path(tempfile.gettempdir()) / "md2slides_preview_registry.json"


def _registry_get(html_key: str) -> str | None:
    if not _REGISTRY.exists():
        return None
    data = json.loads(_REGISTRY.read_text(encoding="utf-8"))
    return data.get(html_key)


def _registry_set(html_key: str, tmp_dir: str):
    data = {}
    if _REGISTRY.exists():
        data = json.loads(_REGISTRY.read_text(encoding="utf-8"))
    data[html_key] = tmp_dir
    _REGISTRY.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _registry_remove(html_key: str):
    if not _REGISTRY.exists():
        return
    data = json.loads(_REGISTRY.read_text(encoding="utf-8"))
    data.pop(html_key, None)
    _REGISTRY.write_text(json.dumps(data, indent=2), encoding="utf-8")


def clean_temp(html_path: pathlib.Path):
    """Delete temp preview dir registered for this HTML file."""
    key = str(html_path.resolve())
    tmp_dir = _registry_get(key)
    if tmp_dir and pathlib.Path(tmp_dir).exists():
        shutil.rmtree(tmp_dir)
        _registry_remove(key)
        print(f"Cleaned: {tmp_dir}")
    else:
        print(f"Nothing to clean for: {html_path.name}")


def html_to_previews(
    html_path: pathlib.Path,
    out_dir: pathlib.Path,
    tree_path: pathlib.Path | None = None,
    width: int = 640,
    wait_ms: int = 1000,
    browser_channel: str | None = None,
    temp: bool = False,
) -> pathlib.Path:
    """Generate slide previews. Returns the output directory path."""
    from playwright.sync_api import sync_playwright

    html_abs = str(html_path.resolve())

    # Resolve tree file
    if tree_path is None:
        slides_dir_tree = html_path.parent / ".slides" / (html_path.stem + ".slide-tree.json")
        stem_tree       = html_path.parent / (html_path.stem + "-tree.json")
        default_tree    = html_path.parent / "slide-tree.json"
        if slides_dir_tree.exists():
            tree_path = slides_dir_tree
        elif stem_tree.exists():
            tree_path = stem_tree
        else:
            tree_path = default_tree

    if tree_path.exists():
        tree  = json.loads(tree_path.read_text(encoding="utf-8"))
        ratio = tree["presentation"]["ratio"]
        total = tree["presentation"]["totalSlides"]
    else:
        import re
        html_content = html_path.read_text(encoding="utf-8")
        ratio = "16:9"
        total = html_content.count('class="slide"')

    slide_w, slide_h = (1280, 720) if ratio == "16:9" else (1024, 768)
    thumb_h = int(slide_h * width / slide_w)

    # Resolve output directory
    if temp:
        tmp_dir = tempfile.mkdtemp(prefix="md2slides_")
        out_dir = pathlib.Path(tmp_dir)
        _registry_set(str(html_path.resolve()), tmp_dir)
    else:
        out_dir.mkdir(parents=True, exist_ok=True)

    browser_label = browser_channel or "chromium (managed)"
    print(f"Generating {total} previews ({width}x{thumb_h}px) via {browser_label}...")

    with sync_playwright() as p:
        if browser_channel in ("msedge", "chrome"):
            browser = p.chromium.launch(channel=browser_channel)
        else:
            browser = p.chromium.launch()

        page = browser.new_page(viewport={"width": slide_w, "height": slide_h})

        file_url = f"file:///{html_abs.replace(os.sep, '/')}"
        page.goto(file_url)
        page.wait_for_timeout(wait_ms)
        page.add_style_tag(content=_PREVIEW_CSS)

        for i in range(total):
            page.evaluate(f"goTo({i})")
            page.wait_for_timeout(50)
            out_file = out_dir / f"slide-{i+1:02d}.png"
            page.screenshot(
                path=str(out_file),
                clip={"x": 0, "y": 0, "width": slide_w, "height": slide_h},
            )
            if width != slide_w:
                _resize_image(out_file, width, thumb_h)
            print(f"  [{i+1:02d}/{total}] {out_file.name}", end="\r", flush=True)

        browser.close()

    print(f"\nPreviews saved to: {out_dir}  ({total} files)")
    if temp:
        print(f"Temp dir — clean up when done:")
        print(f"  python scripts/preview.py --input {html_path} --clean")

    return out_dir


def _resize_image(path: pathlib.Path, width: int, height: int):
    """Resize PNG using Pillow if available, otherwise keep full resolution."""
    try:
        from PIL import Image
        img = Image.open(path)
        img = img.resize((width, height), Image.LANCZOS)
        img.save(path)
    except ImportError:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate slide preview thumbnails")
    parser.add_argument("--input",   required=True, help="Input .html file")
    parser.add_argument("--output",  help="Output directory (default: preview/ next to HTML)")
    parser.add_argument("--tree",    help="slide-tree.json path (auto-detected if omitted)")
    parser.add_argument("--width",   type=int, default=640,
                        help="Thumbnail width in px (default: 640)")
    parser.add_argument("--wait",    type=int, default=1000,
                        help="Wait ms for JS/chart rendering (default: 1000)")
    parser.add_argument("--browser", choices=["msedge", "chrome", "chromium"],
                        help="Force a specific browser (default: auto-detect)")
    parser.add_argument("--temp",    action="store_true",
                        help="Save to system temp dir (register for --clean)")
    parser.add_argument("--clean",   action="store_true",
                        help="Delete temp preview dir registered for this HTML file")
    args = parser.parse_args()

    inp = pathlib.Path(args.input)

    if args.clean:
        clean_temp(inp)
        sys.exit(0)

    if not _check_playwright():
        print("Error: playwright is not installed.")
        print_install_guide()
        sys.exit(1)

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

    out  = pathlib.Path(args.output) if args.output else inp.parent / "preview"
    tree = pathlib.Path(args.tree) if args.tree else None

    html_to_previews(inp, out, tree_path=tree, width=args.width,
                     wait_ms=args.wait, browser_channel=channel, temp=args.temp)
