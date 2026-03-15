#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Knowledge Index Manager - 知识库索引管理器

功能：
1. 构建索引（自动处理层级提升）
2. 更新索引（增量）
3. 全局注册表管理
4. 层级冲突检测和处理
5. AI 摘要生成（需 ANTHROPIC_API_KEY）
6. Wikilink 解析（Obsidian 支持）
7. 智能检索（支持 Obsidian CLI）

使用方法：
    python knowledge-index-manager.py build <知识库路径> [--force] [--no-ai]
    python knowledge-index-manager.py update <知识库路径> [--no-ai]
    python knowledge-index-manager.py list
    python knowledge-index-manager.py search <查询> [--kb <知识库路径>] [--prefer-obsidian] [--no-obsidian]
    python knowledge-index-manager.py info <知识库路径>

参数：
    --force             强制创建索引（忽略父索引）
    --no-ai             禁用 AI 摘要生成
    --kb                指定搜索的知识库路径
    --prefer-obsidian   优先使用 Obsidian CLI 搜索（需桌面应用运行中）
    --no-obsidian       禁用 Obsidian CLI，仅使用索引搜索

Obsidian CLI 集成：
    当 Obsidian 桌面应用运行时，可使用原生搜索能力：
    - 自动检测 CLI 可用性
    - CLI 不可用时自动回退到索引搜索
    - 使用 --prefer-obsidian 强制优先使用 CLI
    - 使用 --no-obsidian 禁用 CLI

