# 工具支持

本文档定义知识库索引的工具支持策略，包括文档读取策略、工具选择和降级处理。

## 核心原则

**本地优先**：优先使用本地工具提取文本，仅将纯文本传给 LLM 生成摘要，避免上传完整文档。

```yaml
处理优先级:
  1. 本地提取文本（PyMuPDF/python-docx）→ LLM 仅处理文本
  2. Claude Read 工具（原生支持，文档上传云端）
  3. 用户可选配置转换工具（doc2md/pandoc）
  4. 自动降级保证功能可用

隐私保护:
  - 敏感文档: 使用 local 策略，文本不出本地
  - 大文件处理: 本地提取，减少 token 消耗
  - 可控上传: 用户决定哪些文档可以云端处理
```

## 读取策略矩阵

### 策略对比

| 策略 | PDF | Word | Markdown | 依赖 | 隐私 | 成本 | 速度 | 质量 | 推荐场景 |
|------|-----|------|---------|------|------|------|------|------|---------|
| **local** | 本地提取 | 本地提取 | 直接读取 | PyMuPDF/docx | ⭐⭐⭐ | 低 | ⚡⚡ | ⭐⭐ | 敏感文档、成本控制 |
| **direct** | 上传云端 | 尝试读取 | 直接读取 | 无 | ⭐ | 高 | ⚡⚡⚡ | ⭐⭐ | 快速索引、公开文档 |
| **convert** | 转换 | 转换 | 直接读取 | doc2md/pandoc | ⭐⭐ | 中 | ⚡ | ⭐⭐⭐ | 复杂文档、保留格式 |
| **hybrid** | 本地提取 | 本地提取 | 直接读取 | PyMuPDF/docx | ⭐⭐⭐ | 低 | ⚡⚡ | ⭐⭐⭐ | 混合格式（推荐） |

### 处理流程对比

```
┌─────────────────────────────────────────────────────────────────┐
│                      local 策略（本地优先）                       │
├─────────────────────────────────────────────────────────────────┤
│  PDF/DOCX ──→ 本地脚本提取文本 ──→ 纯文本 ──→ LLM生成摘要        │
│              (PyMuPDF/docx)        (不上传)   (仅文本)           │
│                                                                 │
│  优势: 隐私保护、成本可控、大文件友好                              │
│  劣势: 需要安装 Python 依赖                                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      direct 策略（直接上传）                      │
├─────────────────────────────────────────────────────────────────┤
│  PDF ──→ Claude Read ──→ LLM 处理完整文档 ──→ 生成摘要           │
│          (上传云端)    (完整内容)                                 │
│                                                                 │
│  优势: 零依赖、速度最快                                           │
│  劣势: 文档上传云端、token 消耗高                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Claude Read 工具能力

| 文件类型 | 支持状态 | 说明 |
|---------|---------|------|
| **Markdown** | ✅ 完全支持 | 原生读取，零依赖 |
| **PDF** | ✅ 完全支持 | 支持文本提取，可指定页码 |
| **图片** | ✅ 完全支持 | 视觉分析，自动 OCR |
| **Word/PPT** | ⚠️ 部分支持 | 建议转换为 PDF 或使用转换工具 |
| **HTML** | ✅ 完全支持 | 原生读取 |

## 读取策略详解

### 0. Local 模式（本地优先，推荐）

**配置**：
```yaml
read_strategy:
  mode: "local"
  local_tools:
    pdf: "pymupdf"      # 或 "pdfplumber"
    word: "python-docx" # 或 "antiword"
    doc: "antiword"     # 旧版 Word
  fallback: "direct"    # 本地提取失败时降级
