---
name: db-mcp
description: 数据库 MCP 服务管理技能。当用户需要查询数据库、管理数据库配置、或使用 MCP 数据库功能时使用此技能。自动检测并安装 MCP 服务，提供便捷的数据库查询接口。
---

# db-mcp - 数据库 MCP 服务管理

## 快速开始

### 首次使用（自动依赖检测）

首次使用本技能时，会自动检测 Python 依赖环境：

```bash
# 自动检测并安装所需的 Python 依赖包
python scripts/db-mcp.py install
```

该脚本会：
- ✓ 自动查找 skill 安装位置
- ✓ 检测已安装的依赖包版本
- ✓ 根据配置文件智能识别需要的数据库驱动
- ✓ 一键安装缺失的依赖
- ✓ 支持核心依赖 + MySQL/PostgreSQL 驱动

### 手动安装依赖

如果自动检测脚本无法使用，可以手动安装：

```bash
# 方式1: 安装所有依赖（含 MySQL 和 PostgreSQL 驱动）
pip install -r references/requirements.txt

# 方式2: 仅安装核心依赖（MCP 框架）
pip install -r references/requirements-core.txt

# 方式3: 按需安装数据库驱动
pip install -r references/requirements-mysql.txt      # MySQL 驱动
pip install -r references/requirements-postgresql.txt # PostgreSQL 驱动
```

### MCP 服务配置

```bash
# 检查 MCP 配置状态
python scripts/db-mcp.py check

# 安装/更新 MCP 服务到 Claude 配置
python scripts/db-mcp.py setup

# 验证数据库配置
python scripts/db-mcp.py validate
```

## 工作流程

### 1. 初始化检查

当用户首次请求数据库操作时：

1. **依赖检测** - 运行 `python scripts/db-mcp.py install` 检查 Python 依赖
2. **MCP 配置** - 运行 `python scripts/db-mcp.py check` 检查 MCP 配置状态
3. **安装服务** - 如果未配置，运行 `python scripts/db-mcp.py setup` 自动安装
4. **重启应用** - 提示用户重启 Claude Code 使配置生效

### 2. 数据库操作

MCP 服务安装后，可直接使用以下 MCP 工具：

| MCP 工具 | 功能 | 使用场景 |
|---------|------|---------|
| `list_tables` | 列出所有表 | 查看数据库中有哪些表 |
| `describe_table` | 查看表结构 | 了解表的字段、类型、索引 |
| `execute_query` | 执行 SELECT 查询 | 查询数据 |
| `get_table_count` | 获取表行数 | 统计表大小 |
| `get_database_info` | 获取数据库信息 | 查看数据库版本、名称 |
| `search_tables` | 搜索表 | 根据关键字查找表 |

### 3. 配置管理

数据库配置文件：`db_config.json`

支持三种数据库类型：
- **MySQL**: 需要 `mysql-connector-python`
- **PostgreSQL**: 需要 `psycopg2-binary`
- **SQLite**: 内置支持

配置示例见 `references/config-format.md`

### 4. 多数据库支持

`db_config.json` 支持多个命名配置：

```json
{
  "default": { "type": "mysql", ... },
  "analytics": { "type": "postgresql", ... },
  "local": { "type": "sqlite", ... }
}
```

使用时指定配置名：`execute_query(query="...", config_name="analytics")`

## 安全特性

- **只读访问**: 所有工具仅允许 SELECT 查询
- **自动 LIMIT**: 默认限制返回 1000 行
- **SQL 注入防护**: 使用参数化查询
- **危险操作拦截**: 禁止 DROP、DELETE、UPDATE、INSERT 等

## 典型使用场景

### 场景 1: 查询用户数据

```
用户: 查询 users 表中的所有管理员
→ 使用 describe_table("users") 了解结构
→ 使用 execute_query("SELECT * FROM users WHERE role = 'admin'")
```

### 场景 2: 数据分析

```
用户: 统计上个月的订单总额
→ 使用 search_tables("order") 查找订单表
→ 使用 describe_table("orders") 查看字段
→ 使用 execute_query("SELECT DATE(order_date), SUM(amount) FROM orders WHERE order_date >= '2024-12-01' GROUP BY DATE(order_date)")
```

### 场景 3: 数据库探索

```
用户: 这个数据库有哪些表？
→ 使用 list_tables()
→ 使用 get_database_info() 查看数据库信息
→ 使用 get_table_count() 获取各表行数统计
```

## 故障排除

### Python 依赖缺失

**症状**: `ModuleNotFoundError: No module named 'fastmcp'`

**解决方案**:
```bash
# 自动检测并安装
python scripts/db-mcp.py install

# 或手动安装核心依赖
pip install -r references/requirements-core.txt
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

1. 先确保 Python 依赖已安装：`python scripts/db-mcp.py install`
2. 检查配置：`python scripts/db-mcp.py check`
3. 重新安装：`python scripts/db-mcp.py setup`
4. 重启 Claude Code

### 连接失败

1. 验证配置：`python scripts/db-mcp.py validate`
2. 检查数据库服务是否运行
3. 检查数据库配置是否正确

### 找到 MCP 工具

MCP 工具由 MCP 服务器提供，不是本技能的直接工具。使用前确保：
1. MCP 服务已安装并运行
2. Claude Code 已重启
3. 在对话中直接调用工具，如 `execute_query(...)`

## 参考文档

- `references/mcp-tools.md` - MCP 工具详细说明
- `references/config-format.md` - 配置文件格式说明

## 技能文件说明

```
db-mcp/
├── SKILL.md              # 本文件，技能主入口
├── README.md             # 项目说明
├── db_config.json        # 数据库配置
├── pyproject.toml        # 项目配置（支持 uvx 启动）
│
├── scripts/              # 核心代码和工具脚本
│   ├── db-mcp.py        # 统一命令行工具
│   ├── server.py        # MCP 服务器主入口
│   ├── config.py        # 配置管理
│   ├── connection.py    # 数据库连接
│   ├── tools.py         # MCP 工具
│   ├── resources.py     # MCP 资源
│   ├── ensure_dependencies.py
│   ├── check_mcp.py
│   ├── install_mcp.py
│   └── validate_config.py
│
└── references/           # 参考文档和模板
    ├── requirements*.txt
    ├── install_config.json
    ├── db_config.example.json
    ├── mcp-tools.md
    └── config-format.md
```

## 使用 scripts/db-mcp.py 命令行工具

**从任何位置运行**（无需 cd 到项目目录）：

```bash
# 显示帮助
python scripts/db-mcp.py

# 安装依赖
python scripts/db-mcp.py install

# 检查配置
python scripts/db-mcp.py check

# 安装 MCP 服务
python scripts/db-mcp.py setup

# 验证配置
python scripts/db-mcp.py validate
```

**自动查找 skill 位置**：
- 脚本所在目录
- 当前工作目录
- `~/.claude/skills/db-mcp/`
- `~/.claude/skills/portable-chatbi-mcp/`
- 当前项目的 `.claude/skills/` 目录
