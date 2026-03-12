# Skills 编写指南

> 本规范基于官方 skill-creator，补充本项目特定约定。

## 官方规范参考

核心原则和通用流程请参考官方 skill-creator：

| 内容 | 说明 |
|------|------|
| **核心原则** | 简洁优先、设置适当的自由度 |
| **Skill 结构** | SKILL.md + scripts/references/assets |
| **渐进式加载** | 三层加载系统（metadata → body → resources） |
| **创建流程** | 理解 → 规划 → 初始化 → 编写 → 测试 → 迭代 |

**官方位置**：`~/.claude/skills/skill-creator/SKILL.md`

## 项目约定

### 目录结构规范

```
skill-name/
├── SKILL.md              # 入口文件（必需，AI 触发时加载）
│
├── references/           # AI 参考文档（按需加载）
│   ├── *.md              # 详细规范、使用指南
│   └── */                # 可按主题分目录
│
├── scripts/              # 可执行脚本（不会被 AI 加载）
│   └── *.py / *.sh       # 实际执行代码
│
├── docs/                 # 开发文档（不会被 AI 加载）
│   ├── design.md         # 设计文档
│   ├── changelog.md      # 变更日志
│   └── _archive/         # 归档文档
│
├── examples/             # 示例文件（不会被 AI 加载）
│   └── sample-files/     # 示例输入/输出
│
├── tests/                # 测试文件（不会被 AI 加载）
│   └── *.py / test-*/
│
├── data/                 # 运行时数据（不会被 AI 加载）
│   └── *.yaml / *.json   # 配置、缓存、注册表
│
└── assets/               # 输出资源（不会被 AI 加载）
    └── templates/        # 模板文件
```

### 目录用途说明

| 目录 | AI 加载 | 用途 | 内容示例 |
|------|---------|------|---------|
| `SKILL.md` | ✅ 触发时 | 入口文件 | 快速开始、决策树、索引 |
| `references/` | ✅ 按需 | AI 参考文档 | 规范、指南、配置说明 |
| `scripts/` | ❌ | 可执行代码 | Python/Bash 脚本 |
| `docs/` | ❌ | 开发文档 | 设计、变更日志、归档 |
| `examples/` | ❌ | 示例文件 | 示例输入/输出文件 |
| `tests/` | ❌ | 测试文件 | 测试用例、测试数据 |
| `data/` | ❌ | 运行时数据 | 配置、缓存、注册表 |
| `assets/` | ❌ | 输出资源 | 模板、静态资源 |

### 文档内容规范

**核心原则**：在保持简洁（按需加载）的前提下，充分兼顾 AI 友好性。

**Markdown 文件中仅允许示例代码**：

```markdown
<!-- ✅ 正确：示例代码（仅展示用法） -->
## 使用示例

\`\`\`bash
python scripts/converter.py document.docx --relative-images
\`\`\`

<!-- ❌ 错误：实际执行代码不应放在 md 中 -->
```

**实际执行代码必须放在 scripts/ 目录**：
- Python 脚本 → `scripts/*.py`
- Shell 脚本 → `scripts/*.sh`
- 配置文件 → `data/` 或 `scripts/`（如需 AI 读取可放 `references/`）

**references/ 特殊规则**：
- 仅存放 `.md` 文档
- 不存放 `.py`、`.sh` 等可执行文件
- 可存放配置模板（如 `requirements.txt`、`config.example.json`）

### AI 友好性设计

**简洁即 AI 友好**：精简的文档减少 token 消耗，清晰的结构降低理解成本。

| 做法 | AI 友好原因 |
|------|------------|
| 表格 > 长段落 | 结构化信息，易于解析 |
| 决策树 | 明确分支，减少判断 |
| 默认值 | 减少选择，快速行动 |
| 任务→文档映射 | 按需加载，精准定位 |
| 标记特殊情况 | 明确边界，避免错误 |

**AI 友好写法示例**：

1. **使用表格**：结构化信息
   ```markdown
   | 场景 | 工具 | 说明 |
   |------|------|------|
   | PDF with tables | mineru | OCR 支持 |
   ```

