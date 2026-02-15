# 排版解析-单栏-自然段

from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .tbpu_types import TextBlocks

from umi_log import logger
from .parser_single_line import SingleLine
from .parser_tools.line_preprocessing import line_preprocessing  # 行预处理
from .parser_tools.paragraph_parse import ParagraphParse  # 段内分析器


class SinglePara(SingleLine):
    """
    单栏-自然段 排版解析器
    
    适用于单栏版面，自动识别自然段。
    继承自 SingleLine，在行识别基础上进行段落分析。
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.tbpu_name: str = "排版解析-单栏-自然段"

        # 段内分析器对象
        get_info = lambda tb: (tb["normalized_bbox"], tb["text"])

        def set_end(tb: dict, end: str) -> None:  # 获取预测的块尾分隔符
            tb["line"][-1]["end"] = end

        self.pp: ParagraphParse = ParagraphParse(get_info, set_end)

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
                logger.debug("SinglePara: 输入为空列表，直接返回")
                return []
            
            # 边界检查：输入类型
            if not isinstance(text_blocks, list):
                logger.warning(f"SinglePara: 输入类型错误: {type(text_blocks)}，期望 list")
                return []
            
            text_blocks = line_preprocessing(text_blocks)  # 预处理
            
            # 预处理后可能为空
            if not text_blocks:
                logger.debug("SinglePara: 预处理后为空")
                return []
            
            lines = self.get_lines(text_blocks)  # 获取每一行
            
            # 如果没有识别到行，返回预处理结果
            if not lines:
                logger.debug("SinglePara: 未识别到行")
                return text_blocks
            
            # 将行封装为tb
            temp_tbs: List[dict] = []
            for line in lines:
                if not line:
                    continue
                b0, b1, b2, b3 = line[0]["normalized_bbox"]
                # 搜索bbox
                for i in range(1, len(line)):
                    bb = line[i]["normalized_bbox"]
                    b1 = min(b1, bb[1])
                    b2 = max(b2, bb[2])
                    b3 = max(b3, bb[3])
                # 构建tb
                temp_tbs.append(
                    {
                        "normalized_bbox": (b0, b1, b2, b3),
                        "text": line[0]["text"][0] + line[-1]["text"][-1],
                        "line": line,
                    }
                )
            
            # 预测结尾分隔符
            if temp_tbs:
                self.pp.run(temp_tbs)
            
            # 解包
            result: TextBlocks = []
            for t in temp_tbs:
                for tb in t["line"]:
                    if tb and "normalized_bbox" in tb:
                        del tb["normalized_bbox"]
                    result.append(tb)
            return result
            
        except Exception as e:
            logger.exception(f"SinglePara 解析器处理失败: {e}")
            return text_blocks if isinstance(text_blocks, list) else []
