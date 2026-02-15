<!-- Parent: ../../../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# ocr/tbpu

## Purpose
TBPU (Text Post-Processing Unit) 文本后处理模块，对OCR识别结果进行排版解析、格式化和过滤。

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `parser_tools/` | 解析工具模块 |

## Key Files

| File | Description |
|------|-------------|
| `tbpu.py` | TBPU基类 |
| `tbpu_types.py` | TBPU数据类型定义 |
| `ignore_area.py` | 忽略区域处理 |
| `parser_*.py` | 各种解析器 |

## Parser Types

| File | Description |
|------|-------------|
| `parser_none.py` | 无处理 |
| `parser_single_none.py` | 单行无处理 |
| `parser_single_line.py` | 单行按行分割 |
| `parser_single_para.py` | 单行按段落分割 |
| `parser_single_code.py` | 单行代码识别 |
| `parser_multi_none.py` | 多行无处理 |
| `parser_multi_line.py` | 多行按行分割 |
| `parser_multi_para.py` | 多行按段落分割 |

## For AI Agents

### Working In This Directory
- TBPU是插件化的，每个解析器都是独立的处理单元
- 解析器支持串联使用
- `parser_tools/` 目录包含共享的解析辅助函数

### Processing Flow
1. OCR识别原始结果
2. 忽略区域过滤
3. 排版解析（行/段落/代码）
4. 格式化输出
