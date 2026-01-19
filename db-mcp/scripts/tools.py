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

    logger.info("所有 MCP 工具已注册")
