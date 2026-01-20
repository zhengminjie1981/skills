#!/usr/bin/env python3
"""
Portable runtime manager for Doc2Md.

Automatically manages bundled tools (Pandoc) or uses system-installed ones.
Supports cross-platform portable execution.
"""

import os
import sys
import subprocess
import platform
import urllib.request
import tarfile
import zipfile
from pathlib import Path


# Version pins for predictable behavior
PANDOC_VERSION = "3.1.11"
PANDOC_DOWNLOADS = {
    "Windows": "https://github.com/jgm/pandoc/releases/download/{ver}/pandoc-{ver}-windows-x86_64.zip",
    "Darwin": "https://github.com/jgm/pandoc/releases/download/{ver}/pandoc-{ver}-x86_64-macOS.zip",
    "Linux": "https://github.com/jgm/pandoc/releases/download/{ver}/pandoc-{ver}-linux-amd64.tar.gz",
}


class PortableRuntime:
    """Manage portable runtime for cross-platform execution."""

    def __init__(self, project_root: Path = None):
        if project_root is None:
            # Default to script directory / project root
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)

        self.bin_dir = self.project_root / "bin"
        self.pandoc_dir = self.bin_dir / "pandoc"
        self.platform = platform.system()
        self.machine = platform.machine().lower()

    def get_pandoc_executable(self) -> Path:
        """Get path to pandoc executable (portable or system)."""
        # Try portable first
        portable_pandoc = self._get_portable_pandoc()
        if portable_pandoc and portable_pandoc.exists():
            return portable_pandoc

        # Fall back to system pandoc
        system_pandoc = self._get_system_pandoc()
        if system_pandoc:
            return Path(system_pandoc)

        return None

    def _get_portable_pandoc(self) -> Path:
        """Get portable pandoc path."""
        if self.platform == "Windows":
            return self.pandoc_dir / "pandoc.exe"
        else:
            return self.pandoc_dir / "bin" / "pandoc"

    def _get_system_pandoc(self) -> str:
        """Check for system-installed pandoc."""
        try:
            result = subprocess.run(
                ["pandoc", "--version"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                return "pandoc"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return None

    def is_pandoc_available(self) -> bool:
        """Check if pandoc is available (portable or system)."""
        return self.get_pandoc_executable() is not None

    def ensure_pandoc(self, auto_install: bool = False) -> bool:
        """
        Ensure pandoc is available.

        Args:
            auto_install: If True, download portable pandoc if missing

        Returns:
            True if pandoc is available
        """
        if self.is_pandoc_available():
            return True

        if not auto_install:
            return False

        print("Pandoc not found. Downloading portable version...")
        return self._download_pandoc()

    def _download_pandoc(self) -> bool:
        """Download and extract portable pandoc."""
        try:
            url_template = PANDOC_DOWNLOADS.get(self.platform)
            if not url_template:
                print(f"Unsupported platform: {self.platform}")
                return False

            url = url_template.format(ver=PANDOC_VERSION)
            self.bin_dir.mkdir(parents=True, exist_ok=True)

            # Download
            download_path = self.bin_dir / f"pandoc-{PANDOC_VERSION}.pkg"
            print(f"Downloading from {url}...")

            urllib.request.urlretrieve(url, download_path)

            # Extract
            print("Extracting...")
            self._extract_archive(download_path)

            # Cleanup
            download_path.unlink()

            print(f"Pandoc installed to: {self.pandoc_dir}")
            return True

        except Exception as e:
            print(f"Failed to download pandoc: {e}")
            return False

    def _extract_archive(self, archive_path: Path):
        """Extract downloaded archive."""
        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path, 'r') as zf:
                # Extract to bin dir, handle nested structure
                members = zf.namelist()
                for member in members:
                    # Extract pandoc executable directly
                    if "pandoc.exe" in member or member.endswith("/bin/pandoc"):
                        # Get the file part
                        parts = Path(member).parts
                        if "pandoc.exe" in member:
                            zf.extract(member, self.bin_dir)
                            # Move to expected location
                            extracted = self.bin_dir / member
                            if extracted.exists():
                                extracted.rename(self._get_portable_pandoc())
                        elif member.endswith("/bin/pandoc"):
                            zf.extract(member, self.bin_dir)
                            extracted = self.bin_dir / member
                            if extracted.exists():
                                extracted.rename(self._get_portable_pandoc())

        elif archive_path.suffix in (".gz", ".tgz"):
            with tarfile.open(archive_path, 'r:gz') as tf:
                tf.extractall(self.bin_dir)

    def get_python_packages_status(self) -> dict:
        """Check status of required Python packages."""
        packages = {
            "mineru": False,
            "pymupdf": False,
        }

        for pkg in packages:
            try:
                # Try alternative import names
                if pkg == "pymupdf":
                    try:
                        __import__("fitz")
                        packages[pkg] = True
                    except ImportError:
                        __import__("PyMuPDF")
                        packages[pkg] = True
                else:
                    __import__(pkg)
                    packages[pkg] = True
            except ImportError:
                pass

        return packages

    def print_status(self):
        """Print current runtime status."""
        print("\n=== Doc2Md Runtime Status ===")
        print(f"Project Root: {self.project_root}")
        print(f"Platform: {self.platform}")

        # Pandoc status
        pandoc_path = self.get_pandoc_executable()
        if pandoc_path:
            print(f"Pandoc: ✓ {pandoc_path}")
            # Get version
            try:
                result = subprocess.run(
                    [str(pandoc_path), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    version = result.stdout.split('\n')[0]
                    print(f"  Version: {version}")
            except:
                pass
        else:
            print("Pandoc: ✗ Not found")

        # Python packages
        packages = self.get_python_packages_status()
        print(f"\nPython Packages:")
        for pkg, installed in packages.items():
            status = "✓" if installed else "✗"
            print(f"  {pkg}: {status}")

        print("=" * 40 + "\n")


def create_bootstrap_script():
    """Create bootstrap scripts for portable execution."""
    bat_content = """@echo off
REM Doc2Md Portable Launcher for Windows

set SCRIPT_DIR=%~dp0
set PYTHONPATH=%SCRIPT_DIR%;%PYTHONPATH%

REM Try portable Python first, then system Python
if exist "%SCRIPT_DIR%\\bin\\python\\python.exe" (
    "%SCRIPT_DIR%\\bin\\python\\python.exe" "%SCRIPT_DIR%\\scripts\\converter.py" %*
) else (
    python "%SCRIPT_DIR%\\scripts\\converter.py" %*
)
"""

    sh_content = """#!/bin/bash
# Doc2Md Portable Launcher for Unix (macOS/Linux)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Try portable Python first, then system Python
if [ -f "${SCRIPT_DIR}/bin/python/bin/python" ]; then
    "${SCRIPT_DIR}/bin/python/bin/python" "${SCRIPT_DIR}/scripts/converter.py" "$@"
else
    python "${SCRIPT_DIR}/scripts/converter.py" "$@"
fi
"""

    project_root = Path(__file__).parent.parent

    # Write Windows launcher
    bat_path = project_root / "doc2md.bat"
    bat_path.write_text(bat_content)

    # Write Unix launcher
    sh_path = project_root / "doc2md.sh"
    sh_path.write_text(sh_content)
    sh_path.chmod(0o755)

    print(f"Created: {bat_path}")
    print(f"Created: {sh_path}")


if __name__ == "__main__":
    runtime = PortableRuntime()
    runtime.print_status()

    # Check if we can run
    if not runtime.is_pandoc_available():
        print("\nPandoc not found.")
        print("Options:")
        print("  1. Install system-wide: choco/brew/apt install pandoc")
        print("  2. Download portable: python scripts/portable_runtime.py --download-pandoc")
        print("  3. Use with --auto-install to download automatically")
