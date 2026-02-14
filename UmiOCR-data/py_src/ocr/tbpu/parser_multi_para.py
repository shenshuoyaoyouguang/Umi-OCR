# 排版解析-多栏-自然段

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .tbpu_types import TextBlocks

from .tbpu import Tbpu
from .parser_tools.line_preprocessing import line_preprocessing  # 行预处理
from .parser_tools.gap_tree import GapTree  # 间隙树排序算法
from .parser_tools.paragraph_parse import ParagraphParse  # 段内分析器


class MultiPara(Tbpu):
    """
    多栏-自然段 排版解析器
    
    适用于多栏版面（如报纸、杂志），自动识别自然段。
    使用间隙树算法进行版面分析，然后对每个区块进行段落分析。
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.tbpuName: str = "排版解析-多栏-自然段"

        # 间隙树对象
        self.gtree: GapTree = GapTree(lambda tb: tb["normalized_bbox"])

        # 段内分析器对象
        get_info = lambda tb: (tb["normalized_bbox"], tb["text"])

        def set_end(tb: dict, end: str) -> None:  # 获取预测的块尾分隔符
            tb["end"] = end

        self.pp: ParagraphParse = ParagraphParse(get_info, set_end)

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
        nodes = self.gtree.get_nodes_text_blocks()  # 获取树节点序列
        # 对每个结点，进行自然段分析
        for tbs in nodes:
            self.pp.run(tbs)  # 预测结尾分隔符
            for tb in tbs:
                del tb["normalized_bbox"]
        return textBlocks
