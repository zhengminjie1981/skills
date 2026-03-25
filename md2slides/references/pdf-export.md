# md2slides PDF 导出指南

> 将 HTML 幻灯片导出为 PDF 时参考本文档。

---

## 主路径：html2pdf.py（推荐）

```bash
python scripts/html2pdf.py --input demo.html --output demo.pdf
```

- 每张幻灯片对应一页 PDF，1280×720px
- 依赖 playwright + Chromium

---

## 方案 A：设置下载镜像（中国网络 Chromium 下载失败时）

```bash
# Windows
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
# Linux/Mac
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/

# 然后安装
playwright install chromium
```

安装完成后重新运行主路径命令。

---

## 方案 B：MCP Playwright（已安装时）

**前提**：先用 `--inline-assets` 生成内联版 HTML（MCP Playwright 不支持 file:// 协议）

```bash
# 1. 生成内联版 HTML
python scripts/convert.py --input demo.md --output demo.html --tree slide-tree.json --inline-assets

# 2. 启动本地 HTTP 服务器
python -m http.server 8080 --directory /path/to/html/dir

# 3. 用 MCP Playwright 打开并逐页截图
#    goTo(0) ... goTo(N-1)，每页保存为 PNG

# 4. 用 Pillow 合并为 PDF
python -c "
from PIL import Image
import glob, os
pngs = sorted(glob.glob('slide_*.png'))
imgs = [Image.open(f) for f in pngs]
imgs[0].save('output.pdf', save_all=True, append_images=imgs[1:])
"
```

---

## 方案 C：手动浏览器（不依赖任何安装）

1. Chrome/Edge 打开 HTML 文件
2. `Ctrl+P` → 另存为 PDF
3. 勾选"背景图形"

> **注意**：图表（Chart.js）可能渲染不完整，适合无图表的演示文稿。

---

## 选择建议

| 情况 | 推荐方案 |
|------|---------|
| 国内网络，首次使用 | 方案 A（设置镜像后用主路径）|
| 已有 MCP Playwright | 方案 B |
| 临时用，无需安装任何东西 | 方案 C（图表可能不完整）|
| 已安装 Chromium | 直接用主路径 |

*版本: 1.0 | 最后更新: 2026-03-25*
