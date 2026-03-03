# 更新说明：用户可控的文档读取策略

**版本**: 2.0
**日期**: 2026-03-03
**更新类型**: 重大架构调整

## 核心变更

### 从"强制转换"到"用户可控"

**之前的设计**：
```yaml
旧原则:
  1. 文档优先：所有文档转换为 Markdown 后再处理
  2. 工具灵活：支持多种转换工具

问题:
  - 强制依赖转换工具（doc2md/pandoc）
  - 增加用户配置负担
  - 简单文档也被转换，效率低
```

**新的设计**：
```yaml
新原则:
  1. 零依赖优先：默认直接读取文档，无需安装任何工具
  2. 用户可控：通过配置决定是否转换、如何转换
  3. 智能降级：工具不可用时自动降级到直接读取
```

## 主要更新内容

### 1. 新增 `read_strategy` 配置项

**位置**: `_index_config.yaml`

```yaml
read_strategy:
  mode: "hybrid"  # direct, convert, hybrid

  formats:
    pdf: "direct"      # PDF 直接读取
    word: "convert"    # Word 转换后读取
    markdown: "direct" # Markdown 直接读取

  conversion_tools:
    - "doc2md"    # 优先使用
    - "pandoc"    # 备选

  on_conversion_failure: "fallback"  # 降级策略

  cache:
    enabled: true
    directory: ".knowledge-index/cache"
```

### 2. 三种读取模式

| 模式 | 依赖 | 速度 | 质量 | 推荐场景 |
|------|------|------|------|---------|
| **direct**（默认） | 无 | ⚡⚡⚡ | ⭐⭐ | 大部分场景 |
| **convert** | doc2md/pandoc | ⚡ | ⭐⭐⭐ | 复杂文档 |
| **hybrid**（推荐） | 可选 | ⚡⚡ | ⭐⭐⭐ | 混合格式 |

### 3. doc2md 角色调整

**之前**：
- 软依赖（优先级最高）
- 推荐安装

**现在**：
- **可选增强工具**（非必需）
- 仅在用户配置需要转换时使用
- 无需安装即可使用 knowledge-index

### 4. 更新的文件

| 文件 | 变更说明 |
|------|---------|
| `SKILL.md` | 更新核心原则和工具支持说明 |
| `references/execution/config-options.md` | 新增 `read_strategy` 配置项说明 |
| `references/core/workflow-spec.md` | 调整 Step 2 从"转换文档"到"读取文档" |
| `references/execution/tools.md` | 完全重写，强调零依赖优先 |
| `references/execution/templates.md` | 更新配置模板，新增多种场景示例 |

## 配置迁移指南

### 场景 1: 旧配置（conversion）

**旧配置**：
```yaml
indexing:
  conversion:
    pdf_engine: "mineru"
    ocr_enabled: true
```

**新配置**（等效）：
```yaml
indexing:
  read_strategy:
    mode: "convert"
    conversion_tools:
      - "doc2md"
    pdf:
      prefer_ocr: true
```

### 场景 2: 无配置（使用默认）

**旧行为**：
- 尝试检测转换工具
- 如果有工具，则转换
- 如果无工具，仅索引 Markdown

**新行为**：
- 默认 `mode: "direct"`
- 所有文档直接读取（PDF/Markdown/图片）
- 无需任何工具

### 场景 3: 仅索引 Markdown

**旧配置**：
```yaml
indexing:
  file_types:
    - ".md"
```

**新配置**（保持不变）：
```yaml
indexing:
  file_types:
    - ".md"
  read_strategy:
    mode: "direct"  # 可省略，默认就是 direct
```

## 推荐配置

### 1. 零依赖配置（适合新用户）

```yaml
indexing:
  file_types:
    - ".md"
    - ".pdf"
  read_strategy:
    mode: "direct"  # 无需安装任何工具
```

**优势**：
- ✅ 开箱即用
- ✅ 零配置
- ✅ 适合大部分场景

### 2. 混合模式配置（推荐）

```yaml
indexing:
  file_types:
    - ".md"
    - ".pdf"
    - ".docx"
  read_strategy:
    mode: "hybrid"
    formats:
      pdf: "direct"
      word: "convert"
      markdown: "direct"
    conversion_tools:
      - "doc2md"
    on_conversion_failure: "fallback"
```

**优势**：
- ✅ 平衡速度和质量
- ✅ 智能降级
- ✅ 仅在需要时转换

### 3. 高质量配置（适合复杂文档）

```yaml
indexing:
  file_types:
    - ".pdf"
  read_strategy:
    mode: "convert"
    conversion_tools:
      - "doc2md"
    pdf:
      prefer_ocr: true
      prefer_structure: true
    cache:
      enabled: true
```

