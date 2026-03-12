---
description: "连接数据库（零配置）"
argument-hint: "<类型> <主机> <数据库> [用户]"
allowed-tools: [Bash, Read, Write]
---

# 连接数据库

零配置连接数据库，支持 MySQL、PostgreSQL、SQLite。

## 工作流

1. **解析参数** - 解析连接参数（类型、主机、数据库、用户）
2. **安装驱动** - 自动检测并安装所需的数据库驱动
3. **创建配置** - 创建 `db_config.json` 配置文件
4. **测试连接** - 测试数据库连接
5. **列出表** - 显示数据库中的表列表

## 支持的数据库类型

| 类型 | 驱动 | 端口 |
|------|------|------|
| mysql | mysql-connector-python | 3306 |
| postgresql | psycopg2-binary | 5432 |
| sqlite | 内置 | - |

## 使用示例

```
/db-mcp:connect mysql localhost mydb root
/db-mcp:connect postgresql localhost analytics admin
/db-mcp:connect sqlite /path/to/database.db
```

## 参考资源

如需详细配置，按需读取：
- `~/.claude/skills/db-mcp/references/config-format.md` - 配置格式说明
- `~/.claude/skills/db-mcp/references/mcp-tools.md` - MCP 工具详情
