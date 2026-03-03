# 运维指南

> 本文档提供文档管理、临时文件清理、归档等运维操作的详细指南

---

## 1. 临时文件管理

### 1.1 临时文件定义

**临时文件包括**：
- 调试脚本、测试数据、性能分析数据
- 草稿文档、实验性代码片段
- 中间产物、临时导出文件

**临时文件不包括**：
- 正式的设计文档（应在 `doc/` 目录）
- 正式的脚本工具（应在 `scripts/` 目录）
- 配置文件（应在项目根目录或 `config/` 目录）

### 1.2 强制要求

- ✅ 临时文件必须放在临时目录（如 `temp/`）
- ✅ 临时目录必须在 `.gitignore` 中排除
- ✅ 定期清理（建议每周），超过 7 天的临时文件应删除或归档

### 1.3 临时文件迁移流程

```
临时文件 → 评估 → 归档或删除
```

#### 流程1：草稿文档完成

```bash
# 1. 移动到对应正式目录
mv temp/drafts/用户认证.md doc/03-模块设计/用户认证模块.md

# 2. 补充完整的文档结构
# - 添加文档定位说明
# - 添加版本历史章节
# - 检查引用的数据结构和接口规范

# 3. 更新文档索引
# 在 doc/README.md 中添加新文档的链接
```

#### 流程2：临时验证报告

```bash
# 1. 重命名（加日期前缀）
mv temp/validation_report.md doc/05-报告/2026-03-02-验证报告.md

# 2. 补充报告结构
# - 添加执行摘要
# - 添加测试环境说明
# - 添加结论和建议

# 3. 更新相关设计文档
# 在相关模块设计文档中引用该报告
```

#### 流程3：临时脚本

```bash
# 1. 评估是否需要保留
# - 是否会重复使用？
# - 是否有通用价值？
# - 是否应该纳入版本管理？

# 2. 需要保留
mv temp/scripts/debug_tool.py scripts/tools/debug_tool.py
# 补充 README 和使用说明

# 3. 不需要保留
rm temp/scripts/one_time_debug.py
```

### 1.4 临时文件清理脚本

**手动清理**：
```bash
# 列出将要删除的文件（先预览）
find temp/ -mtime +7 -type f

# 删除超过7天的临时文件
find temp/ -mtime +7 -type f -delete

# 清理空目录
find temp/ -type d -empty -delete
```

**自动清理脚本**（`scripts/cleanup_temp.sh`）：

```bash
#!/bin/bash
# 临时文件自动清理脚本

TEMP_DIR="temp"
DAYS_TO_KEEP=7

echo "🧹 开始清理临时文件..."

# 删除过期文件
echo "🗑️  删除超过 $DAYS_TO_KEEP 天的文件..."
find "$TEMP_DIR" -mtime +$DAYS_TO_KEEP -type f -delete

# 清理空目录
find "$TEMP_DIR" -type d -empty -delete

echo "✅ 清理完成"
```

**定时任务（可选）**：

```bash
# 添加到 crontab，每周日凌晨2点执行
0 2 * * 0 /path/to/scripts/cleanup_temp.sh
```

---

## 2. 文档归档管理

### 2.1 归档条件

**满足以下任一条件即应归档**：
- 超过 6 个月未更新的非活跃文档
- 已废弃功能的设计文档
- 旧版本的规范文档（已被新版本替代）
- 历史实验报告（不再需要频繁参考）

**不应归档**：
- 正在使用的规范文档
- 仍在维护的模块设计文档
- 最新的测试计划

### 2.2 归档流程

#### 步骤1：添加归档标记

在文档顶部添加：

```markdown
> ⚠️ **本文档已归档**
> - 归档日期：2026-03-03
> - 归档原因：功能已废弃，被新功能替代
> - 替代文档：[新功能设计](../03-模块设计/新功能设计.md)
> - 如需查阅历史版本，请查看 [归档版本](../archive/2026-Q1/03-模块设计/旧功能.md)
```

#### 步骤2：移动到归档目录

```bash
# 保留原目录结构，按季度归档
mkdir -p doc/archive/2026-Q1/03-模块设计/
mv doc/03-模块设计/旧功能.md doc/archive/2026-Q1/03-模块设计/旧功能.md
```

#### 步骤3：创建跳转文件（可选）

在原文档位置创建跳转文件：

```bash
cat > doc/03-模块设计/旧功能.md << 'EOF'
# 旧功能设计

> ⚠️ **本文档已归档**
>
> 请查看 [归档版本](../archive/2026-Q1/03-模块设计/旧功能.md) 或 [替代文档](新功能设计.md)
EOF
```

### 2.3 归档目录结构

```
doc/
└── archive/
    ├── 2025-Q4/
    │   ├── 03-模块设计/
    │   │   ├── 旧认证模块.md
    │   │   └── 废弃功能.md
    │   └── 04-测试验证/
    │       └── 旧测试计划.md
    ├── 2026-Q1/
    │   └── 03-模块设计/
    │       └── 重构前设计.md
    └── README.md              ← 归档目录说明
```

**归档目录 README 示例**：

```markdown
# 归档文档

本目录存放已归档的历史文档。

## 目录结构

按季度归档，保留原目录结构。

## 查找文档

1. 根据时间定位季度目录
2. 根据文档类型定位子目录
3. 查看归档标记获取替代文档信息

## 清理策略

- 归档文档保留至少 1 年
- 每年清理一次，删除超过 2 年的归档文档
```

### 2.4 归档清理

