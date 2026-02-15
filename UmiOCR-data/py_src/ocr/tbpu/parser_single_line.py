# 排版解析-单栏-单行

from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .tbpu_types import TextBlocks, TextBlock, NormalizedBox

from umi_log import logger
from .tbpu import Tbpu
from .parser_tools.line_preprocessing import line_preprocessing  # 行预处理
from .parser_tools.paragraph_parse import word_separator  # 上下句间隔符
from .parser_tools.tbpu_config import TbpuConfig


class SingleLine(Tbpu):
    """
    单栏-单行 排版解析器
    
    适用于单栏版面，每行后强制换行。
    根据垂直位置和水平位置识别同行文本块。
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.tbpu_name: str = "排版解析-单栏-单行"

    def get_lines(self, text_blocks: TextBlocks) -> List[List[dict]]:
        """
        从文本块列表中找出所有行
        
        Args:
            text_blocks: 文本块列表
            
        Returns:
            行列表，每行包含多个文本块
        """
        # 按x排序
        text_blocks.sort(key=lambda tb: tb["normalized_bbox"][0])
        lines: List[List[dict]] = []
        
        for i1, tb1 in enumerate(text_blocks):
            if not tb1:
                continue
            # 最左的一个块
            l1, top1, r1, bottom1 = tb1["normalized_bbox"]
            h1 = bottom1 - top1
            now_line: List[dict] = [tb1]
            
            # 考察右侧哪些块符合条件
            for i2 in range(i1 + 1, len(text_blocks)):
                tb2 = text_blocks[i2]
                if not tb2:
                    continue
                l2, top2, r2, bottom2 = tb2["normalized_bbox"]
                h2 = bottom2 - top2
                # 行2左侧太前
                if l2 < r1 - h1:
                    continue
                # 垂直距离太远
                if top2 < top1 - h1 * TbpuConfig.LINE_HEIGHT_TOLERANCE or bottom2 > bottom1 + h1 * TbpuConfig.LINE_HEIGHT_TOLERANCE:
                    continue
                # 行高差距过大
                if abs(h1 - h2) > min(h1, h2) * TbpuConfig.LINE_HEIGHT_TOLERANCE:
                    continue
                # 符合条件
                now_line.append(tb2)
                text_blocks[i2] = None  # type: ignore
                # 更新搜索条件
                r1 = r2
                
            # 处理完一行
            for i2 in range(len(now_line) - 1):
                # 检查同一行内相邻文本块的水平间隙
                l1, t1, r1_box, b1 = now_line[i2]["normalized_bbox"]
                l2, t2, r2_box, b2 = now_line[i2 + 1]["normalized_bbox"]
                h = (b1 + b2 - t1 - l2) * 0.5
                if l2 - r1_box > h * TbpuConfig.HORIZONTAL_GAP_FACTOR:  # 间隙太大，强制设置空格
                    now_line[i2]["end"] = " "
                    continue
                letter1 = now_line[i2]["text"][-1]
                letter2 = now_line[i2 + 1]["text"][0]
                now_line[i2]["end"] = word_separator(letter1, letter2)
            now_line[-1]["end"] = "\n"
            lines.append(now_line)
            text_blocks[i1] = None  # type: ignore
            
        # 所有行按y排序
        lines.sort(key=lambda tbs: tbs[0]["normalized_bbox"][1])
        return lines

    def run(self, text_blocks: TextBlocks) -> TextBlocks:
        """
        处理文本块列表
        
        Args:
            text_blocks: 输入的文本块列表
            
        Returns:
            处理后的文本块列表
        """
        try:
            # 边界检查：空输入
            if not text_blocks:
                logger.debug("SingleLine: 输入为空列表，直接返回")
                return []
            
            # 边界检查：输入类型
            if not isinstance(text_blocks, list):
                logger.warning(f"SingleLine: 输入类型错误: {type(text_blocks)}，期望 list")
                return []
            
            text_blocks = line_preprocessing(text_blocks)  # 预处理
            
            # 预处理后可能为空
            if not text_blocks:
                logger.debug("SingleLine: 预处理后为空")
                return []
            
            lines = self.get_lines(text_blocks)  # 获取每一行
            
            # 解包
            result: TextBlocks = []
            for line in lines:
                for tb in line:
                    if tb and "normalized_bbox" in tb:
                        del tb["normalized_bbox"]
                    result.append(tb)
            return result
            
        except Exception as e:
            logger.exception(f"SingleLine 解析器处理失败: {e}")
            return text_blocks if isinstance(text_blocks, list) else []
