# 故障排除

本文档提供知识库索引的常见问题和解决方案。

## 错误分类

### 1. 构建阶段错误

#### 1.1 路径不存在

**错误信息**:
```
错误: 指定的路径不存在: /path/to/knowledge-base
```

**原因**: 知识库路径错误或不可访问

**解决方案**:
1. 检查路径拼写是否正确
2. 确认路径是绝对路径或正确的相对路径
3. 检查文件夹权限
4. Windows 用户注意使用正确的路径格式（正斜杠或双反斜杠）

**预防措施**:
- 构建前验证路径存在性
- 使用文件浏览器复制准确路径

---

#### 1.2 无支持的文档

**错误信息**:
```
警告: 未找到支持的文档格式
支持的格式: .md, .pdf, .docx, .doc
```

**原因**: 知识库中没有支持的文档格式

**解决方案**:
1. 检查文件夹中是否有文档
2. 确认文档扩展名正确
3. 检查 `_index_config.yaml` 中的 `file_types` 配置
4. 移除过于严格的排除规则

**示例修复**:
```yaml
# 错误：排除了所有文件
exclude:
  - "*.md"  # ❌ 排除了所有 Markdown

# 正确：只排除特定文件
exclude:
  - "README.md"  # ✅ 只排除特定文件
```

---

#### 1.3 工具不可用

**错误信息**:
```
警告: 未检测到可用的文档转换工具
仅索引 Markdown 文档
```

**原因**: PDF/Word 转换工具未安装

**解决方案**:

**方案 1: 安装 doc2md skill**
```bash
git clone https://github.com/yourname/doc2md-skill ~/.claude/skills/doc2md
```

**方案 2: 安装 pandoc**
```bash
# Windows
choco install pandoc

# macOS
brew install pandoc

# Linux
sudo apt-get install pandoc
```

**方案 3: 安装 PyMuPDF**
```bash
pip install PyMuPDF
```

**降级处理**:
- 如果无法安装工具，仅索引 Markdown 文档
- 手动将 PDF/Word 转换为 Markdown 后再索引

---

### 2. 转换阶段错误

#### 2.1 文档转换失败

**错误信息**:
```
转换失败: 文档名.pdf
原因: [具体错误信息]
```

**常见原因和解决方案**:

| 原因 | 解决方案 |
|------|---------|
| 文件损坏 | 重新下载或导出文档 |
| 文件被锁定 | 关闭文档编辑器，重试 |
| 格式不支持 | 使用其他工具或手动转换 |
| 文件过大 | 分割文档或增加超时时间 |
| 编码错误 | 转换为 UTF-8 编码 |

**处理策略**:
```
检测到转换失败 → 跳过该文档 → 记录错误 → 继续处理其他文档
```

**手动修复**:
1. 使用其他工具手动转换（如在线转换网站）
2. 将转换后的 Markdown 保存到知识库
3. 重新运行索引构建

---

#### 2.2 转换超时

**错误信息**:
```
超时: 文档转换超过 30 秒
文件: large-document.pdf
```

**原因**: 文档过大或复杂

**解决方案**:

**方案 1: 增加超时时间**
```yaml
# _index_config.yaml
conversion:
  timeout_seconds: 60
```

**方案 2: 使用更快的工具**
```yaml
conversion:
  preferred_tool: "pymupdf"  # PyMuPDF 比 doc2md 快
```

**方案 3: 分割文档**
- 将大 PDF 分割为多个小文件
- 每个文件 < 10 MB

---

#### 2.3 转换内容为空

**错误信息**:
```
警告: 转换后内容为空或过短 (< 100 字符)
文件: scanned-document.pdf
```

**原因**:
- PDF 是扫描版，需要 OCR
- PDF 是图片形式
- 文档内容确实很少

**解决方案**:

**方案 1: 启用 OCR**
```yaml
conversion:
  pdf_ocr_enabled: true
  preferred_tool: "mineru"  # mineru 支持 OCR
```

**方案 2: 使用 OCR 工具预处理**
- 使用 Adobe Acrobat OCR
- 使用在线 OCR 服务
- 使用 mineru 或 Tesseract

**方案 3: 接受限制**
- 如果文档确实很短，调整最小长度验证
- 在索引中标注为"简短文档"

---

### 3. AI 摘要生成错误

#### 3.1 摘要生成失败

**错误信息**:
```
AI 摘要生成失败: [错误信息]
```

**常见原因**:
- AI API 调用失败
- 文档内容过长
- 网络问题

