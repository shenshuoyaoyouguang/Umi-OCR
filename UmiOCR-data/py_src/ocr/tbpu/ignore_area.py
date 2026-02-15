# 忽略区域

from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .tbpu_types import TextBlocks, TextBlock, Box

from .tbpu import Tbpu


class IgnoreArea(Tbpu):
    """
    忽略区域处理器
    
    根据指定的忽略区域列表，过滤掉位于这些区域内的文本块。
    用于排除页眉、页脚、页码等不需要识别的区域。
    """
    
    def __init__(self, area_list: List[Box]) -> None:
        """
        初始化忽略区域处理器
        
        Args:
            area_list: 忽略区域列表，每个区域是一个四边形包围盒
        """
        super().__init__()
        self.tbpu_name: str = "忽略区域"
        self.area_list: List[Box] = area_list

    def run(self, text_blocks: TextBlocks) -> TextBlocks:
        """
        处理文本块列表，过滤掉位于忽略区域内的文本块
        
        Args:
            text_blocks: 输入的文本块列表
            
        Returns:
            过滤后的文本块列表
        """
        # 边界检查
        if not text_blocks:
            return []
        
        if not isinstance(text_blocks, list):
            return []
        
        # 返回是否矩形框 a 包含 b
        def isInBox(a: Box, b: Box) -> bool:
            return (
                a[0][0] <= b[0][0]
                and a[0][1] <= b[0][1]
                and a[2][0] >= b[2][0]
                and a[2][1] >= b[2][1]
            )

        new_list: TextBlocks = []
        for b in text_blocks:
            flag = True  # True 为没有被忽略
            # 检测当前文块 b 是否在任何一个检测块 a 内
            for a in self.area_list:
                if isInBox(a, b["box"]):
                    flag = False  # 踩到任何一个块，GG
                    break
            if flag:  # 没有被忽略
                new_list.append(b)

        return new_list