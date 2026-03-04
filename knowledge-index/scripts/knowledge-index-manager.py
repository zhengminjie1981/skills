#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knowledge Index Manager - 知识库索引管理器

功能：
1. 构建索引（自动处理层级提升）
2. 更新索引（增量）
3. 全局注册表管理
4. 层级冲突检测和处理

使用方法：
    python knowledge-index-manager.py build <知识库路径>
    python knowledge-index-manager.py update <知识库路径>
    python knowledge-index-manager.py list
    python knowledge-index-manager.py search <查询>
"""

import os
import sys
import yaml
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any


class KnowledgeBaseManager:
    """知识库管理器"""

    def __init__(self, registry_path: str = None):
        """
        初始化管理器

        Args:
            registry_path: 注册表路径（默认 ~/.knowledge-index/registry.yaml）
        """
        self.registry_path = registry_path or self.get_default_registry_path()
        self.registry = self.load_registry()

    @staticmethod
    def get_default_registry_path() -> str:
        """获取默认注册表路径"""
        home = Path.home()
        registry_dir = home / ".knowledge-index"
        registry_dir.mkdir(parents=True, exist_ok=True)
        return str(registry_dir / "registry.yaml")

    def load_registry(self) -> Dict:
        """加载注册表"""
        if not os.path.exists(self.registry_path):
            return {
                "version": "1.0",
                "last_updated": self.get_timestamp(),
                "knowledge_bases": []
            }

        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {
                    "version": "1.0",
                    "last_updated": self.get_timestamp(),
                    "knowledge_bases": []
                }
        except Exception as e:
            print(f"⚠️ 注册表加载失败: {e}")
            print("  将使用空注册表")
            return {
                "version": "1.0",
                "last_updated": self.get_timestamp(),
                "knowledge_bases": []
            }

    def save_registry(self):
        """保存注册表"""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)

        self.registry["last_updated"] = self.get_timestamp()

        with open(self.registry_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.registry, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # ========== 核心方法 ==========

    def build_index(self, kb_path: str, force: bool = False):
        """
        构建索引（自动处理层级提升）

        Args:
            kb_path: 知识库路径
            force: 是否强制创建（忽略父索引）

        Returns:
            bool: 是否成功
        """
        kb_path = os.path.abspath(kb_path)

        if not os.path.exists(kb_path):
            print(f"❌ 路径不存在: {kb_path}")
            return False

        if not os.path.isdir(kb_path):
            print(f"❌ 不是文件夹: {kb_path}")
            return False

        print(f"\n{'='*60}")
        print(f"构建索引: {kb_path}")
        print(f"{'='*60}\n")

        # Step 1: 检测索引层级
        print("[1/5] 检测索引层级...")
        parent_index = self.find_parent_index(kb_path)
        current_index = self.has_index(kb_path)
        child_indexes = self.find_child_indexes(kb_path)

        print(f"  - 父索引: {'有' if parent_index else '无'}")
        print(f"  - 当前索引: {'有' if current_index else '无'}")
        print(f"  - 子索引: {len(child_indexes)} 个")

        # Step 2: 决策树
        print("\n[2/5] 决策处理策略...")
        if parent_index and not force:
            # 父文件夹有索引
            if current_index:
                # 场景 4, 8: 当前也有索引 → 层级提升
                print("  → 场景: 父子索引冲突，执行层级提升")
                return self.promote_to_parent(kb_path, parent_index)
            else:
                # 场景 3, 7: 当前无索引 → 建议更新父索引
                print("  → 场景: 父索引存在，建议更新父索引")
                return self.suggest_update_parent(kb_path, parent_index)
        else:
            # 父文件夹无索引
            if child_indexes:
                # 场景 5, 6: 子文件夹有索引 → 删除子索引，提升至当前
                print("  → 场景: 子索引存在，执行层级提升至当前")
                return self.promote_to_current(kb_path, child_indexes)
            else:
                # 场景 1, 2: 正常创建或更新
                if current_index:
                    print("  → 场景: 索引已存在，执行更新")
                    return self.update_index(kb_path)
                else:
                    print("  → 场景: 正常创建索引")
                    return self.create_index(kb_path)

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
            # 跳过隐藏文件夹和特殊文件夹
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['.git', '.obsidian', '__pycache__']]

            if "_index.yaml" in files:
                index_path = os.path.join(root, "_index.yaml")
                # 排除当前文件夹的索引
                if index_path != os.path.join(kb_path, "_index.yaml"):
                    child_indexes.append(index_path)

        return child_indexes

    # ========== 层级提升方法 ==========

    def promote_to_parent(self, current_path: str, parent_index_path: str) -> bool:
        """
        提升至父级别索引

        场景 4, 8: 当前有索引，父也有索引
        """
        print(f"\n{'='*60}")
        print("执行层级提升至父级别")
        print(f"{'='*60}\n")

        print(f"⚠️ 检测到父子索引冲突")
        print(f"  - 父索引: {parent_index_path}")
        print(f"  - 当前索引: {os.path.join(current_path, '_index.yaml')}")

        # 1. 查找所有子索引
        child_indexes = self.find_child_indexes(current_path)

        print(f"\n将删除 {1 + len(child_indexes)} 个下级索引")

        # 2. 备份索引
        print("\n[1/4] 备份索引...")
        self.backup_index(current_path)
        for child_index in child_indexes:
            self.backup_index(os.path.dirname(child_index))

        # 3. 删除当前和子索引
        print("\n[2/4] 删除下级索引...")
        self.delete_index(current_path)
        self.unregister_knowledge_base(current_path)

        for child_index in child_indexes:
            child_path = os.path.dirname(child_index)
            print(f"  - 删除: {child_path}")
            self.delete_index(child_path)
            self.unregister_knowledge_base(child_path)

        # 4. 更新父索引
        print("\n[3/4] 更新父索引...")
        parent_path = os.path.dirname(parent_index_path)
        success = self.update_index(parent_path)

        # 5. 验证
        if success:
            print("\n[4/4] 验证索引...")
            self.validate_index(parent_path)

            print(f"\n{'='*60}")
            print("✓ 层级提升完成")
            print(f"{'='*60}")
            print(f"  - 已删除: {1 + len(child_indexes)} 个下级索引")
            print(f"  - 已更新: {parent_index_path}")
            print(f"  - 文档总数: {self.get_document_count(parent_path)}")

        return success

    def promote_to_current(self, current_path: str, child_indexes: List[str]) -> bool:
        """
        提升至当前级别，删除子索引

        场景 5, 6: 子文件夹有索引
        """
        print(f"\n{'='*60}")
        print("执行层级提升至当前级别")
        print(f"{'='*60}\n")

        print(f"⚠️ 检测到子文件夹有索引")
        print(f"  - 子索引数量: {len(child_indexes)}")

        for i, child_index in enumerate(child_indexes, 1):
            print(f"    {i}. {child_index}")

        # 1. 备份
        print("\n[1/3] 备份子索引...")
        for child_index in child_indexes:
            self.backup_index(os.path.dirname(child_index))

        # 2. 删除子索引
        print("\n[2/3] 删除子索引...")
        for child_index in child_indexes:
            child_path = os.path.dirname(child_index)
            print(f"  - 删除: {child_path}")
            self.delete_index(child_path)
            self.unregister_knowledge_base(child_path)

        # 3. 创建或更新当前索引
        print("\n[3/3] 创建/更新当前索引...")
        if self.has_index(current_path):
            success = self.update_index(current_path)
        else:
            success = self.create_index(current_path)

        if success:
            print(f"\n{'='*60}")
            print("✓ 层级提升完成")
            print(f"{'='*60}")
            print(f"  - 已删除: {len(child_indexes)} 个子索引")
            print(f"  - 当前索引: {os.path.join(current_path, '_index.yaml')}")
            print(f"  - 文档总数: {self.get_document_count(current_path)}")

        return success

    def suggest_update_parent(self, current_path: str, parent_index_path: str) -> bool:
        """
        建议更新父索引

        场景 3, 7: 当前无索引，父有索引
        """
        print(f"\n{'='*60}")
        print("检测到父索引存在")
        print(f"{'='*60}\n")

        print(f"⚠️ 检测到父文件夹已有索引")
        print(f"  - 父索引: {parent_index_path}")
        print(f"  - 当前文件夹: {current_path}")
        print(f"  - 当前文件夹已包含在父索引中")

        print("\n建议操作：")
        print("  1. 更新父索引（推荐）")
        print("  2. 强制在当前文件夹创建独立索引（不推荐）")

        try:
            choice = input("\n请选择 (1/2): ").strip()
        except KeyboardInterrupt:
            print("\n\n操作已取消")
            return False

        if choice == "1":
            parent_path = os.path.dirname(parent_index_path)
            success = self.update_index(parent_path)
            if success:
                print(f"\n✓ 已更新父索引: {parent_index_path}")
            return success
        else:
            print("\n⚠️ 警告: 将在子级别创建独立索引")
            print("  这将导致文档重复索引")
            try:
                confirm = input("是否继续？(y/N): ").strip().lower()
            except KeyboardInterrupt:
                print("\n\n操作已取消")
                return False

            if confirm == 'y':
                success = self.create_index(current_path, force=True)
                if success:
                    print("\n✓ 已创建索引（子级别）")
                    print("  建议: 在父索引的 _index_config.yaml 中排除此文件夹")
                return success
            else:
                print("\n操作已取消")
                return False

    # ========== 基础操作方法 ==========

    def create_index(self, kb_path: str, force: bool = False) -> bool:
        """创建索引"""
        print(f"\n{'='*60}")
        print("创建索引")
        print(f"{'='*60}\n")

        index_path = os.path.join(kb_path, "_index.yaml")

        if os.path.exists(index_path) and not force:
            print(f"❌ 索引已存在: {index_path}")
            print("  使用 update 命令更新索引")
            return False

        # 扫描文档
        print("[1/3] 扫描文档...")
        documents = self.scan_documents(kb_path)

        if not documents:
            print("⚠️ 未找到任何文档")
            return False

        print(f"  - 找到 {len(documents)} 个文档")

        # 生成索引内容
        print("\n[2/3] 生成索引...")
        total_size = sum(doc['size'] for doc in documents)

        index_data = {
            "version": "1.0",
            "knowledge_base": {
                "name": os.path.basename(kb_path),
                "path": kb_path,
                "created": self.get_timestamp(),
                "last_updated": self.get_timestamp(),
                "total_documents": len(documents),
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            },
            "documents": documents
        }

        # 写入文件
        with open(index_path, 'w', encoding='utf-8') as f:
            yaml.dump(index_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        print(f"  ✓ 写入索引文件: {index_path}")

        # 注册到全局注册表
        print("\n[3/3] 注册到全局目录...")
        self.register_knowledge_base(kb_path, index_path, index_data)

        print(f"\n{'='*60}")
        print("✓ 索引创建完成")
        print(f"{'='*60}")
        print(f"  - 知识库: {os.path.basename(kb_path)}")
        print(f"  - 文档数量: {len(documents)}")
        print(f"  - 总大小: {round(total_size / (1024 * 1024), 2)} MB")
        print(f"  - 索引文件: {index_path}")

        return True

    def update_index(self, kb_path: str) -> bool:
        """更新索引（增量）"""
        print(f"\n{'='*60}")
        print("更新索引")
        print(f"{'='*60}\n")

        index_path = os.path.join(kb_path, "_index.yaml")

        if not os.path.exists(index_path):
            print(f"❌ 索引不存在: {index_path}")
            print("  使用 build 命令创建索引")
            return False

        # 读取现有索引
        print("[1/3] 读取现有索引...")
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                old_index = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ 索引文件损坏: {e}")
            return False

        # 检测变更
        print("\n[2/3] 检测变更...")
        current_docs = self.scan_documents(kb_path)
        old_docs = {doc['path']: doc for doc in old_index.get('documents', [])}

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

        print(f"  - 新增: {len(changes['added'])} 个")
        print(f"  - 修改: {len(changes['modified'])} 个")
        print(f"  - 删除: {len(changes['deleted'])} 个")

        if not any(changes.values()):
            print("\n✓ 索引已是最新，无需更新")
            return True

        # 更新索引
        print("\n[3/3] 更新索引文件...")
        old_index['documents'] = current_docs
        old_index['knowledge_base']['last_updated'] = self.get_timestamp()
        old_index['knowledge_base']['total_documents'] = len(current_docs)
        old_index['knowledge_base']['total_size_mb'] = round(
            sum(doc['size'] for doc in current_docs) / (1024 * 1024), 2
        )

        # 写入
        with open(index_path, 'w', encoding='utf-8') as f:
            yaml.dump(old_index, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        # 更新注册表
        self.update_registry_entry(kb_path, {
            "document_count": len(current_docs),
            "last_updated": self.get_timestamp()
        })

        print(f"\n{'='*60}")
        print("✓ 索引更新完成")
        print(f"{'='*60}")
        print(f"  - 新增: {len(changes['added'])} 个文档")
        print(f"  - 修改: {len(changes['modified'])} 个文档")
        print(f"  - 删除: {len(changes['deleted'])} 个文档")
        print(f"  - 当前总数: {len(current_docs)} 个文档")

        return True

    def delete_index(self, kb_path: str):
        """删除索引"""
        index_path = os.path.join(kb_path, "_index.yaml")

        if os.path.exists(index_path):
            os.remove(index_path)
            print(f"  ✓ 已删除索引: {index_path}")

    # ========== 注册表操作 ==========

    def register_knowledge_base(self, kb_path: str, index_path: str, index_data: Dict):
        """注册知识库到全局注册表"""

        # 检查是否已注册
        existing = self.find_kb_in_registry(kb_path)
        if existing:
            # 更新现有条目
            existing.update({
                "name": index_data["knowledge_base"]["name"],
                "index_path": index_path,
                "last_updated": index_data["knowledge_base"]["last_updated"],
                "document_count": index_data["knowledge_base"]["total_documents"],
                "total_size_mb": index_data["knowledge_base"]["total_size_mb"],
                "status": "active"
            })
        else:
            # 创建新条目
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

        self.save_registry()
        print(f"  ✓ 已注册到全局目录")

    def unregister_knowledge_base(self, kb_path: str):
        """从注册表移除知识库"""
        before_count = len(self.registry["knowledge_bases"])

        self.registry["knowledge_bases"] = [
            kb for kb in self.registry["knowledge_bases"]
            if kb["path"] != kb_path
        ]

        after_count = len(self.registry["knowledge_bases"])

        if before_count != after_count:
            self.save_registry()
            print(f"  ✓ 已从注册表移除: {kb_path}")

    def update_registry_entry(self, kb_path: str, updates: Dict):
        """更新注册表条目"""
        for kb in self.registry["knowledge_bases"]:
            if kb["path"] == kb_path:
                kb.update(updates)
                break

        self.save_registry()

    def find_kb_in_registry(self, kb_path: str) -> Optional[Dict]:
        """在注册表中查找知识库"""
        for kb in self.registry["knowledge_bases"]:
            if kb["path"] == kb_path:
                return kb
        return None

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
        supported_extensions = ['.md', '.markdown', '.pdf', '.docx', '.doc', '.txt']

        for root, dirs, files in os.walk(kb_path):
            # 跳过隐藏文件夹和特殊文件夹
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['.git', '.obsidian', '__pycache__', 'node_modules']]

            for file in files:
                # 跳过索引文件
                if file in ['_index.yaml', '_index_config.yaml']:
                    continue

                # 检查文件扩展名
                ext = os.path.splitext(file)[1].lower()
                if ext not in supported_extensions:
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, kb_path)

                # 获取文件信息
                try:
                    stat = os.stat(file_path)

                    documents.append({
                        "path": rel_path.replace(os.sep, '/'),  # 使用正斜杠
                        "filename": file,
                        "type": self.get_file_type(file),
                        "modified": self.get_file_modified(stat),
                        "size": stat.st_size
                    })
                except Exception as e:
                    print(f"⚠️ 跳过文件: {file_path} ({e})")
                    continue

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

        shutil.copy(index_path, backup_path)
        print(f"  ✓ 备份: {backup_path}")

    def validate_index(self, kb_path: str) -> bool:
        """验证索引"""
        index_path = os.path.join(kb_path, "_index.yaml")

        if not os.path.exists(index_path):
            print(f"  ❌ 索引文件不存在: {index_path}")
            return False

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = yaml.safe_load(f)

            # 验证必填字段
            required_fields = ["version", "knowledge_base", "documents"]
            for field in required_fields:
                if field not in index_data:
                    print(f"  ❌ 索引缺少必填字段: {field}")
                    return False

            print("  ✓ 索引验证通过")
            return True

        except Exception as e:
            print(f"  ❌ 索引验证失败: {e}")
            return False

    def get_document_count(self, kb_path: str) -> int:
        """获取文档数量"""
        index_path = os.path.join(kb_path, "_index.yaml")

        if not os.path.exists(index_path):
            return 0

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = yaml.safe_load(f)
            return len(index_data.get('documents', []))
        except:
            return 0

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
        return datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()

    @staticmethod
    def get_timestamp() -> str:
        """获取当前时间戳（ISO 8601）"""
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def calculate_depth(kb_path: str, parent_kb: Optional[Dict]) -> int:
        """计算层级深度"""
        if not parent_kb:
            return 0

        parent_path = parent_kb["path"]
        relative = os.path.relpath(kb_path, parent_path)

        return relative.count(os.sep)

    # ========== 其他命令 ==========

    def list_knowledge_bases(self):
        """列出所有知识库"""
        print(f"\n{'='*60}")
        print("已注册的知识库")
        print(f"{'='*60}\n")

        if not self.registry["knowledge_bases"]:
            print("  暂无已注册的知识库")
            return

        for i, kb in enumerate(self.registry["knowledge_bases"], 1):
            if kb["status"] != "active":
                continue

            print(f"{i}. {kb['name']}")
            print(f"   路径: {kb['path']}")
            print(f"   文档: {kb['document_count']} 个")
            print(f"   大小: {kb['total_size_mb']} MB")
            print(f"   更新: {kb['last_updated'][:19]}")
            print()


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    manager = KnowledgeBaseManager()

    if command == "build":
        if len(sys.argv) < 3:
            print("用法: python knowledge-index-manager.py build <知识库路径>")
            sys.exit(1)

        kb_path = sys.argv[2]
        force = "--force" in sys.argv
        manager.build_index(kb_path, force=force)

    elif command == "update":
        if len(sys.argv) < 3:
            print("用法: python knowledge-index-manager.py update <知识库路径>")
            sys.exit(1)

        kb_path = sys.argv[2]
        manager.update_index(kb_path)

    elif command == "list":
        manager.list_knowledge_bases()

    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