2. **提供决策树**：明确分支
   ```markdown
   是 PDF？
   ├─ YES → 有表格/OCR？ → mineru / pymupdf
   └─ NO  → pandoc
   ```

3. **明确默认值**：减少选择
   ```markdown
   ### Safe Defaults
   - `--relative-images`（推荐）
   - `--skip-toc`（推荐）
   ```

4. **任务→文档映射**：精准定位
   ```markdown
   | 任务 | 读取文档 |
   |------|---------|
   | 安装问题 | references/installation.md |
   | 转换失败 | references/troubleshooting.md |
   ```

5. **标记特殊情况**：明确边界
   ```markdown
   ### Red Flags
   - 用户提到 "OCR" → 使用 mineru
   - Python 3.14+ → 使用 pymupdf
   ```

### YAML Front Matter 规范

```yaml
---
name: skill-name
description: |
  简短描述（~50 字）。

  **触发场景**（包含以下关键词）：
  - 场景1：关键词A、关键词B
  - 场景2：关键词C、关键词D

  **不触发场景**：
  - 场景X：关键词Y
---
```

**关键点**：
- `description` 必须包含触发场景（这是 AI 判断是否加载的唯一依据）
- 区分"触发"和"不触发"场景，避免误触发
- 关键词要具体，避免泛化

### 按需加载模式

**加载层级**：

