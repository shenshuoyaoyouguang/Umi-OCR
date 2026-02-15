<!-- Parent: ../../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# server

## Purpose
HTTP服务器模块，基于Bottle框架提供Web API接口。

## Key Files

| File | Description |
|------|-------------|
| `bottle.py` | Bottle框架（第三方库） |
| `ocr_server.py` | OCR识别HTTP接口 |
| `qrcode_server.py` | 二维码识别HTTP接口 |
| `web_server.py` | Web服务器启动和管理 |
| `cmd_server.py` | 命令行服务器 |
| `cmd_client.py` | 命令行客户端 |

## For AI Agents

### Working In This Directory
- HTTP服务器监听本地端口，提供外部调用接口
- 支持OCR识别、二维码识别、通用API等
- 详细API文档见 `docs/http/` 目录

### API Endpoints
- `/ocr` - OCR识别
- `/qrcode` - 二维码识别
- `/doc` - 文档识别
- `/info` - 服务信息
