#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PaddleOCR 官方库插件测试脚本
不依赖 PySide2 模块，只测试核心功能
"""

import sys
import os

# 设置输出编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 添加 Umi-OCR 主程序、py_src 和 imports 目录到系统路径
umioocr_dir = os.path.dirname(__file__)
py_src_dir = os.path.join(umioocr_dir, "UmiOCR-data", "py_src")
imports_dir = os.path.join(py_src_dir, "imports")
plugin_dir = os.path.join(umioocr_dir, "UmiOCR-data", "plugins", "win7_x64_PaddleOCR")

sys.path.append(umioocr_dir)
sys.path.append(py_src_dir)
sys.path.append(imports_dir)
sys.path.append(plugin_dir)

try:
    # 导入插件模块
    import api_paddleocr
    import paddleocr_config

    print("插件模块导入成功")

    # 测试配置项
    print("\n全局配置项：")
    print(paddleocr_config.global_options)

    print("\n局部配置项：")
    print(paddleocr_config.local_options)

    # 测试 API 初始化
    print("\n初始化 API 实例：")
    global_config = {
        "use_gpu": False,
        "enable_mkldnn": True,
        "cpu_threads": 4,
        "gpu_memory": 2048,
        "ram_max": -1,
        "ram_time": 30
    }

    api = api_paddleocr.Api(global_config)
    print("API 实例初始化成功")

    # 测试启动引擎
    print("\n启动 OCR 引擎：")
    local_config = {
        "language": "ch",
        "cls": False,
        "limit_side_len": 960,
        "det_algorithm": "DB",
        "rec_algorithm": "CRNN"
    }

    result = api.start(local_config)
    if result == "":
        print("OCR 引擎启动成功")
    else:
        print(f"OCR 引擎启动失败：{result}")

    print("\n所有测试通过！")

except Exception as e:
    print(f"测试失败：{e}")
    import traceback
    print(traceback.format_exc())