<!-- Parent: ../../../../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# ocr/tbpu/parser_tools

## Purpose
TBPU解析工具模块，提供排版解析和文本预处理的共享辅助函数。

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | 模块入口 |
| `line_preprocessing.py` | 行预处理 |
| `paragraph_parse.py` | 段落解析 |
| `gap_tree.py` | 间距树（用于布局分析） |
| `tbpu_config.py` | TBPU配置 |

## For AI Agents

### Working In This Directory
- 包含TBPU解析器共用的工具函数
- `paragraph_parse.py` - 段落边界检测
- `line_preprocessing.py` - 文本行预处理
- `gap_tree.py` - 基于间距的布局分析算法
