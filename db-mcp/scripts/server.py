"""
便携式 ChatBI MCP 服务器 - 主入口
提供符合 MCP 标准的数据库访问服务
"""

import logging
from collections import abc
from contextlib import asynccontextmanager
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """应用上下文，包含共享的资源"""
    conn_mgr = None


@asynccontextmanager
async def lifespan(server):
    """
    管理 MCP 服务器的生命周期

    在服务器启动时初始化数据库连接管理器，
    在服务器关闭时清理所有连接。

    Args:
        server: FastMCP 服务器实例

    Yields:
        AppContext: 包含连接管理器的应用上下文
    """
    from connection import get_connection_manager

    # 启动时初始化
    logger.info("ChatBI MCP 服务器启动中...")
    conn_mgr = get_connection_manager()
    logger.info("数据库连接管理器已初始化")

    try:
        yield AppContext(conn_mgr=conn_mgr)
    finally:
        # 关闭时清理
        logger.info("ChatBI MCP 服务器关闭中...")
        if conn_mgr:
            conn_mgr.close_all_connections()
        logger.info("所有数据库连接已关闭")


def create_mcp_server():
    """
    创建并配置 ChatBI MCP 服务器

    Returns:
        FastMCP: 配置好的 MCP 服务器实例
    """
    from fastmcp import FastMCP
    import tools
    import resources

    # 创建 MCP 服务器
    mcp = FastMCP(
        name="ChatBI",
        instructions="""便携式 ChatBI MCP 服务器

此服务器提供以下功能：
- 列出数据库中的所有表
- 查看表的详细结构
- 执行安全的只读 SQL 查询
- 获取数据库统计信息
- 搜索包含关键字的表

安全特性：
- 所有查询工具都是只读的
- 自动限制查询返回行数
- 防止 SQL 注入
- 禁止危险操作（DROP, DELETE, UPDATE 等）

配置方式：
- 支持 MySQL、PostgreSQL 和 SQLite
- 通过 db_config.json 配置数据库连接
- 支持环境变量覆盖配置

使用示例：
1. 使用 list_tables 查看所有表
2. 使用 describe_table 查看表结构
3. 使用 execute_query 执行查询
4. 使用 get_table_count 获取表行数
5. 使用资源 schema://table/{表名} 查看详细架构
""",
        lifespan=lifespan
    )

    # 注册工具和资源
    tools.register_all(mcp)
    resources.register_all(mcp)

    return mcp


def main():
    """MCP 服务器主入口"""
    import sys

    # 检查配置文件
    import os
    from pathlib import Path

    script_dir = Path(__file__).parent.parent.absolute()
    config_path = os.getenv('CHATBI_CONFIG', script_dir / 'db_config.json')

    if not Path(config_path).exists():
        print(f"错误: 配置文件不存在: {config_path}", file=sys.stderr)
        print(f"\n请按以下步骤配置：", file=sys.stderr)
        print(f"1. 从 references/db_config.example.json 复制配置:", file=sys.stderr)
        print(f"   cp {script_dir / 'references' / 'db_config.example.json'} {config_path}", file=sys.stderr)
        print(f"\n2. 编辑配置文件，填入数据库连接信息\n", file=sys.stderr)
        sys.exit(1)

    # 创建并运行服务器
    mcp = create_mcp_server()

    # 运行服务器（使用 stdio 传输）
    mcp.run()


if __name__ == "__main__":
    main()
