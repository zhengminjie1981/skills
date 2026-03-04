#!/usr/bin/env python3
"""
检查本地提取所需的依赖

用法:
    python check_dependencies.py

输出依赖状态和安装建议
"""

import sys
import shutil


def check_dependencies():
    """检查并报告依赖状态"""
    dependencies = {
        "PyMuPDF (fitz)": "fitz",
        "pdfplumber": "pdfplumber",
        "python-docx": "docx",
    }

    print("=" * 50)
    print("Knowledge Index - 本地提取依赖检查")
    print("=" * 50)
    print()

    results = {}
    for name, module in dependencies.items():
        try:
            __import__(module)
            results[name] = ("✓ 已安装", True)
        except ImportError:
            results[name] = ("✗ 未安装", False)
        print(f"  {name}: {results[name][0]}")

    # 检查 antiword
    print()
    if shutil.which("antiword"):
        print("  antiword: ✓ 已安装")
        antiword_installed = True
    else:
        print("  antiword: ✗ 未安装 (可选，用于 .doc 文件)")
        antiword_installed = False

    print()
    print("-" * 50)

    # 检查核心依赖
    pymupdf_ok = results["PyMuPDF (fitz)"][1]
    docx_ok = results["python-docx"][1]

    if pymupdf_ok and docx_ok:
        print()
        print("✓ 状态: 核心依赖已安装，可以使用 local 模式")
        print()
        print("支持格式:")
        print("  - PDF: PyMuPDF")
        print("  - DOCX: python-docx")
        if antiword_installed:
            print("  - DOC: antiword")
        else:
            print("  - DOC: 不支持 (需安装 antiword)")
    else:
        print()
        print("✗ 状态: 缺少核心依赖，local 模式不可用")
        print()
        print("安装命令:")
        print()
        print("  pip install PyMuPDF python-docx")
        print()
        print("可选增强:")
        print("  pip install pdfplumber  # PDF 备选方案")
        if sys.platform != "win32":
            print("  brew install antiword   # macOS .doc 支持")
            print("  apt install antiword    # Linux .doc 支持")

    print()
    print("=" * 50)

    return pymupdf_ok and docx_ok


if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)
