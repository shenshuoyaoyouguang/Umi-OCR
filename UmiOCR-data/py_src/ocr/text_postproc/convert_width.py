"""
文本后处理模块 - 半全角转换处理器
"""

from typing import TYPE_CHECKING

from .base import TextPostProcessor

if TYPE_CHECKING:
    from ..tbpu.tbpu_types import TextBlocks


class ConvertWidth(TextPostProcessor):
    """
    半全角转换处理器

    支持全角转半角或半角转全角。
    """

    def __init__(self, mode: str = "full_to_half") -> None:
        """
        Args:
            mode: 转换模式
                - "full_to_half": 全角转半角（默认）
                - "half_to_full": 半角转全角
        """
        super().__init__()
        self.name = "半全角转换"
        self.mode = mode

    def process_text(self, text: str) -> str:
        """执行转换"""
        if not text:
            return ""

        if self.mode == "full_to_half":
            return self._full_to_half(text)
        else:
            return self._half_to_full(text)

    def _full_to_half(self, text: str) -> str:
        """全角转半角"""
        result = []
        for char in text:
            code = ord(char)
            # 全角字符范围: 0xFF01-0xFF5E
            if 0xFF01 <= code <= 0xFF5E:
                result.append(chr(code - 0xFEE0))
            elif code == 0x3000:  # 全角空格
                result.append(" ")
            else:
                result.append(char)
        return "".join(result)

    def _half_to_full(self, text: str) -> str:
        """半角转全角"""
        result = []
        for char in text:
            code = ord(char)
            # 半角数字和字母 (0x21-0x7E 是可打印 ASCII 范围)
            if 0x21 <= code <= 0x7E:
                result.append(chr(code + 0xFEE0))
            elif char == " ":  # 半角空格
                result.append(chr(0x3000))
            else:
                result.append(char)
        return "".join(result)


__all__ = ["ConvertWidth"]
