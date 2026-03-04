# 层级管理实现指南

> **版本**: 2.1
> **最后更新**: 2026-03-04

## 快速实现

### 核心算法

```python
import os
import yaml
from pathlib import Path
from typing import Optional, List, Dict

class KnowledgeBaseManager:
    """知识库管理器"""

    def __init__(self, registry_path: str = None):
        self.registry_path = registry_path or self.get_default_registry_path()
        self.registry = self.load_registry()

    @staticmethod
    def get_default_registry_path() -> str:
        """获取默认注册表路径（位于 skill 目录内）"""
        from pathlib import Path

        # 注册表位于 skill 的 data 目录
        # 假设此脚本在 scripts/ 目录下
        skill_dir = Path(__file__).parent.parent
        return str(skill_dir / "data" / "registry.yaml")

    def load_registry(self) -> Dict:
        """加载注册表"""
        if not os.path.exists(self.registry_path):
            return {"version": "1.0", "knowledge_bases": []}

        with open(self.registry_path, encoding='utf-8') as f:
            return yaml.safe_load(f)

    def save_registry(self):
        """保存注册表"""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.registry, f, allow_unicode=True, default_flow_style=False)

    # ========== 核心方法 ==========

    def build_index(self, kb_path: str, force: bool = False):
        """
        构建索引（自动处理层级提升）

        Args:
            kb_path: 知识库路径
            force: 是否强制创建（忽略父索引）
        """
        kb_path = os.path.abspath(kb_path)

        # Step 1: 检测索引层级
        parent_index = self.find_parent_index(kb_path)
        current_index = self.has_index(kb_path)
        child_indexes = self.find_child_indexes(kb_path)

        # Step 2: 决策树
        if parent_index and not force:
            # 父文件夹有索引
            if current_index:
                # 场景 4, 8: 当前也有索引 → 层级提升
                return self.promote_to_parent(kb_path, parent_index)
            else:
                # 场景 3, 7: 当前无索引 → 建议更新父索引
                return self.suggest_update_parent(kb_path, parent_index)
        else:
            # 父文件夹无索引
            if child_indexes:
                # 场景 5, 6: 子文件夹有索引 → 删除子索引，提升至当前
                return self.promote_to_current(kb_path, child_indexes)
            else:
                # 场景 1, 2: 正常创建或更新
                if current_index:
                    return self.update_index(kb_path)  # 场景 2
                else:
                    return self.create_index(kb_path)  # 场景 1

    # ========== 检测方法 ==========

    def find_parent_index(self, kb_path: str) -> Optional[str]:
        """
        向上查找父知识库索引

        Returns:
            父索引路径，如果不存在则返回 None
        """
        current_path = Path(kb_path).parent

        while current_path and current_path != current_path.parent:
            index_path = current_path / "_index.yaml"
            if index_path.exists():
                return str(index_path)

            current_path = current_path.parent

        return None

    def has_index(self, kb_path: str) -> bool:
        """检查当前文件夹是否有索引"""
        index_path = os.path.join(kb_path, "_index.yaml")
        return os.path.exists(index_path)

    def find_child_indexes(self, kb_path: str) -> List[str]:
        """
        向下查找所有子知识库索引

        Returns:
            子索引路径列表
        """
        child_indexes = []

        for root, dirs, files in os.walk(kb_path):
            # 跳过隐藏文件夹
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            if "_index.yaml" in files:
                index_path = os.path.join(root, "_index.yaml")
                # 排除当前文件夹的索引
                if index_path != os.path.join(kb_path, "_index.yaml"):
                    child_indexes.append(index_path)

        return child_indexes

    # ========== 层级提升方法 ==========

    def promote_to_parent(self, current_path: str, parent_index_path: str):
        """
        提升至父级别索引

        场景 4, 8: 当前有索引，父也有索引
        """
        print(f"⚠️ 检测到父子索引冲突")
        print(f"  - 父索引: {parent_index_path}")
        print(f"  - 当前索引: {os.path.join(current_path, '_index.yaml')}")

        # 1. 查找所有子索引
        child_indexes = self.find_child_indexes(current_path)

        # 2. 备份索引
        print("\n执行层级提升：")
        print("  [1/4] 备份索引...")
        self.backup_index(current_path)
        for child_index in child_indexes:
            self.backup_index(child_index)

        # 3. 删除当前和子索引
        print("  [2/4] 删除下级索引...")
        self.delete_index(current_path)
        self.unregister_knowledge_base(current_path)

        for child_index in child_indexes:
            child_path = os.path.dirname(child_index)
            self.delete_index(child_path)
            self.unregister_knowledge_base(child_path)

        # 4. 更新父索引
        print("  [3/4] 更新父索引...")
        parent_path = os.path.dirname(parent_index_path)
        self.update_index(parent_path)

        # 5. 验证
        print("  [4/4] 验证索引...")
        self.validate_index(parent_path)

        print(f"\n✓ 层级提升完成")
        print(f"  - 已删除: {1 + len(child_indexes)} 个下级索引")
        print(f"  - 已更新: {parent_index_path}")

    def promote_to_current(self, current_path: str, child_indexes: List[str]):
        """
        提升至当前级别，删除子索引

        场景 5, 6: 子文件夹有索引
        """
        print(f"⚠️ 检测到子文件夹有索引")
        print(f"  - 子索引数量: {len(child_indexes)}")

        # 1. 备份
        print("\n执行层级提升：")
        print("  [1/3] 备份子索引...")
        for child_index in child_indexes:
            self.backup_index(os.path.dirname(child_index))

        # 2. 删除子索引
        print("  [2/3] 删除子索引...")
        for child_index in child_indexes:
            child_path = os.path.dirname(child_index)
            self.delete_index(child_path)
            self.unregister_knowledge_base(child_path)

        # 3. 创建或更新当前索引
        print("  [3/3] 创建/更新当前索引...")
        if self.has_index(current_path):
            self.update_index(current_path)
        else:
            self.create_index(current_path)

        print(f"\n✓ 层级提升完成")
        print(f"  - 已删除: {len(child_indexes)} 个子索引")
        print(f"  - 当前索引: {os.path.join(current_path, '_index.yaml')}")

    def suggest_update_parent(self, current_path: str, parent_index_path: str):
        """
        建议更新父索引

        场景 3, 7: 当前无索引，父有索引
        """
        print(f"⚠️ 检测到父文件夹已有索引")
        print(f"  - 父索引: {parent_index_path}")
        print(f"  - 当前文件夹已包含在父索引中")

        print("\n建议操作：")
        print("  1. 更新父索引（推荐）")
        print("  2. 强制在当前文件夹创建独立索引（不推荐）")

        choice = input("\n请选择 (1/2): ").strip()

        if choice == "1":
            parent_path = os.path.dirname(parent_index_path)
            self.update_index(parent_path)
            print(f"\n✓ 已更新父索引")
        else:
            print("\n⚠️ 警告: 将在子级别创建独立索引")
            print("  这将导致文档重复索引")
            confirm = input("是否继续？(y/N): ").strip().lower()
            if confirm == 'y':
                self.create_index(current_path, force=True)
                print("\n✓ 已创建索引（子级别）")
                print("  建议: 在父索引的 _index_config.yaml 中排除此文件夹")

    # ========== 基础操作方法 ==========

    def create_index(self, kb_path: str, force: bool = False):
        """创建索引"""
        index_path = os.path.join(kb_path, "_index.yaml")

        if os.path.exists(index_path) and not force:
            raise Exception(f"索引已存在: {index_path}")

        # 扫描文档
        documents = self.scan_documents(kb_path)

        # 生成索引内容
        index_data = {
            "version": "1.0",
            "knowledge_base": {
                "name": os.path.basename(kb_path),
                "path": kb_path,
                "created": self.get_timestamp(),
                "last_updated": self.get_timestamp(),
                "total_documents": len(documents),
                "total_size_mb": sum(doc['size'] for doc in documents) / (1024 * 1024)
            },
            "documents": documents
        }

        # 写入文件
        with open(index_path, 'w', encoding='utf-8') as f:
            yaml.dump(index_data, f, allow_unicode=True, default_flow_style=False)

        # 注册到全局注册表
        self.register_knowledge_base(kb_path, index_path, index_data)

        print(f"✓ 索引创建完成: {index_path}")

    def update_index(self, kb_path: str):
        """更新索引（增量）"""
        index_path = os.path.join(kb_path, "_index.yaml")

        if not os.path.exists(index_path):
            raise Exception(f"索引不存在: {index_path}")

        # 读取现有索引
        with open(index_path, encoding='utf-8') as f:
            old_index = yaml.safe_load(f)

        # 检测变更
        current_docs = self.scan_documents(kb_path)
        old_docs = {doc['path']: doc for doc in old_index['documents']}

        changes = {"added": [], "modified": [], "deleted": []}

        # 检测新增和修改
        for doc in current_docs:
            if doc['path'] not in old_docs:
                changes["added"].append(doc)
            elif doc['modified'] > old_docs[doc['path']]['modified']:
                changes["modified"].append(doc)

        # 检测删除
        for doc_path in old_docs:
            if not any(doc['path'] == doc_path for doc in current_docs):
                changes["deleted"].append(doc_path)

        # 更新索引
        old_index['documents'] = current_docs
        old_index['knowledge_base']['last_updated'] = self.get_timestamp()
        old_index['knowledge_base']['total_documents'] = len(current_docs)

        # 写入
        with open(index_path, 'w', encoding='utf-8') as f:
            yaml.dump(old_index, f, allow_unicode=True, default_flow_style=False)

        # 更新注册表
        self.update_registry_entry(kb_path, {
            "document_count": len(current_docs),
            "last_updated": self.get_timestamp()
        })

        print(f"✓ 索引更新完成: {index_path}")
        print(f"  - 新增: {len(changes['added'])} 个")
        print(f"  - 修改: {len(changes['modified'])} 个")
        print(f"  - 删除: {len(changes['deleted'])} 个")

    def delete_index(self, kb_path: str):
        """删除索引"""
        index_path = os.path.join(kb_path, "_index.yaml")

        if os.path.exists(index_path):
            os.remove(index_path)
            print(f"✓ 已删除索引: {index_path}")

    # ========== 注册表操作 ==========

    def register_knowledge_base(self, kb_path: str, index_path: str, index_data: Dict):
        """注册知识库到全局注册表"""
        entry = {
            "name": index_data["knowledge_base"]["name"],
            "path": kb_path,
            "index_path": index_path,
            "created": index_data["knowledge_base"]["created"],
            "last_updated": index_data["knowledge_base"]["last_updated"],
            "document_count": index_data["knowledge_base"]["total_documents"],
            "total_size_mb": index_data["knowledge_base"]["total_size_mb"],
            "status": "active"
        }

        # 检测层级
        parent_kb = self.find_parent_kb_in_registry(kb_path)
        child_kbs = self.find_child_kbs_in_registry(kb_path)

        entry["hierarchy"] = {
            "parent": parent_kb["path"] if parent_kb else None,
            "depth": self.calculate_depth(kb_path, parent_kb),
            "children": [child["path"] for child in child_kbs]
        }

        self.registry["knowledge_bases"].append(entry)
        self.registry["last_updated"] = self.get_timestamp()
        self.save_registry()

        print(f"✓ 已注册到全局目录: {kb_path}")

    def unregister_knowledge_base(self, kb_path: str):
        """从注册表移除知识库"""
        before_count = len(self.registry["knowledge_bases"])

        self.registry["knowledge_bases"] = [
            kb for kb in self.registry["knowledge_bases"]
            if kb["path"] != kb_path
        ]

        after_count = len(self.registry["knowledge_bases"])

        if before_count != after_count:
            self.registry["last_updated"] = self.get_timestamp()
            self.save_registry()
            print(f"✓ 已从注册表移除: {kb_path}")

    def update_registry_entry(self, kb_path: str, updates: Dict):
        """更新注册表条目"""
        for kb in self.registry["knowledge_bases"]:
            if kb["path"] == kb_path:
                kb.update(updates)
                break

        self.registry["last_updated"] = self.get_timestamp()
        self.save_registry()

    def find_parent_kb_in_registry(self, kb_path: str) -> Optional[Dict]:
        """在注册表中查找父知识库"""
        for kb in self.registry["knowledge_bases"]:
            if kb["status"] != "active":
                continue

            # 检查是否是父路径
            if kb_path.startswith(kb["path"] + os.sep):
                return kb

        return None

    def find_child_kbs_in_registry(self, kb_path: str) -> List[Dict]:
        """在注册表中查找子知识库"""
        children = []

        for kb in self.registry["knowledge_bases"]:
            if kb["status"] != "active":
                continue

            if kb["path"].startswith(kb_path + os.sep):
                children.append(kb)

        return children

    # ========== 工具方法 ==========

    def scan_documents(self, kb_path: str) -> List[Dict]:
        """扫描文档"""
        documents = []

        for root, dirs, files in os.walk(kb_path):
            # 跳过隐藏文件夹和特殊文件夹
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['.git', '.obsidian']]

            for file in files:
                if file in ['_index.yaml', '_index_config.yaml']:
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, kb_path)

                # 获取文件信息
                stat = os.stat(file_path)

                documents.append({
                    "path": rel_path.replace(os.sep, '/'),  # 使用正斜杠
                    "filename": file,
                    "type": self.get_file_type(file),
                    "modified": self.get_file_modified(stat),
                    "size": stat.st_size
                })

        return documents

    def backup_index(self, kb_path: str):
        """备份索引"""
        index_path = os.path.join(kb_path, "_index.yaml")

        if not os.path.exists(index_path):
            return

        backup_dir = os.path.join(kb_path, ".knowledge-index", "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = self.get_timestamp().replace(":", "-").replace(".", "-")
        backup_path = os.path.join(backup_dir, f"_index_{timestamp}.yaml")

        import shutil
        shutil.copy(index_path, backup_path)

    def validate_index(self, kb_path: str):
        """验证索引"""
        index_path = os.path.join(kb_path, "_index.yaml")

        if not os.path.exists(index_path):
            raise Exception(f"索引文件不存在: {index_path}")

        with open(index_path, encoding='utf-8') as f:
            index_data = yaml.safe_load(f)

        # 验证必填字段
        required_fields = ["version", "knowledge_base", "documents"]
        for field in required_fields:
            if field not in index_data:
                raise Exception(f"索引缺少必填字段: {field}")

        print("  ✓ 索引验证通过")

    @staticmethod
    def get_file_type(filename: str) -> str:
        """获取文件类型"""
        ext = os.path.splitext(filename)[1].lower()

        type_map = {
            ".md": "markdown",
            ".markdown": "markdown",
            ".pdf": "pdf",
            ".docx": "word",
            ".doc": "word",
            ".txt": "text"
        }

        return type_map.get(ext, "unknown")

    @staticmethod
    def get_file_modified(stat) -> str:
        """获取文件修改时间（ISO 8601）"""
        from datetime import datetime, timezone
        return datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()

    @staticmethod
    def get_timestamp() -> str:
        """获取当前时间戳（ISO 8601）"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def calculate_depth(kb_path: str, parent_kb: Optional[Dict]) -> int:
        """计算层级深度"""
        if not parent_kb:
            return 0

        parent_path = parent_kb["path"]
        relative = os.path.relpath(kb_path, parent_path)

        return relative.count(os.sep)


# ========== 使用示例 ==========

if __name__ == "__main__":
    manager = KnowledgeBaseManager()

    # 场景 1: 正常创建索引
    manager.build_index("E:/知识库/新知识库")

    # 场景 3: 当前无索引，父有索引
    manager.build_index("E:/知识库/父知识库/子主题")

    # 场景 5: 当前无索引，子有索引
    manager.build_index("E:/知识库/父知识库")

    # 列出所有知识库
    for kb in manager.registry["knowledge_bases"]:
        print(f"{kb['name']}: {kb['document_count']} 个文档")
```

