<!-- Parent: ../../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# dev-tools/i18n

## Purpose
Qt国际化工具目录，包含用于提取、编译和管理Qt应用翻译文件的脚本和工具。

## Key Files

| File | Description |
|------|-------------|
| `lupdate_all.py` | 从源码提取需要翻译的字符串 |
| `lrelease_all.py` | 编译.ts文件为.qm二进制文件 |
| `convert_ts_txt.py` | .ts转.txt转换器 |
| `convert_txt_ts.py` | .txt转.ts转换器 |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `plugins/` | Qt插件（平台和样式） |
| `release/` | 翻译源文件(.ts) |

## For AI Agents

### Working In This Directory
- 使用Qt的lupdate、lrelease工具管理翻译
- 翻译工作流程：
  1. 运行 `lupdate_all.py` 从源码提取字符串
  2. 在Weblate平台翻译
  3. 运行 `lrelease_all.py` 编译翻译
  4. 将.qm文件复制到 `UmiOCR-data/i18n/`

### Translation Files
翻译源文件(.ts)在 `release/` 目录，包括：ar.ts, en_US.ts, es.ts, fa.ts, fr_FR.ts, he.ts, ja_JP.ts, kab.ts, ko_KR.ts, pt.ts, ru_RU.ts, ta.ts, uz.ts, vi.ts, zh_TW.ts
