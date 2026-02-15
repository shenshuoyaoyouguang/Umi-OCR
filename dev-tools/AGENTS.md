<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# dev-tools

## Purpose
开发工具目录，包含用于国际化（i18n）的工具和脚本，以及发布相关工具。

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `i18n/` | Qt国际化工具（见 `i18n/AGENTS.md`） |

## For AI Agents

### Working In This Directory
- `i18n/` 目录包含Qt翻译工具，用于生成和管理软件的国际化文件
- 开发者使用这些工具来更新翻译文件

### i18n Workflow
1. 使用 `lupdate_all.py` 从源码提取需要翻译的字符串
2. 提交到 Weblate 平台进行翻译
3. 使用 `lrelease_all.py` 将翻译好的 .ts 文件编译为 .qm 二进制文件
4. 将 .qm 文件复制到 `UmiOCR-data/i18n/` 目录
