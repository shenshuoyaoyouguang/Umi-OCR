# 排版解析-单栏-代码段

from __future__ import annotations
from typing import TYPE_CHECKING, List
from bisect import bisect_left

if TYPE_CHECKING:
    from .tbpu_types import TextBlocks, TextBlock, Box

from umi_log import logger
from .parser_single_line import SingleLine
from .parser_tools.line_preprocessing import line_preprocessing  # 行预处理


class SingleCode(SingleLine):
    """
    单栏-代码段 排版解析器
    
    适用于代码段落，自动合并同一行的文本块并添加缩进。
    继承自 SingleLine，在行识别基础上进行代码格式化处理。
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.tbpu_name: str = "排版解析-单栏-代码段"

    def merge_line(self, line: TextBlocks) -> TextBlock:
        """
        合并一行的文本块
        
        Args:
            line: 一行中的文本块列表
            
        Returns:
            合并后的文本块
        """
        A = line[0]
        ba: Box = A["box"]
        ha = ba[3][1] - ba[0][1]  # 块A行高
        score: float = A["score"]
        
        for i in range(1, len(line)):
            B = line[i]
            bb: Box = B["box"]
            ha = (ha + bb[3][1] - bb[0][1]) / 2
            
            # 合并文字，补充与间距相同的空格数
            space = 0
            if bb[0][0] > ba[1][0]:
                space = round((bb[0][0] - ba[1][0]) / ha)
            A["text"] += "  " * space + B["text"]
            
            # 合并包围盒
            yTop = min(ba[0][1], ba[1][1], bb[0][1], bb[1][1])
            yBottom = max(ba[2][1], ba[3][1], bb[2][1], bb[3][1])
            xLeft = min(ba[0][0], ba[3][0], bb[0][0], bb[3][0])
            xRight = max(ba[1][0], ba[2][0], bb[1][0], bb[2][0])
            ba[0][1] = ba[1][1] = yTop  # y上
            ba[2][1] = ba[3][1] = yBottom  # y下
            ba[0][0] = ba[3][0] = xLeft  # x左
            ba[1][0] = ba[2][0] = xRight  # x右
            
            # 置信度
            score += B["score"]
            
        A["score"] = score / len(line)
        del A["normalized_bbox"]
        A["end"] = "\n"
        return A

    def indent(self, tbs: TextBlocks) -> None:
        """
        分析所有行，构造缩进
        
        Args:
            tbs: 文本块列表
        """
        lh = 0  # 平均行高
        xMin = float("inf")  # 句首的最左、最右x值
        xMax = float("-inf")
        
        for tb in tbs:
            b: Box = tb["box"]
            lh += b[3][1] - b[0][1]
            x = b[0][0]
            xMin = min(xMin, x)
            xMax = max(xMax, x)
            
        lh /= len(tbs)
        lh2 = lh / 2
        
        # 构建缩进层级列表
        levelList: List[float] = []
        x = xMin
        while x < xMax:
            levelList.append(x)
            x += lh
            
        # 按照层级，为每行句首加上空格，并调整包围盒
        for tb in tbs:
            b: Box = tb["box"]
            level = bisect_left(levelList, b[0][0] + lh2) - 1  # 二分查找层级点
            tb["text"] = "  " * level + tb["text"]  # 补充空格
            b[0][0] = b[3][0] = xMin  # 左侧归零

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
                logger.debug("SingleCode: 输入为空列表，直接返回")
                return []
            
            if not isinstance(text_blocks, list):
                logger.warning(f"SingleCode: 输入类型错误: {type(text_blocks)}，期望 list")
                return []
            
            text_blocks = line_preprocessing(text_blocks)  # 预处理
            
            if not text_blocks:
                logger.debug("SingleCode: 预处理后为空")
                return []
            
            lines = self.get_lines(text_blocks)  # 获取每一行
            
            if not lines:
                logger.debug("SingleCode: 未识别到行")
                return []
            
            tbs = [self.merge_line(line) for line in lines]  # 合并所有行
            
            if not tbs:
                logger.debug("SingleCode: 合并后为空")
                return []
            
            self.indent(tbs)  # 为每行添加句首缩进
            return tbs
            
        except Exception as e:
            logger.exception(f"SingleCode 解析器处理失败: {e}")
            return text_blocks if isinstance(text_blocks, list) else []
