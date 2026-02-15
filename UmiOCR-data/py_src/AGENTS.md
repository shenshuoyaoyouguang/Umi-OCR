<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# py_src

## Purpose
Python源码目录，包含Umi-OCR的所有业务逻辑。按功能模块划分为多个子目录。

## Key Files

| File | Description |
|------|-------------|
| `run.py` | 运行入口 |
| `umi_log.py` | 日志模块 |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `event_bus/` | 事件总线系统（发布/订阅） |
| `image_controller/` | 图像处理和截图控制 |
| `imports/` | 通用导入和工具 |
| `mission/` | 任务管理（OCR、二维码、文档识别） |
| `ocr/` | OCR识别核心模块 |
| `platform/` | 平台特定代码（Windows/Linux） |
| `plugins_controller/` | 插件控制系统 |
| `server/` | HTTP服务器（Bottle） |
| `tag_pages/` | 页面标签（UI页面逻辑） |
| `utils/` | 工具函数 |

## For AI Agents

### Working In This Directory
- 这是一个复杂的Python项目，模块间通过事件总线进行通信
- 修改核心模块前请先了解事件总线机制
- 插件系统架构允许扩展OCR引擎和输出格式

### Module Architecture

#### event_bus/
事件发布/订阅系统，模块间通信的基础设施。
- `pubsub_service.py` - 发布订阅服务
- `key_mouse/` - 键盘鼠标事件处理

#### mission/
任务管理模块，处理OCR、二维码、文档识别等任务。
- `mission.py` - 任务基类
- `mission_ocr.py` - OCR任务
- `mission_qrcode.py` - 二维码任务
- `mission_doc.py` - 文档识别任务
- `mission_queue.py` - 任务队列

#### ocr/
OCR识别核心模块。
- `api/` - OCR API接口
- `output/` - 输出格式处理（txt, json, csv, pdf等）
- `tbpu/` - 文本后处理（排版解析、忽略区域等）

#### plugins_controller/
插件控制系统。
- `base_plugin.py` - 插件基类
- `plugins_controller.py` - 插件管理器
- `managers/` - 各类管理器（OCR、输出、TBPU、图像）

#### server/
HTTP服务器模块，基于Bottle框架。
- `ocr_server.py` - OCR HTTP接口
- `qrcode_server.py` - 二维码HTTP接口
- `web_server.py` - Web服务启动

#### tag_pages/
UI页面逻辑，对应QML界面。
- `ScreenshotOCR.py` - 截图OCR页面
- `BatchOCR.py` - 批量OCR页面
- `BatchDOC.py` - 文档识别页面
- `QRCode.py` - 二维码页面
