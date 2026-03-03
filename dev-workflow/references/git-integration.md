# Git 工作流集成

> 本文档说明 AI 如何与 Git 工作流集成，确保提交符合规范

---

## 1. 提交前检查

### 1.1 自动检查脚本
AI 在帮助用户提交代码前，应该执行以下检查：

```python
def 提交前检查():
    """Git 提交前的自动化检查"""

    检查结果 = []
    变更的文件 = git_status()

    # 检查 1: 代码与文档一致性
    代码变更 = [f for f in 变更的文件 if f.startswith("src/")]
    文档变更 = [f for f in 变更的文件 if f.startswith("doc/")]

    if 代码变更 and not 文档变更:
        # 检查代码变更是否涉及接口/数据结构
        for 代码文件 in 代码变更:
            变更内容 = git_diff(代码文件)
            if 涉及接口或数据结构(变更内容):
                检查结果.append({
                    "类型": "❌ 代码文档不一致",
                    "说明": f"{代码文件} 已修改但文档未更新",
                    "建议": "先更新相关文档再提交"
                })

    # 检查 2: 临时文件
    临时文件 = [f for f in 变更的文件 if f.startswith("temp/")]
    if 临时文件:
        检查结果.append({
            "类型": "⚠️  临时文件提交",
            "说明": f"检测到临时文件：{', '.join(临时文件)}",
            "建议": "将临时文件移到正式目录或添加到 .gitignore"
        })

    # 检查 3: 版本历史
    if 文档变更:
        for doc in 文档变更:
            if not 文档包含版本历史更新:
                检查结果.append({
                    "类型": "⚠️  缺少版本历史",
                    "说明": f"{doc} 未更新版本历史",
                    "建议": "在版本历史中追加变更记录"
                })

    # 输出结果
    return 检查结果
```

### 1.2 检查流程
```
用户请求提交代码
  ↓
AI 执行提交前检查
  ├─ 通过 ──→ 执行提交
  └─ 不通过 ──→ 输出问题清单 → 建议修复 → 重新检查
```

---

## 2. 提交信息规范

### 2.1 提交信息格式
AI 应该建议用户使用规范的提交信息格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 2.2 提交类型
| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(auth): 实现基于 JWT 的用户认证` |
| `fix` | Bug 修复 | `fix(api): 修复 token 过期未抛出异常的问题` |
| `docs` | 文档变更 | `docs(spec): 更新数据结构规范，添加 CacheConfig` |
| `refactor` | 重构（不改变接口） | `refactor(log): 优化日志分析算法` |
| `test` | 测试相关 | `test(auth): 添加用户认证单元测试` |
| `chore` | 构建/工具相关 | `chore: 更新依赖版本` |

### 2.3 提交信息示例

#### 示例 1：新功能
```
feat(auth): 实现基于 JWT 的用户认证

- 新增用户认证模块设计文档
- 实现 authenticate 和 verify_token 接口
- 单元测试覆盖率 85%

Closes #123
```

#### 示例 2：数据结构变更
```
feat(spec)!: 在 UserAuthInput 中添加 email 字段

BREAKING CHANGE: UserAuthInput 数据结构新增 email 必填字段
影响范围：
- 用户认证模块：已更新
- 用户管理模块：已更新
- 权限验证模块：已更新

建议所有调用方在升级后补充 email 字段
```

#### 示例 3：文档更新
```
docs(design): 更新日志分析模块设计文档

- 补充"核心算法"章节
- 添加性能测试结果
- 更新版本历史至 v1.1
```

### 2.4 AI 生成提交信息
当用户要求提交时，AI 应该自动生成规范的提交信息：

```python
def 生成提交信息(变更内容):
    """根据变更内容生成规范的提交信息"""

    # 分析变更类型
    变更类型 = 分析变更类型(变更内容)

    # 分析影响范围
    影响范围 = 分析影响范围(变更内容)

    # 生成提交信息
    if 变更类型 == "新功能":
        类型 = "feat"
        主题 = 提取功能名称(变更内容)
    elif 变更类型 == "Bug修复":
        类型 = "fix"
        主题 = 提取Bug描述(变更内容)
    elif 变更类型 == "文档更新":
        类型 = "docs"
        主题 = 提取文档名称(变更内容)
    elif 变更类型 == "重构":
        类型 = "refactor"
        主题 = 提取重构内容(变更内容)
    else:
        类型 = "chore"
        主题 = "更新"

    # 生成详细说明
    详细说明 = 生成详细说明(变更内容)

    # 组装提交信息
    提交信息 = f"{类型}({影响范围}): {主题}\n\n{详细说明}"

    return 提交信息
