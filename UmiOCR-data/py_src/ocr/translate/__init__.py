# translate: 在线翻译模块
# 提供 OCR 文本翻译功能，支持腾讯翻译和自定义 API

"""
在线翻译模块

提供 OCR 文本翻译功能，支持腾讯翻译和自定义 API。
作为 TBPU 插件集成到 OCR 流程中，在文本后处理阶段执行翻译。

使用方式：
1. 作为 TBPU 插件使用：
   from ocr.translate import TranslateTbpu, PluginInfo
   
2. 直接使用翻译引擎：
   from ocr.translate import TencentTranslateEngine
   engine = TencentTranslateEngine()
   engine.initialize({"secret_id": "...", "secret_key": "..."})
   result = engine.translate("你好", "zh", "en")
"""

from .translate_plugin import TranslateTbpu, PluginInfo
from .base import (
    TranslateEngine,
    TranslateResult,
    EngineRegistry,
    TRANSLATE_SUCCESS,
    TRANSLATE_ERROR_NETWORK,
    TRANSLATE_ERROR_API,
    TRANSLATE_ERROR_AUTH,
    TRANSLATE_ERROR_QUOTA,
    TRANSLATE_ERROR_INVALID_TEXT,
    TRANSLATE_ERROR_TIMEOUT,
    TRANSLATE_ERROR_PARSE,
    TRANSLATE_ERROR_UNKNOWN,
)


def _register_builtin_engines():
    """注册内置翻译引擎"""
    try:
        from .engines.tencent import TencentTranslateEngine
        EngineRegistry.register(TencentTranslateEngine)
    except ImportError as e:
        pass
    
    try:
        from .engines.custom import CustomTranslateEngine
        EngineRegistry.register(CustomTranslateEngine)
    except ImportError as e:
        pass


# 模块加载时自动注册引擎
_register_builtin_engines()


__all__ = [
    # 插件类
    "TranslateTbpu",
    "PluginInfo",
    # 基类
    "TranslateEngine",
    "TranslateResult",
    "EngineRegistry",
    # 错误码
    "TRANSLATE_SUCCESS",
    "TRANSLATE_ERROR_NETWORK",
    "TRANSLATE_ERROR_API",
    "TRANSLATE_ERROR_AUTH",
    "TRANSLATE_ERROR_QUOTA",
    "TRANSLATE_ERROR_INVALID_TEXT",
    "TRANSLATE_ERROR_TIMEOUT",
    "TRANSLATE_ERROR_PARSE",
    "TRANSLATE_ERROR_UNKNOWN",
]


# 延迟导入引擎类（按需导入）
def __getattr__(name: str):
    """延迟导入引擎类"""
    if name == "TencentTranslateEngine":
        from .engines.tencent import TencentTranslateEngine
        return TencentTranslateEngine
    elif name == "CustomTranslateEngine":
        from .engines.custom import CustomTranslateEngine
        return CustomTranslateEngine
    elif name == "HttpClient":
        from .utils.http_client import HttpClient
        return HttpClient
    elif name == "TencentSigner":
        from .utils.signature import TencentSigner
        return TencentSigner
    raise AttributeError(f"模块 '{__name__}' 没有属性 '{name}'")
