# 结构化模板说明

> 本目录提供 JSON Schema 格式的文档模板定义，供 AI 或工具使用

---

## 使用场景

这些 JSON Schema 文件用于：

1. **AI 文档生成**：AI 可以根据 Schema 生成结构化的文档内容
2. **文档验证**：验证生成的文档是否符合规范
3. **工具集成**：IDE 或编辑器可以使用 Schema 提供自动补全
4. **API 集成**：如果开发文档管理工具，可以使用这些 Schema

---

## 可用 Schema

### 1. module-design.schema.json
- **用途**：L3 模块级文档
- **示例**：`用户认证模块设计`
- **必填字段**：
  - title（标题）
  - documentPosition（文档定位）
  - modulePosition（模块定位与边界）
  - inputOutput（输入输出数据规范）
  - coreAlgorithm（核心算法）
  - verification（验证方案）
  - versionHistory（版本历史）

### 2. data-structure-spec.schema.json
- **用途**：L2 规范级 - 数据结构规范
- **示例**：`数据结构规范`
- **必填字段**：
  - title（标题）
  - documentPosition（文档定位）
  - coreDataStructures（核心数据结构）
  - versionHistory（版本历史）

### 3. interface-spec.schema.json
- **用途**：L2 规范级 - 接口规范
- **示例**：`接口规范`
- **必填字段**：
  - title（标题）
  - documentPosition（文档定位）
  - moduleInterfaces（模块间接口）
  - versionHistory（版本历史）

---

## AI 使用示例

### 示例 1：使用 Schema 生成模块设计文档

```python
import json
from pathlib import Path

def 生成模块文档(模块名, 功能描述, schema_path):
    """使用 JSON Schema 生成模块设计文档"""

    # 1. 加载 Schema
    with open(schema_path) as f:
        schema = json.load(f)

    # 2. 根据 Schema 必填字段生成文档结构
    文档数据 = {
        "title": f"{模块名}设计",
        "documentPosition": {
            "level": "L3",
            "question": f"{模块名}如何实现",
            "parentDocument": "../01-系统设计/系统架构设计.md",
            "childDocument": "../04-测试验证/测试计划.md"
        },
        "modulePosition": {
            "responsibilities": [功能描述],
            "nonResponsibilities": ["待补充"],
            "fileStructure": {
                f"src/{模块名.lower()}/": "模块目录"
            },
            "systemPosition": "../01-系统设计/系统架构设计.md"
        },
        "inputOutput": {
            "input": {
                "dataStructure": "待引用数据结构规范",
                "constraints": []
            },
            "output": {
                "dataStructure": "待引用数据结构规范",
                "constraints": []
            }
        },
        "coreAlgorithm": {
            "flowchart": "待补充",
            "keyParameters": [],
            "designDecisions": []
        },
        "verification": {
            "unitTests": [],
            "integrationTests": []
        },
        "versionHistory": [
            {
                "version": "v1.0",
                "date": get_current_date(),
                "description": "初始版本"
            }
        ]
    }

    # 3. 验证是否符合 Schema
    from jsonschema import validate
    validate(instance=文档数据, schema=schema)

    # 4. 转换为 Markdown
    markdown = 转换为Markdown(文档数据)

    return markdown

# 使用示例
markdown = 生成模块文档(
    "用户认证",
    "提供用户认证和授权功能",
    "templates/schemas/module-design.schema.json"
)
```

### 示例 2：验证现有文档

```python
from jsonschema import validate, ValidationError

def 验证文档(文档JSON, schema_path):
    """验证文档是否符合 Schema"""

    with open(schema_path) as f:
        schema = json.load(f)

    try:
        validate(instance=文档JSON, schema=schema)
        print("✅ 文档符合 Schema 规范")
        return True
    except ValidationError as e:
        print(f"❌ 文档不符合规范：{e.message}")
        return False
```

---

## 与 Markdown 模板的关系

- **Markdown 模板**（`templates.md`）：供人类阅读和手动填写
- **JSON Schema**（本目录）：供 AI 或工具使用，更结构化

两者是互补的：
- AI 可以使用 Schema 生成结构化数据，然后转换为 Markdown
- 人类可以使用 Markdown 模板手动编写
- 工具可以将 Markdown 解析为 JSON，使用 Schema 验证

---

## 扩展建议

如果需要添加新的文档类型 Schema：

1. **创建 Schema 文件**：`<type>.schema.json`
2. **遵循 JSON Schema 规范**：http://json-schema.org/
3. **定义必填字段**：required 数组
4. **添加描述**：每个字段添加 description
5. **提供示例**：examples 数组
6. **更新本文档**：在"可用 Schema"章节添加说明

---

**文档版本**：v1.0
**最后更新**：2026-03-03