```

---

## 3. Pre-commit Hook

### 3.1 Hook 脚本
建议用户创建 `.git/hooks/pre-commit` 脚本：

```bash
#!/bin/bash
# Git pre-commit hook - 检查文档与代码一致性

echo "🔍 执行提交前检查..."

# 获取待提交的文件
STAGED_FILES=$(git diff --cached --name-only)

# 检查 1: 代码变更是否有文档变更
CODE_CHANGED=$(echo "$STAGED_FILES" | grep -c "^src/")
DOCS_CHANGED=$(echo "$STAGED_FILES" | grep -c "^doc/")

if [ "$CODE_CHANGED" -gt 0 ] && [ "$DOCS_CHANGED" -eq 0 ]; then
    # 检查是否涉及接口/数据结构
    for FILE in $STAGED_FILES; do
        if [[ $FILE == src/* ]]; then
            # 简单检查：是否包含 class 或 def 关键字
            if git diff --cached "$FILE" | grep -q "^\+.*\(class\|def\)"; then
                echo "⚠️  检测到代码变更但文档未更新"
                echo "   文件: $FILE"
                echo "   建议: 如果涉及接口或数据结构变更，请先更新文档"
                read -p "是否继续提交？(y/N) " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    exit 1
                fi
            fi
        fi
    done
fi

# 检查 2: 临时文件
TEMP_FILES=$(echo "$STAGED_FILES" | grep "^temp/")
if [ -n "$TEMP_FILES" ]; then
    echo "⚠️  检测到临时文件提交："
    echo "$TEMP_FILES"
    read -p "是否继续提交？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查 3: 提交信息格式
COMMIT_MSG_FILE=$1
if [ -f "$COMMIT_MSG_FILE" ]; then
    COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")
    # 检查是否符合格式：<type>(<scope>): <subject>
    if ! echo "$COMMIT_MSG" | grep -qE "^(feat|fix|docs|refactor|test|chore)(\(.+\))?: .+"; then
        echo "⚠️  提交信息格式不规范"
        echo "   建议格式: <type>(<scope>): <subject>"
        echo "   示例: feat(auth): 实现用户认证功能"
        read -p "是否继续提交？(y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

echo "✅ 检查通过"
exit 0
```

### 3.2 安装 Hook
```bash
# 创建 hook 脚本
cat > .git/hooks/pre-commit << 'EOF'
[粘贴上面的脚本内容]
EOF

# 添加执行权限
chmod +x .git/hooks/pre-commit
```

---

## 4. 分支管理

### 4.1 分支命名规范
| 分支类型 | 命名格式 | 示例 |
|---------|---------|------|
| 功能分支 | `feat/<功能名>` | `feat/user-auth` |
| 修复分支 | `fix/<Bug-ID>` | `fix/issue-123` |
| 文档分支 | `docs/<文档名>` | `docs/api-spec` |
| 重构分支 | `refactor/<模块名>` | `refactor/log-analyzer` |

### 4.2 分支工作流
```
main (主分支)
  ↓
创建功能分支 (feat/xxx)
  ↓
开发 + 文档 + 测试
  ↓
提交前检查 (pre-commit hook)
  ↓
提交代码 (规范的提交信息)
  ↓
推送分支
  ↓
创建 Pull Request
  ↓
代码审查
  ↓
合并到 main
```

### 4.3 AI 在分支管理中的角色
AI 应该：
1. **建议分支名称**：根据任务类型建议合适的分支名
2. **检查分支状态**：提醒用户当前分支和未提交的变更
3. **提示合并风险**：提醒用户可能冲突的文件

```python
def 创建功能分支(功能名称):
    """建议用户创建功能分支"""

    # 检查当前分支
    当前分支 = git_current_branch()
    if 当前分支 != "main":
        print(f"⚠️  当前在分支：{当前分支}")
        print("   建议：从 main 分支创建新功能分支")

    # 建议分支名称
    分支名称 = f"feat/{功能名称}"
    print(f"建议分支名称：{分支名称}")

    # 检查未提交的变更
    未提交 = git_status()
    if 未提交:
        print("⚠️  有未提交的变更：")
        for 文件 in 未提交:
            print(f"  - {文件}")
        print("   建议：先提交或暂存变更")

    # 生成命令
    命令 = f"git checkout -b {分支名称}"
    print(f"\n创建分支命令：\n  {命令}")

    return 分支名称
```

---

## 5. Pull Request 规范

### 5.1 PR 模板
AI 应该建议用户使用 PR 模板：

```markdown
## 变更类型
- [ ] 新功能 (feat)
- [ ] Bug 修复 (fix)
- [ ] 文档更新 (docs)
- [ ] 重构 (refactor)
- [ ] 测试 (test)

## 变更说明
<!-- 简要描述本次变更的内容和原因 -->

## 影响范围
<!-- 列出受影响的模块、接口、数据结构 -->

- 模块：
- 接口：
- 数据结构：

## 文档更新
- [ ] 已更新相关设计文档
- [ ] 已更新数据结构规范（如涉及）
- [ ] 已更新接口规范（如涉及）
- [ ] 已更新版本历史

## 测试
- [ ] 单元测试通过
- [ ] 集成测试通过（如涉及）
- [ ] 测试覆盖率：XX%

## 检查清单
- [ ] 代码与文档一致
- [ ] 无临时文件提交
- [ ] 提交信息规范
- [ ] 版本历史已更新

## 相关 Issue
<!-- 关联的 Issue 编号 -->
Closes #
```

### 5.2 AI 生成 PR 描述
```python
def 生成PR描述(分支变更):
    """根据分支变更生成 PR 描述"""

    # 分析变更
    变更类型 = 分析变更类型(分支变更)
    影响范围 = 分析影响范围(分支变更)
    文档更新 = 分析文档更新(分支变更)

    # 生成 PR 描述
    描述 = f"""
## 变更类型
- {'✅' if 变更类型 == 'feat' else ' '} 新功能 (feat)
- {'✅' if 变更类型 == 'fix' else ' '} Bug 修复 (fix)
- {'✅' if 变更类型 == 'docs' else ' '} 文档更新 (docs)
- {'✅' if 变更类型 == 'refactor' else ' '} 重构 (refactor)

## 变更说明
{提取变更说明(分支变更)}

## 影响范围
- 模块：{影响范围['模块']}
- 接口：{影响范围['接口']}
- 数据结构：{影响范围['数据结构']}

## 文档更新
{生成文档更新清单(文档更新)}

## 测试
- [ ] 单元测试通过
- [ ] 测试覆盖率：待补充

## 检查清单
- [x] 代码与文档一致
- [x] 无临时文件提交
- [x] 提交信息规范
- [x] 版本历史已更新
"""

    return 描述
```

---

## 6. AI 与 Git 集成最佳实践

### 6.1 应该做的
✅ **在提交前主动检查**
- 代码与文档一致性
- 临时文件位置
- 版本历史更新

✅ **生成规范的提交信息**
- 符合格式要求
- 包含影响范围
- 说明变更原因

✅ **建议分支管理策略**
- 合适的分支名称
- 从正确的基础分支创建
- 提醒未提交的变更

✅ **帮助生成 PR 描述**
- 自动分析变更类型
- 列出影响范围
- 生成检查清单

### 6.2 不应该做的
❌ **不要跳过检查直接提交**
- 即使是"小修改"也要检查
- 用户坚持时可以警告但不拒绝

❌ **不要强制使用规范**
- 用户可能有自己的工作流
- 提供建议但尊重用户选择

❌ **不要忽略用户的 Git 配置**
- 用户可能有自己的 hook
- 用户可能使用不同的工作流

❌ **不要自动执行 Git 命令**
- 除非用户明确要求
- 提供命令让用户自己执行

---

## 7. 快速参考表
| 场景 | AI 应该做什么 | 不应该做什么 |
|------|--------------|-------------|
| 用户请求提交 | 执行提交前检查 → 生成提交信息 | 直接执行 git commit |
| 检测到代码变更 | 检查文档是否需要更新 | 强制要求更新文档 |
| 检测到临时文件 | 警告并建议移除 | 自动删除文件 |
| 用户创建分支 | 建议分支名称和命令 | 自动执行 git checkout |
| 用户创建 PR | 生成 PR 描述模板 | 自动创建 PR |
| 用户拒绝规范 | 提供建议但尊重选择 | 强制执行规范 |

---

**文档版本**：v1.0
**最后更新**：2026-03-03
