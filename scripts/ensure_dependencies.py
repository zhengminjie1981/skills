#!/usr/bin/env python3
"""
依赖检测和安装脚本
检测并安装 db-mcp 所需的 Python 依赖包
"""
import sys
import subprocess
import importlib
import json
import os
from pathlib import Path

# Windows 平台启用 ANSI 颜色支持和 UTF-8 编码
if sys.platform == 'win32':
    import ctypes
    import io
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    # 设置 stdout 和 stderr 为 UTF-8 编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# ANSI 颜色代码
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_color(message, color=Colors.ENDC, **kwargs):
    """打印彩色消息"""
    # Remove unsupported kwargs to avoid errors
    kwargs.pop('flush', None)
    print(f"{color}{message}{Colors.ENDC}", **kwargs)


def check_package(package_name, import_name=None):
    """
    检查包是否已安装

    Args:
        package_name: pip 包名
        import_name: 导入名（如果与包名不同）

    Returns:
        bool: 是否已安装
    """
    if import_name is None:
        import_name = package_name

    try:
        importlib.import_module(import_name)
        return True
    except ImportError:
        return False


def get_installed_version(package_name):
    """获取已安装包的版本"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
    except Exception:
        pass
    return None


def install_package(package_name, version_spec=None):
    """
    安装包

    Args:
        package_name: 包名
        version_spec: 版本规格（如 ">=1.0.0"）

    Returns:
        bool: 是否安装成功
    """
    spec = f"{package_name}{version_spec}" if version_spec else package_name
    print_color(f"正在安装 {package_name}...", Colors.OKCYAN)

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", spec],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print_color(f"✓ {package_name} 安装成功", Colors.OKGREEN)
        return True
    except subprocess.CalledProcessError:
        print_color(f"✗ {package_name} 安装失败", Colors.FAIL)
        return False


def detect_database_needs():
    """
    检测用户的数据库配置，确定需要哪些驱动

    Returns:
        set: 需要的数据库驱动集合 {'mysql', 'postgresql', 'sqlite'}
    """
    needs = {'sqlite'}  # SQLite 是内置的

    # 查找配置文件
    script_dir = Path(__file__).parent.parent
    config_files = [
        script_dir / "db_config.json",
        Path.home() / ".claude" / "skills" / "portable-chatbi-mcp" / "db_config.json",
    ]

    for config_file in config_files:
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    for name, db_config in config.items():
                        if not name.startswith('_'):  # 跳过注释字段
                            db_type = db_config.get('type', '').lower()
                            if db_type == 'mysql':
                                needs.add('mysql')
                            elif db_type == 'postgresql':
                                needs.add('postgresql')
            except (json.JSONDecodeError, IOError):
                pass

    return needs


def main():
    """主函数"""
    print_color("\n" + "="*60, Colors.BOLD)
    print_color("db-mcp 依赖检测工具", Colors.HEADER + Colors.BOLD)
    print_color("="*60 + "\n", Colors.BOLD)

    # 定义依赖包
    dependencies = [
        {
            "name": "fastmcp",
            "import": "fastmcp",
            "version": "<3",
            "required": True,
            "description": "MCP 服务器框架（核心依赖）"
        },
    ]

    # 可选的数据库驱动
    db_drivers = {
        "mysql": {
            "name": "mysql-connector-python",
            "import": "mysql",
            "version": ">=8.0.30",
            "description": "MySQL 数据库驱动"
        },
        "postgresql": {
            "name": "psycopg2-binary",
            "import": "psycopg2",
            "version": ">=2.9.0",
            "description": "PostgreSQL 数据库驱动"
        },
    }

    # 检测数据库需求
    db_needs = detect_database_needs()

    # 添加需要的数据库驱动
    for db_type in db_needs:
        if db_type in db_drivers:
            dependencies.append({
                **db_drivers[db_type],
                "required": db_type == 'sqlite'  # SQLite 不是必需安装的
            })

    # 检查依赖
    missing_required = []
    missing_optional = []
    installed_info = []

    for dep in dependencies:
        package_name = dep["name"]
        import_name = dep["import"]
        version_spec = dep.get("version")
        description = dep["description"]
        required = dep.get("required", False)

        if check_package(package_name, import_name):
            version = get_installed_version(package_name)
            status_icon = "✓"
            status_color = Colors.OKGREEN
            installed_info.append({
                "name": package_name,
                "version": version,
                "description": description
            })
        else:
            version = None
            status_icon = "✗"
            status_color = Colors.FAIL
            if required:
                missing_required.append(dep)
            else:
                missing_optional.append(dep)

        # 打印状态
        status_msg = f"{status_icon} {package_name}"
        if version:
            status_msg += f" ({version})"
        if not check_package(package_name, import_name):
            status_msg += f" - {description}"

        print_color(status_msg, status_color)

    print()

    # 如果没有缺失依赖
    if not missing_required and not missing_optional:
        print_color("所有依赖都已安装完成！", Colors.OKGREEN + Colors.BOLD)
        return 0

    # 显示缺失的依赖
    if missing_required:
        print_color("\n缺少必需的依赖:", Colors.WARNING + Colors.BOLD)
        for dep in missing_required:
            print_color(f"  - {dep['name']}: {dep['description']}", Colors.WARNING)
        print()

    if missing_optional:
        print_color("\n缺少可选的数据库驱动:", Colors.OKCYAN)
        for dep in missing_optional:
            print_color(f"  - {dep['name']}: {dep['description']}", Colors.OKCYAN)
        print()

    # 询问是否安装
    if missing_required or missing_optional:
        # 检查是否支持交互式输入
        is_interactive = sys.stdin.isatty()

        if is_interactive:
            print_color("是否现在安装这些依赖包? (y/n): ", Colors.BOLD, end='')
            try:
                choice = input().strip().lower()
                if choice not in ('y', 'yes', '是'):
                    print_color("\n已取消安装。请手动运行以下命令安装依赖:", Colors.WARNING)
                    all_missing = missing_required + missing_optional
                    for dep in all_missing:
                        version = dep.get('version', '')
                        print_color(f"  pip install {dep['name']}{version}", Colors.OKCYAN)
                    return 1
            except (EOFError, KeyboardInterrupt):
                print_color("\n\n已取消安装。", Colors.WARNING)
                return 1
        else:
            # 非交互式环境，自动安装
            print_color("非交互式环境，自动安装依赖包...", Colors.OKCYAN)

        print()
        success_count = 0
        fail_count = 0

        # 安装必需依赖
        for dep in missing_required:
            if install_package(dep['name'], dep.get('version')):
                success_count += 1
            else:
                fail_count += 1

        # 安装可选依赖
        for dep in missing_optional:
            if install_package(dep['name'], dep.get('version')):
                success_count += 1
            else:
                fail_count += 1

        print()
        print_color("="*60, Colors.BOLD)
        if fail_count == 0:
            print_color("✓ 所有依赖安装成功！", Colors.OKGREEN + Colors.BOLD)
            print_color("\n现在可以使用 db-mcp 技能了。", Colors.OKGREEN)
            return 0
        else:
            print_color(f"安装完成: {success_count} 个成功, {fail_count} 个失败", Colors.WARNING)
            print_color("\n请检查错误信息，或手动安装失败的包。", Colors.WARNING)
            return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_color("\n\n已中断安装。", Colors.WARNING)
        sys.exit(1)
