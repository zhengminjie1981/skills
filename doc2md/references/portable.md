# Doc2Md 便携方案

## 问题

在不同电脑和系统下使用时，依赖工具（Pandoc、MinerU）需要重复安装。

## 解决方案

### 1. 自动下载 Pandoc（推荐）

首次使用时自动下载便携版 Pandoc 到项目目录：

```bash
# 自动下载并使用便携版 Pandoc
python scripts/converter.py document.docx --auto-install --relative-images
```

下载的 Pandoc 会被保存到 `bin/pandoc/` 目录，之后无需重复下载。

### 2. 检查运行时状态

```bash
# 查看当前环境状态
python scripts/converter.py --status
```

输出示例：
```
=== Doc2Md Runtime Status ===
Project Root: /path/to/doc2md
Platform: Windows
Pandoc: ✓ E:\skills\doc2md\bin\pandoc\pandoc.exe
  Version: pandoc 3.1.11

Python Packages:
  mineru: ✗

========================================
```

### 3. 便携目录结构

```
doc2md/
├── bin/
│   └── pandoc/
│       └── pandoc.exe           # 自动下载的便携版
├── scripts/
│   ├── converter.py
│   ├── portable_runtime.py      # 便携运行时管理
│   └── mineru_converter.py
└── doc2md.bat                   # Windows 一键启动（待创建）
```

### 4. 使用流程

#### 首次使用
```bash
# 1. 检查状态
python scripts/converter.py --status

# 2. 自动安装 Pandoc
python scripts/converter.py document.docx --auto-install

# 3. 安装 MinerU（可选，用于高级 PDF 处理）
pip install mineru
```

#### 日常使用
```bash
# 直接使用（Pandoc 已在 bin 目录中）
python scripts/converter.py document.docx --relative-images

# 批量转换
python scripts/converter.py "./docs/*.pdf" -o ./output/ --relative-images
```

## 工作原理

### 优先级顺序

1. **便携版 Pandoc** (`bin/pandoc/`) - 优先使用
2. **系统 Pandoc** (`pandoc` 命令) - 降级使用
3. **自动下载** (`--auto-install`) - 按需下载

### 代码流程

```
convert_with_pandoc()
    ↓
get_pandoc_command()
    ↓
PortableRuntime.get_pandoc_executable()
    ├─ 优先返回 bin/pandoc/pandoc.exe
    └─ 降级返回 'pandoc'（系统命令）
```

## 跨平台使用

### Windows
```bash
python scripts/converter.py document.docx --auto-install
# Pandoc 下载到: bin/pandoc/pandoc.exe
```

### macOS
```bash
python scripts/converter.py document.docx --auto-install
# Pandoc 下载到: bin/pandoc/bin/pandoc
```

### Linux
```bash
python scripts/converter.py document.docx --auto-install
# Pandoc 下载到: bin/pandoc/bin/pandoc
```

## MinerU 处理

MinerU 是 Python 包，建议：

### 方案 A：全局安装（推荐）
```bash
pip install mineru
```

### 方案 B：requirements.txt
```bash
# 在项目根目录创建 requirements.txt
pip install -r requirements.txt
```

### 方案 B：虚拟环境
```bash
# 在项目目录创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install mineru
```

## 目录共享

### 同步到云端

将以下目录加入同步：
```
doc2md/
├── bin/              # ← 包含便携版 Pandoc
├── scripts/
└── .venv/            # ← 可选：虚拟环境
```

### Git 管理

建议 `.gitignore`：
```
# 便携工具（可通过 --auto-install 获取）
bin/

# 虚拟环境
.venv/
venv/

# 转换输出
media/
*.md
```

## 命令总结

| 命令 | 说明 |
|------|------|
| `--status` | 查看运行时状态 |
| `--auto-install` | 自动下载便携版 Pandoc |
| `--tool {auto\|pandoc\|mineru}` | 选择转换工具 |
| `--relative-images` | 提取图片到 media/ 文件夹 |
| `--skip-toc` | 移除目录 |

## 故障排除

### Q: 下载失败
**A**: 检查网络连接，或手动下载 Pandoc 到 `bin/` 目录

### Q: 便携版 Pandoc 无法执行
**A**:
- Windows: 添加执行权限：`icacls bin/pandoc/pandoc.exe`
- Unix: `chmod +x bin/pandoc/bin/pandoc`

### Q: MinerU 每次都要装
**A**: 使用全局安装 `pip install mineru` 或项目虚拟环境

## 未来改进

- [ ] 添加 `doc2md.bat` 和 `doc2md.sh` 一键启动脚本
- [ ] 支持 PyInstaller 打包成单文件
- [ ] Docker 镜像支持
