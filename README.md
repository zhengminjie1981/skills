# Skills - AI Skills 集合

为 Claude Code 设计的 AI skills 集合，旨在提升效率并自动化常见任务。

## 可用 Skills

### [dev-workflow](./dev-workflow/) - 文档驱动开发工作流

强制执行文档驱动开发的综合工作流规范：没有文档不写代码，没有文档更新不改代码。

**核心原则：**
- **文档优先**：任何模块或功能实现前，必须先完成技术文档
- **变更追踪**：任何迭代修改前，必须更新相关文档并完成影响分析
- **模块边界**：模块间通过数据结构规范和接口规范交互
- **一致性维护**：文档更新后，同步检查所有引用
- **集中进展**：所有工作计划和进展记录在统一的项目规划文档中

**主要特性：**
- 5 层文档层级（系统 → 规范 → 模块 → 验证 → 报告）
- 编码前和提交前的质量门禁
- 自动化一致性检查工具
- 完整的新模块开发和迭代变更模板与检查清单

**触发场景：**
- 创建新模块或功能
- 修改现有代码、数据结构或接口
- 迭代变更或重构
- 文档一致性检查
- 模块设计、数据结构规范、接口规范

**快速开始：**
```
用户: 帮我开发一个用户认证模块
AI: [加载 dev-workflow skill] 好的，根据文档驱动开发规范，我们需要先...

用户: 帮我重构这个模块
AI: [加载 dev-workflow skill] 在修改代码前，请先确认相关文档...
```

---

### [db-mcp](./db-mcp/) - 数据库 MCP 服务管理

支持零配置启动和自动依赖管理的数据库 MCP 服务。

**特性：**
- **零配置启动** - 无需配置文件即可启动，通过 AI 工具自动设置
- **自动安装依赖** - 自动检测并安装缺失的数据库驱动
- **智能诊断** - 系统能力检测和连接测试
- 支持 MySQL、PostgreSQL 和 SQLite（MySQL 兼容 AnalyticDB 等云数据库变体）
- 安全的只读查询，带 SQL 注入防护

**主要工具：**
- `check_capabilities()` - 检查已安装驱动、配置状态，获取建议
- `auto_setup_database()` - 零配置设置：自动安装驱动、创建配置、测试连接
- `test_connection()` - 测试数据库连接，返回延迟和服务器信息
- `list_tables` - 列出数据库中所有表
- `describe_table` - 查看表结构和 schema
- `execute_query` - 执行 SELECT 查询

**命令行工具区分：**
- `python scripts/db-mcp.py check` — 检查 MCP 服务是否注册（≠ 数据库连接状态）
- `python scripts/db-mcp.py validate` — 验证数据库连接配置

**快速开始：**
```
# 首次使用需安装 MCP 服务（仅需一次）
cd db-mcp && python scripts/db-mcp.py setup
# 然后重启 Claude Code

# 安装后，通过对话使用：
用户: 帮我连接到 MySQL 数据库，主机是 localhost
AI: [调用 check_capabilities 检查状态]
    [调用 auto_setup_database 自动安装驱动并配置]
    连接成功！数据库版本：8.0

用户: 查看有哪些表
AI: [调用 list_tables] 找到 5 个表：users, orders, products...
```

---

### [doc2md](./doc2md/) - 文档转 Markdown

使用 Pandoc 和 MinerU 将 40+ 种文档格式转换为 Markdown。

**特性：**
- **Pandoc**：通用转换器，支持 DOCX、EPUB、HTML、PPTX、LaTeX 等
- **MinerU**：高级 PDF 解析器，支持 OCR、表格提取、版面识别
- **PyMuPDF**：快速轻量的 PDF 转换器
- 支持 glob 模式批量处理
- 灵活的图片处理（相对路径或 Base64 嵌入）

**支持格式：**
- 文档：DOCX、DOC、ODT、RTF、PDF
- 电子书：EPUB、FB2
- 演示文稿：PPTX
- 网页：HTML、XHTML、XML
- 学术：LaTeX、TeX
- 以及 30+ 种其他格式

**快速开始：**
```
用户: 帮我把这个 Word 文档转成 Markdown
AI: [加载 doc2md skill] 好的，我来转换...
    python scripts/converter.py document.docx --relative-images --skip-toc

用户: 这个 PDF 有表格，能保留吗？
AI: 可以，使用 MinerU 工具处理表格...
    python scripts/converter.py document.pdf --tool mineru --relative-images
```

---

### [template-filler](./template-filler/) - 对话式模板文档填写

