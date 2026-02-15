"""
文本后处理模块 - 保留数字处理器
"""

import re
from typing import TYPE_CHECKING

from .base import TextPostProcessor

if TYPE_CHECKING:
    from ..tbpu.tbpu_types import TextBlocks


class FilterDigits(TextPostProcessor):
    """
    保留数字处理器

    提取文本中的数字字符，可选择保留小数点、负号等。
    """

    def __init__(
        self,
        keep_decimal: bool = True,      # 保留小数点
        keep_negative: bool = True,      # 保留负号
        keep_separator: bool = False,   # 保留千位分隔符
    ) -> None:
        super().__init__()
        self.name = "保留数字"
        self.keep_decimal = keep_decimal
        self.keep_negative = keep_negative
        self.keep_separator = keep_separator

    def process_text(self, text: str) -> str:
        """提取数字"""
        if not text:
            return ""

        # 构建正则模式
        pattern_parts = [r"\d"]
        if self.keep_decimal:
            pattern_parts.append("\\.")  # 字面点号
        if self.keep_negative:
            pattern_parts.append(r"-")
        if self.keep_separator:
            pattern_parts.append(r",")

        pattern = "[" + "".join(pattern_parts) + "]+"
        matches = re.findall(pattern, text)
        return "".join(matches)


__all__ = ["FilterDigits"]
