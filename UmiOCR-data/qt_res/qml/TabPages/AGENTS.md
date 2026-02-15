<!-- Parent: ../../../../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# qml/TabPages

## Purpose
功能页面组件目录，包含OCR、二维码、文档识别等功能的QML界面。

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `About/` | 关于页面 |
| `BatchDOC/` | 文档识别页面 |
| `BatchOCR/` | 批量OCR页面 |
| `GlobalConfigsPage/` | 全局设置页面 |
| `Navigation/` | 导航页面 |
| `QRCode/` | 二维码页面 |
| `ScreenshotOCR/` | 截图OCR页面 |

## Key Files

| File | Description |
|------|-------------|
| `TabPage.qml` | 页面基类 |
| `PagesManager.qml` | 页面管理器 |

## For AI Agents

### Working In This Directory
- 每个功能模块有独立的目录
- 页面QML与Python端 `tag_pages/` 对应
- 包含页面布局和交互逻辑
