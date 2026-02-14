# 排版解析-不做处理

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tbpu_types import TextBlocks

from umi_log import logger
from .tbpu import Tbpu


class ParserNone(Tbpu):
    """
    不做处理的排版解析器
    
    仅对文本块添加默认的结尾分隔符，不做任何排序或合并操作。
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.tbpuName: str = "排版解析-不做处理"

    def run(self, textBlocks: TextBlocks) -> TextBlocks:
        """
        处理文本块列表
        
        Args:
            textBlocks: 输入的文本块列表
            
        Returns:
            处理后的文本块列表（添加默认结尾分隔符）
        """
        try:
            # 边界检查
            if not textBlocks:
                logger.debug("ParserNone: 输入为空列表，直接返回")
                return []
            
            if not isinstance(textBlocks, list):
                logger.warning(f"ParserNone: 输入类型错误: {type(textBlocks)}，期望 list")
                return []
            
            for tb in textBlocks:
                if tb and isinstance(tb, dict) and "end" not in tb:
                    tb["end"] = "\n"  # 默认结尾间隔符为换行
            return textBlocks
            
        except Exception as e:
            logger.exception(f"ParserNone 解析器处理失败: {e}")
            return textBlocks if isinstance(textBlocks, list) else []