```

**流程**：
```python
def read_document_local(file_path, file_type, config):
    """本地优先模式 - 文本提取后仅传给 LLM 摘要"""
    import subprocess
    import json

    # Step 1: 使用本地脚本提取文本
    extract_script = "knowledge-index/scripts/extract_text.py"

    result = subprocess.run(
        ["python", extract_script, file_path, "--format", "json"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        # 本地提取失败，降级处理
        if config.get('fallback') == 'direct':
            return Read(file_path)
        else:
            raise Exception(f"本地提取失败: {result.stderr}")

    # Step 2: 解析提取的文本
    extracted = json.loads(result.stdout)
    text_content = extracted['text']

    # Step 3: 仅将文本传给 LLM 生成摘要（不上传完整文档）
    return {
        'text': text_content,
        'metadata': extracted.get('metadata', {}),
        'method': 'local',
        'char_count': len(text_content)
    }
```

**优势**：
- ✅ **隐私保护**：完整文档不上传云端
- ✅ **成本控制**：仅文本传给 LLM，减少 token 消耗
- ✅ **大文件友好**：本地处理无大小限制
- ✅ **可控性强**：用户完全掌控处理流程

**劣势**：
- ❌ 需要安装 Python 依赖（PyMuPDF、python-docx）
- ❌ 复杂格式（表格、图片）可能丢失

**适用场景**：
- 敏感/机密文档
- 大型知识库（成本控制）
- 企业内部部署
- 合规要求高的场景

### 1. Direct 模式（零依赖）

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

---

## 本地提取脚本

### 脚本位置

```
knowledge-index/scripts/
├── extract_text.py      # 核心提取脚本
├── batch_extract.py     # 批量处理脚本
└── check_dependencies.py # 依赖检查
```

### extract_text.py

```python
#!/usr/bin/env python3
"""
本地文档文本提取脚本

用法:
    python extract_text.py <file_path> [--format json|text]
    python extract_text.py document.pdf --format json
    python extract_text.py document.docx

输出 (JSON 格式):
    {
        "text": "提取的纯文本内容",
        "metadata": {
            "page_count": 10,
            "char_count": 5000,
            "extractor": "pymupdf"
        },
        "success": true
    }
"""

import sys
import json
import os
from pathlib import Path


def extract_pdf_pymupdf(file_path: str) -> dict:
    """使用 PyMuPDF 提取 PDF 文本"""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        text_parts = []
        page_count = len(doc)

        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                text_parts.append(f"[第{page_num + 1}页]\n{text}")

        doc.close()

        return {
            "text": "\n\n".join(text_parts),
            "metadata": {
                "page_count": page_count,
                "extractor": "pymupdf",
                "char_count": sum(len(t) for t in text_parts)
            },
            "success": True
        }
    except ImportError:
        return {"success": False, "error": "PyMuPDF 未安装"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_pdf_pdfplumber(file_path: str) -> dict:
    """使用 pdfplumber 提取 PDF 文本（备选方案）"""
    try:
        import pdfplumber

        text_parts = []
        page_count = 0

        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    text_parts.append(f"[第{page_num + 1}页]\n{text}")

        return {
            "text": "\n\n".join(text_parts),
            "metadata": {
                "page_count": page_count,
                "extractor": "pdfplumber",
                "char_count": sum(len(t) for t in text_parts)
            },
            "success": True
        }
    except ImportError:
        return {"success": False, "error": "pdfplumber 未安装"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_docx(file_path: str) -> dict:
    """使用 python-docx 提取 Word 文档文本"""
    try:
        from docx import Document

        doc = Document(file_path)
        text_parts = []

        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)

        # 提取表格文本
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text for cell in row.cells)
                if row_text.strip():
                    text_parts.append(row_text)

        return {
            "text": "\n".join(text_parts),
            "metadata": {
                "extractor": "python-docx",
                "char_count": sum(len(t) for t in text_parts),
                "para_count": len(doc.paragraphs),
                "table_count": len(doc.tables)
            },
            "success": True
        }
    except ImportError:
        return {"success": False, "error": "python-docx 未安装"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_doc(file_path: str) -> dict:
    """提取旧版 .doc 文件文本"""
    # 尝试使用 antiword (Linux/Mac)
    import subprocess

    try:
        result = subprocess.run(
            ["antiword", file_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return {
                "text": result.stdout,
                "metadata": {"extractor": "antiword"},
                "success": True
            }
    except FileNotFoundError:
        pass
    except Exception:
        pass

    # 尝试使用 python-docx (某些 .doc 实际是 .docx)
    try:
        return extract_docx(file_path)
    except:
        pass

    return {
        "success": False,
        "error": "无法提取 .doc 文件，请安装 antiword 或转换为 .docx"
    }


def extract_text(file_path: str) -> dict:
    """根据文件类型选择提取方法"""
    ext = Path(file_path).suffix.lower()

    extractors = {
        ".pdf": [extract_pdf_pymupdf, extract_pdf_pdfplumber],
        ".docx": [extract_docx],
        ".doc": [extract_doc],
    }

    if ext not in extractors:
        return {
            "success": False,
            "error": f"不支持的文件类型: {ext}"
        }

    # 尝试所有可用的提取器
    for extractor in extractors[ext]:
        result = extractor(file_path)
        if result.get("success"):
            return result

    # 所有提取器都失败
    return {
        "success": False,
        "error": "所有提取方法均失败"
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python extract_text.py <file_path> [--format json|text]")
        sys.exit(1)

    file_path = sys.argv[1]
    output_format = "json"

    if "--format" in sys.argv:
        idx = sys.argv.index("--format")
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    if not os.path.exists(file_path):
        result = {"success": False, "error": f"文件不存在: {file_path}"}
    else:
        result = extract_text(file_path)

    if output_format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result.get("success"):
            print(result["text"])
        else:
            print(f"错误: {result.get('error')}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
```

### check_dependencies.py

```python
#!/usr/bin/env python3
"""检查本地提取所需的依赖"""

import sys

def check_dependencies():
    """检查并报告依赖状态"""
    dependencies = {
        "PyMuPDF (fitz)": "fitz",
        "pdfplumber": "pdfplumber",
        "python-docx": "docx",
    }

    print("依赖检查结果:")
    print("-" * 40)

    results = {}
    for name, module in dependencies.items():
        try:
            __import__(module)
            results[name] = "✓ 已安装"
        except ImportError:
            results[name] = "✗ 未安装"
        print(f"{name}: {results[name]}")

    print("-" * 40)

    # 检查 antiword
    import shutil
    if shutil.which("antiword"):
        print("antiword: ✓ 已安装")
    else:
        print("antiword: ✗ 未安装 (可选，用于 .doc 文件)")

    print("\n安装建议:")
    missing = [n for n, s in results.items() if "未安装" in s]

    if missing:
        print("pip install PyMuPDF pdfplumber python-docx")
    else:
        print("所有核心依赖已安装，可以使用 local 模式")


if __name__ == "__main__":
    check_dependencies()
```

### 在 AI Agent 中调用

```python
def extract_text_local(file_path: str) -> dict:
    """AI Agent 调用本地提取脚本"""

    # 使用 Bash 工具调用 Python 脚本
    script_path = "~/.claude/skills/knowledge-index/scripts/extract_text.py"

    result = Bash(
        command=f"python {script_path} '{file_path}' --format json",
        description=f"本地提取文档文本: {file_path}"
    )

    import json
    return json.loads(result)
```

---

## 依赖安装

### 核心依赖（local 模式必需）

```bash
# PDF 提取
pip install PyMuPDF

# Word 文档提取
pip install python-docx

# PDF 备选方案（可选）
pip install pdfplumber
```

### 完整安装命令

```bash
# 一次性安装所有本地提取依赖
pip install PyMuPDF python-docx pdfplumber
```

### 验证安装

```bash
# 运行依赖检查
python ~/.claude/skills/knowledge-index/scripts/check_dependencies.py
```

---

## 隐私与成本对比

### Token 消耗估算

| 文档类型 | 文件大小 | 直接上传 | 本地提取 | 节省 |
|---------|---------|---------|---------|------|
| PDF 报告 | 2 MB | ~50,000 tokens | ~5,000 tokens | 90% |
| Word 文档 | 500 KB | ~15,000 tokens | ~3,000 tokens | 80% |
| 技术手册 | 10 MB | ~200,000 tokens | ~20,000 tokens | 90% |

### 隐私等级

| 策略 | 文档上传 | 文本上传 | 适用场景 |
|------|---------|---------|---------|
| local | ✗ 否 | ✓ 是（仅文本） | 敏感文档、企业内部 |
| direct | ✓ 是 | ✓ 是 | 公开文档、快速索引 |
| hybrid | 部分 | ✓ 是 | 混合场景 |

---

## 最佳实践更新

### 配置选择（更新版）

| 知识库类型 | 推荐配置 | 理由 |
|-----------|---------|------|
| 敏感/机密文档 | `mode: "local"` | 文档不上传，隐私保护 |
| 纯 Markdown | `mode: "direct"` | 零依赖，速度最快 |
| 大型知识库 | `mode: "local"` | 成本控制，token 节省 |
| 复杂 PDF（表格/OCR） | `mode: "convert"` + doc2md | 保留结构 |
| 混合格式 | `mode: "hybrid"` + 本地提取 | 平衡隐私、质量和速度 |

### 推荐默认配置

```yaml
# ~/.knowledge-index/config.yaml
read_strategy:
  mode: "local"  # 改为本地优先
  local_tools:
    pdf: "pymupdf"
    word: "python-docx"
  fallback: "direct"  # 本地失败时降级

  # 可选：指定敏感目录强制本地处理
  sensitive_paths:
    - "~/Documents/机密"
    - "~/Work/内部"

  # 可选：大文件阈值，超过则强制本地处理
  large_file_threshold_mb: 5
```