---

## 使用示例

### 示例 1: 创建新知识库

```python
manager = KnowledgeBaseManager()

# 在空文件夹创建索引
manager.build_index("E:/我的知识库")

# 输出：
# ✓ 索引创建完成: E:/我的知识库/_index.yaml
# ✓ 已注册到全局目录: E:/我的知识库
```

### 示例 2: 父子冲突自动提升

```python
# 假设：
# E:/知识库/_index.yaml          (父索引)
# E:/知识库/子主题/_index.yaml   (子索引)

manager.build_index("E:/知识库/子主题")

# 输出：
# ⚠️ 检测到父子索引冲突
#   - 父索引: E:/知识库/_index.yaml
#   - 当前索引: E:/知识库/子主题/_index.yaml
#
# 执行层级提升：
#   [1/4] 备份索引...
#   [2/4] 删除下级索引...
#   [3/4] 更新父索引...
#   [4/4] 验证索引...
#
# ✓ 层级提升完成
#   - 已删除: 1 个下级索引
#   - 已更新: E:/知识库/_index.yaml
```

### 示例 3: 子索引自动合并

```python
# 假设：
# E:/知识库/子主题A/_index.yaml  (子索引)
# E:/知识库/子主题B/_index.yaml  (子索引)

manager.build_index("E:/知识库")

# 输出：
# ⚠️ 检测到子文件夹有索引
#   - 子索引数量: 2
#
# 执行层级提升：
#   [1/3] 备份子索引...
#   [2/3] 删除子索引...
#   [3/3] 创建/更新当前索引...
#
# ✓ 层级提升完成
#   - 已删除: 2 个子索引
#   - 当前索引: E:/知识库/_index.yaml
```

