# 排版解析-单栏-无换行

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tbpu_types import TextBlocks

from .parser_single_line import SingleLine
from .parser_tools.paragraph_parse import word_separator  # 上下句间隔符


class SingleNone(SingleLine):
    """
    单栏-无换行 排版解析器
    
    适用于单栏版面，根据语言智能判断是否需要空格。
    继承自 SingleLine，在行识别基础上进行智能分隔。
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.tbpuName: str = "排版解析-单栏-无换行"

    def run(self, textBlocks: TextBlocks) -> TextBlocks:
        """
        处理文本块列表
        
        Args:
            textBlocks: 输入的文本块列表
            
        Returns:
            处理后的文本块列表
        """
        textBlocks = super().run(textBlocks)
        # 找到换行符，更改为间隔符
        for i in range(len(textBlocks) - 1):
            if textBlocks[i]["end"] == "\n":
                letter1 = textBlocks[i]["text"][-1]
                letter2 = textBlocks[i + 1]["text"][0]
                textBlocks[i]["end"] = word_separator(letter1, letter2)
        return textBlocks
