"""
便携式 ChatBI MCP 服务器 - MCP 资源定义
提供数据库架构和统计信息的资源访问
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def register_all(mcp):
    """
    注册所有 MCP 资源到 FastMCP 服务器

    Args:
        mcp: FastMCP 服务器实例
    """

    @mcp.resource("schema://tables")
    def get_tables_schema(config_name: str = 'default') -> str:
        """
        获取所有表的架构信息（Markdown 格式）

        Args:
            config_name: 数据库配置名称

        Returns:
            所有表的结构信息，以 Markdown 格式返回
        """
        from connection import get_connection_manager

        conn_mgr = get_connection_manager()
        connection = conn_mgr.get_connection(config_name)
        config = conn_mgr.config.get_config(config_name)
        db_type = config['type']

        cursor = connection.cursor()

        # 获取所有表
        if db_type == 'mysql':
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
        elif db_type == 'postgresql':
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            tables = [row[0] for row in cursor.fetchall()]
        elif db_type == 'sqlite':
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
        else:
            tables = []

        markdown = f"# 数据库表结构\n\n"
        markdown += f"配置: {config_name}\n\n"
        markdown += f"数据库中共有 **{len(tables)}** 个表：\n\n"

        for table in tables:
            markdown += f"## {table}\n\n"

            if db_type == 'mysql':
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()

                markdown += "| 字段名 | 类型 | NULL | 键 | 默认值 | 额外 |\n"
                markdown += "|--------|------|------|-----|--------|------|\n"

                for col in columns:
                    markdown += f"| {col[0]} | {col[1]} | {col[2]} | {col[3] or ''} | {col[4] or ''} | {col[5]} |\n"

            elif db_type == 'postgresql':
                cursor.execute(f"""
                    SELECT
                        column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()

                markdown += "| 字段名 | 类型 | NULL | 默认值 |\n"
                markdown += "|--------|------|------|--------|\n"

                for col in columns:
                    markdown += f"| {col[0]} | {col[1]} | {col[2]} | {col[3] or ''} |\n"

            elif db_type == 'sqlite':
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()

                markdown += "| 字段名 | 类型 | NULL | 默认值 |\n"
                markdown += "|--------|------|------|--------|\n"

                for col in columns:
                    null = 'NO' if col[3] == 1 else 'YES'
                    markdown += f"| {col[1]} | {col[2]} | {null} | {col[4] or ''} |\n"

            markdown += "\n"

        cursor.close()
        logger.info("生成表结构资源")
        return markdown

    @mcp.resource("schema://table/{table_name}")
    def get_table_schema(table_name: str, config_name: str = 'default') -> str:
        """
        获取特定表的详细架构

        Args:
            table_name: 表名
            config_name: 数据库配置名称

        Returns:
            表的详细结构信息（Markdown 格式）
        """
        from connection import get_connection_manager

        conn_mgr = get_connection_manager()
        connection = conn_mgr.get_connection(config_name)
        config = conn_mgr.config.get_config(config_name)
        db_type = config['type']

        cursor = connection.cursor(dictionary=True)

        markdown = f"# 表: {table_name}\n\n"
        markdown += f"配置: {config_name}\n\n"

        # 获取表结构
        if db_type == 'mysql':
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()

            markdown += "## 字段信息\n\n"
            markdown += "| 字段名 | 类型 | NULL | 键 | 默认值 | 额外 |\n"
            markdown += "|--------|------|------|-----|--------|------|\n"

            for col in columns:
                markdown += f"| {col['Field']} | {col['Type']} | {col['Null']} | {col['Key'] or ''} | {col['Default'] or ''} | {col['Extra']} |\n"

            # 获取行数
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            row_count = cursor.fetchone()['count']

            markdown += f"\n## 统计信息\n\n"
            markdown += f"- **总行数**: {row_count:,}\n"

            # 获取创建语句
            cursor.execute(f"SHOW CREATE TABLE {table_name}")
            create_sql = cursor.fetchone()['Create Table']

            markdown += "\n## 创建语句\n\n"
            markdown += "```sql\n"
            markdown += create_sql
            markdown += "\n```\n"

        elif db_type == 'postgresql':
            cursor.execute(f"""
                SELECT
                    column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()

            markdown += "## 字段信息\n\n"
            markdown += "| 字段名 | 类型 | NULL | 默认值 |\n"
            markdown += "|--------|------|------|--------|\n"

            for col in columns:
                markdown += f"| {col['column_name']} | {col['data_type']} | {col['is_nullable']} | {col['column_default'] or ''} |\n"

            # 获取行数
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            row_count = cursor.fetchone()['count']

            markdown += f"\n## 统计信息\n\n"
            markdown += f"- **总行数**: {row_count:,}\n"

        elif db_type == 'sqlite':
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            markdown += "## 字段信息\n\n"
            markdown += "| 字段名 | 类型 | NULL | 默认值 |\n"
            markdown += "|--------|------|------|--------|\n"

            for col in columns:
                null = 'NO' if col['notnull'] == 1 else 'YES'
                markdown += f"| {col['name']} | {col['type']} | {null} | {col['dflt_value'] or ''} |\n"

            # 获取行数
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            row_count = cursor.fetchone()['count']

            markdown += f"\n## 统计信息\n\n"
            markdown += f"- **总行数**: {row_count:,}\n"

            # 获取创建语句
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            result = cursor.fetchone()
            if result and result['sql']:
                create_sql = result['sql']
                markdown += "\n## 创建语句\n\n"
                markdown += "```sql\n"
                markdown += create_sql
                markdown += "\n```\n"

        cursor.close()
        logger.info(f"生成表资源: {table_name}")
        return markdown

    @mcp.resource("stats://database")
    def get_database_stats(config_name: str = 'default') -> str:
        """
        获取数据库统计信息

        Args:
            config_name: 数据库配置名称

        Returns:
            数据库统计信息（JSON 格式）
        """
        from connection import get_connection_manager

        conn_mgr = get_connection_manager()
        connection = conn_mgr.get_connection(config_name)
        config = conn_mgr.config.get_config(config_name)
        db_type = config['type']

        cursor = connection.cursor()

        # 获取所有表
        if db_type == 'mysql':
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
        elif db_type == 'postgresql':
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            tables = [row[0] for row in cursor.fetchall()]
        elif db_type == 'sqlite':
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
        else:
            tables = []

        # 获取每个表的统计信息
        table_stats = {}
        total_rows = 0

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            result = cursor.fetchone()

            if isinstance(result, dict):
                count = result['count']
            else:
                count = result[0]

            table_stats[table] = {
                "row_count": count
            }
            total_rows += count

        cursor.close()

        stats = {
            "config": config_name,
            "database_type": db_type,
            "database": config['database'],
            "total_tables": len(tables),
            "total_rows": total_rows,
            "tables": table_stats
        }

        logger.info("生成数据库统计资源")
        return json.dumps(stats, indent=2, ensure_ascii=False)

    @mcp.resource("info://database")
    def get_database_info(config_name: str = 'default') -> str:
        """
        获取数据库基本信息（纯文本）

        Args:
            config_name: 数据库配置名称

        Returns:
            数据库基本信息（文本格式）
        """
        from connection import get_connection_manager

        conn_mgr = get_connection_manager()
        connection = conn_mgr.get_connection(config_name)
        config = conn_mgr.config.get_config(config_name)
        db_type = config['type']

        cursor = connection.cursor()

        # 获取表数量
        if db_type == 'mysql':
            cursor.execute("SHOW TABLES")
            table_count = len(cursor.fetchall())

            cursor.execute("SELECT DATABASE()")
            database = cursor.fetchone()[0]

            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]

        elif db_type == 'postgresql':
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            table_count = len(cursor.fetchall())

            cursor.execute("SELECT current_database()")
            database = cursor.fetchone()[0]

            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0].split(',')[0]

        elif db_type == 'sqlite':
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_count = len(cursor.fetchall())

            database = config['database']

            cursor.execute("SELECT sqlite_version()")
            version = cursor.fetchone()[0]

        cursor.close()

        info = f"""
便携式 ChatBI MCP 服务器 - 数据库信息
====================================

配置名称: {config_name}
数据库类型: {db_type}
数据库名: {database}
版本: {version}
表数量: {table_count}
主机: {config['host']}
端口: {config['port']}
"""

        logger.info("生成数据库信息资源")
        return info.strip()

    logger.info("所有 MCP 资源已注册")