| 层级 | 内容 | 加载时机 |
|------|------|---------|
| 1 | Front matter (name + description) | 总是加载 |
| 2 | SKILL.md body | skill 触发时 |
| 3 | references/*.md | AI 按需读取 |
| 4 | scripts/, docs/, data/ | **永远不会被 AI 加载** |

**SKILL.md 只包含核心内容**（< 500 行）：
- 一行总结
- 快速开始（引用 scripts/ 中的命令）
- 核心功能表格
- 决策树（3-5 步）
- 参考资源索引

**详细内容放入 references/**（仅 .md 文件）：
- 核心规范 → `references/core/`
- 执行指南 → `references/execution/`
- 高级主题 → `references/advanced/`

**开发相关内容放入 docs/**（不会被 AI 加载）：
- 设计文档 → `docs/design.md`
- 变更日志 → `docs/changelog.md`
- 归档文档 → `docs/_archive/`

### 斜杠指令设计规范

**是否需要创建斜杠指令？**

| 功能数量 | 是否创建指令 | 说明 |
|---------|-------------|------|
| 1 个 | ❌ 不创建 | 直接用 skill 名称调用 |
| 2+ 个 | ✅ 创建 | 为每个功能创建子指令 |

**命名原则**：

1. **简短**：指令名称 1-2 个单词
2. **动作导向**：使用动词（build、search、convert）
3. **避免重复**：子指令名称不应重复 skill 名称

**示例**：

```
❌ 错误（重复表达）：
/knowledge-index:knowledge-search
/doc2md:doc2md-convert

✅ 正确（简短、无重复）：
/knowledge-index:search
/doc2md:convert
```

**单功能 skill 示例**：

```
template-filler 只有一个功能 → 不创建子指令
调用方式：/template-filler（直接用 skill 名称）
```

**多功能 skill 示例**：

```
knowledge-index 有 4 个功能 → 创建子指令
├── /knowledge-index:build
├── /knowledge-index:update
├── /knowledge-index:search
└── /knowledge-index:list
```

**目录结构**：

```
# 多功能 skill
.claude/commands/
└── skill-name/
    ├── subcommand1.md
    └── subcommand2.md

# 单功能 skill
.claude/commands/
└── skill-name.md    # 直接用 skill 名称，无子目录
```

## 快速流程

### 1. 设计阶段

**目标**：明确 skill 的职责边界和触发条件

**检查清单**：[design.md](checklists/design.md)

**关键问题**：
- [ ] 这个 skill 解决什么问题？
- [ ] 用户会说什么话来触发它？
- [ ] 什么场景**不应该**触发它？
- [ ] 需要哪些脚本/文档/资源？

### 2. 实现阶段

**目标**：创建符合模板的 skill 文件

**模板**：[SKILL.md.template](templates/SKILL.md.template)

**检查清单**：[implementation.md](checklists/implementation.md)

**关键步骤**：
1. 复制模板，填写 front matter
2. 编写快速开始（最重要！）
3. 组织 references/ 目录
4. 编写必要的脚本

### 3. 测试阶段

**目标**：验证 skill 能正确触发和执行

**检查清单**：[release.md](checklists/release.md)

**测试用例**：
1. 触发测试：说出触发关键词，验证 skill 被加载
2. 不触发测试：说出不触发关键词，验证 skill 不被加载
3. 功能测试：执行快速开始中的命令，验证结果正确

## 已有 Skill 符合性检查

### 检查流程

```
1. 目录结构检查 → 是否符合规范
2. 代码位置检查 → 是否有代码在 md 中
3. Front Matter 检查 → 触发场景是否完整
4. 按需加载检查 → SKILL.md 是否过长
5. AI 友好性检查 → 是否有表格/决策树/默认值
```

**检查清单**：[compliance.md](checklists/compliance.md)

### 常见问题与优化方案

| 问题 | 影响 | 优化方案 |
|------|------|---------|
| `references/` 中有 `.py` 文件 | 可能被误加载 | 移动到 `scripts/` |
| `SKILL.md` > 500 行 | 加载过重 | 拆分到 `references/` |
| 缺少触发场景描述 | 无法正确触发 | 补充 front matter |
| 缺少不触发场景 | 误触发 | 补充边界说明 |
| 缺少决策树/表格 | AI 判断困难 | 添加结构化指引 |
| 开发文档在 `references/` | 占用 token | 移动到 `docs/` |

### 优化优先级

1. **必须修复**（影响功能）：
   - Front matter 缺少触发场景
   - 可执行代码在 md 中

2. **建议修复**（影响性能）：
   - SKILL.md 过长
   - 开发文档在 references/

3. **可选优化**（提升体验）：
   - 添加决策树
   - 添加默认值说明
   - 添加任务→文档映射

## 参考资源

### 模板和检查清单

| 文件 | 用途 |
|------|------|
| [SKILL.md 模板](templates/SKILL.md.template) | 可直接复制使用 |
| [设计检查清单](checklists/design.md) | 设计阶段验证 |
| [实现检查清单](checklists/implementation.md) | 实现阶段验证 |
| [发布检查清单](checklists/release.md) | 发布前验证 |
| [符合性检查清单](checklists/compliance.md) | 已有 skill 检查和优化 |

## 常见问题

### Q: SKILL.md 应该多长？

**建议**：< 500 行。超过则应拆分到 references/。

### Q: 如何设计触发场景？

**原则**：
1. 具体：避免泛化关键词（如"帮我"）
2. 可区分：与其他 skill 的触发场景不重叠
3. 可测试：能写出明确的测试用例

### Q: 代码应该放在哪里？

| 代码类型 | 存放位置 | AI 是否加载 |
|---------|---------|------------|
| 实际执行代码 | `scripts/*.py` | ❌ |
| 示例代码（展示用法） | `*.md` 中的代码块 | ✅（作为文档） |
| 配置模板 | `references/*.txt` 或 `references/*.example.json` | ✅（按需） |
| 运行时配置 | `data/*.yaml` 或 `data/*.json` | ❌ |

### Q: references/ 如何组织？

**推荐结构**：
```
references/
├── core/           # 核心规范（索引、工作流、质量门禁）
├── execution/      # 执行支持（工具、检查清单、故障排除）
└── advanced/       # 高级主题（可选）
```

**注意**：references/ 仅存放 `.md` 文档和配置模板，不存放可执行代码。

### Q: docs/ 和 references/ 有什么区别？

| 目录 | 用途 | AI 是否加载 |
|------|------|------------|
| `references/` | AI 执行任务时需要参考的文档 | ✅ 按需 |
| `docs/` | 开发过程的记录（设计、变更日志） | ❌ |

---

*版本: 1.4 | 最后更新: 2026-03-12*
