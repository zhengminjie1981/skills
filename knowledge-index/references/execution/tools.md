# 工具支持

本文档定义知识库索引的工具支持策略，包括文档读取策略、工具选择和降级处理。

## 核心原则

**零依赖优先**：knowledge-index 优先使用 Claude Code 原生读取能力，不强制依赖任何外部工具。

```yaml
优先级:
  1. Claude Read 工具（原生支持 PDF/Markdown/图片）
  2. 用户可选配置转换工具（doc2md/pandoc）
  3. 自动降级保证功能可用
```

## 读取策略矩阵

### 策略对比

| 策略 | PDF | Word | Markdown | 依赖 | 速度 | 质量 | 推荐场景 |
|------|-----|------|---------|------|------|------|---------|
| **direct** | 直接读取 | 尝试读取 | 直接读取 | 无 | ⚡⚡⚡ | ⭐⭐ | 大部分场景 |
| **convert** | 转换 | 转换 | 直接读取 | doc2md/pandoc | ⚡ | ⭐⭐⭐ | 复杂文档、保留格式 |
| **hybrid** | 直接读取 | 转换 | 直接读取 | doc2md（可选） | ⚡⚡ | ⭐⭐⭐ | 混合格式知识库（推荐） |

### Claude Read 工具能力

| 文件类型 | 支持状态 | 说明 |
|---------|---------|------|
| **Markdown** | ✅ 完全支持 | 原生读取，零依赖 |
| **PDF** | ✅ 完全支持 | 支持文本提取，可指定页码 |
| **图片** | ✅ 完全支持 | 视觉分析，自动 OCR |
| **Word/PPT** | ⚠️ 部分支持 | 建议转换为 PDF 或使用转换工具 |
| **HTML** | ✅ 完全支持 | 原生读取 |

## 读取策略详解

### 1. Direct 模式（默认，零依赖）

**配置**：
```yaml
read_strategy:
  mode: "direct"
```

**流程**：
```python
def read_document_direct(file_path, file_type):
    """直接读取模式"""
    if file_type == 'markdown':
        return Read(file_path)  # 原生读取

    elif file_type == 'pdf':
        return Read(file_path)  # 原生读取 PDF

    elif file_type == 'image':
        return Read(file_path)  # 视觉分析

    elif file_type in ['word', 'ppt']:
        # 尝试直接读取（可能失败）
        try:
            return Read(file_path)
        except:
            return None  # 返回 None，后续会提示用户
```

**优势**：
- ✅ 零依赖，无需安装任何工具
- ✅ 速度最快
- ✅ 适用于大部分场景

**劣势**：
- ❌ Word/PPT 可能无法读取
- ❌ 复杂 PDF 结构可能丢失

### 2. Convert 模式（高质量）

**配置**：
```yaml
read_strategy:
  mode: "convert"
  conversion_tools:
    - "doc2md"
    - "pandoc"
```

**流程**：
```python
def read_document_convert(file_path, file_type, tools):
    """转换后读取模式"""
    if file_type == 'markdown':
        return Read(file_path)  # Markdown 无需转换

    # 选择转换工具
    tool = select_tool(file_type, tools)

    if tool == 'doc2md':
        markdown = Skill(skill="doc2md", args=file_path)
    elif tool == 'pandoc':
        markdown = convert_with_pandoc(file_path)
    elif tool == 'pymupdf' and file_type == 'pdf':
        markdown = convert_with_pymupdf(file_path)
    else:
        return None

    return markdown
```

**优势**：
- ✅ 质量最高，保留结构
- ✅ 支持 OCR
- ✅ 支持所有格式

**劣势**：
- ❌ 需要安装工具
- ❌ 速度较慢

### 3. Hybrid 模式（推荐）

**配置**：
```yaml
read_strategy:
  mode: "hybrid"
  formats:
    pdf: "direct"      # PDF 直接读取
    word: "convert"    # Word 转换
    markdown: "direct" # Markdown 直接读取
  conversion_tools:
    - "doc2md"
  on_conversion_failure: "fallback"
```

**流程**：
```python
def read_document_hybrid(file_path, file_type, config):
    """混合读取模式"""
    strategy = config['formats'].get(file_type, 'direct')

    if strategy == 'direct' or file_type == 'markdown':
        # 直接读取
        return Read(file_path)

    elif strategy == 'convert':
        # 尝试转换
        try:
            markdown = convert_document(file_path, config['conversion_tools'])
            return markdown
        except Exception as e:
            # 降级处理
            if config.get('on_conversion_failure') == 'fallback':
                return Read(file_path)
            else:
                raise
```

**优势**：
- ✅ 平衡速度和质量
- ✅ 智能降级
- ✅ 灵活配置

## 工具检测

### 检测逻辑

