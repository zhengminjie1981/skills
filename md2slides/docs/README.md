# md2slides 文档导航

> 文档版本：v0.5 | 最后更新：2026-03-24

## 文档列表

| 文档 | 层级 | 描述 |
|------|------|------|
| [requirements.md](requirements.md) | L1 系统级 | 功能需求与设计目标 |
| [design.md](design.md) | L2 详细设计 | 架构、模块、数据结构、HTML模板、主题、图表、PDF转换 |
| [user-manual.md](user-manual.md) | L3 用户文档 | 使用场景、操作方法、快速参考 |

## 项目概述

md2slides 是一个 Claude Code skill，帮助用户将原始材料或文档转换为 HTML 格式的演示文稿。采用两阶段工作流：先由 AI 策划 MD 内容（明确分页、提取数据），再生成 HTML；支持数据图表（Chart.js）、键盘导航、页码显示、元素级调整和 HTML→PDF 导出。

## 进展记录

| 日期 | 阶段 | 状态 | 备注 |
|------|------|------|------|
| 2026-03-23 | 需求文档 v0.1 | ✅ 完成 | 基于 reveal.js 的初稿 |
| 2026-03-24 | 需求文档 v0.2 | ✅ 完成 | 重构：两阶段工作流、元素树、PDF 导出 |
| 2026-03-24 | 需求文档 v0.3 | ✅ 完成 | 新增数据可视化需求 |
| 2026-03-24 | 详细设计文档 v1.0 | ✅ 完成 | 架构、模块、模板、主题、图表、PDF |
| 2026-03-24 | 用户手册 v1.0 | ✅ 完成 | 5个使用场景、操作说明、主题/图表参考 |
| 2026-03-24 | 需求变更：内容变更功能 | ✅ 完成 | 同步更新 requirements v0.4、design v1.1、手册 v1.1 |
| 2026-03-24 | 实现 v1.0 | ✅ 完成 | convert.py + html2pdf.py + 5主题 + 元素树 + preserve-styles |
| 2026-03-24 | 验收测试 | ✅ 完成 | 场景A-F全部通过，示例文件：examples/q4-report.md |
| 2026-03-24 | Bug 修复 v1.1 | ✅ 完成 | dataSource/dataFile 兼容、flex min-height、adjustSlideSpacing、highlight.js UMD |
| 2026-03-24 | CDN 优化 | ✅ 完成 | 默认改用 bootcdn.cn（中国网络友好）+ --inline-assets 离线化选项 |