**年度清理脚本**（`scripts/cleanup_archive.sh`）：

```bash
#!/bin/bash
# 归档文档年度清理脚本

ARCHIVE_DIR="doc/archive"
YEARS_TO_KEEP=2

echo "📚 开始清理归档文档..."

# 列出超过2年的归档目录
echo "将要删除的归档："
find "$ARCHIVE_DIR" -maxdepth 1 -type d -mtime +$((YEARS_TO_KEEP * 365))

# 确认删除
read -p "确认删除？(y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    find "$ARCHIVE_DIR" -maxdepth 1 -type d -mtime +$((YEARS_TO_KEEP * 365)) -exec rm -rf {} +
    echo "✅ 清理完成"
else
    echo "❌ 取消操作"
fi
```

---

## 3. 文档导航维护

### 3.1 文档导航入口

**强制要求**：文档根目录下必须有 `README.md` 作为导航入口。

### 3.2 导航文档模板

```markdown
# 项目文档导航

## 快速导航

### 📋 项目管理
- [项目计划与进展记录](项目计划与进展记录.md) - 唯一进展跟踪

### 🏗️ 系统设计
- [系统架构设计](01-系统设计/系统架构设计.md)
- [技术选型](01-系统设计/技术选型.md)

### 📐 技术规范
- [数据结构规范](02-技术规范/数据结构规范.md)
- [接口规范](02-技术规范/接口规范.md)
- [编码规范](02-技术规范/编码规范.md)

### 🔧 模块设计
- [用户认证模块](03-模块设计/用户认证模块.md)
- [数据处理模块](03-模块设计/数据处理模块.md)

### ✅ 测试验证
- [测试计划](04-测试验证/测试计划.md)
- [性能测试报告](04-测试验证/性能测试报告.md)

### 📊 报告
- [2026-03 里程碑1总结](05-报告/2026-03-里程碑1总结.md)

### 📚 归档
- [归档文档](archive/README.md)

## 文档规范

本项目遵循 [dev-workflow](../dev-workflow/SKILL.md) 规范。

## 新建文档

1. 确定文档层级（L1-L5）
2. 使用对应模板：[templates.md](../dev-workflow/references/templates.md)
3. 更新本导航文档

## 文档搜索

\```bash
# 按关键词搜索文档
grep -r "关键词" doc/

# 按文件名查找
find doc/ -name "*.md"
\```
```

### 3.3 自动更新导航脚本

**脚本**（`scripts/update_doc_index.py`）：

```python
#!/usr/bin/env python3
"""自动更新文档导航索引"""

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

    categories = {
        '01-系统设计': '🏗️ 系统设计',
        '02-技术规范': '📐 技术规范',
        '03-模块设计': '🔧 模块设计',
        '04-测试验证': '✅ 测试验证',
        '05-报告': '📊 报告'
    }

    for category_dir, category_name in categories.items():
        category_path = doc_path / category_dir
        if not category_path.exists():
            continue

        index_lines.append(f"\n### {category_name}\n")
        for md_file in sorted(category_path.glob('*.md')):
            title = extract_title(md_file)
            relative_path = md_file.relative_to(doc_path)
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
    readme_path = project_root / 'doc' / 'README.md'
    doc_path = project_root / 'doc'

    if readme_path.exists():
        update_readme(readme_path, doc_path)
        print("✅ 已更新文档导航索引")
    else:
        print("❌ 未找到 doc/README.md")
```

**使用方法**：

```bash
python scripts/update_doc_index.py
```

---

## 4. 版本历史维护

### 4.1 版本历史格式

```markdown
## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | YYYY-MM-DD | 初始版本 |
| v1.1 | YYYY-MM-DD | [变更类型] 变更描述。影响范围：XXX模块 |
```

**变更类型标签**：
- `[数据结构变更]` - 数据结构字段增删改
- `[接口变更]` - 接口签名变更
- `[算法变更]` - 核心算法修改
- `[参数变更]` - 参数调整
- `[文档修正]` - 文档错误修正
- `[架构变更]` - 架构调整

### 4.2 自动生成版本历史

**从 Git 提交生成**：

```bash
# 查看特定文件的提交历史
git log --oneline --since="2026-03-01" doc/03-模块设计/用户认证模块.md

# 格式化输出
git log --pretty=format:"| %h | %ad | %s |" --date=short doc/03-模块设计/*.md
```

**自动更新脚本**（`scripts/update_version_history.py`）：

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

---

## 5. 定期维护任务

### 5.1 每周任务

```bash
# 1. 清理临时文件
./scripts/cleanup_temp.sh

# 2. 检查文档一致性
python scripts/check_consistency.py

# 3. 更新文档索引
python scripts/update_doc_index.py

# 4. 更新项目进展记录
# 手动更新 doc/项目计划与进展记录.md
```

### 5.2 每月任务

```bash
# 1. 完整文档一致性审查
python scripts/check_consistency.py --full

# 2. 检查测试覆盖率
pytest --cov=src/ --cov-report=term-missing

# 3. 归档非活跃文档
# 手动识别并归档

# 4. 更新 README 状态
# 手动更新
```

### 5.3 每年任务

```bash
# 1. 清理归档文档
./scripts/cleanup_archive.sh

# 2. 文档全面审查
# - 检查所有文档的时效性
# - 更新过时的技术选型
# - 归档不再使用的文档

# 3. 规范更新
# - 根据项目经验更新 dev-workflow 规范
```

---

**文档版本**：v1.0
**最后更新**：2026-03-03
