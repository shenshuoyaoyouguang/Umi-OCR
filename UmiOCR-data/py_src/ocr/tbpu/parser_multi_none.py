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
        self.tbpuName: str = "排版解析-多栏-无换行"

        # 构建算法对象，指定包围盒的元素位置
        self.gtree: GapTree = GapTree(lambda tb: tb["normalized_bbox"])

    def run(self, textBlocks: TextBlocks) -> TextBlocks:
        """
        处理文本块列表
        
        Args:
            textBlocks: 输入的文本块列表
            
        Returns:
            处理后的文本块列表
        """
        textBlocks = line_preprocessing(textBlocks)  # 预处理
        textBlocks = self.gtree.sort(textBlocks)  # 构建间隙树
        # 补充行尾间隔符
        for i in range(len(textBlocks)):
            tb = textBlocks[i]
            if i < len(textBlocks) - 1:
                letter1 = tb["text"][-1]  # 行1结尾字母
                letter2 = textBlocks[i + 1]["text"][0]  # 行2开头字母
                tb["end"] = word_separator(letter1, letter2)  # 获取间隔符
            else:
                tb["end"] = "\n"
            del tb["normalized_bbox"]
        return textBlocks
