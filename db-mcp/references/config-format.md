# 配置文件格式说明

本文档详细说明 `db_config.json` 的配置格式。

## 配置文件位置

```
db-mcp/
├── db_config.example.json    # 配置模板
└── db_config.json            # 实际配置文件（需自行创建）
```

## 配置格式

`db_config.json` 是一个 JSON 对象，支持多个命名配置。

### 基本结构

```json
{
  "配置名称1": { ...数据库配置... },
  "配置名称2": { ...数据库配置... },
  "配置名称3": { ...数据库配置... }
}
```

至少需要一个名为 `default` 的配置。

---

## MySQL 配置

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

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `type` | string | 是 | 固定值 `"mysql"` |
| `host` | string | 是 | 数据库主机地址 |
| `port` | number | 是 | 端口号，通常为 3306 |
| `user` | string | 是 | 用户名 |
| `password` | string | 是 | 密码 |
| `database` | string | 是 | 数据库名 |

### 使用环境变量

```json
{
  "default": {
    "type": "mysql",
    "host": "${DB_HOST}",
    "port": 3306,
    "user": "${DB_USER}",
    "password": "${DB_PASSWORD}",
    "database": "${DB_NAME}"
  }
}
```

环境变量会在运行时自动展开。

---

## PostgreSQL 配置

```json
{
  "analytics": {
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "your-password",
    "database": "analytics_db"
  }
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `type` | string | 是 | 固定值 `"postgresql"` |
| `host` | string | 是 | 数据库主机地址 |
| `port` | number | 是 | 端口号，通常为 5432 |
| `user` | string | 是 | 用户名 |
| `password` | string | 是 | 密码 |
| `database` | string | 是 | 数据库名 |

### 使用环境变量

```json
{
  "analytics": {
    "type": "postgresql",
    "host": "${PG_HOST}",
    "port": 5432,
    "user": "${PG_USER}",
    "password": "${PG_PASSWORD}",
    "database": "${PG_DATABASE}"
  }
}
```

---

## SQLite 配置

```json
{
  "local": {
    "type": "sqlite",
    "database": "/path/to/your/database.db"
  }
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `type` | string | 是 | 固定值 `"sqlite"` |
| `database` | string | 是 | 数据库文件路径 |

### 相对路径

SQLite 配置支持相对路径：

```json
{
  "local": {
    "type": "sqlite",
    "database": "./data/mydb.db"
  }
}
```

路径相对于 `db_config.json` 所在目录。

---

## 多配置示例

```json
{
  "default": {
    "type": "mysql",
    "host": "production-db.example.com",
    "port": 3306,
    "user": "app_user",
    "password": "${DB_PASSWORD}",
    "database": "production_db"
  },

  "analytics": {
    "type": "postgresql",
    "host": "analytics-db.example.com",
    "port": 5432,
    "user": "analyst",
    "password": "${ANALYTICS_PASSWORD}",
    "database": "analytics"
  },

  "local": {
    "type": "sqlite",
    "database": "./local_cache.db"
  },

  "staging": {
    "type": "mysql",
    "host": "staging-db.example.com",
    "port": 3306,
    "user": "staging_user",
    "password": "${STAGING_PASSWORD}",
    "database": "staging_db"
  }
}
```

### 使用不同配置

```python
# 使用默认配置
tables = list_tables()  # 使用 "default"

# 使用特定配置
tables = list_tables(config_name="analytics")
data = execute_query("SELECT * FROM events", config_name="analytics")

# 查询本地数据库
cache = execute_query("SELECT * FROM cache", config_name="local")
```

---

## 环境变量设置

### Windows (PowerShell)

```powershell
$env:DB_HOST="localhost"
$env:DB_USER="myuser"
$env:DB_PASSWORD="mypassword"
$env:DB_NAME="mydb"
```

### Windows (CMD)

```cmd
set DB_HOST=localhost
set DB_USER=myuser
set DB_PASSWORD=mypassword
set DB_NAME=mydb
```

### Linux/macOS (Bash)

```bash
export DB_HOST=localhost
export DB_USER=myuser
export DB_PASSWORD=mypassword
export DB_NAME=mydb
```

### 持久化环境变量

**Windows (系统环境变量)**:
1. 右键"此电脑" → 属性
2. 高级系统设置 → 环境变量
3. 添加用户/系统环境变量

**Linux/macOS (~/.bashrc 或 ~/.zshrc)**:
```bash
export DB_HOST=localhost
export DB_USER=myuser
export DB_PASSWORD=mypassword
export DB_NAME=mydb
```

---

## 配置验证

创建配置后，使用验证工具检查：

```bash
# 验证配置格式
python scripts/validate_config.py

# 测试数据库连接
python test_connection.py
```

---

## 常见问题

### 1. 密码包含特殊字符

JSON 字符串中的特殊字符需要转义：

```json
{
  "password": "p@ssw0rd#123"
}
```

或者使用环境变量避免转义问题。

### 2. 连接超时

如果连接远程数据库超时，检查：
- 防火墙设置
- 数据库是否允许远程连接
- 网络连接

### 3. 权限问题

确保数据库用户有以下权限：
- `SELECT` - 读取数据
- `SHOW DATABASES` - 列出数据库（可选）
- `SHOW TABLES` - 列出表（可选）

由于本工具是只读的，不需要 INSERT、UPDATE、DELETE 等权限。

### 4. 字符集问题

如果遇到中文乱码，确保：

**MySQL**:
```json
{
  "type": "mysql",
  "charset": "utf8mb4",
  ...
}
```

**PostgreSQL**:
```json
{
  "type": "postgresql",
  "client_encoding": "UTF8",
  ...
}
```

---

## 安全建议

1. **使用环境变量**: 不要在配置文件中硬编码密码
2. **限制权限**: 使用只读数据库用户
3. **配置文件权限**: 确保 `db_config.json` 只有所有者可读
4. **密码复杂度**: 使用强密码
5. **网络隔离**: 生产数据库使用 VPN 或专线访问

---

## 示例：完整配置

```json
{
  "_comment": "db-mcp 数据库配置文件",

  "default": {
    "type": "mysql",
    "host": "${DB_HOST}",
    "port": 3306,
    "user": "${DB_USER}",
    "password": "${DB_PASSWORD}",
    "database": "${DB_NAME}"
  },

  "analytics": {
    "type": "postgresql",
    "host": "analytics.example.com",
    "port": 5432,
    "user": "analyst",
    "password": "${ANALYTICS_PASSWORD}",
    "database": "analytics_db"
  },

  "local_cache": {
    "type": "sqlite",
    "database": "./cache/local.db"
  }
}
```