**解决方案**:

**方案 1: 使用文档前 N 字符作为摘要**
```python
# 自动降级
summary = document_content[:200] + "..."
```

**方案 2: 减少输入长度**
```yaml
summary:
  max_input_length: 5000  # 限制输入长度
```

**方案 3: 重试机制**
- 等待 5 秒后重试
- 最多重试 3 次
- 仍失败则使用降级方案

---

#### 3.2 摘要质量不佳

**问题**: 摘要过于笼统或缺少关键信息

**解决方案**:

**方案 1: 调整摘要长度**
```yaml
summary:
  max_length: 300  # 增加长度
  min_length: 100
```

**方案 2: 使用结构化提示词**
- 在 AI 提示词中明确要求结构化输出
- 要求按要点列出
- 指定包含哪些信息

**方案 3: 手动优化**
- 对重要文档手动编写摘要
- 更新索引中的摘要字段

---

### 4. 索引文件错误

#### 4.1 YAML 语法错误

**错误信息**:
```
YAML 解析错误: line 25, column 10
```

**常见错误**:

| 错误 | 示例 | 修正 |
|------|------|------|
| 缩进错误 | 使用了 Tab | 使用 2 空格缩进 |
| 引号不匹配 | `"summary` | `"summary"` |
| 特殊字符未转义 | `path: C:\Users` | `path: "C:\\Users"` |
| 列表格式错误 | `keywords: "a", "b"` | `keywords: ["a", "b"]` |

**修复步骤**:
1. 使用 YAML 验证工具检查语法
2. 修正错误行
3. 重新保存文件

**在线验证工具**:
- YAML Lint: http://www.yamllint.com/
- Online YAML Parser: https://yaml-online-parser.appspot.com/

---

#### 4.2 索引文件损坏

**错误信息**:
```
错误: 无法读取索引文件
```

**解决方案**:

**方案 1: 从备份恢复**
```bash
# 如果有备份
cp _index.yaml.backup _index.yaml
```

**方案 2: 重建索引**
```
用户: 重建「知识库」索引
```

**预防措施**:
- 定期备份索引文件
- 增量更新前创建备份
- 使用版本控制（如 git）

---

#### 4.3 字段缺失

**错误信息**:
```
验证失败: 文档 5 缺少必填字段 'summary'
```

**解决方案**:

**方案 1: 手动补充字段**
```yaml
# 打开 _index.yaml，补充缺失字段
- path: "文档.md"
  filename: "文档.md"
  type: "markdown"
  summary: "手动添加的摘要"  # 补充此字段
  keywords: ["关键词"]
```

**方案 2: 重新生成**
- 删除有问题的文档条目
- 重新运行索引更新

---

### 5. 增量更新错误

#### 5.1 变更检测不准确

**问题**: 文档未修改但被标记为已修改

**原因**:
- mtime 方法受文件系统操作影响
- 文件复制或移动改变了 mtime

**解决方案**:

**方案 1: 使用 hash 方法**
```yaml
update_detection:
  method: "hash"  # 更精确但较慢
```

**方案 2: 混合方法**
```yaml
update_detection:
  method: "mtime"  # 初筛
  verify_with_hash: true  # 用 hash 精确验证
```

---

#### 5.2 合并冲突

**错误信息**:
```
合并失败: 文档数量不一致
预期: 15, 实际: 12
```

**原因**: 索引更新过程中断或出错

**解决方案**:

**方案 1: 回滚到旧索引**
```bash
# 恢复备份
cp _index.yaml.backup _index.yaml
```

**方案 2: 重建索引**
```
用户: 重建「知识库」索引
```

**预防措施**:
- 增量更新前自动创建备份
- 使用原子写入（先写临时文件，再重命名）

---

### 6. 智能检索错误

#### 6.1 索引文件不存在

**错误信息**:
```
错误: 知识库未建立索引
请先运行: 为「知识库名」建立索引
```

**解决方案**:
```
用户: 为「知识库名」建立索引
```

---

#### 6.2 检索结果不相关

**问题**: 返回的文档与查询不相关

**原因**:
- 关键词提取不准确
- 摘要质量不佳
- 索引过期

**解决方案**:

**方案 1: 更新索引**
```
用户: 更新「知识库名」的索引
```

**方案 2: 优化关键词**
- 手动编辑索引中的关键词字段
- 添加更具体的关键词

