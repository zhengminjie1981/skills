---
name: db-mcp
description: |
  数据库 MCP 服务管理技能，支持零配置启动和自动依赖安装。

  **触发场景**（包含以下关键词）：
  - 连接数据库：连接 MySQL、连接 PostgreSQL、连接 SQLite、数据库连接
  - 查询数据：查询数据库、执行 SQL、SELECT 查询、数据库查询
  - 管理配置：数据库配置、MCP 数据库、db-mcp
  - 诊断问题：测试连接、检查数据库、数据库诊断

  **不触发场景**：
  - 纯粹的 SQL 语法问题（不涉及连接和执行）
  - 其他类型的 MCP 服务配置
---

# db-mcp - 数据库 MCP 服务管理

## 一行总结

> 零配置数据库连接服务，支持 MySQL、PostgreSQL、SQLite 的安全只读查询。

## 决策树

```
需要数据库操作？
├─ 首次使用 → auto_setup_database() → 自动配置
│             └─ 自动安装驱动 → 创建配置 → 测试连接
├─ 已配置 → 直接使用工具
│           ├─ list_tables / describe_table → 探索结构
│           ├─ execute_query → 查询数据
│           └─ test_connection → 诊断问题
└─ 连接问题 → check_capabilities() → 查看状态
              └─ 获取优化建议
```

## 快速开始

### 零配置自动启动（推荐）

**首次使用最简单的方式**：

1. **启动服务**: `python scripts/db-mcp.py setup`
2. **重启 Claude Code**
3. **自动配置**: 在对话中调用 `auto_setup_database()` 工具

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

工具会自动完成：
- ✓ 检测并安装所需的数据库驱动
- ✓ 创建配置文件
- ✓ 测试连接
- ✓ 验证基本功能（列出表）

### 传统手动配置

<details>
<summary>点击展开传统配置步骤</summary>

#### 首次使用（自动依赖检测）

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

#### 手动安装依赖

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

#### MCP 服务配置

```bash
# 检查 MCP 配置状态
python scripts/db-mcp.py check

# 安装/更新 MCP 服务到 Claude 配置
python scripts/db-mcp.py setup

# 验证数据库配置
python scripts/db-mcp.py validate
```

</details>

## 工作流程

### 1. 零配置启动（推荐流程）

当用户首次请求数据库操作时：

1. **启动服务** - 服务器可在无配置时启动（延迟加载）
2. **自动配置** - 调用 `auto_setup_database()` 工具配置数据库
3. **自动安装** - 工具自动检测并安装所需的数据库驱动
4. **立即使用** - 配置完成后直接开始使用数据库工具

**无需手动操作步骤！**

### 2. 传统工作流程

<details>
<summary>点击展开传统流程</summary>

1. **依赖检测** - 运行 `python scripts/db-mcp.py install` 检查 Python 依赖
2. **MCP 配置** - 运行 `python scripts/db-mcp.py check` 检查 MCP 配置状态
3. **安装服务** - 如果未配置，运行 `python scripts/db-mcp.py setup` 自动安装
4. **重启应用** - 提示用户重启 Claude Code 使配置生效

</details>

### 3. 数据库操作

MCP 服务安装后，可直接使用以下 MCP 工具：

#### 诊断和配置工具（新增）

| MCP 工具 | 功能 | 使用场景 |
|---------|------|---------|
| `check_capabilities` | 检查系统能力 | 查看已安装驱动、配置状态、优化建议 |
| `auto_setup_database` | 自动配置数据库 | 零配置启动，自动安装驱动并创建配置 |
| `test_connection` | 测试数据库连接 | 诊断连接问题，查看延迟和服务器信息 |

#### 数据库操作工具

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

### 场景 0: 零配置首次使用

```
用户: 我想连接到 MySQL 数据库，地址是 localhost，用户名 root
→ 使用 check_capabilities() 查看当前系统状态
→ 使用 auto_setup_database() 自动配置
   - 自动检测并安装 MySQL 驱动
   - 创建配置文件
   - 测试连接
   - 验证基本功能
→ 立即开始使用数据库工具
```

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

### 场景 4: 连接诊断

