# text_postproc : 文本后处理模块
# ===============================================
# 提供OCR文本后处理功能（保留数字、半全角转换、文本纠错等）
# 与排版解析模块(tbpu)串行执行
# ===============================================

"""
文本后处理模块

该模块提供OCR识别后的文本处理功能：
- 保留数字：提取文本中的数字
- 半全角转换：全角/半角字符转换
- 文本纠错：OCR常见错误纠正

执行流程：
    OCR结果 -> 忽略区域 -> 排版解析 -> 文本后处理 -> 最终输出
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional, List, Type

if TYPE_CHECKING:
    from .base import TextPostProcessor
    from ..tbpu.tbpu_types import TextBlocks

# 导入日志模块
from umi_log import logger

# ===============================================
# 处理器基类导入
# ===============================================

from .base import TextPostProcessor

# ===============================================
# 处理器实现导入
# ===============================================

from .filter_digits import FilterDigits
from .convert_width import ConvertWidth
from .correct_ocr import CorrectOcr

# ===============================================
# 处理器注册表
# ===============================================

# 内置处理器注册表
_builtInProcessors: Dict[str, Type[TextPostProcessor]] = {
    "filter_digits": FilterDigits,
    "convert_width": ConvertWidth,
    "correct_ocr": CorrectOcr,
}


# ===============================================
# 兼容字典（动态代理）
# ===============================================

class _ProcessorDict(dict):
    """
    处理器字典类 - 动态代理到内置注册表
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: str) -> Type[TextPostProcessor]:
        """获取处理器类"""
        if key in _builtInProcessors:
            return _builtInProcessors[key]
        raise KeyError(f"未知的后处理器: {key}")

    def __contains__(self, key: object) -> bool:
        """检查是否存在指定的处理器"""
        return key in _builtInProcessors

    def keys(self) -> List[str]:
        """获取所有处理器名称"""
        return list(_builtInProcessors.keys())

    def get(self, key: str, default: Any = None) -> Any:
        """安全获取处理器类"""
        return _builtInProcessors.get(key, default)


# 创建处理器字典实例
Processor: _ProcessorDict = _ProcessorDict()


# ===============================================
# 公开函数
# ===============================================

def get_processor(name: str, **kwargs) -> Optional[TextPostProcessor]:
    """
    获取处理器实例

    Args:
        name: 处理器名称
        **kwargs: 处理器初始化参数

    Returns:
        处理器实例，不存在返回 None
    """
    if name in _builtInProcessors:
        return _builtInProcessors[name](**kwargs)
    logger.warning(f"未知的后处理器: {name}")
    return None


def get_processor_names() -> List[str]:
    """获取所有处理器名称"""
    return list(_builtInProcessors.keys())


def create_chain(processor_configs: List[Dict[str, Any]]) -> List[TextPostProcessor]:
    """
    根据配置创建处理器链

    Args:
        processor_configs: 处理器配置列表
            [{"name": "filter_digits", "params": {...}}, ...]

    Returns:
        处理器实例列表
    """
    chain: List[TextPostProcessor] = []
    for config in processor_configs:
        name = config.get("name")
        params = config.get("params", {})
        processor = get_processor(name, **params)
        if processor:
            chain.append(processor)
        else:
            logger.warning(f"无法创建处理器: {name}")
    return chain


def run_chain(text_blocks: "TextBlocks", chain: List[TextPostProcessor]) -> "TextBlocks":
    """
    在文本块上执行处理器链

    Args:
        text_blocks: 文本块列表
        chain: 处理器链

    Returns:
        处理后的文本块列表
    """
    if not chain or not text_blocks:
        return text_blocks

    result = text_blocks
    for processor in chain:
        try:
            result = processor.run(result)
        except Exception as e:
            logger.error(f"处理器 {processor.name} 执行失败: {e}")

    return result


# ===============================================
# 导出列表
# ===============================================

__all__ = [
    # 基类
    "TextPostProcessor",
    # 处理器实现
    "FilterDigits",
    "ConvertWidth",
    "CorrectOcr",
    # 注册表和函数
    "Processor",
    "get_processor",
    "get_processor_names",
    "create_chain",
    "run_chain",
]