索引版本: 2.1（文档分类索引结构，支持 folders/categories）
Obsidian CLI: 支持（搜索功能增强）
"""

import os
import sys
import yaml
import json
import shutil
import re
import hashlib
import time
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple


class ObsidianCLIClient:
    """
    Obsidian CLI 客户端

    用于检测和使用 Obsidian 官方 CLI 进行搜索。
    CLI 需要 Obsidian 桌面应用正在运行。

    命令格式：
        obsidian search query="test" format=json limit=5
        obsidian search query="GitLab" path="子系统/" format=json
    """

    def __init__(self, vault_path: str = None):
        """
        初始化 Obsidian CLI 客户端

        Args:
            vault_path: 知识库路径（用于路径转换）
        """
        self.vault_path = vault_path
        self._available = None

    def is_available(self) -> bool:
        """
        检测 Obsidian CLI 是否可用

        Returns:
            bool: CLI 是否可用
        """
        if self._available is not None:
            return self._available

        try:
            result = subprocess.run(
                ["obsidian", "vault"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            self._available = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            self._available = False

        return self._available

    def search(self, query: str, path: str = None, limit: int = 10) -> List[str]:
        """
        执行搜索并返回结果列表

        Args:
            query: 搜索查询
            path: 限制搜索路径（可选）
            limit: 返回结果数量限制

        Returns:
            匹配的文件路径列表
        """
        if not self.is_available():
            return []

        cmd = ["obsidian", "search", f"query={query}", "format=json", f"limit={limit}"]

        if path:
            # 确保路径格式正确
            path = path.replace("\\", "/").rstrip("/")
            cmd.append(f"path={path}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )

            if result.returncode == 0 and result.stdout.strip():
                # 解析 JSON 数组输出
                return json.loads(result.stdout.strip())
        except (json.JSONDecodeError, subprocess.TimeoutExpired, Exception):
            pass

        return []

    def search_with_fallback(self, query: str, path: str = None,
                             limit: int = 10) -> Tuple[List[str], str]:
        """
        执行搜索，返回结果和来源标识

        Args:
            query: 搜索查询
            path: 限制搜索路径
            limit: 结果数量限制

        Returns:
            (结果列表, 来源标识)
            来源标识: "obsidian_cli" 或 "unavailable"
        """
        if self.is_available():
            results = self.search(query, path, limit)
            if results:
                return results, "obsidian_cli"

        return [], "unavailable"


class ProgressReporter:
    """
    进度报告器

    用于长时间任务（索引构建、检索）时给用户实时进度反馈。
    显示格式：[任务名] 当前/总数 (百分比), 预计剩余 XXs
    """

    def __init__(self, total: int, task_name: str = "处理中"):
        """
        初始化进度报告器

        Args:
            total: 总任务数
            task_name: 任务名称（显示在进度前缀）
        """
        self.total = total
        self.current = 0
        self.task_name = task_name
        self.start_time = time.time()
        self._last_message = ""

    def update(self, increment: int = 1, message: str = None) -> None:
        """
        更新进度

        Args:
            increment: 增量（默认 1）
            message: 附加消息（可选）
        """
        self.current += increment
        percentage = (self.current / self.total) * 100
        elapsed = time.time() - self.start_time

        # 估算剩余时间
        if self.current > 0 and self.current < self.total:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f", 预计剩余 {eta:.0f}s"
        else:
            eta_str = ""

        msg = f"\r[{self.task_name}] {self.current}/{self.total} ({percentage:.1f}%){eta_str}"
        if message:
            msg += f" - {message}"

        # 清除之前的输出（如果新消息更短）
        if len(self._last_message) > len(msg):
            msg += " " * (len(self._last_message) - len(msg))

        self._last_message = msg
        print(msg, end="", flush=True)

    def complete(self, message: str = "完成") -> float:
        """
        完成进度

        Args:
            message: 完成消息

        Returns:
            总耗时（秒）
        """
        elapsed = time.time() - self.start_time

        # 清除之前的输出
        clear_msg = "\r" + " " * len(self._last_message) + "\r"
        print(clear_msg, end="")

        print(f"[{self.task_name}] {self.total}/{self.total} (100%) - {message}，耗时 {elapsed:.1f}s")
        return elapsed

    def skip(self) -> None:
        """跳过进度（无需处理时调用）"""
        print(f"[{self.task_name}] 跳过（共 {self.total} 项）")


class KnowledgeBaseManager:
    """知识库管理器"""

    # Wikilink 正则模式：匹配 [[link]], [[link#section]], [[link|alias]], [[link#section|alias]]
    WIKILINK_PATTERN = re.compile(r'\[\[([^\]\|#]+)(?:#([^\]\|]+))?(?:\|([^\]]+))?\]\]')

    def __init__(self, registry_path: str = None, enable_ai_summary: bool = True,
                 obsidian_cli_mode: str = "auto"):
        """
        初始化管理器

        Args:
            registry_path: 注册表路径（默认 ~/.knowledge-index/registry.yaml）
            enable_ai_summary: 是否启用 AI 摘要（默认 True）
            obsidian_cli_mode: Obsidian CLI 模式
                - "auto": 自动检测，CLI 可用时优先使用（默认）
                - "prefer": 优先使用 CLI，结果与索引合并
                - "disabled": 禁用 CLI，仅使用索引
        """
        self.registry_path = registry_path or self.get_default_registry_path()
        self.registry = self.load_registry()
        self.enable_ai_summary = enable_ai_summary
        self._ai_cache = {}  # 内存缓存
        self._cache_dir = None
        self.obsidian_cli_mode = obsidian_cli_mode
        self._obsidian_cli = None

    @property
    def obsidian_cli(self) -> ObsidianCLIClient:
        """获取 Obsidian CLI 客户端（延迟初始化）"""
        if self._obsidian_cli is None:
            self._obsidian_cli = ObsidianCLIClient()
        return self._obsidian_cli

    @staticmethod
    def get_default_registry_path() -> str:
        """获取默认注册表路径"""
        home = Path.home()
        registry_dir = home / ".knowledge-index"
        registry_dir.mkdir(parents=True, exist_ok=True)
        return str(registry_dir / "registry.yaml")

    @property
    def cache_dir(self) -> str:
        """获取缓存目录"""
        if self._cache_dir is None:
            home = Path.home()
            self._cache_dir = str(home / ".knowledge-index" / "cache")
            os.makedirs(self._cache_dir, exist_ok=True)
        return self._cache_dir

    def get_content_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]

    def get_cached_summary(self, content_hash: str) -> Optional[Dict]:
        """从缓存获取摘要"""
        # 先检查内存缓存
        if content_hash in self._ai_cache:
            return self._ai_cache[content_hash]

        # 检查文件缓存
        cache_file = os.path.join(self.cache_dir, f"{content_hash}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._ai_cache[content_hash] = data
                    return data
            except:
                pass
        return None

    def save_cached_summary(self, content_hash: str, summary_data: Dict):
        """保存摘要到缓存"""
        self._ai_cache[content_hash] = summary_data
        cache_file = os.path.join(self.cache_dir, f"{content_hash}.json")
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
        except:
            pass

    def generate_ai_summary(self, content: str, doc_path: str = "") -> Dict[str, Any]:
        """
        生成 AI 摘要和关键词

        Args:
            content: 文档内容
            doc_path: 文档路径（用于日志）

        Returns:
            {"summary": "...", "keywords": [...], "topics": [...]}
        """
        # 检查缓存
        content_hash = self.get_content_hash(content)
        cached = self.get_cached_summary(content_hash)
        if cached:
            print(f"    ✓ 使用缓存: {doc_path}")
            return cached

        # 如果禁用 AI 摘要，返回基础信息
        if not self.enable_ai_summary:
            return self._generate_basic_summary(content)

        # 尝试调用 Claude API
        try:
            result = self._call_claude_api(content)
            if result:
                self.save_cached_summary(content_hash, result)
                return result
        except Exception as e:
            print(f"    ⚠️ AI 摘要失败 ({doc_path}): {e}")

        # 降级为基础摘要
        return self._generate_basic_summary(content)

    def _call_claude_api(self, content: str) -> Optional[Dict]:
        """调用 Claude API 生成摘要"""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return None

        # 截断过长内容
        max_chars = 8000
        if len(content) > max_chars:
            content = content[:max_chars] + "\n... (内容已截断)"

        prompt = f"""请分析以下文档，生成：
1. 一句话摘要（50-100字）
2. 5-10个关键词（具有检索价值）
3. 3-5个主题标签（反映文档类别）

文档内容：
{content}

请严格按以下 YAML 格式输出（不要有其他内容）：
summary: "摘要内容"
keywords:
  - 关键词1
  - 关键词2