**方案 3: 使用更具体的查询**
```
❌ "Git"
✅ "GitLab CI/CD 流水线配置"
```

---

#### 6.3 索引过期

**警告信息**:
```
警告: 索引已过期（最后更新: 30 天前）
建议更新索引以获得最新结果
```

**解决方案**:
```
用户: 更新「知识库名」的索引
```

**预防措施**:
```yaml
# 在 _index_config.yaml 中配置
update_detection:
  auto_check: true
  check_interval_hours: 168  # 每周检查一次
```

---

## 性能问题

### 7.1 构建速度慢

**问题**: 大型知识库构建时间过长

**解决方案**:

**方案 1: 优化批处理**
```yaml
performance:
  batch_size: 100  # 增加批处理大小
  parallel_workers: 8  # 增加并行数
```

**方案 2: 使用快速工具**
```yaml
conversion:
  preferred_tool: "pymupdf"  # 比 doc2md 快
```

**方案 3: 减少摘要长度**
```yaml
summary:
  max_length: 200  # 减少摘要长度
```

---

### 7.2 内存占用高

**问题**: 构建过程内存占用过高

**解决方案**:

**方案 1: 减少批处理大小**
```yaml
performance:
  batch_size: 20  # 减小批处理
```

**方案 2: 禁用缓存**
```yaml
performance:
  enable_cache: false
```

**方案 3: 分批构建**
- 将知识库分为多个子目录
- 分别构建索引
- 手动合并索引文件

---

## 恢复机制

### 8.1 索引备份

**自动备份**:
- 每次更新前自动创建备份
- 备份文件名: `_index.yaml.backup`
- 保留最近 3 个备份

**手动备份**:
```bash
cp _index.yaml _index.yaml.backup.$(date +%Y%m%d)
```

---

### 8.2 错误日志

**日志位置**: `_index_errors.log`

**日志格式**:
```
[2026-03-03 16:00:00] ERROR: 转换失败 - document.pdf
[2026-03-03 16:00:05] WARNING: 摘要过短 - short-doc.md
[2026-03-03 16:00:10] INFO: 索引构建完成 - 15/16 成功
```

---

### 8.3 完全重建

**触发条件**:
- 索引文件损坏无法修复
- 大量错误无法增量修复

**重建步骤**:
```bash
# 1. 备份旧索引
mv _index.yaml _index.yaml.old

# 2. 删除旧索引
rm _index.yaml

# 3. 重新构建
用户: 为「知识库」建立索引
```

---

## 调试技巧

### 9.1 详细日志

**启用调试模式**:
```yaml
advanced:
  debug_mode: true
  log_level: "debug"
```

**输出示例**:
```
[DEBUG] 扫描文件夹: /path/to/kb
[DEBUG] 找到文件: doc1.md
[DEBUG] 转换工具: doc2md
[DEBUG] 转换中: doc1.pdf
[DEBUG] 转换成功: 1234 字符
[DEBUG] 生成摘要...
[DEBUG] 摘要长度: 180 字符
```

---

### 9.2 单文档测试

**测试单个文档转换**:
```python
# 使用 Python 测试
from tools import convert_document

result = convert_document("test.pdf", available_tools)
print(result)
```

---

### 9.3 验证脚本

**运行验证**:
```python
python validate_index.py _index.yaml
```

**输出**:
```
✓ YAML 语法正确
✓ 字段完整
✓ 统计一致
✓ 时间格式正确

总体评分: A
```

---

## 获取帮助

### 10.1 检查清单

遇到问题时，按以下顺序检查:

- [ ] 路径是否正确
- [ ] 文档格式是否支持
- [ ] 工具是否安装
- [ ] 配置文件语法是否正确
- [ ] 磁盘空间是否充足
- [ ] 文件权限是否正确
- [ ] 网络连接是否正常（AI 摘要需要）

### 10.2 常用诊断命令

```bash
# 检查文件是否存在
ls -la /path/to/kb

# 检查文件权限
stat /path/to/kb

# 检查磁盘空间
df -h

# 检查工具可用性
which pandoc
python -c "import fitz; print('PyMuPDF OK')"
```

### 10.3 报告问题

提供以下信息以帮助诊断:

1. 错误信息完整输出
2. 知识库大小和文档数量
3. 配置文件内容
4. 工具检测结果
5. 操作系统版本

---

## 相关资源

- 检查清单: `references/execution/checklist.md`
- 工具支持: `references/execution/tools.md`
- 质量门禁: `references/core/quality-gates.md`
