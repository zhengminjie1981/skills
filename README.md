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
- 支持 MySQL、PostgreSQL 和 SQLite
- 安全的只读查询，带 SQL 注入防护

**主要工具：**
- `check_capabilities()` - 检查已安装驱动、配置状态，获取建议
- `auto_setup_database()` - 零配置设置：自动安装驱动、创建配置、测试连接
- `test_connection()` - 测试数据库连接，返回延迟和服务器信息
- `list_tables` - 列出数据库中所有表
- `describe_table` - 查看表结构和 schema
- `execute_query` - 执行 SELECT 查询

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

### [obsidian-slides](./obsidian-slides/) - Obsidian Slides 配置生成

帮助用户生成 Obsidian Slides Extended（reveal.js）演示文稿的布局代码、主题配置和动画语法。

**核心能力（AI 可靠执行）：**
- **幻灯片生成**：新建幻灯片 / 内容转换
- **布局生成**：grid/split 布局代码
- **主题配置**：frontmatter 主题设置（含 transition）
- **动画语法**：fragment 类名

**触发场景：**
- 幻灯片生成：创建幻灯片、新建 slides、转成幻灯片、Markdown 转 slides
- 布局生成：幻灯片布局、grid 布局、分栏布局
- 主题配置：幻灯片主题、换主题、深色主题
- 动画效果：逐条显示、fragment、动画

**快速开始：**
```
用户: 帮我创建一个产品介绍幻灯片
AI: [加载 obsidian-slides skill] 好的，我来帮你创建...
    - 询问目标受众和演示时长
    - 选择模板和主题风格
    - 生成完整 Markdown 文件

用户: 帮我做一个左右分栏布局
AI: 询问比例后，生成 split 布局代码...

用户: 配置一个深色主题
AI: 列出深色主题选项（black/night/moon），用户选择后生成 frontmatter...
```

**模板列表：**

| 模板 | 用途 | 深浅适配 |
|------|------|---------|
| `product-pitch.md` | 产品介绍 | ✅ dark/light |
| `meeting-report.md` | 会议汇报 | ✅ dark/light |
| `tutorial.md` | 教程演示 | ✅ dark/light |
| `technical.md` | 技术分享 | 内置主题 |
| `announcement.md` | 公告通知 | 内置主题 |

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

### 安装 Skills

将需要的 skill 目录复制到 Claude Code 的 skills 目录：

```bash
# 安装单个 skill
cp -r <skill-name> ~/.claude/skills/                     # Linux/Mac
xcopy <skill-name> %USERPROFILE%\.claude\skills\ /E /I  # Windows

# 安装全部 skills
cp -r */ ~/.claude/skills/                               # Linux/Mac（在项目根目录执行）
```

### 安装斜杠指令（可选）

项目已包含斜杠指令文件（`.claude/commands/`），有两种使用方式：

| 方式 | 说明 |
|------|------|
| **项目内使用** | 无需安装，clone 项目后在项目目录内即可使用 |
| **全局使用** | 复制到全局目录，可在任意项目使用 |

```bash
# 全局安装（可选）
cp -r .claude/commands/* ~/.claude/commands/              # Linux/Mac
xcopy .claude\commands\ %USERPROFILE%\.claude\commands\ /E /I  # Windows
```

**注意**：斜杠指令为可选功能，不影响 skill 的正常触发和使用。

## 使用方法

每个 skill 都有自己的 `SKILL.md` 文件，包含详细说明：

- `dev-workflow/SKILL.md` - 文档驱动开发工作流规范
- `db-mcp/SKILL.md` - 数据库管理使用指南
- `doc2md/SKILL.md` - 文档转换工作流
- `knowledge-index/SKILL.md` - 知识库索引指南
- `template-filler/SKILL.md` - 对话式模板文档填写
- `obsidian-slides/SKILL.md` - Obsidian Slides 配置生成

## 斜杠指令列表

部分 skill 提供了斜杠指令，支持显式调用和预授权工具：

| Skill | 指令 | 说明 |
|-------|------|------|
| dev-workflow | `/dev-workflow:new` | 启动新模块开发 |
| | `/dev-workflow:change` | 修改现有模块 |
| | `/dev-workflow:check` | 验证文档一致性 |
| db-mcp | `/db-mcp:connect` | 连接数据库 |
| | `/db-mcp:query` | 执行只读查询 |
| doc2md | `/doc2md:convert` | 转换文档为 Markdown |
| | `/doc2md:batch` | 批量转换文档 |
| knowledge-index | `/knowledge-index:build` | 构建知识索引 |
| | `/knowledge-index:update` | 增量更新索引 |
| | `/knowledge-index:search` | 搜索知识库 |
| | `/knowledge-index:list` | 列出所有知识库 |
| template-filler | `/template-filler` | 对话式填写模板 |
| obsidian-slides | `/obsidian-slides:new` | 创建演示文稿 |
| | `/obsidian-slides:layout` | 生成幻灯片布局 |
| | `/obsidian-slides:theme` | 配置主题样式 |

**设计原则**：单功能 skill 直接用名称，多功能 skill 使用子指令。详见 [斜杠指令设计规范](./standards/skill-guide.md#斜杠指令设计规范)。

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
