<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# qt_res

## Purpose
Qt/QML界面资源目录，包含所有QML界面组件、图标和主题资源。

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `images/` | 静态图片资源 |
| `images/icons/` | SVG图标文件 |
| `qml/` | QML界面组件 |

## qml/ Subdirectories

| Directory | Purpose |
|-----------|---------|
| `MainWindow/` | 主窗口管理 |
| `TabBar/` | 标签栏组件 |
| `TabPages/` | 页面组件（OCR、二维码、设置等） |
| `TabView/` | 标签视图管理 |
| `Widgets/` | 通用UI组件 |
| `Themes/` | 主题系统 |
| `Configs/` | 配置界面组件 |
| `EventBus/` | 事件总线QML绑定 |
| `ImageManager/` | 图像管理器 |
| `ApiManager/` | API管理器 |
| `Popup/` | 弹出窗口组件 |

## Key QML Files

| File | Description |
|------|-------------|
| `Main.qml` | 主界面入口 |
| `TabPages/PagesManager.qml` | 页面管理器 |

## For AI Agents

### Working In This Directory
- QML界面采用组件化设计，每个功能模块有独立的目录
- UI与Python后端通过事件总线通信
- 修改UI组件时需确保与对应的Python页面逻辑匹配

### Common Patterns
- 使用 `IconButton`、`IconTextButton` 等组件创建按钮
- 页面配置通过 `Configs` 目录下的组件处理
- 主题系统支持明暗模式切换
