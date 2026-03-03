# db-mcp - 数据库 MCP 服务管理

一个便捷的数据库 MCP 服务器技能，提供安全的数据库查询功能。支持 MySQL、PostgreSQL 和 SQLite，零配置启动，自动依赖检测和安装。

## 特点

- ✅ **零配置启动** - 首次使用无需手动配置，服务器可在无配置时启动
- ✅ **自动安装** - 运行时自动检测并安装缺失的数据库驱动
- ✅ **智能诊断** - 提供能力探测和连接测试功能
- ✅ **便捷管理** - 提供统一的命令行工具管理 MCP 服务
- ✅ **多数据库** - 支持 MySQL、PostgreSQL 和 SQLite
- ✅ **安全可靠** - 只读查询，防止 SQL 注入和危险操作
- ✅ **灵活配置** - 支持多数据库配置和环境变量

## 快速开始

### 方式 1: 零配置自动启动（推荐）

**最简单的方式** - 无需手动操作！

1. **安装技能**：将 `db-mcp` 文件夹拷贝到技能目录
2. **启动服务**：`python scripts/db-mcp.py setup`
3. **重启 Claude Code**
4. **自动配置**：在对话中直接调用 `auto_setup_database()` 工具

```python
# 在 Claude Code 对话中直接使用
auto_setup_database(
    db_type="mysql",
    connection_params={
        "host": "localhost",
        "port": 3306,
        "user": "username",
        "password": "password",
        "database": "dbname"
    }
)
```

工具会自动：
- ✓ 检测并安装所需的数据库驱动
- ✓ 创建配置文件
- ✓ 测试连接
- ✓ 验证基本功能

### 方式 2: 传统手动配置

<details>
<summary>点击展开传统配置步骤</summary>

#### 1. 安装技能

将 `db-mcp` 文件夹拷贝到技能目录：

```bash
# Windows
xcopy db-mcp %USERPROFILE%\.claude\skills\ /E /I

# Linux/Mac
cp -r db-mcp ~/.claude/skills/
```

#### 2. 自动安装依赖

```bash
cd db-mcp
python scripts/db-mcp.py install
```

该脚本会自动检测并安装所需的依赖包。

#### 3. 配置数据库

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

#### 4. 安装 MCP 服务

```bash
python scripts/db-mcp.py setup
```

#### 5. 重启 Claude Code

重启后即可使用！

</details>

## 可用工具

### 诊断和配置工具（新增）

| 工具名 | 说明 | 使用场景 |
|--------|------|----------|
| `check_capabilities` | 检查系统数据库能力 | 查看已安装驱动、配置状态、优化建议 |
| `auto_setup_database` | 自动配置数据库 | 零配置启动，自动安装驱动并创建配置 |
| `test_connection` | 测试数据库连接 | 诊断连接问题，查看延迟和服务器信息 |

### 数据库操作工具

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

# 自动安装依赖（按需安装驱动）
python scripts/db-mcp.py install

# 仅安装 MySQL 驱动
python scripts/db-mcp.py install --db-type mysql

# 仅安装 PostgreSQL 驱动
python scripts/db-mcp.py install --db-type postgresql

# 安装所有驱动
python scripts/db-mcp.py install --db-type all

# 列出缺失的依赖（不安装）
python scripts/db-mcp.py install --list-needs

# 检查 MCP 配置状态
python scripts/db-mcp.py check

# 安装 MCP 服务
python scripts/db-mcp.py setup

# 验证数据库配置
python scripts/db-mcp.py validate
```

## 使用示例

### 示例 1: 零配置首次使用

```
用户: 我想连接到 MySQL 数据库
→ 调用 check_capabilities() 查看当前状态
→ 调用 auto_setup_database() 自动配置
→ 开始使用数据库工具
```

### 示例 2: 查询用户数据

```
用户: 查询 users 表中的所有管理员
→ 使用 describe_table("users") 了解结构
→ 使用 execute_query("SELECT * FROM users WHERE role = 'admin'")
```

### 示例 3: 数据分析

```
用户: 统计上个月的订单总额
→ 使用 search_tables("order") 查找订单表
→ 使用 describe_table("orders") 查看字段
→ 使用 execute_query("SELECT DATE(order_date), SUM(amount) FROM orders WHERE order_date >= '2024-12-01' GROUP BY DATE(order_date)")
```

### 示例 4: 连接诊断

```
用户: 测试数据库连接
→ 使用 test_connection() 查看延迟和服务器信息
→ 使用 check_capabilities() 检查驱动和配置状态
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

### 依赖自动安装

**症状**: 调用工具时提示驱动缺失

**解决方案**: 无需手动操作！系统会自动安装缺失的驱动。

<details>
<summary>手动安装（可选）</summary>

```bash
# 自动检测并安装
python scripts/db-mcp.py install

# 或指定数据库类型
python scripts/db-mcp.py install --db-type mysql

# 或手动安装
pip install -r references/requirements-mysql.txt      # MySQL 驱动
pip install -r references/requirements-postgresql.txt # PostgreSQL 驱动
```

</details>

### Python 依赖缺失

**症状**: `ModuleNotFoundError: No module named 'fastmcp'`

**解决方案**:
```bash
python scripts/db-mcp.py install
```

### 配置文件不存在

**症状**: 服务器启动时提示配置文件不存在

**解决方案**:

**方式 1**: 使用 `auto_setup_database()` 工具自动创建配置（推荐）

**方式 2**: 手动创建配置文件
```bash
cp references/db_config.example.json db_config.json
# 然后编辑配置文件
```

### MCP 服务未启动

1. 检查配置：`python scripts/db-mcp.py check`
2. 重新安装：`python scripts/db-mcp.py setup`
3. 重启 Claude Code

### 连接失败

**方式 1**: 使用诊断工具
```python
# 查看当前状态
check_capabilities()

# 测试连接
test_connection()
```

**方式 2**: 命令行验证
```bash
python scripts/db-mcp.py validate
```

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
