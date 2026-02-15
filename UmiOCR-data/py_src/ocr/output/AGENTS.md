<!-- Parent: ../../../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# ocr/output

## Purpose
OCR输出格式处理模块，支持将识别结果导出为多种格式。

## Key Files

| File | Description |
|------|-------------|
| `output.py` | 输出基类 |
| `tools.py` | 输出工具函数 |

## Output Formats

| File | Description |
|------|-------------|
| `output_txt.py` | 纯文本输出 |
| `output_txt_plain.py` | 纯文本（无格式） |
| `output_txt_individual.py` | 单文件输出 |
| `output_jsonl.py` | JSONL格式 |
| `output_csv.py` | CSV表格 |
| `output_md.py` | Markdown格式 |
| `output_pdf_one_layer.py` | 单层PDF |
| `output_pdf_layered.py` | 双层可搜索PDF |

## For AI Agents

### Working In This Directory
- 每种输出格式对应一个输出类，继承自基类
- 支持批量导出和单文件导出
- PDF输出支持文本层和图像层分离
