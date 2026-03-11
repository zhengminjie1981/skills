# 索引完整规范

本文档详细定义知识库索引文件的完整格式规范。

## 索引版本

当前版本：**2.1**（检索性能优化版）

### 版本 2.1 特性

基于 v2.0 所有功能，增加以下新特性：

- **文件夹分区索引**：`folders` 字段，用于两阶段检索
- **语义分类索引**：`categories` 字段，从 topics 自动聚合
- **路径权重**：检索时路径匹配获得额外权重

- **进度反馈**：长时间任务显示实时进度和预估剩余时间

- **CLI 分类筛选**：`--category` 参数支持按分类查询

### 版本 2.0 特性（继承)

- **文档分类**：`markdown_documents` + `other_documents` 两个列表
- Wikilink 支持：`links` 和 `backlinks` 字段
- Obsidian 集成：自动检测 `.obsidian` 文件夹
- AI 摘要：`summary`、`keywords`、`topics` 字段

## 索引文件位置
- **文件名**: `_index.yaml`
- **位置**: 知识库根目录
- **编码**: UTF-8
- **格式**: YAML
## 完整格式规范（v2.1）
```yaml
# ===== 索引元数据 =====
version: "2.1"
knowledge_base:
  name: "知识库名称"
  path: "绝对路径"
  type: "obsidian"                    # obsidian 或 generic
  has_obsidian: true                  # 是否有 .obsidian 文件夹
  created: "2026-03-03T10:00:00Z"      # ISO 8601 格式
  last_updated: "2026-03-03T15:30:00Z"
  total_documents: 15
  total_size_mb: 2.5

# ===== 文件夹分区索引（v2.1 新增） =====
folders:
  - path: "子系统/"                  # 文件夹相对路径（以/结尾）
    document_count: 12              # 该文件夹下文档数
    keywords_aggregated: ["API", "认证", "权限"]  # 茚合关键词（前20个）
    topics_aggregated: ["接口设计", "安全"]          # 聚合主题（前10个）

  - path: "子系统/模块A/"
    document_count: 8
    keywords_aggregated: ["用户管理", "角色"]
    topics_aggregated: ["身份认证"]

# ===== 语义分类索引（v2.1 新增） =====
categories:
  - name: "配置管理"                # 分类名称
    keywords: ["配置", "环境", "变量", "settings"]  # 关键词列表（前15个）
    document_count: 15              # 该分类下文档数
    folders: ["", "子系统/"]            # 相关文件夹列表

  - name: "安全认证"
    keywords: ["认证", "权限", "安全", "登录"]
    document_count: 10
    folders: ["子系统/", "子系统/模块A/"]

# ===== Markdown 文档 =====
markdown_documents:
  - path: "相对路径/文档名.md"
    filename: "文档名.md"
    type: "markdown"
    modified: "2026-02-28T10:30:00Z"
    size: 15234
    # AI 生成的摘要和关键词
    summary: "文档摘要内容（50-500字符）"
    keywords: ["关键词1", "关键词2"]    # 5-10个
    topics: ["主题1", "主题2"]          # 3-5个
    # Obsidian 特有字段（has_obsidian=true 时）
    links: ["config.md", "security.md"]      # 出链（wikilink）
    backlinks: ["index.md", "tutorial.md"]   # 反向链接
    tags: ["#api", "#security"]              # 标签

# ===== 其他格式文档 =====
other_documents:
  - path: "相对路径/报告.pdf"
    filename: "报告.pdf"
    type: "pdf"                        # pdf, word, text
    modified: "2026-02-28T10:30:00Z"
    size: 102400
```

## 兼容性说明
### 版本 2.0 兼容
系统同时支持读取旧版 2.0 格式索引：
```yaml
# v2.0 格式（无 folders/categories，仍可读取）
version: "2.0"
knowledge_base:
  # ...（无 type 字段）
markdown_documents:
  # ...
```
v2.0 索引加载时会自动生成 `folders` 和 `categories`（动态生成，不持久化）
### 版本 1.0 兼容
系统同时支持读取旧版 1.0 格式索引：
```yaml
# v1.0 格式（已弃用但仍可读取）
version: "1.0"
documents:
  - path: "文档.md"
    type: "markdown"
    # ...
```
### 升级路径
- v1.0 → v2.0： 自动升级，索引结构
- v2.0 -> v2.1: 自动添加 folders 和 categories 字段

