<!-- Parent: ../../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# plugins_controller

## Purpose
插件控制系统，管理OCR引擎插件、输出插件、TBPU插件和图像处理插件。

## Key Files

| File | Description |
|------|-------------|
| `base_plugin.py` | 插件基类 |
| `plugins_controller.py` | 插件控制器 |
| `plugin_group.py` | 插件组 |
| `config_manager.py` | 配置管理器 |
| `dependency_resolver.py` | 依赖解析器 |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `managers/` | 各类插件管理器 |

## For AI Agents

### Working In This Directory
- 插件系统采用管理器模式，每种插件类型有专门的管理器
- 插件支持热插拔，可在运行时加载/卸载
- 插件间可能有依赖关系，通过依赖解析器处理

### Plugin Types

#### managers/
- `ocr_manager.py` - OCR引擎插件管理
- `output_manager.py` - 输出格式插件管理
- `tbpu_manager.py` - TBPU后处理插件管理
- `image_manager.py` - 图像处理插件管理
- `base_manager.py` - 管理器基类
