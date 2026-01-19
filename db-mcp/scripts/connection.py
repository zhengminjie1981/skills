"""
便携式 ChatBI MCP 服务器 - 数据库连接管理模块
支持 MySQL、PostgreSQL 和 SQLite
"""

import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ConnectionManager:
    """数据库连接管理器"""

    def __init__(self):
        """初始化连接管理器"""
        from config import get_config

        self.config = get_config()
        self.connections: Dict[str, Any] = {}

    def get_connection(self, name: str = 'default'):
        """
        获取数据库连接

        Args:
            name: 配置名称，默认为 'default'

        Returns:
            数据库连接对象
        """
        # 如果连接已存在，检查是否有效
        if name in self.connections:
            if self._is_connection_valid(name):
                logger.debug(f"使用现有连接: {name}")
                return self.connections[name]
            else:
                # 连接无效，移除并重新创建
                logger.warning(f"连接 {name} 已失效，重新连接")
                del self.connections[name]

        # 创建新连接
        logger.info(f"创建新连接: {name}")
        connection = self._create_connection(name)
        self.connections[name] = connection

        return connection

    def _create_connection(self, name: str):
        """
        创建数据库连接

        Args:
            name: 配置名称

        Returns:
            数据库连接对象
        """
        config = self.config.get_config(name)
        db_type = config['type']

        if db_type == 'mysql':
            return self._create_mysql_connection(config)
        elif db_type == 'postgresql':
            return self._create_postgresql_connection(config)
        elif db_type == 'sqlite':
            return self._create_sqlite_connection(config)
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

    def _create_mysql_connection(self, config: Dict[str, Any]):
        """
        创建 MySQL 连接

        Args:
            config: 数据库配置

        Returns:
            MySQL 连接对象
        """
        try:
            import mysql.connector
        except ImportError:
            raise ImportError(
                "未安装 mysql-connector-python\n"
                "请运行: pip install mysql-connector-python"
            )

        try:
            connection = mysql.connector.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                charset='utf8mb4',
                autocommit=False
            )

            logger.info(
                f"MySQL 连接成功: {config['host']}:{config['port']}/{config['database']}"
            )
            return connection

        except Exception as e:
            logger.error(f"MySQL 连接失败: {e}")
            raise

    def _create_postgresql_connection(self, config: Dict[str, Any]):
        """
        创建 PostgreSQL 连接

        Args:
            config: 数据库配置

        Returns:
            PostgreSQL 连接对象
        """
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError:
            raise ImportError(
                "未安装 psycopg2-binary\n"
                "请运行: pip install psycopg2-binary"
            )

        try:
            connection = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database']
            )

            # 使用 RealDictCursor 返回字典格式结果
            connection.cursor_factory = psycopg2.extras.RealDictCursor

            logger.info(
                f"PostgreSQL 连接成功: {config['host']}:{config['port']}/{config['database']}"
            )
            return connection

        except Exception as e:
            logger.error(f"PostgreSQL 连接失败: {e}")
            raise

    def _create_sqlite_connection(self, config: Dict[str, Any]):
        """
        创建 SQLite 连接

        Args:
            config: 数据库配置

        Returns:
            SQLite 连接对象
        """
        import sqlite3

        try:
            connection = sqlite3.connect(config['database'])
            connection.row_factory = sqlite3.Row  # 返回字典格式结果

            logger.info(f"SQLite 连接成功: {config['database']}")
            return connection

        except Exception as e:
            logger.error(f"SQLite 连接失败: {e}")
            raise

    def _is_connection_valid(self, name: str) -> bool:
        """
        检查连接是否有效

        Args:
            name: 配置名称

        Returns:
            连接是否有效
        """
        if name not in self.connections:
            return False

        connection = self.connections[name]
        config = self.config.get_config(name)
        db_type = config['type']

        try:
            if db_type == 'mysql':
                return connection.is_connected()
            elif db_type == 'postgresql':
                cursor = connection.cursor()
                cursor.execute('SELECT 1')
                cursor.close()
                return True
            elif db_type == 'sqlite':
                # SQLite 连接通常保持有效
                return True
            else:
                return False

        except Exception as e:
            logger.warning(f"连接验证失败: {name}, {e}")
            return False

    def close_connection(self, name: str) -> None:
        """
        关闭指定连接

        Args:
            name: 配置名称
        """
        if name in self.connections:
            try:
                self.connections[name].close()
                logger.info(f"连接已关闭: {name}")
            except Exception as e:
                logger.warning(f"关闭连接时出错: {name}, {e}")
            finally:
                del self.connections[name]

    def close_all_connections(self) -> None:
        """关闭所有连接"""
        for name in list(self.connections.keys()):
            self.close_connection(name)

    @contextmanager
    def get_cursor(self, name: str = 'default', dictionary: bool = True):
        """
        获取数据库游标（上下文管理器）

        Args:
            name: 配置名称
            dictionary: 是否返回字典格式结果（仅 MySQL）

        Yields:
            数据库游标
        """
        connection = self.get_connection(name)
        config = self.config.get_config(name)
        db_type = config['type']

        cursor = None
        try:
            if db_type == 'mysql':
                cursor = connection.cursor(dictionary=dictionary)
            else:
                cursor = connection.cursor()

            yield cursor

        finally:
            if cursor:
                cursor.close()


# 全局连接管理器实例
_global_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """
    获取全局连接管理器实例（单例模式）

    Returns:
        ConnectionManager 实例
    """
    global _global_connection_manager

    if _global_connection_manager is None:
        _global_connection_manager = ConnectionManager()

    return _global_connection_manager
