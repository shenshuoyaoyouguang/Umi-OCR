<!-- Parent: ../../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# tag_pages

## Purpose
页面标签模块，包含各功能页面的Python逻辑，与QML界面一一对应。

## Key Files

| File | Description |
|------|-------------|
| `page.py` | 页面基类 |
| `ScreenshotOCR.py` | 截图OCR页面 |
| `BatchOCR.py` | 批量OCR页面 |
| `BatchDOC.py` | 文档识别页面 |
| `QRCode.py` | 二维码页面 |
| `tag_pages_connector.py` | 页面连接器 |

## For AI Agents

### Working In This Directory
- 每个页面类对应一个QML界面组件
- 页面通过事件总线与后端模块通信
- 页面配置通过配置管理器持久化

### Page Types
- `ScreenshotOCR` - 实时截图识别
- `BatchOCR` - 批量图片OCR
- `BatchDOC` - PDF/文档OCR
- `QRCode` - 二维码识别/生成
