# TBPU 模块类型定义
# 为文本块处理单元提供完整的类型注解支持

from __future__ import annotations
from typing import List, Dict, Any, Tuple, Callable, Optional, Union

# =============== 基础类型 ===============

# 四边形包围盒：四个顶点的坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
Box = List[List[int]]

# 标准化包围盒：(左侧x, 顶部y, 右侧x, 底部y)
NormalizedBox = Tuple[float, float, float, float]

# 文本块：包含包围盒、文本内容、置信度等信息
class TextBlock(Dict[str, Any]):
    """
    文本块类型
    
    典型结构:
    {
        'box': Box,           # 四边形包围盒
        'text': str,          # 文本内容
        'score': float,       # 置信度 (0-1)
        'end': str,           # 结尾分隔符 (可选)
        'normalized_bbox': NormalizedBox,  # 标准化包围盒 (可选，内部使用)
    }
    """
    pass

# 文本块列表
TextBlocks = List[TextBlock]

# =============== 函数类型 ===============

# 获取文本块标准化包围盒的函数类型
GetBboxFunc = Callable[[TextBlock], NormalizedBox]

# 获取文本块信息和文本的函数类型
GetInfoFunc = Callable[[TextBlock], Tuple[NormalizedBox, str]]

# 设置文本块结尾分隔符的函数类型
SetEndFunc = Callable[[TextBlock, str], None]

# 解析器字典类型
ParserDict = Dict[str, Any]

# =============== 辅助类型 ===============

# 间隙树节点类型
GapTreeNode = Dict[str, Any]

# 间隙树单元类型: (标准化包围盒, 原始文本块)
GapTreeUnit = Tuple[NormalizedBox, TextBlock]

# 行类型（一行中的文本块列表）
Line = List[TextBlock]

# 多行列表类型
Lines = List[Line]

# 段落类型（一个段落中的文本块列表）
Paragraph = List[GapTreeUnit]

# 多段落列表类型
Paragraphs = List[Paragraph]

# 解析器类类型（用于类引用）
ParserClass = type

# 忽略区域类型（区域列表）
IgnoreAreaList = List[Box]
