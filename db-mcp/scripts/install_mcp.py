#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装 db-mcp 服务到 Claude 配置

自动检测并配置 MCP 服务
"""

import json
import os
import sys
import shutil
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

    # 优先使用已存在的配置文件
    for path in possible_paths:
        if path.exists():
            return path

    # 如果都不存在，使用默认位置
    return home / ".claude.json"


def get_current_project_path():
    """获取当前项目路径（使用相对路径）"""
    # 使用相对路径，使配置可移植
    # "." 表示当前项目根目录
    return "."


def get_current_directory():
    """获取当前项目目录的绝对路径"""
    return Path(__file__).parent.parent.absolute()


def get_db_config_path():
    """获取数据库配置文件路径"""
    current_dir = get_current_directory()
    return current_dir / "db_config.json"


def check_db_config():
    """检查数据库配置是否存在"""
    db_config_path = get_db_config_path()

    if not db_config_path.exists():
        print(f"⚠️  数据库配置文件不存在: {db_config_path}")
        print(f"\n请按以下步骤配置:")
        print(f"1. 复制配置模板:")
        print(f"   cp db_config.example.json db_config.json")
        print(f"2. 编辑 db_config.json，填入数据库连接信息")
        return False

    # 验证配置格式
    try:
        with open(db_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        if not config:
            print("❌ 数据库配置文件为空")
            return False

        print(f"✅ 数据库配置文件存在")
        print(f"   配置的数据库: {', '.join(config.keys())}")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ 数据库配置文件格式错误: {e}")
        return False


def generate_mcp_config():
    """生成 MCP 配置"""
    # 使用相对路径，使配置可移植
    current_dir = "."  # 项目根目录
    db_config_path = "./db_config.json"  # 相对路径配置文件

    # 读取数据库配置以确定需要哪些依赖（使用绝对路径读取）
    needs_mysql = False
    needs_postgres = False

    db_config_abs_path = get_db_config_path()
    try:
        with open(db_config_abs_path, 'r', encoding='utf-8') as f:
            db_config = json.load(f)

        for cfg in db_config.values():
            db_type = cfg.get('type', '').lower()
            if db_type == 'mysql':
                needs_mysql = True
            elif db_type == 'postgresql':
                needs_postgres = True
    except:
        pass

    # 构建参数列表
    args = [
        "--directory",
        current_dir,  # "."
    ]

    # 添加数据库依赖
    if needs_mysql:
        args.extend(["--with", "mysql-connector-python"])
    if needs_postgres:
        args.extend(["--with", "psycopg2-binary"])

    args.append("chatbi-mcp")

    mcp_config = {
        "command": "uvx",
        "args": args,
        "env": {
            "CHATBI_CONFIG": db_config_path  # "./db_config.json"
        }
    }

    return mcp_config


def install_mcp_config():
    """安装 MCP 配置到 Claude 配置文件"""
    config_path = get_claude_config_path()
    current_dir = get_current_directory()

    print("=" * 60)
    print("db-mcp 安装工具")
    print("=" * 60)
    print()

    # 1. 检查数据库配置
    print("步骤 1: 检查数据库配置")
    if not check_db_config():
        print()
        print("❌ 安装取消: 请先配置数据库")
        return False
    print()

    # 2. 生成 MCP 配置
    print("步骤 2: 生成 MCP 配置")
    mcp_config = generate_mcp_config()

    print(f"  工作目录: {mcp_config['args'][1]}")
    print(f"  命令: {mcp_config['command']}")
    print(f"  参数: {' '.join(mcp_config['args'][2:])}")
    print(f"  配置文件: {mcp_config['env']['CHATBI_CONFIG']}")
    print()

    # 3. 读取或创建配置文件
    print("步骤 3: 更新 Claude 配置")

    config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"  读取现有配置: {config_path}")
        except json.JSONDecodeError as e:
            print(f"  ⚠️  配置文件格式错误，将创建新配置: {e}")
            config = {}
    else:
        print(f"  创建新配置文件: {config_path}")

    # 确保 projects 节点存在
    if 'projects' not in config:
        config['projects'] = {}

    # 获取当前项目路径
    project_path = get_current_project_path()
    print(f"  项目路径: {project_path}")

    # 确保项目配置存在
    if project_path not in config['projects']:
        config['projects'][project_path] = {}

    project_config = config['projects'][project_path]

    # 确保项目的 mcpServers 节点存在
    if 'mcpServers' not in project_config:
        project_config['mcpServers'] = {}

    mcp_servers = project_config['mcpServers']

    # 4. 检查是否已存在配置
    existing_configs = [
        name for name in mcp_servers.keys()
        if 'db-mcp' in name.lower() or 'chatbi' in name.lower()
    ]

    if existing_configs:
        print(f"  ⚠️  发现已存在的配置: {', '.join(existing_configs)}")

        # 检查是否支持交互式输入
        is_interactive = sys.stdin.isatty()

        if is_interactive:
            # 询问是否更新
            try:
                response = input("  是否更新配置? (y/N): ").strip().lower()
                if response != 'y':
                    print("  安装取消")
                    return False
            except EOFError:
                # 非交互式环境，采用默认行为（更新配置）
                print("  非交互式环境，自动更新配置")
        else:
            # 非交互式环境，直接更新
            print("  非交互式环境，自动更新配置")

        # 删除旧配置
        for name in existing_configs:
            del mcp_servers[name]
            print(f"  删除旧配置: {name}")

    # 5. 添加新配置
    config_name = "db-mcp"
    mcp_servers[config_name] = mcp_config
    print(f"  ✅ 添加配置: {config_name}")
    print()

    # 6. 保存配置
    print("步骤 4: 保存配置")

    # 确保父目录存在
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"  ✅ 配置已保存: {config_path}")
    print()

    # 7. 显示后续步骤
    print("=" * 60)
    print("✅ 安装完成!")
    print()
    print("后续步骤:")
    print("1. 重启 Claude Code")
    print("2. 使用以下 MCP 工具:")
    print("   - list_tables()       : 列出所有表")
    print("   - describe_table(name) : 查看表结构")
    print("   - execute_query(sql)   : 执行查询")
    print()
    print("测试连接:")
    print("   python test_connection.py")
    print()
    print("检查配置:")
    print("   python scripts/check_mcp.py")
    print("=" * 60)

    return True


def main():
    """主函数"""
    try:
        success = install_mcp_config()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n安装已取消")
        return 1
    except Exception as e:
        print(f"\n❌ 安装失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
