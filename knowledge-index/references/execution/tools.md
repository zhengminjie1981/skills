# 工具支持

本文档定义知识库索引的工具支持策略，包括文档转换工具的自动检测、选择和降级处理。

## 工具矩阵

### 支持的文档转换工具

| 优先级 | 工具 | 支持格式 | 使用场景 | 安装要求 |
|--------|------|---------|---------|---------|
| 1 | doc2md skill | PDF, Word, PPT | 已有 doc2md skill 环境 | Claude Code + doc2md skill |
| 2 | pandoc | PDF, Word, Markdown, HTML, RST | 通用转换，功能强大 | pandoc 可执行文件 |
| 3 | mineru | PDF | PDF 专用，支持 OCR | Python + mineru 包 |
| 4 | PyMuPDF | PDF | 纯文本 PDF，快速 | Python + PyMuPDF 包 |
| 5 | 直接读取 | Markdown | 仅索引 Markdown | 无需额外工具 |

### 工具选择策略

```
检测可用工具 → 按优先级选择 → 格式匹配 → 执行转换 → 失败 fallback
```

## 工具检测流程

### 检测逻辑（Python 伪代码）

```python
def detect_available_tools():
    """检测可用的文档转换工具"""
    tools = []

    # 1. 检测 doc2md skill
    if has_doc2md_skill():
        tools.append({
            'name': 'doc2md',
            'priority': 1,
            'formats': ['pdf', 'word', 'ppt']
        })

    # 2. 检测 pandoc
    if is_command_available('pandoc'):
        version = get_pandoc_version()
        tools.append({
            'name': 'pandoc',
            'priority': 2,
            'formats': ['pdf', 'word', 'markdown', 'html', 'rst'],
            'version': version
        })

    # 3. 检测 mineru
    if is_python_package_installed('mineru'):
        tools.append({
            'name': 'mineru',
            'priority': 3,
            'formats': ['pdf']
        })

    # 4. 检测 PyMuPDF
    if is_python_package_installed('fitz'):  # PyMuPDF 的导入名
        tools.append({
            'name': 'pymupdf',
            'priority': 4,
            'formats': ['pdf']
        })

    # 5. 始终支持 Markdown
    tools.append({
        'name': 'direct',
        'priority': 5,
        'formats': ['markdown']
    })

    return tools

def has_doc2md_skill():
    """检测 doc2md skill 是否可用"""
    # 检查技能目录或技能列表
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
  ✓ doc2md skill: 可用 (优先级 1)
  ✓ pandoc: 可用 v2.19.2 (优先级 2)
  ✗ mineru: 未安装
  ✓ PyMuPDF: 可用 v1.23.0 (优先级 4)
  ✓ 直接读取: 始终可用

推荐工具链:
  PDF: doc2md → pandoc → PyMuPDF
  Word: doc2md → pandoc
  Markdown: 直接读取
```

## 工具选择策略

### 按文档类型选择

```python
def select_tool(doc_type, available_tools):
    """根据文档类型选择最优工具"""
    # 按优先级排序
    sorted_tools = sorted(available_tools, key=lambda x: x['priority'])

    # 查找支持该格式的工具
    for tool in sorted_tools:
        if doc_type in tool['formats']:
            return tool['name']

    return None  # 无可用工具
```

### 选择矩阵

| 文档类型 | 首选工具 | 备选工具 1 | 备选工具 2 |
|---------|---------|-----------|-----------|
| PDF | doc2md | pandoc | PyMuPDF |
| Word (.docx/.doc) | doc2md | pandoc | - |
| PowerPoint | doc2md | pandoc | - |
| Markdown | 直接读取 | - | - |
| HTML | pandoc | - | - |

## 工具使用接口

### doc2md skill 接口

```python
def convert_with_doc2md(file_path):
    """使用 doc2md skill 转换文档"""
    # 在 Claude Code 中调用 skill
    # Skill tool: skill="doc2md", args=file_path
    markdown = call_doc2md_skill(file_path)
    return markdown
```

### pandoc 接口

```python
import subprocess

def convert_with_pandoc(file_path, output_format='markdown'):
    """使用 pandoc 转换文档"""
    cmd = [
        'pandoc',
        '-f', detect_format(file_path),  # 自动检测输入格式
        '-t', output_format,
        file_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return result.stdout
    else:
        raise Exception(f"pandoc 转换失败: {result.stderr}")
```

### PyMuPDF 接口

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

### mineru 接口

```python
# 示例接口（具体实现取决于 mineru 的 API）
def convert_with_mineru(file_path):
    """使用 mineru 转换 PDF"""
    from mineru import convert_pdf
    return convert_pdf(file_path, output_format='markdown')
```

## 失败处理和降级

### Fallback 策略

