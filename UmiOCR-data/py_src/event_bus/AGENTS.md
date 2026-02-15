<!-- Parent: ../../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# event_bus

## Purpose
事件总线系统，提供发布/订阅模式的模块间通信机制。

## Key Files

| File | Description |
|------|-------------|
| `pubsub_service.py` | 发布订阅服务核心 |
| `pubsub_connector.py` | 发布订阅连接器 |
| `key_mouse/keyboard.py` | 键盘事件处理 |
| `key_mouse/key_mouse_connector.py` | 键鼠连接器 |

## For AI Agents

### Working In This Directory
- 这是应用的事件基础设施，所有模块通过它进行松耦合通信
- Python端和QML端都使用相同的事件总线
- 发布事件使用 `publish()`，订阅使用 `subscribe()`

### Event Patterns
- `OCR_TASK_START` - OCR任务开始
- `OCR_TASK_DONE` - OCR任务完成
- `CONFIG_CHANGED` - 配置变更
- `IMAGE_LOADED` - 图像加载完成
