# Knowledge Index - 开发文档

## 目录结构

```
knowledge-index/
├── SKILL.md              # 入口文件（AI 友好，按需加载）
├── docs/                 # 开发文档
│   └── README.md
├── references/           # AI 参考文档（按需加载）
│   ├── core/             # 核心规范
│   ├── execution/        # 执行支持
│   ├── decision/         # 决策支持
│   └── advanced/         # 高级主题
├── scripts/              # 工具脚本
│   ├── knowledge-index-manager.py  # 主脚本
│   ├── extract_text.py             # 本地文本提取
│   └── check_dependencies.py       # 依赖检查
└── tests/                # 测试用例
```

## 详细规范位置

| 规范 | 位置 |
|------|------|
| 索引文件规范 | `references/core/index-spec.md` |
| 工作流程规范 | `references/core/workflow-spec.md` |
| 全局注册表规范 | `references/advanced/global-registry-spec.md` |
| 层级管理规范 | `references/advanced/hierarchy-management.md` |

## 测试

```bash
# 运行单元测试
python tests/test_unit.py

# 检查依赖
python scripts/check_dependencies.py
```
