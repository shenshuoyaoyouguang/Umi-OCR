<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# docs

## Purpose
文档目录，包含HTTP API文档、命令行文档和软件截图说明。

## Key Files

| File | Description |
|------|-------------|
| `README_CLI.md` | 命令行调用说明 |
| `http/README.md` | HTTP API总览 |
| `http/api_doc.md` | 通用HTTP API文档 |
| `http/api_ocr.md` | OCR识别HTTP API |
| `http/api_qrcode.md` | 二维码HTTP API |
| `http/argv.md` | 命令行参数说明 |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `http/` | HTTP API文档 |
| `images/` | 软件截图和图标 |

## For AI Agents

### Working In This Directory
- `http/` 目录包含HTTP接口的详细文档
- `images/` 目录包含README中使用的软件截图
- 修改API文档时需同步更新对应的演示文件

### API Documentation
HTTP API基于Bottle框架实现，监听本地端口提供服务。详见 `http/README.md`。
