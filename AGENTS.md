<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# Umi-OCR

## Purpose
免费、开源、可批量的离线OCR软件，适用于 Windows 7 x64 和 Linux x64。支持截图OCR、批量OCR、PDF识别、二维码识别和公式识别。

## Key Files

| File | Description |
|------|-------------|
| `README.md` | 项目主文档（中文） |
| `README_en.md` | 项目英文文档 |
| `CHANGE_LOG.md` | 更新日志 |
| `LICENSE` | MIT开源许可证 |
| `UmiOCR-data/main.py` | 主程序入口 |
| `UmiOCR-data/py_src/run.py` | 运行入口 |
| `dev-tools/` | 开发工具目录 |
| `docs/` | 文档目录 |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `UmiOCR-data/` | 主程序数据和源码（见 `UmiOCR-data/AGENTS.md`） |
| `dev-tools/` | 开发工具（i18n国际化工具）（见 `dev-tools/AGENTS.md`） |
| `docs/` | 文档目录（API文档、截图说明）（见 `docs/AGENTS.md`） |
| `.github/ISSUE_TEMPLATE/` | GitHub Issue模板 |

## For AI Agents

### Working In This Directory
- 这是一个完整的Qt/QML + Python OCR应用项目
- 主要代码在 `UmiOCR-data/` 目录下
- `UmiOCR-data/py_src/` 包含所有Python源码
- `UmiOCR-data/qt_res/` 包含QML界面资源
- 开发前请阅读 `README.md` 中的构建说明

### Project Architecture
- **前端**: Qt/QML 界面
- **后端**: Python 3.x
- **OCR引擎**: RapidOCR-json (基于ONNX Runtime)
- **HTTP服务**: 内置Bottle服务器
- **插件系统**: 支持扩展OCR引擎、输出格式、TBPU后处理

### Common Commands
```powershell
# 运行开发版本
python UmiOCR-data/main.py
```

## Dependencies

### External
- Python 3.8+
- Qt 5.x (通过PySide2)
- RapidOCR-json (ONNX Runtime)
- Pillow (图像处理)

<!-- MANUAL: -->
