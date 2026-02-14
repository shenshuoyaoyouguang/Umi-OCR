# ===============================================
# =============== 插件管理器模块 ===============
# ===============================================

"""
插件管理器模块

提供各类插件的统一管理接口，包括：
- OCR 插件管理器
- 输出插件管理器
- 后处理插件管理器
- 图像处理插件管理器
"""

from .base_manager import PluginGroupManager
from .ocr_manager import OcrPluginManager
from .output_manager import OutputPluginManager
from .tbpu_manager import TbpuPluginManager
from .image_manager import ImagePluginManager

# 兼容旧接口的导出
from .ocr_manager import (
    initOcrPlugins,
    getApiOcr,
    getLocalOptions,
    ApiDict,
    AllDict,
)
from .tbpu_manager import (
    getParser,
    Parser,
    get_available_parsers,
    has_parser,
)

__all__ = [
    # 基类
    "PluginGroupManager",
    # 具体管理器
    "OcrPluginManager",
    "OutputPluginManager",
    "TbpuPluginManager",
    "ImagePluginManager",
    # OCR 兼容接口
    "initOcrPlugins",
    "getApiOcr",
    "getLocalOptions",
    "ApiDict",
    "AllDict",
    # TBPU 兼容接口
    "getParser",
    "Parser",
    "get_available_parsers",
    "has_parser",
]
