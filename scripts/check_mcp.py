#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 Claude MCP 配置状态

检测 Claude Code 是否已配置 db-mcp 服务
"""

import json
import os
import sys
from pathlib import Path

# 设置输出编码为 UTF-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def get_claude_config_path():
    """获取 Claude 配置文件路径"""
    home = Path.home()

    # 可能的配置文件位置
    possible_paths = [
        home / ".claude.json",
        home / ".claude" / "config.json",
        home / ".claude" / "claude.json",
        home / ".config" / "claude" / "config.json",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    # 如果都不存在，返回默认路径
    return home / ".claude.json"


def get_current_project_path():
    """获取当前项目路径（标准化为配置格式）"""
    current_dir = Path(__file__).parent.parent.absolute()
    # 转换为与 Claude 配置一致的格式
    # Windows: E:\db-mcp -> E:/db-mcp
    path_str = str(current_dir).replace('\\', '/')
    # 确保不以 / 结尾
    return path_str.rstrip('/')


def check_mcp_config():
    """检查 MCP 配置状态"""
    config_path = get_claude_config_path()

    print(f"检查配置文件: {config_path}")

    if not config_path.exists():
        print("❌ Claude 配置文件不存在")
        print(f"   预期位置: {config_path}")
        return False

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        return False

    # 检查是否有 projects 节点
    if 'projects' not in config:
        print("❌ 配置文件中没有 projects 节点")
        print("\n提示: 运行 'python scripts/install_mcp.py' 安装 MCP 服务")
        return False

    projects = config['projects']

    # 获取当前项目路径
    project_path = get_current_project_path()
    print(f"当前项目路径: {project_path}")

    # 检查当前项目配置
    if project_path not in projects:
        print(f"❌ 当前项目未在配置文件中")
        print("\n提示: 运行 'python scripts/install_mcp.py' 安装 MCP 服务")
        return False

    project_config = projects[project_path]

    # 检查是否有 mcpServers 节点
    if 'mcpServers' not in project_config:
        print("❌ 当前项目没有 mcpServers 节点")
        print("\n提示: 运行 'python scripts/install_mcp.py' 安装 MCP 服务")
        return False

    mcp_servers = project_config['mcpServers']

    # 检查是否有 db-mcp 或 chatbi 相关配置
    db_mcp_configs = [
        (name, server) for name, server in mcp_servers.items()
        if 'db-mcp' in name.lower() or 'chatbi' in name.lower() or 'database' in name.lower()
    ]

    if not db_mcp_configs:
        print("❌ 未找到 db-mcp 相关配置")
        print("\n当前项目的 MCP 服务:")
        if mcp_servers:
            for name in mcp_servers.keys():
                print(f"  - {name}")
        else:
            print("  (无)")
        print("\n提示: 运行 'python scripts/install_mcp.py' 安装 MCP 服务")
        return False

    # 检查配置详情
    print("✅ 找到 db-mcp 配置:")
    current_dir = Path(__file__).parent.parent.absolute()

    for name, server_config in db_mcp_configs:
        print(f"\n  配置名称: {name}")
        print(f"  命令: {server_config.get('command', 'N/A')}")

        args = server_config.get('args', [])
        if args:
            print(f"  参数: {' '.join(args)}")

            # 检查目录参数
            for i, arg in enumerate(args):
                if arg == "--directory" and i + 1 < len(args):
                    dir_path = Path(args[i + 1])
                    print(f"  工作目录: {dir_path}")

                    # 展开环境变量
                    if str(dir_path).startswith("%"):
                        import shutil
                        dir_path_expanded = Path(os.path.expandvars(str(dir_path)))
                        print(f"  展开后: {dir_path_expanded}")

                    # 检查目录是否存在
                    if dir_path.exists():
                        print(f"  ✅ 目录存在")
                    else:
                        print(f"  ⚠️  目录不存在")

        env = server_config.get('env', {})
        if env:
            print(f"  环境变量:")
            for key, value in env.items():
                print(f"    {key}={value}")

    return True


def main():
    """主函数"""
    print("=" * 60)
    print("db-mcp 配置检查工具")
    print("=" * 60)
    print()

    success = check_mcp_config()

    print()
    print("=" * 60)

    if success:
        print("✅ MCP 服务已配置")
        print("\n如果 MCP 工具不可用，请尝试:")
        print("1. 重启 Claude Code")
        print("2. 检查 db_config.json 是否正确配置")
        print("3. 运行 'python test_connection.py' 测试连接")
    else:
        print("❌ MCP 服务未配置")
        print("\n请运行: python scripts/install_mcp.py")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