通过对话访谈方式引导用户按 Markdown 模板逐步填写内容，最终自动生成并保存完整文档文件。

**特性：**
- **分段访谈**：逐章节（H2/H3）提问，每节不超过 3 个问题
- **分段预览**：每章节完成后展示草稿，确认后继续
- **灵活控制**：支持跳过章节、返回修改、一次性提供全部信息
- **自动保存**：全部章节确认后，写入指定路径（默认去掉 `.template` 后缀）

**触发场景：**
- 填写模板、按模板写、根据模板生成文档
- 引导我填写、对话式写文档、访谈式写文档

**快速开始：**
```
用户: 帮我按这个模板写文档 /path/to/template.md
AI: 已读取模板，共 N 个章节。我们从「章节名」开始...
```

---

### [md2slides](./md2slides/) - Markdown 转演示文稿

将原始材料或 Markdown 文件转换为 HTML 格式的演示文稿，支持 AI 版式规划（27 种布局模板）、图片嵌入、数据图表和 PDF 导出。

**核心能力：**
- **内容策划**：AI 分析材料，自动规划页面结构和内容分配，生成 MD 提纲
- **版式规划**：AI 逐页分析内容，从 27 种布局模板中选择最佳版式，写入 tree JSON
- **图片支持**：标准 Markdown 语法引用图片，路径自动修正，支持多种布局集成方式
- **数据图表**：自动识别数据并生成柱状图、折线图、饼图等（Chart.js）
- **5 套主题**：professional-dark/light、creative-gradient、minimal-clean、warm-earth
- **精细调整**：通过对话调整任意页面版式、样式；内容变更后保留已有版式
- **PDF 导出**：每张幻灯片对应一页 PDF，支持离线资源内联

**主题速查：**

| 主题 | 适用场景 |
|------|---------|
| `professional-dark` | 商务汇报、客户演示 |
| `professional-light` | 正式文档、打印版 |
| `keynote-white` | 产品发布、All-hands、对外演讲 |
| `tech-terminal` | 工程师分享、架构评审 |
| `celebration` | 年会、颁奖、节日庆典 |
| `caring-green` | 员工关怀、团建、企业文化 |
| `creative-gradient` | AI 展示、创意提案 |
| `minimal-clean` | 极简风、设计评审 |
| `warm-earth` | 企业历史、文化宣讲 |

**触发场景：**
- 生成演示文稿：做成演示文稿、做成幻灯片、做成 PPT、转成 HTML、生成 slides
- 版式规划：设计版式、帮我排版、版式规划、选布局、换版式、换布局
- 数据图表：数据可视化、柱状图、折线图、饼图
- PDF 导出：转成 PDF、导出 PDF

**快速开始：**
```bash
# 阶段一：AI 策划 MD 内容（直接对话）

# 阶段二：AI 版式规划，写入 slide-tree.json（直接对话）

# 阶段三：MD + tree -> HTML（--serve 生成后直接用浏览器打开）
python scripts/convert.py --input demo.md --output demo.html --tree slide-tree.json --serve

# 推荐：内联资源，离线可用（中国网络友好）
python scripts/convert.py --input demo.md --output demo.html --tree slide-tree.json --inline-assets

# 批量截图预览所有页面
python scripts/preview.py --input demo.html

# HTML -> PDF
python scripts/html2pdf.py --input demo.html --output demo.pdf
```

---

### [knowledge-index](./knowledge-index/) - 本地知识库智能索引

为本地文档集合构建 AI 可读的索引，支持自动摘要、增量更新和智能检索。

**核心特性：**
- **本地优先**：使用本地工具提取文本，避免上传文档到云端
- **AI 摘要**：为每个文档生成简洁摘要（50-500 字）和关键词（5-10 个）
- **增量更新**：检测文件变更，仅更新修改过的文档
- **智能检索**：关键词匹配 + Wikilink 扩展，Markdown 软加权
- **Obsidian CLI**：支持 Obsidian 原生搜索（需桌面应用运行中）
- **层级管理**：自动处理父子索引冲突，维护单一顶级索引
- **全局注册表**：从 `~/.knowledge-index/registry.yaml` 管理所有知识库

**触发场景：**
- "给 [知识库] 建立索引"
- "更新 [知识库] 索引"
- "在知识库中搜索..."
- "查看所有知识库"

