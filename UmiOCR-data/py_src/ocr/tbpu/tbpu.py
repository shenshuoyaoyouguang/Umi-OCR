# tbpu : text block processing unit
# 文块处理器的基类。
# OCR返回的结果中，一项包含文字、包围盒、置信度的元素，称为一个"文块" - text block 。
# 文块不一定是完整的一句话或一个段落。反之，一般是零散的文字。
# 一个OCR结果常由多个文块组成。
# 文块处理器就是：将传入的多个文块进行处理，比如合并、排序、删除文块。

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tbpu_types import TextBlocks


class Tbpu:
    """
    文块处理器基类
    
    所有排版解析器都继承自此类。
    提供统一的接口用于处理 OCR 返回的文本块列表。
    """
    
    def __init__(self) -> None:
        self.tbpu_name: str = "文块处理单元-未知"

    def run(self, text_blocks: TextBlocks) -> TextBlocks:
        """
        处理文本块列表
        
        输入：text_blocks 文块列表。例：
        [
            {'box': [[29, 19], [172, 19], [172, 44], [29, 44]], 'score': 0.89, 'text': '文本111'},
            {'box': [[29, 60], [161, 60], [161, 86], [29, 86]], 'score': 0.75, 'text': '文本222'},
        ]
        
        输出：排序后的 text_blocks 文块列表，每个块增加键：
        'end' 结尾间隔符
        
        Args:
            text_blocks: 输入的文本块列表
            
        Returns:
            处理后的文本块列表
        """
        return text_blocks
    
    def __getattr__(self, name: str) -> any:
        """
        向后兼容：处理已废弃的属性名
        """
        deprecated = {
            'tbpuName': 'tbpu_name',
        }
        if name in deprecated:
            import warnings
            warnings.warn(
                f"'{name}' 已废弃，请使用 '{deprecated[name]}'",
                DeprecationWarning,
                stacklevel=2
            )
            return getattr(self, deprecated[name])
        raise AttributeError(f"'{self.__class__.__name__}' 对象没有属性 '{name}'")
