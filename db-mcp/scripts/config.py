"""
便携式 ChatBI MCP 服务器 - 配置管理模块
支持 JSON 配置文件和环境变量覆盖
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """配置管理类"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径，默认为脚本目录下的 db_config.json
        """
        # 获取项目根目录
        self.script_dir = Path(__file__).parent.parent.absolute()

        # 配置文件路径
        if config_path:
            self.config_path = Path(config_path)
        else:
            # 支持环境变量覆盖
            env_config = os.getenv('CHATBI_CONFIG')
            if env_config:
                self.config_path = Path(env_config)
            else:
                self.config_path = self.script_dir / 'db_config.json'

        # 加载配置
        self.configs = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件

        Returns:
            配置字典
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"配置文件不存在: {self.config_path}\n"
                f"请从 db_config.example.json 复制并配置数据库连接信息"
            )

        with open(self.config_path, 'r', encoding='utf-8') as f:
            configs = json.load(f)

        # 验证配置
        self._validate_config(configs)

        return configs

    def _validate_config(self, configs: Dict[str, Any]) -> None:
        """
        验证配置文件格式

        Args:
            configs: 配置字典

        Raises:
            ValueError: 配置无效时
        """
        if not configs:
            raise ValueError("配置文件为空")

        for name, config in configs.items():
            # 检查必需字段
            required_fields = ['type', 'host', 'port', 'user', 'password', 'database']
            missing_fields = [f for f in required_fields if f not in config]

            if missing_fields:
                raise ValueError(
                    f"配置 '{name}' 缺少必需字段: {', '.join(missing_fields)}"
                )

            # 检查数据库类型
            if config['type'] not in ['mysql', 'postgresql', 'sqlite']:
                raise ValueError(
                    f"配置 '{name}' 不支持的数据库类型: {config['type']}\n"
                    f"支持的类型: mysql, postgresql, sqlite"
                )

    def get_config(self, name: str = 'default') -> Dict[str, Any]:
        """
        获取指定名称的配置

        Args:
            name: 配置名称，默认为 'default'

        Returns:
            配置字典（已展开环境变量）
        """
        if name not in self.configs:
            raise ValueError(f"配置 '{name}' 不存在")

        config = self.configs[name].copy()

        # 展开环境变量
        config = self._expand_env_vars(config)

        return config

    def _expand_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        展开配置中的环境变量

        支持两种格式：
        1. "${ENV_VAR}" - 纯环境变量
        2. 如果字段值以 ${ 开头，则使用环境变量

        Args:
            config: 配置字典

        Returns:
            展开环境变量后的配置
        """
        result = {}

        for key, value in config.items():
            if isinstance(value, str):
                # 支持 ${ENV_VAR} 格式
                if value.startswith('${') and value.endswith('}'):
                    env_var = value[2:-1]
                    env_value = os.getenv(env_var)

                    if env_value is None:
                        raise ValueError(
                            f"环境变量 {env_var} 未定义\n"
                            f"请在配置或环境变量中设置 {env_var}"
                        )

                    result[key] = env_value
                else:
                    # 优先使用环境变量覆盖
                    env_key = f"CHATBI_{key.upper()}"
                    result[key] = os.getenv(env_key, value)
            else:
                result[key] = value

        return result

    def list_configs(self) -> list:
        """
        列出所有配置名称

        Returns:
            配置名称列表
        """
        return list(self.configs.keys())

    def get_connection_url(self, name: str = 'default') -> str:
        """
        生成数据库连接 URL

        Args:
            name: 配置名称

        Returns:
            数据库连接 URL
        """
        config = self.get_config(name)

        db_type = config['type']
        host = config['host']
        port = config['port']
        user = config['user']
        password = config['password']
        database = config['database']

        if db_type == 'mysql':
            # MySQL URL: mysql+mysqlconnector://user:password@host:port/database
            return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
        elif db_type == 'postgresql':
            # PostgreSQL URL: postgresql://user:password@host:port/database
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        elif db_type == 'sqlite':
            # SQLite URL: sqlite:///database
            return f"sqlite:///{database}"
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")


# 全局配置实例
_global_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    获取全局配置实例（单例模式）

    Args:
        config_path: 配置文件路径

    Returns:
        Config 实例
    """
    global _global_config

    if _global_config is None:
        _global_config = Config(config_path)

    return _global_config
