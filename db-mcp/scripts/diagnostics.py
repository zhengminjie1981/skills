"""
便携式 ChatBI MCP 服务器 - 诊断模块
提供能力探测、错误诊断和结构化错误处理
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import importlib
import logging

logger = logging.getLogger(__name__)


class DependencyStatus(Enum):
    """依赖状态枚举"""
    INSTALLED = "installed"
    MISSING = "missing"
    VERSION_MISMATCH = "version_mismatch"


@dataclass
class DiagnosticResult:
    """诊断结果"""
    component: str
    status: DependencyStatus
    message: str
    fix_command: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class DatabaseError(Exception):
    """数据库操作基础异常"""
    def __init__(self, message: str, fix_command: Optional[str] = None):
        self.message = message
        self.fix_command = fix_command
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "error": self.message,
            "error_type": self.__class__.__name__
        }
        if self.fix_command:
            result["fix_command"] = self.fix_command
        return result


class DriverMissingError(DatabaseError):
    """数据库驱动缺失异常"""
    pass


class ConfigError(DatabaseError):
    """配置错误异常"""
    pass


class ConnectionError(DatabaseError):
    """连接错误异常"""
    pass


class Diagnostics:
    """诊断工具类"""

    @staticmethod
    def check_database_driver(db_type: str) -> DiagnosticResult:
        """
        检查特定数据库驱动

        Args:
            db_type: 数据库类型 ('mysql', 'postgresql', 'sqlite')

        Returns:
            DiagnosticResult: 诊断结果
        """
        driver_map = {
            'mysql': {
                'package': 'mysql-connector-python',
                'import': 'mysql',
                'version': '>=8.0.30',
                'install_cmd': 'pip install mysql-connector-python>=8.0.30'
            },
            'postgresql': {
                'package': 'psycopg2-binary',
                'import': 'psycopg2',
                'version': '>=2.9.0',
                'install_cmd': 'pip install psycopg2-binary>=2.9.0'
            },
            'sqlite': {
                'package': 'sqlite3',
                'import': 'sqlite3',
                'version': 'built-in',
                'install_cmd': None
            }
        }

        if db_type not in driver_map:
            return DiagnosticResult(
                component=f"{db_type}_driver",
                status=DependencyStatus.MISSING,
                message=f"不支持的数据库类型: {db_type}",
                fix_command=None
            )

        driver_info = driver_map[db_type]

        try:
            module = importlib.import_module(driver_info['import'])
            version = getattr(module, '__version__', 'unknown')

            return DiagnosticResult(
                component=f"{db_type}_driver",
                status=DependencyStatus.INSTALLED,
                message=f"{driver_info['package']} 已安装 (版本: {version})",
                fix_command=None,
                details={
                    "package": driver_info['package'],
                    "version": version
                }
            )

        except ImportError:
            return DiagnosticResult(
                component=f"{db_type}_driver",
                status=DependencyStatus.MISSING,
                message=f"{driver_info['package']} 未安装",
                fix_command=driver_info['install_cmd'],
                details={
                    "package": driver_info['package'],
                    "required_version": driver_info['version']
                }
            )

    @staticmethod
    def check_config_file(config_path: Optional[str] = None) -> DiagnosticResult:
        """
        检查配置文件状态

        Args:
            config_path: 配置文件路径（可选）

        Returns:
            DiagnosticResult: 诊断结果
        """
        from pathlib import Path

        if config_path:
            path = Path(config_path)
        else:
            # 默认配置路径
            script_dir = Path(__file__).parent.parent
            import os
            env_config = os.getenv('CHATBI_CONFIG')
            path = Path(env_config) if env_config else script_dir / 'db_config.json'

        if not path.exists():
            return DiagnosticResult(
                component="config_file",
                status=DependencyStatus.MISSING,
                message=f"配置文件不存在: {path}",
                fix_command="使用 auto_setup_database() 工具创建配置",
                details={
                    "path": str(path),
                    "example_path": str(path.parent / "references" / "db_config.example.json")
                }
            )

        try:
            import json
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            return DiagnosticResult(
                component="config_file",
                status=DependencyStatus.INSTALLED,
                message=f"配置文件已加载: {path}",
                fix_command=None,
                details={
                    "path": str(path),
                    "configs": list(config.keys())
                }
            )

        except Exception as e:
            return DiagnosticResult(
                component="config_file",
                status=DependencyStatus.VERSION_MISMATCH,
                message=f"配置文件格式错误: {e}",
                fix_command=f"检查并修复配置文件: {path}",
                details={
                    "path": str(path),
                    "error": str(e)
                }
            )

    @staticmethod
    def run_full_diagnostics() -> Dict[str, Any]:
        """
        运行完整诊断

        Returns:
            Dict: 包含所有诊断结果和建议
        """
        results = {
            "drivers": {},
            "config": {},
            "recommendations": []
        }

        # 检查所有数据库驱动
        for db_type in ['mysql', 'postgresql', 'sqlite']:
            result = Diagnostics.check_database_driver(db_type)
            results['drivers'][db_type] = {
                "status": result.status.value,
                "message": result.message,
                "fix_command": result.fix_command,
                "details": result.details
            }

        # 检查配置文件
        config_result = Diagnostics.check_config_file()
        results['config'] = {
            "status": config_result.status.value,
            "message": config_result.message,
            "fix_command": config_result.fix_command,
            "details": config_result.details
        }

        # 生成建议
        recommendations = []

        # 检查缺失的驱动
        missing_drivers = [
            db_type for db_type, info in results['drivers'].items()
            if info['status'] == 'missing' and db_type != 'sqlite'
        ]
        if missing_drivers:
            recommendations.append(
                f"建议安装数据库驱动: {', '.join(missing_drivers)}"
            )

        # 检查配置
        if results['config']['status'] == 'missing':
            recommendations.append(
                "建议使用 auto_setup_database() 工具自动配置数据库连接"
            )
        elif results['config']['status'] == 'version_mismatch':
            recommendations.append(
                "建议检查配置文件格式并修复错误"
            )

        results['recommendations'] = recommendations

        return results

    @staticmethod
    def test_database_connection(config_name: str = 'default') -> Dict[str, Any]:
        """
        测试数据库连接

        Args:
            config_name: 配置名称

        Returns:
            Dict: 连接测试结果
        """
        from datetime import datetime
        import time

        result = {
            "success": False,
            "config_name": config_name,
            "latency_ms": None,
            "server_info": None,
            "error": None,
            "troubleshooting": None
        }

        try:
            from connection import get_connection_manager

            conn_mgr = get_connection_manager()

            # 测试连接时间
            start_time = time.time()
            connection = conn_mgr.get_connection(config_name)
            elapsed_ms = (time.time() - start_time) * 1000

            result["latency_ms"] = round(elapsed_ms, 2)

            # 获取服务器信息
            config = conn_mgr.config.get_config(config_name)
            db_type = config['type']

            cursor = connection.cursor()

            if db_type == 'mysql':
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                cursor.execute("SELECT DATABASE()")
                db_name = cursor.fetchone()[0]
                result["server_info"] = {
                    "type": "MySQL",
                    "version": version,
                    "database": db_name
                }

            elif db_type == 'postgresql':
                cursor.execute("SELECT version()")
                version = cursor.fetchone()[0]
                cursor.execute("SELECT current_database()")
                db_name = cursor.fetchone()[0]
                result["server_info"] = {
                    "type": "PostgreSQL",
                    "version": version.split(',')[0],
                    "database": db_name
                }

            elif db_type == 'sqlite':
                cursor.execute("SELECT sqlite_version()")
                version = cursor.fetchone()[0]
                result["server_info"] = {
                    "type": "SQLite",
                    "version": version,
                    "database": config['database']
                }

            cursor.close()

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)

            # 生成故障排除建议
            error_msg = str(e).lower()

            if 'import' in error_msg or 'module' in error_msg:
                result["troubleshooting"] = "数据库驱动未安装，请运行 ensure_dependencies 或使用 auto_setup_database() 工具"
            elif 'connection' in error_msg or 'connect' in error_msg:
                result["troubleshooting"] = "无法连接到数据库服务器，请检查主机地址、端口和网络连接"
            elif 'authentication' in error_msg or 'access denied' in error_msg:
                result["troubleshooting"] = "认证失败，请检查用户名和密码"
            elif 'config' in error_msg or 'not found' in error_msg:
                result["troubleshooting"] = "配置错误，请使用 auto_setup_database() 工具重新配置"
            else:
                result["troubleshooting"] = f"未知错误: {str(e)}"

        return result