## 字段说明
### 元数据字段（必填）
| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `version` | string | 索引格式版本 | `"2.1"` |
| `knowledge_base.name` | string | 知识库显示名称 | `"信息化知识库"` |
| `knowledge_base.path` | string | 知识库绝对路径 | `"E:/知识库/信息化"` |
| `knowledge_base.type` | string | 知识库类型 | `"obsidian"` 或 `"generic"` |
| `knowledge_base.has_obsidian` | bool | 是否有 Obsidian | `true` / `false` |
| `knowledge_base.created` | datetime | 索引创建时间 | `"2026-03-03T10:00:00Z"` |
| `knowledge_base.last_updated` | datetime | 最后更新时间 | `"2026-03-03T15:30:00Z"` |
| `knowledge_base.total_documents` | integer | 文档总数 | `15` |
| `knowledge_base.total_size_mb` | float | 总大小（MB） | `2.5` |
### 文件夹分区索引字段（v2.1 新增）
| 字段 | 类型 | 说明 |
|------|------|------|
| `path` | string | 文件夹相对路径（以/结尾） | `"子系统/"` |
| `document_count` | integer | 该文件夹下文档数 | `12` |
| `keywords_aggregated` | array | 聚合关键词（前20个） | `["API", "认证"]` |
| `topics_aggregated` | array | 聚合主题（前10个） | `["接口设计", "安全"]` |
### 语义分类索引字段（v2.1 新增）
| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 分类名称 | `"配置管理"` |
| `keywords` | array | 关键词列表（前15个） | `["配置", "环境"]` |
| `document_count` | integer | 该分类下文档数 | `15` |
| `folders` | array | 相关文件夹列表 | `["", "子系统/"]` |
### Markdown 文档字段
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `path` | string | ✅ | 文档相对路径 |
| `filename` | string | ✅ | 文件名（含扩展名） |
| `type` | string | ✅ | 固定为 `"markdown"` |
| `modified` | datetime | ✅ | 最后修改时间 |
| `size` | integer | ✅ | 文件大小（字节） |
| `summary` | string | ❌ | AI 生成的摘要（需启用 AI） |
| `keywords` | array | ❌ | 关键词列表（5-10个，需启用 AI） |
| `topics` | array | ❌ | 主题标签列表（3-5个） |
| `links` | array | ❌ | 出链列表（Obsidian） |
| `backlinks` | array | ❌ | 反向链接列表（Obsidian） |
| `tags` | array | ❌ | 标签列表（Obsidian） |
### 其他格式文档字段
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `path` | string | ✅ | 文档相对路径 |
| `filename` | string | ✅ | 文件名（含扩展名） |
| `type` | string | ✅ | 文档类型： `pdf`、`word`、`text` |
| `modified` | datetime | ✅ | 最后修改时间 |
| `size` | integer | ✅ | 文件大小（字节） |
| `summary` | string | ❌ | AI 生成的摘要（需启用 AI） |
| `keywords` | array | ❌ | 关键词列表（需启用 AI） |
## 摘要质量要求
### 结构化摘要（推荐）
```yaml
summary: |
  本文档介绍 XXX 的完整流程：
  1. 功能模块A：详细说明
  2. 功能模块B：详细说明
  3. 功能模块C：详细说明
```
### 摘要长度
- **推荐**: 100-300 字符
- **最小**: 50 字符
- **最大**: 500 字符（可在配置中调整）
### 关键词要求
- **数量**: 5-10 个
- **特性**: 具有检索价值，避免通用词
- **示例**: ✅ `["GitLab", "CI/CD", "流水线"]` ❌ `["文档", "说明", "介绍"]`
### 主题标签要求
- **数量**: 3-5 个
- **特性**: 反映文档类别和所属领域
- **示例**: `["配置管理", "协作开发", "持续集成"]`
## Wikilink 解析规则
### 支持的格式
| 格式 | 解析结果 |
|------|---------|
| `[[文档名]]` | `文档名.md` |
| `[[文档名#标题]]` | `文档名.md`（忽略标题） |
| `[[文档名\|别名]]` | `文档名.md`（忽略别名） |
| `[[folder/文档名]]` | `folder/文档名.md` |
### 反向链接计算
反向链接在索引构建时自动计算：
1. 扫描所有 Markdown 文档
2. 提取每个文档的 `links`
3. 构建反向链接映射
4. 写入每个文档的 `backlinks` 字段
## 检索策略（v2.1 更新）
### 两阶段检索
```
用户查询 → 文件夹预筛选（匹配 folders.keywords_aggregated）
                ↓
           筛选相关文件夹（减少 50-70% 扫描量）
                ↓
           文档精细检索（仅在相关文件夹内）
                ↓
           Markdown 软加权 +10%
                ↓
           按相关度分数排序
```
### 相关度计算（v2.1 更新）
| 匹配字段 | 权重 |
|---------|------|
| 文件名 | 0.4 |
| **路径** | **0.15**（v2.1 新增） |
| 摘要 | 0.3 |
| 关键词 | 0.3 |
| 标签 | 0.2（Markdown 额外加分） |
### 路径权重说明（v2.1 新增）
路径匹配权重较低（0.15），因为路径信息通常比文件名更具组织性，能提升检索精准度：
示例：查询 "API" 可能匹配到 `子系统/API/` 文件夹路径中的 "API" 关键词
### 软加权说明
- **Markdown +10%**: 因为包含 links、backlinks、tags 等额外信息
- **其他格式**：基础分数，不加权
- **同名优先**：同名文件 Markdown 优先
- **目的**: 不阻断其他格式，让相关度决定排序
## 进度反馈机制（v2.1 新增）
### ProgressReporter 类
用于长时间任务（索引构建、检索）显示实时进度
```python
class ProgressReporter:
    def __init__(self, total: int, task_name: str = "处理中"):
        self.total = total
        self.task_name = task_name
        self.start_time = time.time()
    def update(self, increment: int = 1, message: str = None):
        """更新进度"""
        elapsed = time.time() - self.start_time
        percentage = (self.current / self.total) * 100
        # 估算剩余时间
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
        else:
            eta = 0
        print(f"\r[{self.task_name}] {self.current}/{self.total} ({percentage:.1f}%), 预计剩余 {eta:.0f}s - {message}")
    def complete(self, message: str = "完成"):
        elapsed = time.time() - self.start_time
        print(f"[{self.task_name}] 完成 - {message}，耗时 {elapsed:.1f}s")
```
### 应用场景
| 任务 | 进度显示示例 |
|------|---------|
| 索引构建 | `[构建索引] 15/300 (5.0%), 预计剩余 45s - 正在处理: 配置文档.md` |
| 噪量更新 | `[增量更新] 3/5 (60.0%) - 已检测到 3 个变更 |
| AI 摘要 | `[生成摘要] 8/50 (16.0%), 预计剩余 120s |
| 检索（>100 文档） | `[检索中] 扫描 120/300 文档... |
## 编码和格式
### YAML 格式要求
- 使用 2 空格缩进
- 字符串优先使用双引号
- 多行文本使用 `|` 或 `>`
### 时间格式
- 标准：ISO 8601
- 格式： `YYYY-MM-DDTHH:MM:SSZ`
- 示例: `"2026-03-03T10:00:00Z"`
### 路径格式
- 使用正斜杠 `/`（跨平台兼容）
- 相对于知识库根目录
- 示例: `"子文件夹/文档名.md"`
## 验证清单
构建或更新索引后，应验证:
- [ ] 所有必填字段已填写
- [ ] 时间格式符合 ISO 8601
- [ ] 路径使用正斜杠
- [ ] 摘要长度在合理范围
    - [ ] 关键词数量适中（5-10个）
- [ ] YAML 语法正确
- [ ] 文件编码为 UTF-8
    - [ ] folders 字段存在（v2.1）
    - [ ] categories 字段存在（v2.1）
    - [ ] keywords_aggregated 不为空（前20个）
    - [ ] topics_aggregated 不为空（前10个）
    - [ ] document_count > 0
## 示例索引
完整的示例索引见 `references/execution/templates.md`。