```
用户: 测试数据库连接是否正常
→ 使用 test_connection() 查看延迟和服务器信息
→ 使用 check_capabilities() 检查驱动和配置状态
→ 获取优化建议
```

## 故障排除

### 依赖自动安装（新增）

**症状**: 调用工具时提示驱动缺失

**解决方案**: 无需手动操作！系统会自动安装缺失的驱动。

如需手动控制：
```bash
# 自动检测并安装
python scripts/db-mcp.py install

# 指定数据库类型
python scripts/db-mcp.py install --db-type mysql

# 列出缺失的依赖
python scripts/db-mcp.py install --list-needs
```

### Python 依赖缺失

**症状**: `ModuleNotFoundError: No module named 'fastmcp'`

**解决方案**:
```bash
# 自动检测并安装
python scripts/db-mcp.py install

# 或手动安装核心依赖
pip install -r references/requirements-core.txt
```

### 配置文件不存在

**症状**: 服务器启动时提示配置文件不存在

**解决方案**:

**方式 1**: 使用 `auto_setup_database()` 工具自动创建配置（推荐）

**方式 2**: 手动创建配置文件
```bash
python scripts/db-mcp.py validate
# 或从示例复制
cp references/db_config.example.json db_config.json
```

### 数据库驱动缺失

**症状**: `ModuleNotFoundError: No module named 'mysql.connector'`

**解决方案**:

**方式 1**: 自动安装（推荐）
```python
# 使用 auto_setup_database() 工具会自动安装
auto_setup_database(db_type="mysql", ...)
```

**方式 2**: 手动安装
```bash
python scripts/db-mcp.py install --db-type mysql
# 或
pip install -r references/requirements-mysql.txt
```

### MCP 服务未启动

1. 先确保 Python 依赖已安装：`python scripts/db-mcp.py install`
2. 检查配置：`python scripts/db-mcp.py check`
3. 重新安装：`python scripts/db-mcp.py setup`
4. 重启 Claude Code

### 连接失败

**方式 1**: 使用诊断工具（推荐）
```python
# 查看当前状态
check_capabilities()

# 测试连接
test_connection(config_name="default", detailed=True)
```

**方式 2**: 命令行验证
```bash
python scripts/db-mcp.py validate
```

### 找到 MCP 工具

MCP 工具由 MCP 服务器提供，不是本技能的直接工具。使用前确保：
1. MCP 服务已安装并运行
2. Claude Code 已重启
3. 在对话中直接调用工具，如 `execute_query(...)`

## 参考文档

按需加载的详细文档：

| 任务 / 场景 | 读取文档 | 关键内容 |
|------------|---------|---------|
| 了解工具详情 | `references/mcp-tools.md` | 所有 MCP 工具的详细说明 |
| 配置数据库 | `references/config-format.md` | 配置文件格式说明 |
| 首次安装 | `references/requirements*.txt` | 依赖包列表 |

## 目录结构

```
db-mcp/
├── SKILL.md              # 入口文件
├── db_config.json        # 数据库配置（运行时）
├── pyproject.toml        # 项目配置
│
├── scripts/              # 可执行脚本
│   ├── db-mcp.py        # 统一命令行工具
│   ├── server.py        # MCP 服务器
│   └── *.py             # 其他模块
│
├── references/           # 参考文档
│   ├── mcp-tools.md     # 工具详细说明
│   ├── config-format.md # 配置格式说明
│   └── requirements*.txt # 依赖列表
│
└── docs/                 # 开发文档
    ├── README.md        # 项目说明
    └── IMPLEMENTATION_SUMMARY.md
```

## 使用 scripts/db-mcp.py 命令行工具

**从任何位置运行**（无需 cd 到项目目录）：

```bash
# 显示帮助
python scripts/db-mcp.py

# 安装依赖（智能检测）
python scripts/db-mcp.py install

# 指定数据库类型安装
python scripts/db-mcp.py install --db-type mysql      # 仅 MySQL
python scripts/db-mcp.py install --db-type postgresql # 仅 PostgreSQL
python scripts/db-mcp.py install --db-type all        # 所有驱动

# 列出缺失的依赖（不安装）
python scripts/db-mcp.py install --list-needs

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
