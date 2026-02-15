<!-- Parent: ../../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# ocr

## Purpose
OCR识别核心模块，包含OCR API接口、输出格式处理和文本后处理（TBPU）。

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `api/` | OCR API接口 |
| `output/` | 输出格式处理模块 |
| `tbpu/` | 文本后处理模块（排版解析、忽略区域等） |

## Key Files

| File | Description |
|------|-------------|
| `tbpu/tbpu.py` | TBPU后处理基类 |
| `tbpu/tbpu_types.py` | TBPU数据类型定义 |

## For AI Agents

### Module Architecture

#### api/
OCR引擎API封装，对接RapidOCR-json等OCR库。

#### output/
输出格式处理，支持多种导出格式：
- `output_txt.py` - 纯文本
- `output_jsonl.py` - JSONL格式
- `output_csv.py` - CSV表格
- `output_md.py` - Markdown
- `output_pdf_*.py` - PDF文件

#### tbpu/
文本后处理（Text Post-Processing Unit），包括：
- 排版解析（行/段落/代码识别）
- 忽略区域处理
- 文本格式化
