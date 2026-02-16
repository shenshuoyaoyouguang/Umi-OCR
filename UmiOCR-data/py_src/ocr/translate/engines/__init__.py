# translate/engines: 翻译引擎实现模块

"""
翻译引擎实现模块

包含各种翻译 API 的具体实现。
"""

from ..base import EngineRegistry

# 延迟导入，避免循环依赖
def _register_engines():
    """注册所有内置引擎"""
    try:
        from .tencent import TencentTranslateEngine
        EngineRegistry.register(TencentTranslateEngine)
    except ImportError:
        pass
    
    try:
        from .custom import CustomTranslateEngine
        EngineRegistry.register(CustomTranslateEngine)
    except ImportError:
        pass


# 模块加载时自动注册
_register_engines()

__all__ = [
    "EngineRegistry",
]
