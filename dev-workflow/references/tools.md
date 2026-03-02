# 自动化工具指南

## 文档一致性检查

### 检查数据结构定义一致性

```bash
# 提取数据结构规范中的定义
grep -n "class.*:" doc/技术规范/数据结构规范.md > /tmp/spec_structures.txt

# 提取模块文档中的引用
grep -rn "class.*:" doc/模块设计/ > /tmp/module_structures.txt

# 对比差异
diff /tmp/spec_structures.txt /tmp/module_structures.txt
```

### 检查接口签名一致性

```bash
# 提取接口规范中的函数签名
grep -n "def " doc/技术规范/接口规范.md > /tmp/spec_interfaces.txt

# 提取代码中的函数签名
grep -rn "def " src/ > /tmp/code_interfaces.txt

# 对比（需要人工确认）
diff /tmp/spec_interfaces.txt /tmp/code_interfaces.txt
```

### 自动化一致性检查脚本

创建 `scripts/check_consistency.py`：

```python
#!/usr/bin/env python3
"""文档一致性检查工具"""

import os
import re
from pathlib import Path

def extract_data_structures(doc_path):
    """从文档中提取数据结构定义"""
    structures = []
    pattern = r'class\s+(\w+).*:'

    for md_file in Path(doc_path).rglob('*.md'):
        content = md_file.read_text(encoding='utf-8')
        matches = re.findall(pattern, content)
        for match in matches:
            structures.append({
                'file': str(md_file),
                'class': match
            })

    return structures

def check_consistency(project_root):
    """检查文档一致性"""
    spec_path = project_root / 'doc' / '技术规范'
    design_path = project_root / 'doc' / '模块设计'

    # 提取规范和设计中的数据结构
    spec_structures = extract_data_structures(spec_path)
    design_structures = extract_data_structures(design_path)

    # 检查重复定义
    spec_classes = {s['class'] for s in spec_structures}
    design_classes = {s['class'] for s in design_structures}

    duplicates = spec_classes & design_classes

    if duplicates:
        print(f"⚠️  发现重复定义的数据结构：{duplicates}")
        print("   应在模块文档中引用规范，而非重复定义")
        return False

    print("✅ 文档一致性检查通过")
    return True

if __name__ == '__main__':
    import sys
    project_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    check_consistency(project_root)
```

**使用方法**：
```bash
python scripts/check_consistency.py .
```

## 版本历史生成

### 从 Git 提交生成版本历史

```bash
# 查看特定文件的提交历史
git log --oneline --since="2026-03-01" doc/模块设计/特征提取模块设计.md

# 格式化输出
git log --pretty=format:"| %h | %ad | %s |" --date=short doc/模块设计/*.md
```

### 自动更新版本历史脚本

创建 `scripts/update_version_history.py`：

```python
#!/usr/bin/env python3
"""从 Git 提交记录更新文档版本历史"""

import subprocess
from pathlib import Path
from datetime import datetime

def get_git_log(file_path):
    """获取文件的 Git 提交历史"""
    cmd = ['git', 'log', '--pretty=format:%ad|%s', '--date=short', str(file_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

    commits = []
    for line in result.stdout.strip().split('\n'):
        if line:
            date, message = line.split('|', 1)
            commits.append({'date': date, 'message': message})

    return commits

def update_version_history(md_file, commits):
    """更新 Markdown 文件的版本历史章节"""
    content = md_file.read_text(encoding='utf-8')

    # 生成版本历史表格
    version_table = "## 版本历史\n\n| 版本 | 日期 | 说明 |\n|------|------|------|\n"
    for i, commit in enumerate(commits, 1):
        version = f"v1.{len(commits) - i}"
        version_table += f"| {version} | {commit['date']} | {commit['message']} |\n"

    # 替换或追加版本历史
    if '## 版本历史' in content:
        # 替换现有版本历史
        parts = content.split('## 版本历史')
        content = parts[0] + version_table
    else:
        # 追加版本历史
        content += '\n\n' + version_table

    md_file.write_text(content, encoding='utf-8')

if __name__ == '__main__':
    import sys
    file_path = Path(sys.argv[1])
    commits = get_git_log(file_path)
    update_version_history(file_path, commits)
    print(f"✅ 已更新 {file_path} 的版本历史")
```