**快速开始：**
```
用户: 帮我给这个知识库建立索引 /path/to/knowledge-base
AI: [加载 knowledge-index skill]
    - 扫描文档并生成摘要
    - 创建文件夹分区和语义分类索引
    - 写入 _index.yaml 并注册到全局目录

用户: 在知识库中搜索"机器学习"
AI: 检索索引，找到 5 个相关文档，按相关度排序返回
    （若 Obsidian CLI 可用，自动使用原生搜索）
```

**索引版本**: v2.1

---

## 安装

将需要的 skill 目录复制到 Claude Code 的 skills 目录：

```bash
# 安装单个 skill
cp -r <skill-name> ~/.claude/skills/                     # Linux/Mac
xcopy <skill-name> %USERPROFILE%\.claude\skills\ /E /I  # Windows

# 安装全部 skills
cp -r */ ~/.claude/skills/                               # Linux/Mac（在项目根目录执行）
```

## 使用方法

每个 skill 都有自己的 `SKILL.md` 文件，包含详细说明：

- `dev-workflow/SKILL.md` - 文档驱动开发工作流规范
- `db-mcp/SKILL.md` - 数据库管理使用指南
- `doc2md/SKILL.md` - 文档转换工作流
- `knowledge-index/SKILL.md` - 知识库索引指南
- `template-filler/SKILL.md` - 对话式模板文档填写
- `md2slides/SKILL.md` - Markdown 转演示文稿

## 技能调用格式

每个 skill 都支持两种触发方式：

1. **自动触发**：通过描述中的触发场景关键词，AI 自动识别并加载相应技能
2. **显式调用**：使用 `/skill-name [参数]` 格式直接调用

**推荐调用格式**（使用空格分隔参数）：

| Skill | 调用示例 | 说明 |
|-------|---------|------|
| dev-workflow | `/dev-workflow new <模块名>` | 启动新模块开发 |
| | `/dev-workflow change <模块名>` | 修改现有模块 |
| | `/dev-workflow check [模块名]` | 验证文档一致性 |
| db-mcp | `/db-mcp connect <类型> <主机> <库> [用户]` | 连接数据库 |
| | `/db-mcp query <SQL>` | 执行只读查询 |
| doc2md | `/doc2md convert <文件> [--tool ...]` | 转换文档为 Markdown |
| | `/doc2md batch <模式> [-o 目录]` | 批量转换文档 |
| knowledge-index | `/knowledge-index build <路径>` | 构建知识索引 |
| | `/knowledge-index update <路径>` | 增量更新索引 |
| | `/knowledge-index search <查询>` | 搜索知识库 |
| | `/knowledge-index list` | 列出所有知识库 |
| template-filler | `/template-filler <模板路径>` | 对话式填写模板 |
| md2slides | `/md2slides convert <文件>` | MD 转 HTML 演示文稿 |
| | `/md2slides pdf <文件>` | HTML 导出 PDF |

**注意**：以上格式使用空格分隔参数，符合 Claude Code 最新规范。AI 会根据上下文理解参数含义。

## 贡献

欢迎贡献！可以提交 issue 或 pull request：
- Bug 修复
- 新功能
- 文档改进
- 新增 skills

### 创建新 Skill

创建或修改 skill 时，请遵循 [Skills 编写指南](./standards/skill-guide.md)。

**关键资源：**
- [SKILL.md 模板](./standards/templates/SKILL.md.template) - 复制并自定义
- [设计检查清单](./standards/checklists/design.md) - 实现前验证
- [实现检查清单](./standards/checklists/implementation.md) - 开发时验证
- [发布检查清单](./standards/checklists/release.md) - 发布前测试
- [符合性检查清单](./standards/checklists/compliance.md) - 检查现有 skills
- [设计模式](./standards/examples/patterns.md) - 通用设计模式

**快速开始：**
1. 阅读 [standards/skill-guide.md](./standards/skill-guide.md) 了解规范
2. 复制 [模板](./standards/templates/SKILL.md.template)
3. 按检查清单完成：设计 → 实现 → 发布
4. 参考 [patterns.md](./standards/examples/patterns.md) 了解最佳实践

### 检查现有 Skills

使用 [符合性检查清单](./standards/checklists/compliance.md) 验证现有 skills 是否符合规范：

1. **目录结构** - 文件在正确位置
2. **代码位置** - 可执行代码不在 markdown 中
3. **Front Matter** - 触发场景已定义
4. **按需加载** - SKILL.md 不超过 500 行
5. **AI 友好** - 有决策树、表格、默认值

## 许可证

本仓库采用 MIT 许可证。各 skill 目录中的特定许可证信息请参阅对应文件。