```python
def detect_available_tools():
    """检测可用的转换工具"""
    tools = []

    # 1. Claude Read 工具（始终可用）
    tools.append({
        'name': 'claude-read',
        'priority': 0,
        'formats': ['pdf', 'markdown', 'image', 'html'],
        'always_available': True
    })

    # 2. 检测 doc2md skill
    if has_doc2md_skill():
        tools.append({
            'name': 'doc2md',
            'priority': 1,
            'formats': ['pdf', 'word', 'ppt']
        })

    # 3. 检测 pandoc
    if is_command_available('pandoc'):
        tools.append({
            'name': 'pandoc',
            'priority': 2,
            'formats': ['pdf', 'word', 'html', 'markdown']
        })

    # 4. 检测 PyMuPDF
    if is_python_package_installed('fitz'):
        tools.append({
            'name': 'pymupdf',
            'priority': 3,
            'formats': ['pdf']
        })

    return tools

def has_doc2md_skill():
    """检测 doc2md skill 是否可用"""
    import os
    skill_path = os.path.expanduser('~/.claude/skills/doc2md')
    return os.path.exists(skill_path)

def is_command_available(cmd):
    """检测系统命令是否可用"""
    import shutil
    return shutil.which(cmd) is not None

def is_python_package_installed(package):
    """检测 Python 包是否安装"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False
```

### 检测输出

```yaml
工具检测报告:
  ✓ Claude Read: 始终可用（原生支持）
  ✓ doc2md skill: 可用（优先级 1）
  ✓ pandoc: 可用 v2.19.2（优先级 2）
  ✗ PyMuPDF: 未安装

推荐配置:
  mode: "hybrid"
  formats:
    pdf: "direct"      # 使用 Claude Read
    word: "convert"    # 使用 doc2md
    markdown: "direct"
```

## 工具选择策略

### 按文档类型选择

```python
def select_conversion_tool(file_type, available_tools):
    """选择转换工具"""
    # 按优先级排序
    sorted_tools = sorted(
        [t for t in available_tools if t['name'] != 'claude-read'],
        key=lambda x: x['priority']
    )

    # 查找支持该格式的工具
    for tool in sorted_tools:
        if file_type in tool['formats']:
            return tool['name']

    return None  # 无可用工具
```

### 选择矩阵

| 文档类型 | Claude Read | doc2md | pandoc | PyMuPDF |
|---------|------------|--------|--------|---------|
| Markdown | ✅ 首选 | - | - | - |
| PDF | ✅ 首选 | 备选 | 备选 | 备选 |
| Word | ⚠️ 尝试 | ✅ 首选 | 备选 | - |
| PPT | ⚠️ 尝试 | ✅ 首选 | 备选 | - |
| HTML | ✅ 首选 | - | 备选 | - |

## 工具使用接口

### Claude Read（原生）

```python
# 直接使用 Read 工具
content = Read(file_path="document.pdf")

# PDF 可指定页码
content = Read(file_path="large.pdf", pages="1-10")
```

### doc2md skill

```python
# 使用 Skill tool 调用
markdown = Skill(skill="doc2md", args="document.pdf --tool mineru")
```

### pandoc

```python
import subprocess

def convert_with_pandoc(file_path, output_format='markdown'):
    """使用 pandoc 转换文档"""
    cmd = [
        'pandoc',
        '-f', detect_format(file_path),
        '-t', output_format,
        file_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return result.stdout
    else:
        raise Exception(f"pandoc 转换失败: {result.stderr}")
```

### PyMuPDF

```python
import fitz  # PyMuPDF

def convert_with_pymupdf(file_path):
    """使用 PyMuPDF 提取 PDF 文本"""
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text()

    doc.close()
    return text
```

## 失败处理和降级

### 降级策略

```python
def read_document_with_fallback(file_path, file_type, config):
    """带降级的文档读取"""
    mode = config.get('mode', 'direct')

    # Direct 模式：直接读取
    if mode == 'direct':
        content = Read(file_path)
        if content:
            return {'success': True, 'content': content, 'method': 'direct'}
        else:
            return {'success': False, 'error': '无法直接读取'}

    # Convert 模式：尝试转换
    elif mode == 'convert':
        try:
            tool = select_conversion_tool(file_type, detect_available_tools())
            if tool:
                content = convert_with_tool(tool, file_path)
                return {'success': True, 'content': content, 'method': f'convert:{tool}'}
            else:
                # 无可用工具，降级到直接读取
                content = Read(file_path)
                return {'success': True, 'content': content, 'method': 'direct(fallback)'}
        except Exception as e:
            # 转换失败，检查是否允许降级
            if config.get('on_conversion_failure') == 'fallback':
                content = Read(file_path)
                if content:
                    return {'success': True, 'content': content, 'method': 'direct(fallback)'}
            return {'success': False, 'error': str(e)}

    # Hybrid 模式：根据配置选择
    elif mode == 'hybrid':
        strategy = config.get('formats', {}).get(file_type, 'direct')
        if strategy == 'direct':
            content = Read(file_path)
            return {'success': True, 'content': content, 'method': 'direct'}
        else:
            # 使用 Convert 模式的逻辑
            return read_document_with_fallback(
                file_path, file_type,
                {**config, 'mode': 'convert'}
            )
```