---

## AI Agent 集成

### Claude Code 中的使用

```python
# 在 SKILL.md 中定义的触发词
用户: 为「E:/知识库/信息化」建立索引

# AI Agent 执行流程
1. 识别触发词 → 调用 knowledge-index skill
2. 创建 KnowledgeBaseManager 实例
3. 调用 manager.build_index("E:/知识库/信息化")
4. 自动处理层级冲突
5. 输出结果给用户
```

---

## 测试用例

```python
import unittest
import tempfile
import shutil

class TestKnowledgeBaseManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = KnowledgeBaseManager()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_scenario_1_create_new_index(self):
        """场景 1: 正常创建索引"""
        kb_path = os.path.join(self.temp_dir, "知识库")
        os.makedirs(kb_path)

        # 创建测试文档
        with open(os.path.join(kb_path, "test.md"), 'w') as f:
            f.write("# 测试文档")

        # 构建索引
        self.manager.build_index(kb_path)

        # 验证
        self.assertTrue(os.path.exists(os.path.join(kb_path, "_index.yaml")))
        self.assertEqual(len(self.manager.registry["knowledge_bases"]), 1)

    def test_scenario_4_parent_child_conflict(self):
        """场景 4: 父子索引冲突"""
        parent_path = os.path.join(self.temp_dir, "父知识库")
        child_path = os.path.join(parent_path, "子主题")

        os.makedirs(child_path)

        # 创建父索引
        self.manager.create_index(parent_path)

        # 创建子索引（模拟冲突）
        with open(os.path.join(child_path, "_index.yaml"), 'w') as f:
            f.write("version: '1.0'")

        # 尝试在子文件夹创建索引
        self.manager.build_index(child_path)

        # 验证子索引被删除
        self.assertFalse(os.path.exists(os.path.join(child_path, "_index.yaml")))

        # 验证父索引存在
        self.assertTrue(os.path.exists(os.path.join(parent_path, "_index.yaml")))

    # 更多测试用例...
```

---

## 相关资源

- 层级管理规范：`references/advanced/hierarchy-management.md`
- 全局注册表规范：`references/advanced/global-registry-spec.md`
- 索引文件规范：`references/core/index-spec.md`

---

**版本**: 2.1
**最后更新**: 2026-03-04
