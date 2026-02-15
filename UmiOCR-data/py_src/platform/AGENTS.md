<!-- Parent: ../../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# platform

## Purpose
平台特定代码模块，处理不同操作系统间的API差异。

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `win32/` | Windows平台特定代码 |
| `linux/` | Linux平台特定代码 |

## For AI Agents

### Working In This Directory
- `win32/` - Windows API封装（键盘钩子、系统托盘等）
- `linux/` - Linux平台适配
- 通过平台检测动态加载对应模块
