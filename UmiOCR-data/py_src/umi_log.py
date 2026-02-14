# -*- coding: utf-8 -*-
"""
umi_log - 日志模块 Mock（用于测试）

在实际运行环境中，这个模块会被真实的日志实现替换。
此 mock 版本仅用于确保测试能够正常导入和运行。
"""

import logging
import sys

# 创建 logger
logger = logging.getLogger("umi")
logger.setLevel(logging.DEBUG)

# 创建控制台处理器
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# 导出常用方法
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical
exception = logger.exception