### 降级提示

```yaml
⚠️ 工具降级提示

检测到 doc2md skill 不可用，已切换至直接读取模式。

如需更高质量的转换：
  - 安装 doc2md skill: git clone https://github.com/yourname/doc2md-skill ~/.claude/skills/doc2md
  - 或安装 pandoc: choco install pandoc (Windows) / brew install pandoc (macOS)

当前配置将继续使用 Claude Read 工具直接读取文档。
```

## 与 doc2md skill 的关系

### 定位

```yaml
关系类型: 可选增强（非必需）
优先级: 最高（如果可用且用户配置需要转换）
```

### 协作场景

**场景 1: 用户未配置 read_strategy**
```yaml
# 默认使用 direct 模式
# 不调用 doc2md
```

**场景 2: 用户配置 convert 模式**
```yaml
read_strategy:
  mode: "convert"
  conversion_tools:
    - "doc2md"

# 会尝试使用 doc2md
# 如果不可用，降级到直接读取
```

**场景 3: 用户配置 hybrid 模式**
```yaml
read_strategy:
  mode: "hybrid"
  formats:
    pdf: "direct"      # PDF 不调用 doc2md
    word: "convert"    # Word 调用 doc2md

# 仅 Word 文档会使用 doc2md
```

## 工具安装指南

### 安装 doc2md skill

```bash
# 克隆到 Claude Code skills 目录
git clone https://github.com/yourname/doc2md-skill ~/.claude/skills/doc2md
```

### 安装 pandoc

**Windows**:
```bash
choco install pandoc
# 或下载安装包: https://pandoc.org/installing.html
```

**macOS**:
```bash
brew install pandoc
```

**Linux**:
```bash
sudo apt-get install pandoc  # Debian/Ubuntu
sudo yum install pandoc      # CentOS/RHEL
```

### 安装 PyMuPDF

```bash
pip install PyMuPDF
```

## 性能优化

### 读取性能对比

| 方法 | PDF 读取速度 | 内存占用 | 质量评分 |
|------|-------------|---------|---------|
| Claude Read | 快 | 低 | 7/10 |
| doc2md | 慢 | 中 | 9/10 |
| pandoc | 中 | 低 | 7/10 |
| PyMuPDF | 极快 | 低 | 6/10 |

### 缓存策略

```yaml
read_strategy:
  mode: "convert"
  cache:
    enabled: true
    directory: ".knowledge-index/cache"
    max_age_days: 30

# 缓存结构
.knowledge-index/cache/
├── a1b2c3d4.md  ← document.pdf 的转换缓存
└── e5f6g7h8.md  ← document.docx 的转换缓存
```

### 批量读取优化

```python
def batch_read(file_paths, config, batch_size=50):
    """批量读取文档"""
    results = []

    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i+batch_size]

        # 并行处理
        batch_results = parallel_read(batch, config)
        results.extend(batch_results)

        # 进度报告
        print(f"进度: {min(i+batch_size, len(file_paths))}/{len(file_paths)}")

    return results
```

## 最佳实践

### 1. 配置选择

| 知识库类型 | 推荐配置 | 理由 |
|-----------|---------|------|
| 纯 Markdown | `mode: "direct"` | 零依赖，速度最快 |
| PDF + Markdown | `mode: "direct"` | Claude Read 原生支持 |
| 混合格式 | `mode: "hybrid"` | 平衡质量和速度 |
| 复杂 PDF（表格/OCR） | `mode: "convert"` + doc2md | 保留结构 |

### 2. 错误处理

- 转换失败时自动降级
- 记录所有失败信息
- 在最终报告中汇总

### 3. 性能优化

- 批量处理时使用并行读取
- 启用缓存避免重复转换
- 大文件使用流式处理

### 4. 用户提示

- 工具不可用时提供安装指南
- 转换失败时提供详细错误信息
- 建议最优配置

## 总结

**knowledge-index 的工具策略**：

```yaml
核心理念:
  1. 零依赖优先：默认直接读取，无需任何工具
  2. 用户可控：通过配置决定是否转换
  3. 智能降级：工具不可用时自动回退
  4. 质量可选：提供多种质量等级

推荐配置:
  大部分场景: mode: "direct"
  混合格式: mode: "hybrid"
  复杂文档: mode: "convert" + doc2md

关键优势:
  - 无需安装任何工具即可使用
  - 用户完全控制转换策略
  - 自动降级保证功能可用
  - 灵活适配不同场景
```

**doc2md 的角色**：

- **不是必需依赖**
- **是可选增强工具**
- **仅在用户配置需要转换时使用**
- **提供更高质量的文档转换**