**优势**：
- ✅ 质量最高
- ✅ 保留结构
- ✅ 支持 OCR

## Claude Read 工具能力

**重要更新**：Claude Code 的 Read 工具原生支持多种格式：

| 文件类型 | 支持状态 | 说明 |
|---------|---------|------|
| **Markdown** | ✅ 完全支持 | 零依赖 |
| **PDF** | ✅ 完全支持 | 文本提取，可指定页码 |
| **图片** | ✅ 完全支持 | 视觉分析，自动 OCR |
| **HTML** | ✅ 完全支持 | 原生读取 |
| **Word/PPT** | ⚠️ 部分支持 | 建议转换 |

## 降级策略

### 自动降级流程

```
1. 用户配置 mode: "convert"
2. 尝试使用 doc2md 转换
3. 如果 doc2md 不可用：
   ├─ 尝试使用 pandoc
   └─ 如果 pandoc 也不可用：
      └─ 降级到直接读取（Claude Read）
4. 始终保证索引生成完成
```

### 降级提示

```yaml
⚠️ 工具降级提示

检测到 doc2md skill 不可用，已切换至直接读取模式。

当前配置将继续使用 Claude Read 工具直接读取文档。

如需更高质量的转换，可选择安装：
  - doc2md skill: git clone https://github.com/yourname/doc2md-skill ~/.claude/skills/doc2md
  - pandoc: choco install pandoc (Windows) / brew install pandoc (macOS)
```

## 性能对比

### 读取速度（单个文档）

| 方法 | PDF | Word | Markdown |
|------|-----|------|---------|
| **Direct** | 0.5s | 尝试 | 0.1s |
| **Convert** | 3-5s | 2-3s | 0.1s |
| **Hybrid** | 0.5s | 2-3s | 0.1s |

### 依赖安装

| 模式 | 必需工具 | 可选工具 |
|------|---------|---------|
| **Direct** | 无 | - |
| **Convert** | doc2md 或 pandoc | PyMuPDF |
| **Hybrid** | 无 | doc2md（用于 Word） |

## 迁移建议

### 对于现有用户

**如果已经安装 doc2md**：
```yaml
# 推荐配置
read_strategy:
  mode: "hybrid"
  formats:
    pdf: "direct"      # PDF 不需要转换
    word: "convert"    # Word 使用 doc2md
```

**如果未安装 doc2md**：
```yaml
# 使用默认配置即可
read_strategy:
  mode: "direct"  # 无需任何工具
```

### 对于新用户

**快速开始**：
```bash
# 1. 创建知识库目录
mkdir my-knowledge-base

# 2. 添加文档（PDF/Markdown）

# 3. 直接构建索引（无需配置）
用户: 为「my-knowledge-base」建立索引

# AI 将使用 Direct 模式，直接读取所有文档
```

## 常见问题

### Q1: 是否必须安装 doc2md？

**A**: 不需要。默认的 Direct 模式无需任何工具。

### Q2: 什么时候需要安装 doc2md？

**A**: 当你配置了 `mode: "convert"` 或 `mode: "hybrid"` 且 `formats.word: "convert"` 时。

### Q3: Direct 模式的质量够用吗？

**A**: 对于大部分场景（PDF 文本、Markdown、图片），Direct 模式的质量已经足够。仅当需要：
- 保留复杂表格结构
- OCR 扫描件
- 保留数学公式

时，建议使用 Convert 模式。

### Q4: 旧配置还能用吗？

**A**: 可以。旧的 `conversion` 配置项仍然支持，但会提示建议迁移到 `read_strategy`。

### Q5: 如何选择模式？

**A**:
- 纯 Markdown/PDF → `mode: "direct"`
- 混合格式 → `mode: "hybrid"`（推荐）
- 复杂文档（表格/OCR）→ `mode: "convert"`

## 总结

### 核心改进

1. **零依赖优先**：无需安装任何工具即可使用
2. **用户可控**：通过配置决定是否转换
3. **智能降级**：自动处理工具不可用情况
4. **灵活配置**：三种模式适配不同场景

### doc2md 的新角色

- **之前**：软依赖（推荐安装）
- **现在**：可选增强（仅在需要时使用）

### 推荐行动

1. **新用户**：直接使用，无需配置
2. **现有用户**：评估是否需要转换，调整配置
3. **复杂文档**：配置 `mode: "convert"` + doc2md

---

**版本**: 2.0
**向后兼容**: ✅ 旧配置仍然支持
**破坏性变更**: ❌ 无

如有疑问，请参考：
- `references/execution/config-options.md` - 配置详解
- `references/execution/tools.md` - 工具说明
- `references/execution/templates.md` - 配置模板
