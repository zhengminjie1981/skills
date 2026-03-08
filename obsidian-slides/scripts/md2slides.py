#!/usr/bin/env python3
"""
Markdown to Obsidian Slides 转换脚本

功能：
- 自动根据 H1/H2 分页
- 自动添加 frontmatter
- 可选应用主题
- 支持深浅主题切换

用法：
    python md2slides.py input.md -o output.md --theme dark
    python md2slides.py input.md -o output.md --theme light
    python md2slides.py input.md -o output.md --theme night --template product-pitch
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional


# 主题配置
THEMES = {
    "dark": {
        "theme": "night",
        "description": "深色主题",
    },
    "light": {
        "theme": "white",
        "description": "浅色主题",
    },
    "night": {
        "theme": "night",
        "description": "深蓝黑底",
    },
    "black": {
        "theme": "black",
        "description": "纯黑底",
    },
    "white": {
        "theme": "white",
        "description": "纯白底",
    },
    "league": {
        "theme": "league",
        "description": "灰色背景",
    },
}


def generate_frontmatter(theme: str = "night", slide_number: bool = True) -> str:
    """生成 frontmatter"""
    theme_config = THEMES.get(theme, THEMES["night"])

    frontmatter = f'''---
slideOptions:
  theme: {theme_config["theme"]}
  transition: slide
  slideNumber: {"true" if slide_number else "false"}
---

'''
    return frontmatter


def split_by_headers(content: str, level: int = 2) -> list[str]:
    """根据标题级别分割内容"""
    # 使用正则表达式找到标题
    pattern = rf'^(#{{{level}}})\s+(.+)$'
    lines = content.split('\n')

    slides = []
    current_slide = []

    for line in lines:
        match = re.match(pattern, line)
        if match:
            if current_slide:
                slides.append('\n'.join(current_slide))
            current_slide = [line]
        else:
            current_slide.append(line)

    if current_slide:
        slides.append('\n'.join(current_slide))

    return slides


def add_slide_separators(content: str) -> str:
    """添加幻灯片分隔符"""
    lines = content.split('\n')
    result = []
    prev_was_separator = True  # 开头不需要分隔符

    for line in lines:
        # 检测 H1 或 H2 标题
        is_h1 = line.startswith('# ') and not line.startswith('## ')
        is_h2 = line.startswith('## ') and not line.startswith('### ')

        if (is_h1 or is_h2) and not prev_was_separator:
            result.append('')
            result.append('---')
            result.append('')

        result.append(line)
        prev_was_separator = line.strip() == '---'

    return '\n'.join(result)


def convert_to_slides(
    input_content: str,
    theme: str = "night",
    split_by_h1: bool = False,
    slide_number: bool = True,
) -> str:
    """
    将 Markdown 转换为 Obsidian Slides 格式

    Args:
        input_content: 输入的 Markdown 内容
        theme: 主题名称
        split_by_h1: 是否按 H1 分页（默认按 H2）
        slide_number: 是否显示页码

    Returns:
        转换后的 Obsidian Slides Markdown
    """
    # 生成 frontmatter
    frontmatter = generate_frontmatter(theme, slide_number)

    # 移除原有的 frontmatter（如果存在）
    content = input_content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    # 添加幻灯片分隔符
    if split_by_h1:
        slides = split_by_headers(content, level=1)
        content = '\n\n---\n\n'.join(slides)
    else:
        content = add_slide_separators(content)

    # 清理多余的空行
    content = re.sub(r'\n{4,}', '\n\n\n', content)

    return frontmatter + content


def main():
    parser = argparse.ArgumentParser(
        description="将 Markdown 转换为 Obsidian Slides 格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本转换（深色主题）
  python md2slides.py document.md -o slides.md

  # 指定浅色主题
  python md2slides.py document.md -o slides.md --theme light

  # 按 H1 分页
  python md2slides.py document.md -o slides.md --split-h1

  # 不显示页码
  python md2slides.py document.md -o slides.md --no-slide-number
        """,
    )

    parser.add_argument("input", help="输入的 Markdown 文件")
    parser.add_argument("-o", "--output", help="输出文件路径（默认：打印到标准输出）")
    parser.add_argument(
        "--theme",
        choices=list(THEMES.keys()),
        default="dark",
        help=f"主题选择（默认：dark）",
    )
    parser.add_argument(
        "--split-h1",
        action="store_true",
        help="按 H1 标题分页（默认按 H2）",
    )
    parser.add_argument(
        "--no-slide-number",
        action="store_true",
        help="不显示页码",
    )

    args = parser.parse_args()

    # 读取输入文件
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误：文件不存在 - {input_path}", file=sys.stderr)
        sys.exit(1)

    input_content = input_path.read_text(encoding='utf-8')

    # 转换
    output_content = convert_to_slides(
        input_content,
        theme=args.theme,
        split_by_h1=args.split_h1,
        slide_number=not args.no_slide_number,
    )

    # 输出
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output_content, encoding='utf-8')
        print(f"转换完成：{output_path}")
    else:
        print(output_content)


if __name__ == "__main__":
    main()
