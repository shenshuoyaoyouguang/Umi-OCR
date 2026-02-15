<!-- Parent: ../../AGENTS.md -->
<!-- Generated: 2026-02-15 | Updated: 2026-02-15 -->

# mission

## Purpose
任务管理模块，处理OCR识别、二维码、文档识别等任务的调度和执行。

## Key Files

| File | Description |
|------|-------------|
| `mission.py` | 任务基类 |
| `mission_ocr.py` | OCR识别任务 |
| `mission_qrcode.py` | 二维码识别任务 |
| `mission_doc.py` | 文档识别任务 |
| `mission_queue.py` | 任务队列管理 |
| `simple_mission.py` | 简单任务封装 |

## For AI Agents

### Working In This Directory
- 所有识别任务都继承自 `Mission` 基类
- 任务通过队列调度，支持并发处理
- 任务结果通过事件总线通知上层

### Task Flow
1. 创建任务实例（OCR/二维码/文档）
2. 添加到任务队列
3. 执行识别
4. 输出结果
5. 触发完成事件
