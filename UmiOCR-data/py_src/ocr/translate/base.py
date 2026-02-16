# translate/base.py: 翻译引擎基类和错误码定义

"""
翻译引擎基类和类型定义

定义翻译引擎的抽象接口、结果类型和错误码常量。
所有翻译引擎实现都应继承 TranslateEngine 基类。
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


# ===============================================
# 错误码定义
# ===============================================

TRANSLATE_SUCCESS = 100           # 成功
TRANSLATE_ERROR_NETWORK = 201     # 网络错误
TRANSLATE_ERROR_API = 202         # API 返回错误
TRANSLATE_ERROR_AUTH = 203        # 认证失败（密钥错误）
TRANSLATE_ERROR_QUOTA = 204       # 配额不足
TRANSLATE_ERROR_INVALID_TEXT = 205  # 文本无效（空文本等）
TRANSLATE_ERROR_TIMEOUT = 206     # 请求超时
TRANSLATE_ERROR_PARSE = 207       # 响应解析失败
TRANSLATE_ERROR_UNKNOWN = 299     # 未知错误


# ===============================================
# 结果类型定义
# ===============================================

@dataclass
class TranslateResult:
    """
    翻译结果数据类
    
    封装翻译操作的结果，包含原文、译文、状态码和错误信息。
    """
    
    code: int                           # 状态码
    original_text: str                  # 原文
    translated_text: str                # 译文（失败时为空字符串）
    source: str                         # 引擎标识
    error_message: str = ""             # 错误信息
    
    def is_success(self) -> bool:
        """判断翻译是否成功"""
        return self.code == TRANSLATE_SUCCESS
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "code": self.code,
            "original_text": self.original_text,
            "translated_text": self.translated_text,
            "source": self.source,
            "error_message": self.error_message,
        }


# ===============================================
# 语言代码映射
# ===============================================

# 常用语言代码
LANGUAGE_CODES = {
    "zh": "中文",
    "en": "英语",
    "ja": "日语",
    "ko": "韩语",
    "fr": "法语",
    "de": "德语",
    "es": "西班牙语",
    "ru": "俄语",
    "pt": "葡萄牙语",
    "it": "意大利语",
    "vi": "越南语",
    "th": "泰语",
    "ar": "阿拉伯语",
    "auto": "自动检测",
}


# ===============================================
# 翻译引擎基类
# ===============================================

class TranslateEngine(ABC):
    """
    翻译引擎抽象基类
    
    所有翻译引擎实现都必须继承此类并实现抽象方法。
    提供统一的翻译接口，支持配置初始化和语言列表查询。
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        引擎名称标识
        
        Returns:
            引擎的唯一标识符，如 "tencent", "baidu"
        """
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """
        引擎显示名称
        
        Returns:
            用于 UI 显示的名称，如 "腾讯翻译君"
        """
        pass
    
    @abstractmethod
    def translate(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str
    ) -> TranslateResult:
        """
        执行翻译
        
        Args:
            text: 待翻译文本
            source_lang: 源语言代码（如 "zh", "en", "auto"）
            target_lang: 目标语言代码
            
        Returns:
            TranslateResult 实例
        """
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化引擎
        
        Args:
            config: 配置字典，包含 API 密钥等
            
        Returns:
            初始化是否成功
        """
        pass
    
    def get_supported_languages(self) -> List[str]:
        """
        获取支持的语言列表
        
        Returns:
            语言代码列表，如 ["zh", "en", "ja", "ko"]
        """
        return ["zh", "en", "ja", "ko", "auto"]
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置是否有效
        
        Args:
            config: 配置字典
            
        Returns:
            配置是否有效
        """
        return bool(config)
    
    def shutdown(self) -> None:
        """
        关闭引擎，释放资源
        
        子类可重写此方法以执行清理操作。
        """
        pass


# ===============================================
# 引擎注册表
# ===============================================

class EngineRegistry:
    """
    翻译引擎注册表
    
    管理所有可用的翻译引擎，支持动态注册和获取。
    """
    
    _engines: Dict[str, type] = {}
    
    @classmethod
    def register(cls, engine_class: type) -> None:
        """
        注册引擎类
        
        Args:
            engine_class: 翻译引擎类（必须继承 TranslateEngine）
        """
        if not issubclass(engine_class, TranslateEngine):
            raise TypeError(f"{engine_class} 必须继承 TranslateEngine")
        
        # 创建临时实例获取名称
        instance = engine_class()
        cls._engines[instance.name] = engine_class
    
    @classmethod
    def get(cls, name: str) -> Optional[type]:
        """
        获取引擎类
        
        Args:
            name: 引擎名称标识
            
        Returns:
            引擎类，不存在返回 None
        """
        return cls._engines.get(name)
    
    @classmethod
    def get_all(cls) -> Dict[str, type]:
        """
        获取所有已注册的引擎类
        
        Returns:
            引擎名称到引擎类的映射
        """
        return cls._engines.copy()
    
    @classmethod
    def create_instance(cls, name: str) -> Optional[TranslateEngine]:
        """
        创建引擎实例
        
        Args:
            name: 引擎名称标识
            
        Returns:
            引擎实例，不存在返回 None
        """
        engine_class = cls.get(name)
        if engine_class:
            return engine_class()
        return None
