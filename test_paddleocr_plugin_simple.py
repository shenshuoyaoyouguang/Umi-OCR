#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PaddleOCR 官方库插件简单测试脚本
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
    # 导入插件配置模块
    import paddleocr_config

    print("Plugin config module imported successfully")

    # 测试配置项
    print("\nGlobal options:")
    print(paddleocr_config.global_options)

    print("\nLocal options:")
    print(paddleocr_config.local_options)

    # 测试获取最佳线程数函数
    print("\nOptimal threads:")
    from paddleocr_config import _get_threads
    print(f"Optimal threads: {_get_threads()}")

    # 测试 i18n 国际化
    print("\nInternationalization support:")
    from plugin_i18n import Translator, setLangCode

    # 测试中文
    setLangCode("zh_CN")
    tr = Translator(paddleocr_config.__file__, "i18n.csv")
    print(f"Chinese: {tr('PaddleOCR（官方库）')}")

    # 测试英文
    setLangCode("en_US")
    tr = Translator(paddleocr_config.__file__, "i18n.csv")
    print(f"English: {tr('PaddleOCR（官方库）')}")

    # 测试日文
    setLangCode("ja_JP")
    tr = Translator(paddleocr_config.__file__, "i18n.csv")
    print(f"Japanese: {tr('PaddleOCR（官方库）')}")

    # 测试是否已安装 paddleocr 库
    print("\nPaddleOCR library check:")
    try:
        import paddleocr
        print("PaddleOCR library installed")
        print(f"Version: {paddleocr.__version__}")
    except ImportError:
        print("PaddleOCR library not installed, please use pip install paddleocr command")

    print("\nAll core functions tested successfully!")

except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    print(traceback.format_exc())