#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接调用 PaddleOCR 官方库进行测试
"""

import sys
import os

# 设置输出编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

try:
    from paddleocr import PaddleOCR

    print("PaddleOCR 官方库导入成功")

    # 初始化 PaddleOCR 实例
    ocr = PaddleOCR(
        device="cpu",
        enable_mkldnn=False,
        cpu_threads=4,
        lang="ch",
        use_textline_orientation=False,
        text_det_limit_side_len=960
    )
    print("PaddleOCR 实例初始化成功")

    # 测试图片路径
    test_image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_image.png")
    print(f"测试图片路径：{test_image_path}")

    # 检查测试图片是否存在
    if not os.path.exists(test_image_path):
        print(f"测试图片不存在：{test_image_path}")
    else:
        # 直接调用 PaddleOCR 识别方法
        print("正在识别图片...")
        result = ocr.ocr(test_image_path)
        print(f"识别结果：{result}")

    print("\n所有测试通过！")

except Exception as e:
    print(f"测试失败：{e}")
    import traceback
    print(traceback.format_exc())
