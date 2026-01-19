#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证数据库配置文件

检查 db_config.json 的格式和有效性
"""

import json
import sys
from pathlib import Path

# 设置输出编码为 UTF-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def get_db_config_path():
    """获取数据库配置文件路径"""
    current_dir = Path(__file__).parent.parent.absolute()
    return current_dir / "db_config.json"


def validate_config():
    """验证数据库配置"""
    config_path = get_db_config_path()

    print("=" * 60)
    print("数据库配置验证工具")
    print("=" * 60)
    print()

    # 检查文件是否存在
    print("步骤 1: 检查配置文件")
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print()
        print("请按以下步骤创建配置:")
        print(f"1. 复制模板: cp {config_path.parent / 'db_config.example.json'} {config_path}")
        print("2. 编辑配置文件，填入数据库连接信息")
        return False

    print(f"✅ 配置文件存在: {config_path}")
    print()

    # 读取配置
    print("步骤 2: 读取配置")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ 配置文件格式错误: {e}")
        return False

    print(f"✅ 配置文件格式正确")
    print()

    # 验证配置内容
    print("步骤 3: 验证配置内容")

    if not config:
        print("❌ 配置文件为空")
        return False

    all_valid = True

    for config_name, db_config in config.items():
        print(f"\n配置名称: {config_name}")
        print("-" * 40)

        # 检查必需字段
        if 'type' not in db_config:
            print("  ❌ 缺少 'type' 字段")
            all_valid = False
            continue

        db_type = db_config['type'].lower()
        print(f"  数据库类型: {db_type}")

        # 验证不同数据库类型的配置
        if db_type == 'mysql':
            valid = validate_mysql_config(db_config)
        elif db_type == 'postgresql':
            valid = validate_postgresql_config(db_config)
        elif db_type == 'sqlite':
            valid = validate_sqlite_config(db_config)
        else:
            print(f"  ❌ 不支持的数据库类型: {db_type}")
            valid = False

        if valid:
            print(f"  ✅ 配置有效")

        all_valid = all_valid and valid

    print()
    print("=" * 60)

    if all_valid:
        print("✅ 所有配置验证通过")
        print()
        print("下一步:")
        print("1. 测试连接: python test_connection.py")
        print("2. 安装 MCP: python scripts/install_mcp.py")
    else:
        print("❌ 配置验证失败")
        print()
        print("请检查并修正配置错误")

    return all_valid


def validate_mysql_config(config):
    """验证 MySQL 配置"""
    required_fields = ['host', 'port', 'user', 'database']

    all_valid = True
    for field in required_fields:
        if field not in config:
            print(f"  ❌ 缺少必需字段: {field}")
            all_valid = False
        else:
            value = config[field]
            # 检查是否是环境变量引用
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                print(f"  {field}: {value} (环境变量)")
            else:
                print(f"  {field}: {value}")

    # password 可以是可选的（某些配置可能不需要）
    if 'password' in config:
        password = config['password']
        if isinstance(password, str) and password.startswith('${'):
            print(f"  password: **** (环境变量)")
        else:
            print(f"  password: ****")

    return all_valid


def validate_postgresql_config(config):
    """验证 PostgreSQL 配置"""
    required_fields = ['host', 'port', 'user', 'database']

    all_valid = True
    for field in required_fields:
        if field not in config:
            print(f"  ❌ 缺少必需字段: {field}")
            all_valid = False
        else:
            value = config[field]
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                print(f"  {field}: {value} (环境变量)")
            else:
                print(f"  {field}: {value}")

    if 'password' in config:
        password = config['password']
        if isinstance(password, str) and password.startswith('${'):
            print(f"  password: **** (环境变量)")
        else:
            print(f"  password: ****")

    return all_valid


def validate_sqlite_config(config):
    """验证 SQLite 配置"""
    if 'database' not in config:
        print("  ❌ 缺少必需字段: database")
        return False

    db_path = config['database']
    print(f"  database: {db_path}")

    # 检查文件是否存在
    if isinstance(db_path, str) and not db_path.startswith('${'):
        path = Path(db_path)
        if path.exists():
            print(f"  ✅ 数据库文件存在")
        else:
            print(f"  ⚠️  数据库文件不存在 (将在首次连接时创建)")

    return True


def main():
    """主函数"""
    try:
        success = validate_config()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
