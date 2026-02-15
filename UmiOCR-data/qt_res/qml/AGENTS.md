<!-- Parent: ../../../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# qt_res/qml

## Purpose
QML界面组件目录，包含所有用户界面组件，按功能模块组织。

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `MainWindow/` | 主窗口管理 |
| `TabBar/` | 标签栏组件 |
| `TabPages/` | 功能页面（OCR、二维码、设置等） |
| `TabView/` | 标签视图 |
| `Widgets/` | 通用UI组件库 |
| `Themes/` | 主题系统 |
| `Configs/` | 配置界面组件 |
| `EventBus/` | 事件总线QML绑定 |
| `ImageManager/` | 图像管理器 |
| `ApiManager/` | API管理器 |
| `Popup/` | 弹出窗口组件 |

## For AI Agents

### Working In This Directory
- QML界面采用组件化设计
- 页面逻辑在Python端（`tag_pages/`），QML负责展示
- 事件总线连接Python和QML层
- 主题系统支持明暗模式

### UI Architecture
- `Main.qml` - 应用入口
- `TabPages/PagesManager.qml` - 页面管理器
- 每个TabPage有对应的QML和Python文件
