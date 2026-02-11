#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 PaddleOCR 原始识别结果格式
"""

import sys
import os

# 设置输出编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 添加 Umi-OCR 主程序、py_src 和 imports 目录到系统路径
umioocr_dir = os.path.dirname(os.path.abspath(__file__))
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

    print("插件模块导入成功")

    # 初始化 API 实例
    global_config = {
        "use_gpu": False,
        "enable_mkldnn": False,
        "cpu_threads": 4,
        "gpu_memory": 2048,
        "ram_max": -1,
        "ram_time": 30
    }

    api = api_paddleocr.Api(global_config)
    print("API 实例初始化成功")

    # 启动 OCR 引擎
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

    # 测试 runPath 方法
    print("\n测试 runPath 方法：")
    test_image_path = os.path.join(umioocr_dir, "test_image.png")

    if not os.path.exists(test_image_path):
        print(f"测试图片不存在：{test_image_path}")
        print("请在当前目录下创建一张名为 test_image.png 的图片进行测试")
    else:
        # 直接调用 PaddleOCR 实例的 ocr 方法，打印原始结果
        import numpy as np
        from PIL import Image
        import io

        print("PaddleOCR 实例：", api.api)

        try:
            # 直接调用 ocr 方法获取原始结果
            raw_result = api.api.ocr(test_image_path)
            print("原始识别结果类型：", type(raw_result))
            print("原始识别结果：", raw_result)
        except Exception as e:
            print(f"识别过程中出错：{e}")
            import traceback
            print(traceback.format_exc())

except Exception as e:
    print(f"测试失败：{e}")
    import traceback
    print(traceback.format_exc())
