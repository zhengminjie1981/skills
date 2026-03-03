"""
便携式 ChatBI MCP 服务器 - MCP 工具定义
提供所有数据库操作的工具函数
"""

from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def register_all(mcp):
    """
    注册所有 MCP 工具到 FastMCP 服务器

    Args:
        mcp: FastMCP 服务器实例
    """

    @mcp.tool(annotations={"readOnlyHint": True})
    def list_tables(
        config_name: str = 'default'
    ) -> List[str]:
        """
        列出数据库中的所有表

        Args:
            config_name: 数据库配置名称（默认使用 default）

        Returns:
            表名列表
        """
        from connection import get_connection_manager

        conn_mgr = get_connection_manager()
        connection = conn_mgr.get_connection(config_name)
        config = conn_mgr.config.get_config(config_name)
        db_type = config['type']

        cursor = connection.cursor()

        if db_type == 'mysql':
            cursor.execute("SHOW TABLES")
        elif db_type == 'postgresql':
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        elif db_type == 'sqlite':
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")

        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()

        logger.info(f"列出表: {config_name}, 找到 {len(tables)} 个表")
        return tables

    @mcp.tool(annotations={"readOnlyHint": True})
    def describe_table(
        table_name: str,
        config_name: str = 'default'
    ) -> Dict[str, Any]:
        """
        获取表的详细结构信息

        Args:
            table_name: 表名
            config_name: 数据库配置名称

        Returns:
            表结构信息，包括字段名、类型、是否为空、键等
        """
        from connection import get_connection_manager

        conn_mgr = get_connection_manager()
        connection = conn_mgr.get_connection(config_name)
        config = conn_mgr.config.get_config(config_name)
        db_type = config['type']

        cursor = connection.cursor(dictionary=True)

        if db_type == 'mysql':
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()

            result = {
                "table_name": table_name,
                "columns": [
                    {
                        "field": col['Field'],
                        "type": col['Type'],
                        "null": col['Null'],
                        "key": col['Key'],
                        "default": col['Default'],
                        "extra": col['Extra']
                    }
                    for col in columns
                ]
            }

        elif db_type == 'postgresql':
            cursor.execute(f"""
                SELECT
                    column_name as field,
                    data_type as type,
                    is_nullable as null,
                    column_default as default_value
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()

            result = {
                "table_name": table_name,
                "columns": [
                    {
                        "field": col['field'],
                        "type": col['type'],
                        "null": col['null'],
                        "key": "",
                        "default": col['default_value'],
                        "extra": ""
                    }
                    for col in columns
                ]
            }

        elif db_type == 'sqlite':
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            result = {
                "table_name": table_name,
                "columns": [
                    {
                        "field": col['name'],
                        "type": col['type'],
                        "null": 'YES' if col['notnull'] == 0 else 'NO',
                        "key": 'PRI' if col['pk'] == 1 else '',
                        "default": col['dflt_value'],
                        "extra": ""
                    }
                    for col in columns
                ]
            }

        cursor.close()

        logger.info(f"描述表: {table_name}")
        return result

    @mcp.tool(annotations={"readOnlyHint": True})
    def execute_query(
        query: str,
        config_name: str = 'default',
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        执行只读 SQL 查询

        安全限制:
        - 仅允许 SELECT 查询
        - 自动注入 LIMIT 限制（默认1000行）
        - 防止 SQL 注入

        Args:
            query: SQL 查询语句（必须是 SELECT）
            config_name: 数据库配置名称
            limit: 最大返回行数（默认1000）

        Returns:
            查询结果列表，每行是一个字典

        Raises:
            ValueError: 如果查询不是 SELECT 语句
        """
        # 安全验证
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT"):
            raise ValueError(
                "只允许 SELECT 查询以保护数据安全。"
                f"检测到查询类型: {query_upper[:50]}..."
            )

        # 禁止危险关键字
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER"]
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f"禁止使用 {keyword} 语句")

        from connection import get_connection_manager

        conn_mgr = get_connection_manager()
        connection = conn_mgr.get_connection(config_name)
        config = conn_mgr.config.get_config(config_name)
        db_type = config['type']

        # 添加 LIMIT 限制（如果查询中没有）
        if "LIMIT" not in query_upper:
            query = f"{query} LIMIT {limit}"

        cursor = connection.cursor(dictionary=True)
        start_time = datetime.now()

        try:
            cursor.execute(query)
            results = cursor.fetchall()

            # 转换 datetime 对象为字符串
            for row in results:
                for key, value in row.items():
                    if isinstance(value, datetime):
                        row[key] = value.isoformat()
                    elif isinstance(value, bytes):
                        row[key] = "<binary data>"

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"执行查询: {config_name}, 返回 {len(results)} 行, "
                f"耗时 {elapsed:.2f}s"
            )

            return results

        finally:
            cursor.close()

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_table_count(
        table_name: str,
        config_name: str = 'default'
    ) -> Dict[str, Any]:
        """
        获取表的行数统计信息

        Args:
            table_name: 表名
            config_name: 数据库配置名称

        Returns:
            包含表名和行数的字典
        """
        from connection import get_connection_manager

        conn_mgr = get_connection_manager()
        connection = conn_mgr.get_connection(config_name)

        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        result = cursor.fetchone()
        cursor.close()

        logger.info(f"统计表行数: {table_name}")

        # 处理不同数据库的返回格式
        if isinstance(result, dict):
            count = result['count']
        else:
            count = result[0]

        return {"table_name": table_name, "row_count": count}

    @mcp.tool(annotations={"readOnlyHint": True})
    def get_database_info(
        config_name: str = 'default'
    ) -> Dict[str, Any]:
        """
        获取数据库的基本信息

        Args:
            config_name: 数据库配置名称

        Returns:
            数据库信息，包括数据库名、版本、字符集等
        """
        from connection import get_connection_manager

        conn_mgr = get_connection_manager()
        connection = conn_mgr.get_connection(config_name)
        config = conn_mgr.config.get_config(config_name)
        db_type = config['type']

        cursor = connection.cursor()

        if db_type == 'mysql':
            cursor.execute("SELECT DATABASE() as db")
            db_name = cursor.fetchone()['db']

            cursor.execute("SELECT VERSION() as version")
            version = cursor.fetchone()['version']

            cursor.close()

            result = {
                "config_name": config_name,
                "database_type": "MySQL",
                "database": db_name,
                "version": version
            }

        elif db_type == 'postgresql':
            cursor.execute("SELECT current_database() as db")
            db_name = cursor.fetchone()['db']

            cursor.execute("SELECT version() as version")
            version = cursor.fetchone()['version'].split(',')[0]

            cursor.close()

            result = {
                "config_name": config_name,
                "database_type": "PostgreSQL",
                "database": db_name,
                "version": version
            }

        elif db_type == 'sqlite':
            db_name = config['database']

            cursor.execute("SELECT sqlite_version() as version")
            version = cursor.fetchone()['version']

            cursor.close()

            result = {
                "config_name": config_name,
                "database_type": "SQLite",
                "database": db_name,
                "version": version
            }

        else:
            cursor.close()
            result = {
                "config_name": config_name,
                "database_type": db_type,
                "database": "Unknown",
                "version": "Unknown"
            }

        logger.info(f"获取数据库信息: {config_name}")
        return result

    @mcp.tool(annotations={"readOnlyHint": True})
    def search_tables(
        keyword: str,
        config_name: str = 'default'
    ) -> List[Dict[str, Any]]:
        """
        搜索包含特定关键字的表

        Args:
            keyword: 搜索关键字
            config_name: 数据库配置名称

        Returns:
            匹配的表及其行数
        """
        from connection import get_connection_manager

        conn_mgr = get_connection_manager()
        connection = conn_mgr.get_connection(config_name)

        cursor = connection.cursor()

        # 获取所有表
        config = conn_mgr.config.get_config(config_name)
        db_type = config['type']

        if db_type == 'mysql':
            cursor.execute("SHOW TABLES")
            all_tables = [row[0] for row in cursor.fetchall()]
        elif db_type == 'postgresql':
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            all_tables = [row[0] for row in cursor.fetchall()]
        elif db_type == 'sqlite':
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            all_tables = [row[0] for row in cursor.fetchall()]
        else:
            all_tables = []

        # 过滤包含关键字的表
        matched_tables = [
            table for table in all_tables
            if keyword.lower() in table.lower()
        ]

        results = []
        for table in matched_tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count_result = cursor.fetchone()

            # 处理不同数据库的返回格式
            if isinstance(count_result, dict):
                count = count_result['count']
            else:
                count = count_result[0]

            results.append({
                "table_name": table,
                "row_count": count
            })

        cursor.close()

        logger.info(f"搜索表: 关键字 '{keyword}', 找到 {len(results)} 个匹配表")
        return results

    @mcp.tool(annotations={"readOnlyHint": True})
    def check_capabilities() -> Dict[str, Any]:
        """
        检查当前系统的数据库能力

        返回已安装的驱动、配置状态和优化建议

        Returns:
            包含驱动状态、配置状态和建议的字典
        """
        from diagnostics import Diagnostics

        logger.info("检查系统能力")

        # 运行完整诊断
        diagnostics = Diagnostics.run_full_diagnostics()

        # 添加连接测试（如果有配置）
        connection_test = None
        config_status = diagnostics['config']

        if config_status['status'] == 'installed':
            # 尝试测试默认连接
            try:
                connection_test = Diagnostics.test_database_connection('default')
            except Exception as e:
                connection_test = {
                    "success": False,
                    "error": str(e),
                    "troubleshooting": "无法测试连接，请检查配置"
                }

        return {
            "installed_drivers": diagnostics['drivers'],
            "config_status": {
                "status": config_status['status'],
                "message": config_status['message'],
                "details": config_status.get('details')
            },
            "connection_test": connection_test,
            "recommendations": diagnostics['recommendations']
        }

    @mcp.tool()
    def auto_setup_database(
        db_type: str,
        connection_params: Dict[str, Any],
        config_name: str = 'default'
    ) -> Dict[str, Any]:
        """
        自动配置并测试数据库连接

        步骤:
        1. 检测并安装所需驱动
        2. 创建或更新配置文件
        3. 测试连接
        4. 验证基本功能

        Args:
            db_type: 数据库类型 ("mysql" | "postgresql" | "sqlite")
            connection_params: 连接参数 (host, port, user, password, database)
            config_name: 配置名称（默认 'default'）

        Returns:
            包含状态、配置路径和测试结果的字典
        """
        import json
        import tempfile
        from pathlib import Path
        from diagnostics import Diagnostics, DriverMissingError

        logger.info(f"自动配置数据库: {db_type}, 配置名: {config_name}")

        result = {
            "success": False,
            "driver_installed": False,
            "config_created": False,
            "connection_test": None,
            "error": None,
            "config_path": None
        }

        try:
            # 1. 检查并安装驱动
            driver_result = Diagnostics.check_database_driver(db_type)

            if driver_result.status.value == 'missing':
                # 自动安装驱动
                import subprocess
                import sys

                logger.info(f"正在安装 {db_type} 驱动...")

                package_map = {
                    'mysql': 'mysql-connector-python>=8.0.30',
                    'postgresql': 'psycopg2-binary>=2.9.0'
                }

                if db_type in package_map:
                    try:
                        subprocess.check_call(
                            [sys.executable, "-m", "pip", "install", package_map[db_type]],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        result["driver_installed"] = True
                        logger.info(f"{db_type} 驱动安装成功")
                    except subprocess.CalledProcessError as e:
                        raise DriverMissingError(
                            f"自动安装 {db_type} 驱动失败",
                            fix_command=f"pip install {package_map[db_type]}"
                        )
            else:
                result["driver_installed"] = True

            # 2. 创建或更新配置文件
            script_dir = Path(__file__).parent.parent.absolute()
            config_path = script_dir / 'db_config.json'

            # 读取现有配置（如果存在）
            existing_configs = {}
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        existing_configs = json.load(f)
                except:
                    pass

            # 准备新配置
            new_config = {
                "type": db_type,
                **connection_params
            }

            # 合并配置
            existing_configs[config_name] = new_config

            # 原子写入配置文件
            temp_path = config_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(existing_configs, f, indent=2, ensure_ascii=False)
            temp_path.rename(config_path)

            result["config_created"] = True
            result["config_path"] = str(config_path)
            logger.info(f"配置文件已创建: {config_path}")

            # 3. 重置全局配置实例（清除缓存）
            from config import _global_config
            global _global_config
            _global_config = None

            # 4. 测试连接
            connection_test = Diagnostics.test_database_connection(config_name)
            result["connection_test"] = connection_test

            if connection_test["success"]:
                # 5. 验证基本功能（列出表）
                try:
                    tables = list_tables(config_name)
                    result["tables_count"] = len(tables)
                    result["success"] = True
                    logger.info(f"自动配置成功，找到 {len(tables)} 个表")
                except Exception as e:
                    result["success"] = True  # 连接成功即可
                    result["warning"] = f"连接成功但无法列出表: {str(e)}"
                    logger.warning(f"列出表失败: {e}")
            else:
                result["error"] = connection_test.get("error")
                result["troubleshooting"] = connection_test.get("troubleshooting")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"自动配置失败: {e}")

            # 添加修复建议
            if hasattr(e, 'fix_command'):
                result["fix_command"] = e.fix_command

        return result

    @mcp.tool(annotations={"readOnlyHint": True})
    def test_connection(
        config_name: str = 'default',
        detailed: bool = False
    ) -> Dict[str, Any]:
        """
        测试数据库连接并返回诊断信息

        Args:
            config_name: 数据库配置名称
            detailed: 是否返回详细的服务器信息

        Returns:
            包含连接状态、延迟和诊断信息的字典
        """
        from diagnostics import Diagnostics

        logger.info(f"测试连接: {config_name}")

        result = Diagnostics.test_database_connection(config_name)

        # 如果不需要详细信息，简化返回结果
        if not detailed and result.get("server_info"):
            # 只保留基本信息
            result["server_info"] = {
                "type": result["server_info"].get("type"),
                "version": result["server_info"].get("version")
            }

        return result

    logger.info("所有 MCP 工具已注册")
