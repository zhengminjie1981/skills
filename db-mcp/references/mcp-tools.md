# MCP 工具参考

本文档详细说明 db-mcp 提供的所有 MCP 工具。

## 工具列表

### 1. list_tables

**功能**: 列出数据库中的所有表

**参数**:
- `config_name` (可选): 数据库配置名称，默认 'default'

**返回**: 表名列表 `List[str]`

**示例**:
```python
# 列出默认数据库的所有表
tables = list_tables()

# 列出特定配置的表
tables = list_tables(config_name="analytics")
```

**使用场景**:
- 探索数据库结构
- 查找可用的表

---

### 2. describe_table

**功能**: 获取表的详细结构信息

**参数**:
- `table_name` (必需): 表名
- `config_name` (可选): 数据库配置名称，默认 'default'

**返回**: 表结构信息 `Dict[str, Any]`
```json
{
  "table_name": "users",
  "columns": [
    {
      "field": "id",
      "type": "int",
      "null": "NO",
      "key": "PRI",
      "default": null,
      "extra": "auto_increment"
    },
    ...
  ]
}
```

**示例**:
```python
# 查看 users 表结构
structure = describe_table("users")

# 查看字段信息
for col in structure["columns"]:
    print(f"{col['field']}: {col['type']}")
```

**使用场景**:
- 了解表结构
- 查找字段名和类型
- 识别主键和索引

---

### 3. execute_query

**功能**: 执行只读 SQL 查询

**参数**:
- `query` (必需): SQL 查询语句（必须是 SELECT）
- `config_name` (可选): 数据库配置名称，默认 'default'
- `limit` (可选): 最大返回行数，默认 1000

**返回**: 查询结果列表 `List[Dict[str, Any]]`

**安全限制**:
- 仅允许 SELECT 查询
- 禁止 DROP、DELETE、UPDATE、INSERT、ALTER 等操作
- 自动注入 LIMIT（如果查询中没有）
- 防止 SQL 注入

**示例**:
```python
# 简单查询
results = execute_query("SELECT * FROM users LIMIT 10")

# 带条件的查询
results = execute_query(
    "SELECT * FROM orders WHERE status = 'completed'"
)

# 自定义限制
results = execute_query(
    "SELECT * FROM products",
    limit=100
)

# 聚合查询
results = execute_query("""
    SELECT
        category,
        COUNT(*) as count,
        AVG(price) as avg_price
    FROM products
    GROUP BY category
""")
```

**使用场景**:
- 查询数据
- 数据分析
- 生成报表

---

### 4. get_table_count

**功能**: 获取表的行数统计信息

**参数**:
- `table_name` (必需): 表名
- `config_name` (可选): 数据库配置名称，默认 'default'

**返回**: 统计信息 `Dict[str, Any]`
```json
{
  "table_name": "users",
  "row_count": 12345
}
```

**示例**:
```python
# 获取表行数
count = get_table_count("users")
print(f"Total users: {count['row_count']}")
```

**使用场景**:
- 快速了解表大小
- 数据量统计

---

### 5. get_database_info

**功能**: 获取数据库的基本信息

**参数**:
- `config_name` (可选): 数据库配置名称，默认 'default'

**返回**: 数据库信息 `Dict[str, Any]`
```json
{
  "config_name": "default",
  "database_type": "MySQL",
  "database": "mydb",
  "version": "8.0.32"
}
```

**示例**:
```python
# 获取数据库信息
info = get_database_info()
print(f"Database: {info['database']}")
print(f"Version: {info['version']}")
```

**使用场景**:
- 确认数据库连接
- 查看数据库版本
- 识别数据库类型

---

### 6. search_tables

**功能**: 搜索包含特定关键字的表

**参数**:
- `keyword` (必需): 搜索关键字
- `config_name` (可选): 数据库配置名称，默认 'default'

**返回**: 匹配的表及其行数 `List[Dict[str, Any]]`
```json
[
  {
    "table_name": "user_profiles",
    "row_count": 5000
  },
  {
    "table_name": "user_settings",
    "row_count": 300
  }
]
```

**示例**:
```python
# 搜索包含 "user" 的表
results = search_tables("user")

for result in results:
    print(f"{result['table_name']}: {result['row_count']} rows")
```

**使用场景**:
- 根据关键字查找表
- 快速定位相关表

---

## 工作流程示例

### 场景 1: 数据探索

```python
# 1. 查看所有表
tables = list_tables()
print(f"Found {len(tables)} tables")

# 2. 获取数据库信息
info = get_database_info()
print(f"Connected to: {info['database']}")

# 3. 查找特定表
results = search_tables("order")
for result in results:
    print(f"Table: {result['table_name']}, Rows: {result['row_count']}")

# 4. 查看表结构
structure = describe_table("orders")

# 5. 查询数据
data = execute_query("SELECT * FROM orders LIMIT 10")
```

### 场景 2: 数据分析

```python
# 1. 了解数据量
count = get_table_count("sales")
print(f"Total sales records: {count['row_count']}")

# 2. 按类别统计
results = execute_query("""
    SELECT
        category,
        COUNT(*) as count,
        SUM(amount) as total
    FROM sales
    GROUP BY category
    ORDER BY total DESC
""")

# 3. 时间序列分析
results = execute_query("""
    SELECT
        DATE(created_at) as date,
        COUNT(*) as daily_count,
        SUM(amount) as daily_total
    FROM sales
    WHERE created_at >= '2024-01-01'
    GROUP BY DATE(created_at)
    ORDER BY date
""")
```

### 场景 3: 多数据库操作

```python
# 从不同数据库查询数据
mysql_data = execute_query(
    "SELECT * FROM customers",
    config_name="mysql_db"
)

pg_data = execute_query(
    "SELECT * FROM analytics",
    config_name="analytics_db"
)

sqlite_data = execute_query(
    "SELECT * FROM local_cache",
    config_name="local_db"
)
```

---

## 注意事项

1. **只读限制**: 所有工具都是只读的，不会修改数据
2. **自动 LIMIT**: execute_query 默认限制 1000 行，可自定义
3. **多配置支持**: 所有工具都支持 config_name 参数
4. **错误处理**: 查询失败会抛出异常，需要适当处理
5. **数据类型**: datetime 和 binary 数据会被自动转换

---

## MCP 资源

除了工具，还提供以下资源：

- `schema://tables` - 所有表的架构（Markdown）
- `schema://table/{表名}` - 特定表的详细架构
- `stats://database` - 数据库统计信息（JSON）
- `info://database` - 数据库基本信息（文本）
