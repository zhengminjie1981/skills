---
description: "执行只读 SQL 查询"
argument-hint: "<SQL>"
allowed-tools: [Bash]
---

# 执行只读 SQL 查询

安全执行 SELECT 查询，返回结果。

## 工作流

1. **验证 SQL** - 确认是 SELECT 语句
2. **执行查询** - 调用 MCP 工具执行查询
3. **显示结果** - 格式化显示查询结果

## 安全特性

- ✅ 仅允许 SELECT 查询
- ✅ 自动 LIMIT（默认 1000 行）
- ✅ 参数化查询防止 SQL 注入
- ❌ 禁止 DROP、DELETE、UPDATE、INSERT

## 使用示例

```
/db-mcp:query SELECT * FROM users LIMIT 10
/db-mcp:query SELECT COUNT(*) FROM orders WHERE status = 'active'
```

## 参考资源

如需详细说明，按需读取：
- `~/.claude/skills/db-mcp/references/mcp-tools.md` - MCP 工具详情