```python
def convert_document(file_path, available_tools):
    """转换文档，支持失败降级"""
    doc_type = detect_document_type(file_path)
    tools = get_tools_for_format(doc_type, available_tools)

    errors = []

    for tool_name in tools:
        try:
            # 尝试转换
            markdown = convert_with_tool(tool_name, file_path)

            # 验证转换结果
            if is_valid_conversion(markdown):
                return {
                    'success': True,
                    'tool': tool_name,
                    'content': markdown
                }
        except Exception as e:
            errors.append(f"{tool_name}: {str(e)}")
            continue

    # 所有工具都失败
    return {
        'success': False,
        'errors': errors,
        'content': None
    }

def is_valid_conversion(content):
    """验证转换结果"""
    if not content or len(content.strip()) < 100:
        return False
    # 可添加更多验证逻辑
    return True
```

### 降级处理场景

#### 场景 1: doc2md skill 不可用

```
首选: doc2md → 降级: pandoc
```

#### 场景 2: PDF 转换失败

```
首选: doc2md → 备选: pandoc → 备选: PyMuPDF → 失败: 跳过该文档
```

#### 场景 3: 所有转换工具不可用

```
检测: 无可用工具 → 降级: 仅索引 Markdown 文档 → 提示用户安装工具
```

### 降级提示

```yaml
⚠️ 工具降级警告

检测到 doc2md skill 不可用，已切换至 pandoc。

推荐安装 doc2md skill 以获得更好的转换质量：
  - 支持 PDF/Word/PPT
  - AI 增强的格式处理
  - 保留文档结构

安装方法:
  git clone https://github.com/yourname/doc2md-skill ~/.claude/skills/doc2md
```

## 与 doc2md skill 的协作

### 协作方式

本 skill **不强制依赖** doc2md skill，但优先使用：

```yaml
依赖类型: 软依赖（可选）
优先级: 最高（如果可用）
```

### 协作流程

```
1. 检测 doc2md skill 可用性
2. 如果可用:
   - 调用 doc2md 转换 PDF/Word/PPT
   - 使用转换后的 Markdown 生成摘要
3. 如果不可用:
   - 使用 pandoc 或其他工具
   - 继续索引流程
```

### 调用示例

在 Claude Code 中调用 doc2md skill:

```python
# 使用 Skill tool
markdown = Skill(skill="doc2md", args="/path/to/document.pdf")
```

## 工具安装指南

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

### 安装 mineru

```bash
pip install mineru
```

### 安装 doc2md skill

```bash
# 克隆到 Claude Code skills 目录
git clone https://github.com/yourname/doc2md-skill ~/.claude/skills/doc2md
```

## 性能优化

### 工具性能对比

| 工具 | PDF 转换速度 | 内存占用 | 质量评分 |
|------|-------------|---------|---------|
| doc2md | 中 | 中 | 9/10 |
| pandoc | 快 | 低 | 7/10 |
| PyMuPDF | 极快 | 低 | 6/10 |
| mineru | 慢 | 高 | 8/10 |

### 批量转换优化

```python
def batch_convert(file_paths, available_tools, batch_size=50):
    """批量转换文档"""
    results = []

    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i+batch_size]

        # 并行处理（如支持）
        batch_results = parallel_convert(batch, available_tools)
        results.extend(batch_results)

        # 进度报告
        print(f"进度: {min(i+batch_size, len(file_paths))}/{len(file_paths)}")

    return results
```

## 索引验证工具

### YAML 验证

```python
import yaml

def validate_yaml(index_path):
    """验证索引文件的 YAML 语法"""
    try:
        with open(index_path, encoding='utf-8') as f:
            yaml.safe_load(f)
        return {'valid': True}
    except yaml.YAMLError as e:
        return {'valid': False, 'error': str(e)}
```

### 字段完整性验证

```python
def validate_index_fields(index_path):
    """验证索引字段完整性"""
    with open(index_path, encoding='utf-8') as f:
        index = yaml.safe_load(f)

    errors = []

    # 检查元数据
    required_meta = ['version', 'knowledge_base']
    for field in required_meta:
        if field not in index:
            errors.append(f"缺少必填字段: {field}")

    # 检查文档
    required_doc_fields = ['path', 'filename', 'type', 'summary']
    for i, doc in enumerate(index.get('documents', [])):
        for field in required_doc_fields:
            if field not in doc:
                errors.append(f"文档 {i} 缺少字段: {field}")

    return {'valid': len(errors) == 0, 'errors': errors}
```

## 最佳实践

### 1. 工具选择

- 优先使用 doc2md skill（质量最高）
- 大规模知识库使用 PyMuPDF（速度最快）
- 复杂格式文档使用 pandoc（兼容性最好）

### 2. 错误处理

- 转换失败时自动切换工具
- 记录所有失败信息
- 在最终报告中汇总失败原因

### 3. 性能优化

- 批量处理时使用并行转换
- 大文件使用流式处理
- 缓存转换结果避免重复工作

### 4. 用户提示

- 工具不可用时提供安装指南
- 转换失败时提供详细错误信息
- 建议最优工具配置
