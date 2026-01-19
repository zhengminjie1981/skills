# db-mcp - 数据库 MCP 服务管理

一个便捷的数据库 MCP 服务器技能，提供安全的数据库查询功能。支持 MySQL、PostgreSQL 和 SQLite，自动依赖检测，一键安装配置。

## 特点

- ✅ **便捷管理** - 提供统一的命令行工具管理 MCP 服务
- ✅ **自动检测** - 智能检测并安装所需的 Python 依赖
- ✅ **多数据库** - 支持 MySQL、PostgreSQL 和 SQLite
- ✅ **安全可靠** - 只读查询，防止 SQL 注入和危险操作
- ✅ **灵活配置** - 支持多数据库配置和环境变量

## 快速开始

### 1. 安装技能

将 `db-mcp` 文件夹拷贝到技能目录：

```bash
# Windows
xcopy db-mcp %USERPROFILE%\.claude\skills\ /E /I

# Linux/Mac
cp -r db-mcp ~/.claude/skills/
```

### 2. 自动安装依赖

```bash
cd db-mcp
python scripts/db-mcp.py install
```

该脚本会自动检测并安装所需的依赖包。

### 3. 配置数据库

编辑 `db_config.json`，填入数据库连接信息：

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

### 4. 安装 MCP 服务

```bash
python scripts/db-mcp.py setup
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

## 命令行工具

`scripts/db-mcp.py` 提供统一的命令行接口：

```bash
# 显示帮助
python scripts/db-mcp.py

# 自动安装依赖
python scripts/db-mcp.py install

# 检查 MCP 配置状态
python scripts/db-mcp.py check

# 安装 MCP 服务
python scripts/db-mcp.py setup

# 验证数据库配置
python scripts/db-mcp.py validate
```

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

### 多数据库配置

支持多个命名配置：

```json
{
  "default": {
    "type": "mysql",
    "host": "prod-server",
    ...
  },
  "analytics": {
    "type": "postgresql",
    "host": "analytics-db",
    ...
  },
  "local": {
    "type": "sqlite",
    "database": "./local.db"
  }
}
```

使用时指定配置名：`list_tables(config_name="analytics")`

### 环境变量配置

支持使用环境变量提高安全性：

```json
{
  "type": "mysql",
  "host": "${DB_HOST}",
  "user": "${DB_USER}",
  "password": "${DB_PASSWORD}",
  "database": "${DB_NAME}"
}
```

详细配置说明请参考 `references/config-format.md`。

## 安全特性

- ✅ **只读查询** - 仅允许 SELECT 查询
- ✅ **危险操作拦截** - 禁止 DROP、DELETE、UPDATE 等
- ✅ **自动 LIMIT** - 默认限制返回 1000 行
- ✅ **SQL 注入防护** - 使用参数化查询

## 故障排除

### Python 依赖缺失

**症状**: `ModuleNotFoundError: No module named 'fastmcp'`

**解决方案**:
```bash
python scripts/db-mcp.py install
```

### 数据库驱动缺失

**症状**: `ModuleNotFoundError: No module named 'mysql.connector'`

**解决方案**:
```bash
# MySQL 驱动
pip install -r references/requirements-mysql.txt

# PostgreSQL 驱动
pip install -r references/requirements-postgresql.txt
```

### MCP 服务未启动

1. 安装依赖：`python scripts/db-mcp.py install`
2. 检查配置：`python scripts/db-mcp.py check`
3. 重新安装：`python scripts/db-mcp.py setup`
4. 重启 Claude Code

### 连接失败

1. 验证配置：`python scripts/db-mcp.py validate`
2. 检查数据库服务是否运行
3. 检查网络连接和防火墙设置
4. 确认用户权限正确

## 项目结构

```
db-mcp/
├── SKILL.md                  # 技能入口文件
├── README.md                 # 本文档
├── db_config.json            # 数据库配置
├── pyproject.toml            # 项目配置
│
├── scripts/                  # 核心代码
│   ├── db-mcp.py            # 命令行工具
│   ├── server.py            # MCP 服务器
│   ├── config.py            # 配置管理
│   ├── connection.py        # 数据库连接
│   ├── tools.py             # MCP 工具
│   ├── resources.py         # MCP 资源
│   └── ...
│
└── references/               # 参考文档
    ├── config-format.md      # 配置格式说明
    ├── mcp-tools.md          # MCP 工具详细说明
    ├── db_config.example.json
    └── requirements*.txt
```

## 参考文档

- `SKILL.md` - 技能使用指南
- `references/config-format.md` - 配置文件格式说明
- `references/mcp-tools.md` - MCP 工具详细文档

## 许可证

MIT License
