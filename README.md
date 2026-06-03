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

### [viz3d](./viz3d/) - 3D场景生成器

通过自然语言生成3D场景HTML文件，支持规则分布的自动展开和配置驱动渲染。

**核心特性：**
- **配置驱动**：使用 `distribution` 描述规则分布（circle/grid/line/layers）
- **自动展开**：浏览器JS自动计算坐标，无需手动指定每个点
- **组引用连线**：连线可引用整个组（如 `"from": "orbit"` 自动展开）
- **数据验证**：自动检测配置错误并显示警告
- **多种分布**：circle、grid、line、layers 等规则分布模式

**支持的分布：**
- `circle` - 圆形分布（count, radius, center, offset）
- `grid` - 网格分布（rows, cols, spacing, center）
- `line` - 线性分布（count, spacing, axis, center）
- `layers` - 多层圆环（layers: [{radius, count, height}]）

**触发场景：**
- "创建3D场景"、"三维可视化"、"画点位"、"空间布局"
- "生成场景"、"可视化场景"

**快速开始：**
```
用户: 创建48个点围成圆，半径25米
AI: ✓ 已生成 scene.json 和 preview.html
    修改配置后刷新浏览器或重新生成HTML

用户: 把半径改成30米
AI: ✓ 已修改 radius: 30
    刷新浏览器查看
```

---

### [task-stack](./task-stack/) - 跨会话任务堆栈管理

用栈式模型管理主线任务、临时插入任务和后续待办，支持跨会话恢复。

**核心特性：**
- **轻量待办**：`.tasks/backlog.jsonl` 一行一个后续任务，记录待办不打断当前工作
- **执行流栈**：`.tasks/stack.json` 只保存 active 和 stack 顺序
- **恢复上下文**：active / suspended / blocked 任务使用 `.tasks/tasks/<id>.json` 保存 `resume_hint` 和 `progress_snapshot`
- **先快照再插入**：临时插入新任务前，自动保存当前任务进展和关键判断
- **提示词迁移**：支持从 v1 大 JSON 结构迁移到 v2.1 混合模型

**触发场景：**
- 任务管理：创建任务、查看任务、任务堆栈、我的任务、待办
- 任务切换：先处理、临时插入、挂起任务、继续任务、回到主线
- 后续记录：后续还要做、先记一下、追加待办

**快速开始：**
```
用户: 后续还要补 API 文档和优化缓存策略
AI: [加载 task-stack skill] 已记录 2 项后续任务，当前任务不变。

用户: 先停一下，马上修 token 刷新 bug
AI: [保存当前任务 progress_snapshot]
    已挂起当前任务并开始新任务。
```

---

### [socrates](./socrates/) - 苏格拉底式思考伙伴

通过提问引导用户自己发现答案，而非直接提供解决方案。

**核心能力：**
- **苏格拉底追问** - 澄清概念、探测假设、追问证据
- **结构化分析** - 5 Whys、MECE、First Principles、逆向思维
- **思维树对比** - 多路径探索、假设验证、决策支持
- **对话节奏控制** - 自动判断深挖或收敛时机

**交互模式：**
- 快速梳理：2-3 个问题快速定位
- 深度分析：完整苏格拉底对话
- 决策支持：思维树多路径对比

**触发场景：**
- 梳理思路："梳理思路"、"帮我理一下"、"分析一下"
- 逻辑验证："这个逻辑对吗"、"想想这个问题"
- 决策支持："哪个方案更好"、"怎么选择"

**快速开始：**
```
用户: 帮我理一下这个项目的思路
AI: [加载 socrates skill] 让我帮你理清。先确认一下——你说的「这个项目」具体指的是？

用户: 这个逻辑对不对？
AI: [加载 socrates skill] 我们来检验一下。你的核心假设是什么？

用户: A 和 B 两个方案，选哪个好？
AI: [加载 socrates skill] 两个各有优劣。先明确一下——你最看重什么？
```

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
- `knowledge-index/SKILL.md` - 知识库索引指南
- `template-filler/SKILL.md` - 对话式模板文档填写
- `task-stack/SKILL.md` - 跨会话任务堆栈管理
- `socrates/SKILL.md` - 苏格拉底式思考伙伴
- `viz3d/SKILL.md` - 3D场景生成器（配置驱动，自动展开）

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
| knowledge-index | `/knowledge-index build <路径>` | 构建知识索引 |
| | `/knowledge-index update <路径>` | 增量更新索引 |
| | `/knowledge-index search <查询>` | 搜索知识库 |
| | `/knowledge-index list` | 列出所有知识库 |
| template-filler | `/template-filler <模板路径>` | 对话式填写模板 |
| task-stack | `/task-stack list` | 查看当前任务栈和待办 |
| | `/task-stack add <任务>` | 记录后续待办，不打断当前任务 |
| | `/task-stack push <任务>` | 保存当前进展并临时插入新任务 |
| | `/task-stack done` | 完成当前任务并恢复主线 |
| | `/task-stack resume [任务ID]` | 恢复挂起任务 |
| viz3d | `/viz3d create <项目名>` | 创建3D场景项目 |
| | `/viz3d generate <项目名>` | 生成或更新场景HTML |
| socrates | `/socrates` | 启动苏格拉底式对话 |

**注意**：以上格式使用空格分隔参数，符合 Claude Code 最新规范。AI 会根据上下文理解参数含义。

## 贡献

欢迎贡献！可以提交 issue 或 pull request：
- Bug 修复
- 新功能
- 文档改进
- 新增 skills

---

## 自动反馈系统

本仓库包含一个**自动反馈系统**，用于收集 skill 使用中的改进建议。

### 功能特性

- **自动收集**：AI 检测到改进机会时自动收集反馈信息
- **隐私保护**：自动脱敏文件路径、用户数据、敏感信息
- **用户授权**：首次使用时需确认协议并选择反馈渠道
- **限流去重**：每日上限 5 条，相似反馈自动合并

### 支持的反馈渠道

| 渠道 | 仓库 | 说明 |
|------|------|------|
| **GitHub** | `zhengminjie1981/skills` | 默认渠道 |
| **GitLab** | `Antbook/AI/skills` | 备选渠道 |

### 用户命令

| 命令 | 功能 |
|------|------|
| `/feedback-setup` | 首次设置：阅读协议 → 选择渠道 → 授权 |
| `/feedback-status` | 查看当前授权状态和已注册 skill |
| `/feedback-disable` | 一键关闭自动反馈 |
| `/feedback-enable` | 重新启用 |
| `/feedback-queue` | 查看最近发送的反馈记录 |

### 无 Feedback Skill 时的行为

如果本地不存在 `feedback/` skill，系统会**自动忽略**所有 skill 中的反馈相关配置，不影响 skill 的正常使用。

### 为 Skill 添加反馈支持

在 `SKILL.md` 中添加：

```yaml
# Front matter
feedback:
  enabled: true
  version: "x.x.x"
  author: "your-name"
```

```markdown
<!-- 文件末尾 -->
## 反馈机制

本 skill 支持自动反馈改进。

<!-- FEEDBACK-TRIGGER-START -->
<feedback-config>
{
  "triggers": ["execution_failure", "user_retry"],
  "collect": ["error_type", "environment"],
  "sanitize": ["file_paths", "user_data"]
}
</feedback-config>
<!-- FEEDBACK-TRIGGER-END -->
```

详见 [feedback/SKILL.md](./feedback/SKILL.md)。

---

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
