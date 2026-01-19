#!/usr/bin/env python3
"""
db-mcp 统一命令行工具

无论 skill 安装在哪个项目的 .claude/skills/ 目录下，
都可以从任何位置运行此脚本。

使用方法:
    python db-mcp.py install    # 安装依赖
    python db-mcp.py check      # 检查配置
    python db-mcp.py setup      # 安装 MCP 服务
    python db-mcp.py validate   # 验证配置
"""
import sys
import subprocess
from pathlib import Path


def find_project_root():
    """
    查找 db-mcp 项目根目录

    搜索顺序:
    1. 脚本所在目录
    2. 当前工作目录
    3. ~/.claude/skills/db-mcp/
    4. ~/.claude/skills/portable-chatbi-mcp/
    """
    # 1. 脚本所在目录
    script_path = Path(__file__).resolve().parent
    if (script_path / "db_config.json").exists() or (script_path / "scripts" / "server.py").exists():
        return script_path

    # 2. 当前工作目录
    cwd = Path.cwd()
    if (cwd / "db_config.json").exists() or (cwd / "scripts" / "server.py").exists():
        return cwd

    # 3. 常见的 skill 安装位置
    possible_paths = [
        Path.home() / ".claude" / "skills" / "db-mcp",
        Path.home() / ".claude" / "skills" / "portable-chatbi-mcp",
        Path.cwd() / ".claude" / "skills" / "db-mcp",
        Path.cwd() / ".claude" / "skills" / "portable-chatbi-mcp",
    ]

    for path in possible_paths:
        if path.exists() and ((path / "db_config.json").exists() or (path / "scripts" / "server.py").exists()):
            return path

    # 4. 未找到，返回脚本所在目录（让后续逻辑处理错误）
    return script_path


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("db-mcp - 数据库 MCP 服务管理工具")
        print()
        print("使用方法:")
        print("  python db-mcp.py install    安装 Python 依赖")
        print("  python db-mcp.py check      检查 MCP 配置状态")
        print("  python db-mcp.py setup      安装 MCP 服务")
        print("  python db-mcp.py validate   验证数据库配置")
        print()
        print("示例:")
        print("  python db-mcp.py install")
        print("  python /path/to/skills/db-mcp/db-mcp.py check")
        return 1

    command = sys.argv[1].lower()
    project_root = find_project_root()
    scripts_dir = project_root / "scripts"

    # 命令映射
    commands = {
        "install": ("ensure_dependencies.py", "安装依赖"),
        "check": ("check_mcp.py", "检查配置"),
        "setup": ("install_mcp.py", "安装 MCP 服务"),
        "validate": ("validate_config.py", "验证配置"),
    }

    if command not in commands:
        print(f"错误: 未知命令 '{command}'")
        print()
        print("可用命令:")
        for cmd, (_, desc) in commands.items():
            print(f"  {cmd:12} {desc}")
        return 1

    script_name, desc = commands[command]
    script_path = scripts_dir / script_name

    if not script_path.exists():
        print(f"错误: 找不到脚本 {script_path}")
        print(f"项目根目录: {project_root}")
        return 1

    print(f"db-mcp: {desc}...")
    print(f"项目位置: {project_root}")
    print()

    # 运行脚本
    result = subprocess.run(
        [sys.executable, str(script_path)] + sys.argv[2:],
        cwd=str(project_root),
        env=dict(**subprocess.os.environ, PYTHONPATH=str(scripts_dir))
    )

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
