# 便携式 ChatBI MCP 服务器

一个像技能一样便携的 MCP 服务器，提供数据库查询功能。无需 pip install，使用 uvx 自动管理依赖。

## 特点

- ✅ **便携** - 拷贝文件夹到任意位置即可使用
- ✅ **零安装** - 无需手动 pip install，uvx 自动下载依赖
- ✅ **多数据库** - 支持 MySQL、PostgreSQL 和 SQLite
- ✅ **安全** - 只读查询，防止 SQL 注入和危险操作
- ✅ **灵活配置** - 支持配置文件和环境变量

## 快速开始

### 1. 安装 uvx

```bash
pip install uv
```

### 2. 拷贝文件

将 `portable-chatbi-mcp` 文件夹拷贝到任意位置，例如：

```bash
# Windows
xcopy portable-chatbi-mcp %USERPROFILE%\.claude\skills\ /E /I

# Linux/Mac
cp -r portable-chatbi-mcp ~/.claude/skills/
```

### 3. 配置数据库

```bash
# 复制配置模板
cd portable-chatbi-mcp
cp db_config.example.json db_config.json

# 编辑 db_config.json，填入数据库信息
```

配置示例：

```json
{
  "default": {
    "type": "mysql",
    "host": "localhost",
    "port": 3306,
    "user": "your-username",
    "password": "your-password",
    "database": "your-database"
  }
}
```

### 4. 配置 Claude Code

将以下配置添加到 `~/.claude.json` 中：

**Windows:**
```json
{
  "mcpServers": {
    "chatbi": {
      "command": "uvx",
      "args": [
        "--directory",
        "%USERPROFILE%\\.claude\\skills\\portable-chatbi-mcp",
        "--with",
        "mysql-connector-python",
        "chatbi-mcp"
      ]
    }
  }
}
```

**Linux/Mac:**
```json
{
  "mcpServers": {
    "chatbi": {
      "command": "uvx",
      "args": [
        "--directory",
        "/home/username/.claude/skills/portable-chatbi-mcp",
        "--with",
        "mysql-connector-python",
        "chatbi-mcp"
      ]
    }
  }
}
```

### 5. 重启 Claude Code

重启后即可使用！

## 可用工具

| 工具名 | 说明 | 示例 |
|--------|------|------|
| `list_tables` | 列出所有表 | "列出所有表" |
| `describe_table` | 查看表结构 | "查看 users 表的结构" |
| `execute_query` | 执行查询 | "查询 users 表的前 10 条记录" |
| `get_table_count` | 获取表行数 | "users 表有多少行？" |
| `get_database_info` | 获取数据库信息 | "数据库版本是多少？" |
| `search_tables` | 搜索表 | "搜索包含 user 的表" |

## 可用资源

| 资源 URI | 说明 |
|----------|------|
| `schema://tables` | 所有表的架构（Markdown） |
| `schema://table/{表名}` | 特定表的详细架构 |
| `stats://database` | 数据库统计信息（JSON） |
| `info://database` | 数据库基本信息（文本） |

## 配置详解

### 支持的数据库类型

#### MySQL
```json
{
  "type": "mysql",
  "host": "localhost",
  "port": 3306,
  "user": "username",
  "password": "password",
  "database": "dbname"
}
```

#### PostgreSQL
```json
{
  "type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "user": "postgres",
  "password": "password",
  "database": "dbname"
}
```

#### SQLite
```json
{
  "type": "sqlite",
  "database": "/path/to/database.db"
}
```

### 环境变量配置

支持使用环境变量，提高安全性：

```json
{
  "type": "mysql",
  "host": "${DB_HOST}",
  "user": "${DB_USER}",
  "password": "${DB_PASSWORD}",
  "database": "${DB_NAME}"
}
```

或在 Claude 配置中设置环境变量：

```json
{
  "mcpServers": {
    "chatbi": {
      "command": "uvx",
      "args": ["--directory", "...", "chatbi-mcp"],
      "env": {
        "DB_HOST": "localhost",
        "DB_USER": "myuser",
        "DB_PASSWORD": "mypass",
        "DB_NAME": "mydb"
      }
    }
  }
}
```

## 常见问题

### Q: uvx 是什么？

A: uvx 是 uv 的工具执行器，类似于 npx。它会自动下载并运行 Python 工具，无需手动安装依赖。

### Q: 首次运行会很慢吗？

A: 首次运行时 uvx 会下载依赖包，需要网络连接。下载完成后会缓存，后续启动很快。

### Q: 支持多数据库配置吗？

A: 支持！在 `db_config.json` 中添加多个配置：

```json
{
  "prod": {
    "type": "mysql",
    "host": "prod-server",
    ...
  },
  "dev": {
    "type": "mysql",
    "host": "localhost",
    ...
  }
}
```

使用时指定配置名：`list_tables(config_name="prod")`

### Q: 如何查看日志？

A: MCP 服务器的日志会输出到 Claude Code 的日志中。如需调试，可以在终端直接运行：

```bash
cd portable-chatbi-mcp
python server.py
```

### Q: 忘记配置 db_config.json 会怎样？

A: 服务器启动时会提示配置文件路径，并给出配置指引。

## 安全特性

- ✅ **只读查询** - 仅允许 SELECT 查询
- ✅ **危险操作拦截** - 禁止 DROP、DELETE、UPDATE 等
- ✅ **自动 LIMIT** - 默认限制返回 1000 行
- ✅ **SQL 注入防护** - 使用参数化查询

## 故障排除

### 问题: 无法连接数据库

检查：
1. `db_config.json` 中的连接信息是否正确
2. 数据库服务是否正在运行
3. 网络连接是否正常
4. 用户权限是否足够

### 问题: uvx 命令未找到

解决：
```bash
pip install uv
```

### 问题: 依赖安装失败

1. 检查网络连接
2. 尝试手动安装：`uvx --directory /path/to/portable-chatbi-mcp --with mysql-connector-python chatbi-mcp`

## 项目结构

```
portable-chatbi-mcp/
├── server.py                 # 主入口
├── connection.py             # 连接管理
├── tools.py                  # MCP 工具
├── resources.py              # MCP 资源
├── config.py                 # 配置管理
├── pyproject.toml            # 项目配置
├── db_config.example.json    # 配置模板
├── install_config.json       # Claude 配置模板
└── README.md                 # 本文档
```

## 许可证

MIT License

## 相关资源

- [Claude Code 文档](https://docs.anthropic.com/claude-code)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [uv 工具](https://github.com/astral-sh/uv)
