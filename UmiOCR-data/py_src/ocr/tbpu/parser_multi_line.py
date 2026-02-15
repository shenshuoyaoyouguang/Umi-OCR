# 排版解析-多栏-单行

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tbpu_types import TextBlocks

from umi_log import logger
from .tbpu import Tbpu
from .parser_tools.line_preprocessing import line_preprocessing  # 行预处理
from .parser_tools.gap_tree import GapTree  # 间隙树排序算法


class MultiLine(Tbpu):
    """
    多栏-单行 排版解析器
    
    适用于多栏版面（如报纸、杂志），每行后强制换行。
    使用间隙树算法进行版面分析。
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.tbpu_name: str = "排版解析-多栏-单行"

        # 构建算法对象，指定包围盒的元素位置
        self.gtree: GapTree = GapTree(lambda tb: tb["normalized_bbox"])

    def run(self, text_blocks: TextBlocks) -> TextBlocks:
        """
        处理文本块列表
        
        Args:
            text_blocks: 输入的文本块列表
            
        Returns:
            处理后的文本块列表
        """
        try:
            # 边界检查
            if not text_blocks:
                logger.debug("MultiLine: 输入为空列表，直接返回")
                return []
            
            if not isinstance(text_blocks, list):
                logger.warning(f"MultiLine: 输入类型错误: {type(text_blocks)}，期望 list")
                return []
            
            text_blocks = line_preprocessing(text_blocks)  # 预处理
            
            if not text_blocks:
                logger.debug("MultiLine: 预处理后为空")
                return []
            
            text_blocks = self.gtree.sort(text_blocks)  # 构建间隙树
            
            # 补充行尾间隔符
            for tb in text_blocks:
                if tb:
                    tb["end"] = "\n"
                    if "normalized_bbox" in tb:
                        del tb["normalized_bbox"]
            return text_blocks
            
        except Exception as e:
            logger.exception(f"MultiLine 解析器处理失败: {e}")
            return text_blocks if isinstance(text_blocks, list) else []