topics:
  - 主题1
  - 主题2"""

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-sonnet-4-6-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text

            # 解析 YAML 响应
            # 移除可能的 markdown 代码块标记
            if "```yaml" in response_text:
                response_text = response_text.split("```yaml")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]

            result = yaml.safe_load(response_text.strip())

            # 验证结果
            if isinstance(result, dict) and "summary" in result:
                return {
                    "summary": result.get("summary", ""),
                    "keywords": result.get("keywords", []),
                    "topics": result.get("topics", [])
                }
        except ImportError:
            # anthropic 包未安装
            pass
        except Exception as e:
            raise e

        return None

    def _generate_basic_summary(self, content: str) -> Dict[str, Any]:
        """生成基础摘要（无 AI 时降级）"""
        # 提取前 200 字符作为摘要
        lines = content.strip().split('\n')
        # 尝试找标题
        title = ""
        for line in lines[:10]:
            if line.startswith('# '):
                title = line[2:].strip()
                break

        # 提取前几段作为摘要
        paragraphs = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                paragraphs.append(line)
                if len(' '.join(paragraphs)) > 200:
                    break

        summary = ' '.join(paragraphs)[:200]
        if title:
            summary = f"【{title}】{summary}"

        # 从内容中提取可能的关键词（简单实现）
        keywords = []
        # 提取代码相关词
        code_patterns = ['API', 'HTTP', 'JSON', 'REST', 'Git', 'Docker', 'Python', 'JavaScript']
        for pattern in code_patterns:
            if pattern.lower() in content.lower():
                keywords.append(pattern)

        return {
            "summary": summary or "（无摘要）",
            "keywords": keywords[:5],
            "topics": []
        }

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

    def suggest_update_parent(self, current_path: str, parent_index_path: str,
                             force: bool = False, update_parent: bool = True) -> bool:
        """
        建议更新父索引（支持非交互式）

        Args:
            current_path: 当前知识库路径
            parent_index_path: 父索引路径
            force: 强制创建子索引
            update_parent: 更新父索引（默认 True）

        Returns:
            是否成功
        """
        print(f"\n{'='*60}")
        print("检测到父索引存在")
        print(f"{'='*60}\n")

        print(f"⚠️ 检测到父文件夹已有索引")
        print(f"  - 父索引: {parent_index_path}")
        print(f"  - 当前文件夹: {current_path}")
        print(f"  - 当前文件夹已包含在父索引中")

        if force:
            # 非交互式：强制创建子索引
            print("\n[非交互模式] 强制创建子索引...")
            success = self.create_index(current_path, force=True)
            if success:
                print("\n✓ 已创建索引（子级别）")
                print("  建议: 在父索引的 _index_config.yaml 中排除此文件夹")
            return success

        if update_parent:
            # 非交互式：更新父索引
            print("\n[非交互模式] 更新父索引...")
            parent_path = os.path.dirname(parent_index_path)
            success = self.update_index(parent_path)
            if success:
                print(f"\n✓ 已更新父索引: {parent_index_path}")
            return success

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

        # 扫描文档（分类结构）
        print("[1/3] 扫描文档...")
        markdown_docs, other_docs = self.scan_documents(kb_path, generate_summaries=self.enable_ai_summary)

        total_docs = len(markdown_docs) + len(other_docs)
        if total_docs == 0:
            print("⚠️ 未找到任何文档")
            return False

        print(f"  - Markdown 文档: {len(markdown_docs)} 个")
        print(f"  - 其他格式文档: {len(other_docs)} 个")

        # 检测 Obsidian
        has_obsidian = os.path.exists(os.path.join(kb_path, '.obsidian'))
        kb_type = "obsidian" if has_obsidian else "generic"

        # 生成索引内容
        print("\n[2/3] 生成索引...")
        total_size = sum(doc['size'] for doc in markdown_docs + other_docs)

        # 生成文件夹分区索引和语义分类索引
        folders = self._generate_folder_index(markdown_docs, other_docs)
        categories = self._generate_category_index(markdown_docs, other_docs, folders)

        index_data = {
            "version": "2.1",
            "knowledge_base": {
                "name": os.path.basename(kb_path),
                "path": kb_path,
                "type": kb_type,
                "has_obsidian": has_obsidian,
                "created": self.get_timestamp(),
                "last_updated": self.get_timestamp(),
                "total_documents": total_docs,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            },
            "folders": folders,
            "categories": categories,
            "markdown_documents": markdown_docs,
            "other_documents": other_docs
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
        print(f"  - 类型: {kb_type}")
        print(f"  - Markdown 文档: {len(markdown_docs)} 个")
        print(f"  - 其他格式文档: {len(other_docs)} 个")
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
        print("[1/4] 读取现有索引...")
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                old_index = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ 索引文件损坏: {e}")
            return False

        # 检测变更
        print("\n[2/4] 检测变更...")
        markdown_docs, other_docs = self.scan_documents(kb_path, generate_summaries=self.enable_ai_summary)
        current_docs = {doc['path']: doc for doc in markdown_docs + other_docs}

        # 兼容旧版索引格式
        old_docs = {}
        if 'documents' in old_index:
            old_docs = {doc['path']: doc for doc in old_index.get('documents', [])}
        else:
            # 新版分类索引
            for doc in old_index.get('markdown_documents', []):
                old_docs[doc['path']] = doc
            for doc in old_index.get('other_documents', []):
                old_docs[doc['path']] = doc

        changes = {"added": [], "modified": [], "deleted": []}

        # 检测新增和修改
        for doc_path, doc in current_docs.items():
            if doc_path not in old_docs:
                changes["added"].append(doc)
            elif doc['modified'] > old_docs[doc_path]['modified']:
                changes["modified"].append(doc)

        # 检测删除
        for doc_path in old_docs:
            if doc_path not in current_docs:
                changes["deleted"].append(doc_path)

        print(f"  - 新增: {len(changes['added'])} 个")
        print(f"  - 修改: {len(changes['modified'])} 个")
        print(f"  - 删除: {len(changes['deleted'])} 个")

        if not any(changes.values()):
            print("\n✓ 索引已是最新，无需更新")
            return True

        # 更新索引
        print("\n[3/4] 更新索引文件...")
        total_size = sum(doc['size'] for doc in markdown_docs + other_docs)

        # 检测 Obsidian
        has_obsidian = os.path.exists(os.path.join(kb_path, '.obsidian'))
        kb_type = "obsidian" if has_obsidian else "generic"

        # 生成文件夹分区索引和语义分类索引
        folders = self._generate_folder_index(markdown_docs, other_docs)
        categories = self._generate_category_index(markdown_docs, other_docs, folders)

        old_index['version'] = '2.1'
        old_index['knowledge_base']['type'] = kb_type
        old_index['knowledge_base']['has_obsidian'] = has_obsidian
        old_index['knowledge_base']['last_updated'] = self.get_timestamp()
        old_index['knowledge_base']['total_documents'] = len(markdown_docs) + len(other_docs)
        old_index['knowledge_base']['total_size_mb'] = round(total_size / (1024 * 1024), 2)

        # 添加文件夹和分类索引
        old_index['folders'] = folders
        old_index['categories'] = categories

        # 使用分类索引结构
        old_index['markdown_documents'] = markdown_docs
        old_index['other_documents'] = other_docs
        if 'documents' in old_index:
            del old_index['documents']

        # 写入
        with open(index_path, 'w', encoding='utf-8') as f:
            yaml.dump(old_index, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        # 更新注册表
        print("\n[4/4] 更新注册表...")
        self.update_registry_entry(kb_path, {
            "document_count": len(markdown_docs) + len(other_docs),
            "last_updated": self.get_timestamp()
        })

        print(f"\n{'='*60}")
        print("✓ 索引更新完成")
        print(f"{'='*60}")
        print(f"  - 新增: {len(changes['added'])} 个文档")
        print(f"  - 修改: {len(changes['modified'])} 个文档")
        print(f"  - 删除: {len(changes['deleted'])} 个文档")
        print(f"  - 当前总数: {len(markdown_docs) + len(other_docs)} 个文档")

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

    def scan_documents(self, kb_path: str, generate_summaries: bool = True,
                       progress: bool = True) -> Tuple[List[Dict], List[Dict]]:
        """
        扫描文档，返回分类结构（markdown_documents, other_documents）

        Args:
            kb_path: 知识库路径
            generate_summaries: 是否生成 AI 摘要
            progress: 是否显示进度

        Returns:
            (markdown_documents, other_documents)
        """
        markdown_docs = []
        other_docs = []
        supported_extensions = {
            'markdown': ['.md', '.markdown'],
            'pdf': ['.pdf'],
            'word': ['.docx', '.doc'],
            'text': ['.txt']
        }

        # 检测是否有 Obsidian
        has_obsidian = os.path.exists(os.path.join(kb_path, '.obsidian'))

        # Phase 1: 快速扫描获取文件列表（用于进度显示）
        all_files = []
        for root, dirs, files in os.walk(kb_path):
            # 跳过隐藏文件夹和特殊文件夹
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['.git', '.obsidian', '__pycache__', 'node_modules']]

            for file in files:
                # 跳过索引文件
                if file in ['_index.yaml', '_index_config.yaml']:
                    continue

                # 检查文件扩展名
                ext = os.path.splitext(file)[1].lower()

                # 确定文件类型
                doc_type = None
                for type_name, extensions in supported_extensions.items():
                    if ext in extensions:
                        doc_type = type_name
                        break

                if doc_type:
                    all_files.append((root, file, doc_type))

        # 初始化进度报告器
        reporter = None
        if progress and len(all_files) > 10:
            reporter = ProgressReporter(len(all_files), "扫描文档")

        # Phase 2: 逐个处理文件
        for idx, (root, file, doc_type) in enumerate(all_files):
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, kb_path).replace(os.sep, '/')

            # 更新进度
            if reporter:
                reporter.update(1, rel_path[:40] + ('...' if len(rel_path) > 40 else ''))

            # 获取文件信息
            try:
                stat = os.stat(file_path)
                doc_info = {
                    "path": rel_path,
                    "filename": file,
                    "type": doc_type,
                    "modified": self.get_file_modified(stat),
                    "size": stat.st_size
                }

                if doc_type == 'markdown':
                    # Markdown 文档：提取 wikilink、tags、生成摘要
                    content = self._read_file_content(file_path)

                    if content:
                        # 提取 wikilinks
                        if has_obsidian:
                            doc_info['links'] = self.extract_wikilinks(content)

                        # 提取 tags
                        tags = self.extract_frontmatter_tags(content)
                        tags.extend(self.extract_content_tags(content))
                        if tags:
                            doc_info['tags'] = list(set(tags))

                        # 生成 AI 摘要
                        if generate_summaries:
                            summary_data = self.generate_ai_summary(content, rel_path)
                            doc_info['summary'] = summary_data.get('summary', '')
                            doc_info['keywords'] = summary_data.get('keywords', [])
                            if summary_data.get('topics'):
                                doc_info['topics'] = summary_data['topics']

                    markdown_docs.append(doc_info)
                else:
                    # 其他格式文档：基础信息
                    other_docs.append(doc_info)

            except Exception as e:
                print(f"\n⚠️ 跳过文件: {file_path} ({e})")
                continue

        # 完成进度
        if reporter:
            reporter.complete(f"发现 {len(markdown_docs)} 个 Markdown, {len(other_docs)} 个其他文档")

        # 计算反向链接
        if has_obsidian and markdown_docs:
            backlinks = self.calculate_backlinks(markdown_docs)
            for doc in markdown_docs:
                doc_path = doc.get('path', '')
                # 尝试多种匹配方式
                backlink_paths = backlinks.get(doc_path, [])
                if not backlink_paths:
                    # 尝试不带扩展名匹配
                    base_name = doc_path.rsplit('.', 1)[0]
                    backlink_paths = backlinks.get(f"{base_name}.md", [])
                if backlink_paths:
                    doc['backlinks'] = list(set(backlink_paths))

        return markdown_docs, other_docs

    def _read_file_content(self, file_path: str) -> Optional[str]:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    return f.read()
            except:
                return None
        except:
            return None

    def _generate_folder_index(self, markdown_docs: List[Dict],
                               other_docs: List[Dict]) -> List[Dict]:
        """
        生成文件夹分区索引

        Args:
            markdown_docs: Markdown 文档列表
            other_docs: 其他格式文档列表

        Returns:
            文件夹索引列表
        """
        # 按文件夹分组
        folder_map: Dict[str, Dict] = {}

        all_docs = markdown_docs + other_docs
        for doc in all_docs:
            path = doc.get('path', '')
            parts = path.split('/')
            if len(parts) <= 1:
                # 根目录文件，跳过
                continue

            # 提取文件夹路径（排除文件名）
            folder_path = '/'.join(parts[:-1])
            if not folder_path:
                continue

            if folder_path not in folder_map:
                folder_map[folder_path] = {
                    'path': folder_path + '/',
                    'document_count': 0,
                    'keywords_aggregated': set(),
                    'topics_aggregated': set()
                }

            folder_map[folder_path]['document_count'] += 1

            # 聚合关键词和主题
            for kw in doc.get('keywords', []):
                folder_map[folder_path]['keywords_aggregated'].add(kw.lower())
            for topic in doc.get('topics', []):
                folder_map[folder_path]['topics_aggregated'].add(topic)

        # 转换为列表格式
        folders = []
        for folder_path in sorted(folder_map.keys()):
            folder = folder_map[folder_path]
            folders.append({
                'path': folder['path'],
                'document_count': folder['document_count'],
                'keywords_aggregated': list(folder['keywords_aggregated'])[:20],  # 限制数量
                'topics_aggregated': list(folder['topics_aggregated'])[:10]
            })

        return folders

    def _generate_category_index(self, markdown_docs: List[Dict],
                                 other_docs: List[Dict],
                                 folder_index: List[Dict]) -> List[Dict]:
        """
        生成语义分类索引（从 topics 自动聚合）

        Args:
            markdown_docs: Markdown 文档列表
            other_docs: 其他格式文档列表
            folder_index: 文件夹索引

        Returns:
            分类索引列表
        """
        # 按主题分组
        category_map: Dict[str, Dict] = {}

        all_docs = markdown_docs + other_docs
        for doc in all_docs:
            topics = doc.get('topics', [])
            keywords = doc.get('keywords', [])
            path = doc.get('path', '')

            # 提取文件夹
            parts = path.split('/')
            folder = '/'.join(parts[:-1]) + '/' if len(parts) > 1 else ''

            for topic in topics:
                topic_lower = topic.lower()
                if topic_lower not in category_map:
                    category_map[topic_lower] = {
                        'name': topic,
                        'keywords': set(),
                        'document_count': 0,
                        'folders': set()
                    }

                category_map[topic_lower]['document_count'] += 1
                category_map[topic_lower]['folders'].add(folder)

                # 聚合关键词
                for kw in keywords:
                    category_map[topic_lower]['keywords'].add(kw.lower())

        # 转换为列表格式，按文档数排序
        categories = []
        for topic in sorted(category_map.keys(),
                           key=lambda t: category_map[t]['document_count'],
                           reverse=True):
            cat = category_map[topic]
            if cat['document_count'] >= 2:  # 至少 2 个文档才创建分类
                categories.append({
                    'name': cat['name'],
                    'keywords': list(cat['keywords'])[:15],
                    'document_count': cat['document_count'],
                    'folders': [f for f in cat['folders'] if f]
                })

        return categories[:20]  # 限制分类数量

    def scan_documents_old(self, kb_path: str) -> List[Dict]:
        """扫描文档（旧方法，保持兼容）"""
        markdown_docs, other_docs = self.scan_documents(kb_path, generate_summaries=True)
        return markdown_docs + other_docs

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

            # 兼容新旧格式
            if 'documents' in index_data:
                return len(index_data.get('documents', []))
            else:
                md_count = len(index_data.get('markdown_documents', []))
                other_count = len(index_data.get('other_documents', []))
                return md_count + other_count
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

    def extract_wikilinks(self, content: str) -> List[str]:
        """
        提取文档中的所有 wikilink

        Args:
            content: 文档内容

        Returns:
            链接目标列表（不含 #section 和 |alias）
        """
        matches = self.WIKILINK_PATTERN.findall(content)
        return [m[0].strip() for m in matches if m[0].strip()]

    def calculate_backlinks(self, documents: List[Dict]) -> Dict[str, List[str]]:
        """
        计算每个文档的反向链接

        Args:
            documents: 文档列表（每个文档需包含 'path' 和 'links' 字段）

        Returns:
            {文档路径: [引用它的文档路径列表]}
        """
        backlinks = {}

        for doc in documents:
            doc_path = doc.get('path', '')
            links = doc.get('links', [])

            for link in links:
                # 规范化链接目标
                link_target = self._normalize_link_target(link, doc_path)
                if link_target not in backlinks:
                    backlinks[link_target] = []
                backlinks[link_target].append(doc_path)

        return backlinks

    def _normalize_link_target(self, link: str, source_path: str) -> str:
        """
        规范化链接目标

        将 wikilink 转换为相对路径格式
        """
        # 移除扩展名（如果有）
        if link.endswith('.md'):
            return link

        # 尝试添加 .md 扩展名
        return f"{link}.md"

    def extract_frontmatter_tags(self, content: str) -> List[str]:
        """
        提取 YAML frontmatter 中的 tags

        Args:
            content: 文档内容

        Returns:
            标签列表
        """
        tags = []

        # 检查是否有 frontmatter
        if not content.startswith('---'):
            return tags

        parts = content.split('---', 2)
        if len(parts) < 3:
            return tags

        try:
            frontmatter = yaml.safe_load(parts[1])
            if isinstance(frontmatter, dict):
                # 支持 tags 和 tag 字段
                raw_tags = frontmatter.get('tags', frontmatter.get('tag', []))
                if isinstance(raw_tags, str):
                    tags.append(raw_tags)
                elif isinstance(raw_tags, list):
                    tags.extend(raw_tags)
        except:
            pass

        return tags

    def extract_content_tags(self, content: str) -> List[str]:
        """
        提取内容中的 #tag 格式标签

        Args:
            content: 文档内容

        Returns:
            标签列表（去重）
        """
        # 匹配 #tag 格式（排除 wikilink 中的 #section）
        pattern = r'(?<!\[\[)#([a-zA-Z\u4e00-\u9fa5][a-zA-Z0-9\u4e00-\u9fa5_]*)'
        matches = re.findall(pattern, content)
        return list(set(matches))

    # ========== 其他命令 ==========

    def search_index(self, query: str, kb_path: str, top_k: int = 10,
                     show_progress: bool = True) -> List[Dict]:
        """
        智能检索

        Args:
            query: 查询文本
            kb_path: 知识库路径
            top_k: 返回结果数量
            show_progress: 是否显示进度（文档数 > 100 时生效）

        Returns:
            排序后的结果列表
        """
        index_path = os.path.join(kb_path, "_index.yaml")

        if not os.path.exists(index_path):
            return []

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = yaml.safe_load(f)
        except:
            return []

        # 提取查询关键词
        query_keywords = self._extract_query_keywords(query)

        results = []

        # 统计文档总数（用于进度显示）
        md_docs = index_data.get('markdown_documents', [])
        other_docs = index_data.get('other_documents', [])
        total_docs = len(md_docs) + len(other_docs)

        # 初始化进度报告器（文档数 > 100 时显示）
        reporter = None
        if show_progress and total_docs > 100:
            reporter = ProgressReporter(total_docs, "检索中")

        # 统一检索 Markdown 文档
        processed = 0
        for doc in md_docs:
            score = self._calculate_relevance_score(doc, query_keywords)
            if score > 0:
                doc_copy = doc.copy()
                doc_copy['score'] = score * 1.1  # Markdown 软加权 +10%
                doc_copy['doc_type'] = 'markdown'
                results.append(doc_copy)

            processed += 1
            if reporter and processed % 10 == 0:
                reporter.update(10, f"扫描 {processed}/{total_docs}")

        # 利用 wikilink 扩展相关文档
        if results:
            results = self._expand_by_links(results, md_docs, query_keywords)

        # 检索其他格式文档
        for doc in other_docs:
            score = self._calculate_relevance_score(doc, query_keywords, is_markdown=False)
            if score > 0:
                doc_copy = doc.copy()
                doc_copy['score'] = score  # 其他格式不加权
                doc_copy['doc_type'] = doc.get('type', 'other')
                results.append(doc_copy)

            processed += 1
            if reporter and processed % 10 == 0:
                reporter.update(10, f"扫描 {processed}/{total_docs}")

        # 完成进度
        if reporter:
            reporter.complete(f"找到 {len(results)} 个匹配")

        # 兼容旧版索引格式
        if not results and 'documents' in index_data:
            for doc in index_data.get('documents', []):
                score = self._calculate_relevance_score(doc, query_keywords, is_markdown=False)
                if score > 0:
                    doc_copy = doc.copy()
                    doc_copy['score'] = score
                    doc_copy['doc_type'] = doc.get('type', 'unknown')
                    results.append(doc_copy)

        # 按分数排序，同名文件 Markdown 优先
        def sort_key(x):
            type_priority = 0 if x.get('doc_type') == 'markdown' else 1
            return (x['score'], -type_priority)

        results.sort(key=sort_key, reverse=True)

        return results[:top_k]

    def _extract_query_keywords(self, query: str) -> List[str]:
        """从查询中提取关键词"""
        # 简单实现：按空格和标点分割
        import re
        keywords = re.split(r'[\s,，、。？！;；：:\+\-\*]+', query)
        return [k.strip().lower() for k in keywords if k.strip() and len(k.strip()) > 1]

    def _calculate_relevance_score(self, doc: Dict, query_keywords: List[str],
                                   is_markdown: bool = True) -> float:
        """
        计算文档相关度分数

        权重：
        - filename: 0.4（文件名匹配）
        - path: 0.15（路径文件夹匹配，排除文件名）
        - summary: 0.3（摘要匹配）
        - keywords: 0.3（关键词匹配）
        - tags: 0.2（标签匹配）
        """
        score = 0.0

        # 文件名匹配
        filename = doc.get('filename', doc.get('path', '')).lower()
        for keyword in query_keywords:
            if keyword in filename:
                score += 0.4

        # 路径匹配（新增：文件夹路径权重）
        path = doc.get('path', '').lower()
        path_parts = [p for p in path.split('/') if p]
        for keyword in query_keywords:
            # 只匹配路径中的文件夹部分（排除文件名本身）
            for part in path_parts[:-1] if len(path_parts) > 1 else []:
                if keyword in part:
                    score += 0.15

        # 摘要匹配（仅 Markdown）
        if is_markdown:
            summary = doc.get('summary', '').lower()
            for keyword in query_keywords:
                if keyword in summary:
                    score += 0.3

            # 关键词匹配
            doc_keywords = [k.lower() for k in doc.get('keywords', [])]
            for keyword in query_keywords:
                if keyword in doc_keywords:
                    score += 0.3

            # 标签匹配
            tags = [t.lower() for t in doc.get('tags', [])]
            for keyword in query_keywords:
                if keyword in tags:
                    score += 0.2

        return score

    def _expand_by_links(self, results: List[Dict], all_docs: List[Dict],
                         query_keywords: List[str]) -> List[Dict]:
        """通过 wikilink 扩展相关文档"""
        result_paths = {r['path'] for r in results}
        expanded = []

        for result in results:
            # 查找出链文档
            links = result.get('links', [])
            for link in links:
                # 规范化链接
                link_path = self._normalize_link_target(link, result['path'])

                # 查找链接的文档
                for doc in all_docs:
                    if doc['path'] not in result_paths:
                        doc_path = doc['path']
                        # 尝试多种匹配
                        if doc_path == link_path or doc_path == link or \
                           doc_path.rsplit('.', 1)[0] == link_path.rsplit('.', 1)[0]:
                            # 计算链接文档的分数（略低）
                            link_score = self._calculate_relevance_score(doc, query_keywords)
                            if link_score > 0:
                                doc_copy = doc.copy()
                                doc_copy['score'] = (link_score * 0.5 + result['score'] * 0.1) * 1.1  # Markdown 软加权
                                doc_copy['doc_type'] = 'markdown'
                                doc_copy['linked_from'] = result['path']
                                expanded.append(doc_copy)
                                result_paths.add(doc['path'])
                            break

        results.extend(expanded)
        return results

    def search_cli(self, query: str, kb_path: str = None,
                   prefer_obsidian: bool = False, no_obsidian: bool = False):
        """
        CLI 搜索命令

        Args:
            query: 查询文本
            kb_path: 知识库路径（可选，不指定则全局搜索）
            prefer_obsidian: 优先使用 Obsidian CLI
            no_obsidian: 禁用 Obsidian CLI
        """
        print(f"\n{'='*60}")
        print(f"搜索: {query}")
        print(f"{'='*60}\n")

        # 确定搜索模式
        use_obsidian = False
        obsidian_mode = "disabled" if no_obsidian else ("prefer" if prefer_obsidian else self.obsidian_cli_mode)

        # 检查 Obsidian CLI 可用性
        if obsidian_mode != "disabled":
            if self.obsidian_cli.is_available():
                use_obsidian = True
                print("🔍 搜索模式: Obsidian CLI（原生搜索）")
            else:
                print("🔍 搜索模式: 索引检索（Obsidian CLI 不可用）")
        else:
            print("🔍 搜索模式: 索引检索（CLI 已禁用）")

        # 确定搜索范围
        if kb_path:
            kb_name = os.path.basename(kb_path)
            print(f"知识库: {kb_name}")

            # 优先尝试 Obsidian CLI 搜索
            if use_obsidian:
                obsidian_results, source = self._search_with_obsidian_cli(query, kb_path)
                if obsidian_results:
                    self._display_obsidian_results(obsidian_results, kb_path)
                    return

            # 回退到索引搜索
            results = self.search_index(query, kb_path)
        else:
            print("搜索范围: 所有知识库")

            # 全局搜索：尝试用 Obsidian CLI（不限制路径）
            if use_obsidian:
                obsidian_results, source = self._search_with_obsidian_cli(query, None)
                if obsidian_results:
                    self._display_obsidian_results(obsidian_results, None)
                    return

            # 回退到全局索引搜索
            results = []
            for kb in self.registry.get('knowledge_bases', []):
                if kb.get('status') != 'active':
                    continue
                kb_results = self.search_index(query, kb['path'])
                for r in kb_results:
                    r['kb_name'] = kb['name']
                results.extend(kb_results)

            results.sort(key=lambda x: x['score'], reverse=True)
            results = results[:10]

        if not results:
            print("\n未找到相关文档")
            return

        print(f"\n找到 {len(results)} 个相关文档:\n")

        for i, doc in enumerate(results, 1):
            kb_name = doc.get('kb_name', os.path.basename(kb_path) if kb_path else '')
            score = doc.get('score', 0)
            path = doc.get('path', '')
            summary = doc.get('summary', '')[:100] + '...' if doc.get('summary') else ''

            print(f"{i}. [{score:.2f}] {path}")
            if kb_name:
                print(f"   知识库: {kb_name}")
            if summary:
                print(f"   摘要: {summary}")
            if doc.get('keywords'):
                print(f"   关键词: {', '.join(doc['keywords'][:5])}")
            if doc.get('linked_from'):
                print(f"   关联自: {doc['linked_from']}")
            print()

    def _search_with_obsidian_cli(self, query: str, kb_path: str = None) -> Tuple[List[str], str]:
        """
        使用 Obsidian CLI 执行搜索

        Args:
            query: 查询文本
            kb_path: 知识库路径（可选）

        Returns:
            (结果列表, 来源标识)
        """
        # 转换路径格式
        search_path = None
        if kb_path:
            search_path = os.path.basename(kb_path)

        return self.obsidian_cli.search_with_fallback(query, search_path, limit=10)

    def _display_obsidian_results(self, results: List[str], kb_path: str = None):
        """
        显示 Obsidian CLI 搜索结果

        Args:
            results: Obsidian CLI 返回的文件路径列表
            kb_path: 知识库路径（用于显示）
        """
        print(f"\n找到 {len(results)} 个相关文档:\n")

        for i, path in enumerate(results, 1):
            print(f"{i}. {path}")
            if kb_path:
                full_path = os.path.join(kb_path, path) if not os.path.isabs(path) else path
                print(f"   完整路径: {full_path}")
            print()

        print("💡 提示: 使用 --no-obsidian 可切换到索引搜索模式（含相关度分数）")

    def show_info(self, kb_path: str):
        """显示知识库信息"""
        index_path = os.path.join(kb_path, "_index.yaml")

        if not os.path.exists(index_path):
            print(f"❌ 知识库未索引: {kb_path}")
            return

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = yaml.safe_load(f)
        except Exception as e:
            print(f"❌ 读取索引失败: {e}")
            return

        kb_info = index_data.get('knowledge_base', {})

        print(f"\n{'='*60}")
        print("知识库信息")
        print(f"{'='*60}\n")

        print(f"名称: {kb_info.get('name', 'N/A')}")
        print(f"路径: {kb_info.get('path', kb_path)}")
        print(f"类型: {kb_info.get('type', 'generic')}")
        print(f"Obsidian: {'是' if kb_info.get('has_obsidian') else '否'}")
        print(f"创建时间: {kb_info.get('created', 'N/A')[:19]}")
        print(f"更新时间: {kb_info.get('last_updated', 'N/A')[:19]}")

        md_docs = index_data.get('markdown_documents', [])
        other_docs = index_data.get('other_documents', [])

        print(f"\n文档统计:")
        print(f"  - Markdown: {len(md_docs)} 个")
        print(f"  - 其他格式: {len(other_docs)} 个")
        print(f"  - 总大小: {kb_info.get('total_size_mb', 0)} MB")

        # 统计链接
        if md_docs:
            total_links = sum(len(d.get('links', [])) for d in md_docs)
            total_backlinks = sum(len(d.get('backlinks', [])) for d in md_docs)
            print(f"\n链接统计:")
            print(f"  - 出链: {total_links} 个")
            print(f"  - 反向链接: {total_backlinks} 个")

            # 统计标签
            all_tags = []
            for doc in md_docs:
                all_tags.extend(doc.get('tags', []))
            if all_tags:
                from collections import Counter
                tag_counts = Counter(all_tags)
                print(f"\n热门标签:")
                for tag, count in tag_counts.most_common(10):
                    print(f"  - {tag}: {count}")

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

    # 解析通用参数
    enable_ai = "--no-ai" not in sys.argv

    manager = KnowledgeBaseManager(enable_ai_summary=enable_ai)

    if command == "build":
        if len(sys.argv) < 3:
            print("用法: python knowledge-index-manager.py build <知识库路径> [--force] [--no-ai]")
            sys.exit(1)

        kb_path = sys.argv[2]
        force = "--force" in sys.argv
        manager.build_index(kb_path, force=force)

    elif command == "update":
        if len(sys.argv) < 3:
            print("用法: python knowledge-index-manager.py update <知识库路径> [--no-ai]")
            sys.exit(1)

        kb_path = sys.argv[2]
        manager.update_index(kb_path)

    elif command == "list":
        manager.list_knowledge_bases()

    elif command == "search":
        if len(sys.argv) < 3:
            print("用法: python knowledge-index-manager.py search <查询> [--kb <知识库路径>] [--prefer-obsidian] [--no-obsidian]")
            sys.exit(1)

        query = sys.argv[2]
        kb_path = None
        prefer_obsidian = "--prefer-obsidian" in sys.argv
        no_obsidian = "--no-obsidian" in sys.argv

        if "--kb" in sys.argv:
            kb_idx = sys.argv.index("--kb")
            if kb_idx + 1 < len(sys.argv):
                kb_path = sys.argv[kb_idx + 1]

        manager.search_cli(query, kb_path, prefer_obsidian=prefer_obsidian, no_obsidian=no_obsidian)

    elif command == "info":
        if len(sys.argv) < 3:
            print("用法: python knowledge-index-manager.py info <知识库路径>")
            sys.exit(1)

        kb_path = sys.argv[2]
        manager.show_info(kb_path)

    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