**使用方法**：
```bash
python scripts/update_version_history.py doc/模块设计/特征提取模块设计.md
```

## 临时文件管理

### 清理过期临时文件

```bash
# 清理超过7天的临时文件
find temp/ -mtime +7 -type f -delete

# 列出将要删除的文件（先预览）
find temp/ -mtime +7 -type f

# 清理空目录
find temp/ -type d -empty -delete
```

### 归档重要临时文件

```bash
# 将重要的临时文件迁移到正式目录
mv temp/reports/验证报告_20260302.md doc/报告/

# 带时间戳归档
tar -czf archive/temp_$(date +%Y%m%d).tar.gz temp/
rm -rf temp/*
```

### 自动清理脚本

创建 `scripts/cleanup_temp.sh`：

```bash
#!/bin/bash
# 临时文件自动清理脚本

TEMP_DIR="temp"
ARCHIVE_DIR="archive"
DAYS_TO_KEEP=7

echo "🧹 开始清理临时文件..."

# 创建归档目录
mkdir -p "$ARCHIVE_DIR"

# 归档重要文件（可选）
if [ -d "$TEMP_DIR/reports" ]; then
    echo "📦 归档报告文件..."
    cp -r "$TEMP_DIR/reports"/* doc/报告/ 2>/dev/null || true
fi

# 清理过期文件
echo "🗑️  删除超过 $DAYS_TO_KEEP 天的文件..."
find "$TEMP_DIR" -mtime +$DAYS_TO_KEEP -type f -delete

# 清理空目录
find "$TEMP_DIR" -type d -empty -delete

echo "✅ 清理完成"
```

**使用方法**：
```bash
chmod +x scripts/cleanup_temp.sh
./scripts/cleanup_temp.sh
```

## 文档索引生成

### 自动生成文档目录

```bash
# 生成所有 Markdown 文件的目录树
find doc/ -name "*.md" -type f | sort

# 生成带标题的文档索引
for file in $(find doc/ -name "*.md" -type f | sort); do
    title=$(grep "^# " "$file" | head -1 | sed 's/^# //')
    echo "- [$title]($file)"
done
```

### 自动更新 README 文档索引

创建 `scripts/update_readme_index.py`：

```python
#!/usr/bin/env python3
"""自动更新 README 中的文档索引"""

from pathlib import Path
import re

def extract_title(md_file):
    """提取 Markdown 文件的一级标题"""
    content = md_file.read_text(encoding='utf-8')
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    return match.group(1) if match else md_file.stem

def generate_index(doc_path):
    """生成文档索引"""
    index_lines = ["## 文档索引\n"]

    for category in ['系统设计', '技术规范', '模块设计', '测试验证', '报告']:
        category_path = doc_path / category
        if not category_path.exists():
            continue

        index_lines.append(f"\n### {category}\n")
        for md_file in sorted(category_path.glob('*.md')):
            title = extract_title(md_file)
            relative_path = md_file.relative_to(doc_path.parent)
            index_lines.append(f"- [{title}]({relative_path})\n")

    return ''.join(index_lines)

def update_readme(readme_path, doc_path):
    """更新 README 文件"""
    readme_content = readme_path.read_text(encoding='utf-8')
    new_index = generate_index(doc_path)

    # 替换文档索引部分
    pattern = r'## 文档索引.*?(?=\n## |$)'
    updated_content = re.sub(pattern, new_index, readme_content, flags=re.DOTALL)

    readme_path.write_text(updated_content, encoding='utf-8')

if __name__ == '__main__':
    project_root = Path('.')
    readme_path = project_root / 'README.md'
    doc_path = project_root / 'doc'

    update_readme(readme_path, doc_path)
    print("✅ 已更新 README 文档索引")
```

**使用方法**：
```bash
python scripts/update_readme_index.py
```

## 代码与文档同步检查

### 检查 TODO 注释

```bash
# 查找代码中的 TODO 注释
grep -rn "TODO\|FIXME\|XXX" src/

# 检查是否需要在文档中记录
```

### 检查文档中的代码示例

```bash
# 提取文档中的代码块
grep -A 10 '```python' doc/**/*.md

# 验证代码示例是否可执行（可选）
```

---

**文档版本**：v1.0
**最后更新**：2026-03-02
