# 排版解析-多栏-无换行

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tbpu_types import TextBlocks

from .tbpu import Tbpu
from .parser_tools.line_preprocessing import line_preprocessing  # 行预处理
from .parser_tools.gap_tree import GapTree  # 间隙树排序算法
from .parser_tools.paragraph_parse import word_separator  # 上下句间隔符


class MultiNone(Tbpu):
    """
    多栏-无换行 排版解析器
    
    适用于多栏版面（如报纸、杂志），根据语言智能判断是否需要空格。
    使用间隙树算法进行版面分析。
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.tbpu_name: str = "排版解析-多栏-无换行"

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
                logger.debug("MultiNone: 输入为空列表，直接返回")
                return []
            
            if not isinstance(text_blocks, list):
                logger.warning(f"MultiNone: 输入类型错误: {type(text_blocks)}，期望 list")
                return []
            
            text_blocks = line_preprocessing(text_blocks)  # 预处理
            
            if not text_blocks:
                logger.debug("MultiNone: 预处理后为空")
                return []
            
            text_blocks = self.gtree.sort(text_blocks)  # 构建间隙树
            # 补充行尾间隔符
            for i in range(len(text_blocks)):
                tb = text_blocks[i]
                if i < len(text_blocks) - 1:
                    letter1 = tb["text"][-1]  # 行1结尾字母
                    letter2 = text_blocks[i + 1]["text"][0]  # 行2开头字母
                    tb["end"] = word_separator(letter1, letter2)  # 获取间隔符
                else:
                    tb["end"] = "\n"
                del tb["normalized_bbox"]
            return text_blocks
            
        except Exception as e:
            logger.exception(f"MultiNone 解析器处理失败: {e}")
            return text_blocks if isinstance(text_blocks, list) else []
