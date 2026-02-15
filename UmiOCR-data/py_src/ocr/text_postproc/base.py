"""
文本后处理模块 - 基类定义
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tbpu.tbpu_types import TextBlocks


class TextPostProcessor:
    """
    文本后处理器基类

    与 Tbpu 基类设计一致，提供统一的处理接口。
    处理器对每个文本块的 text 字段进行处理。
    """

    def __init__(self) -> None:
        self.name: str = "文本后处理器-未知"
        self.enabled: bool = True

    def process_text(self, text: str) -> str:
        """
        处理单个文本字符串

        Args:
            text: 输入文本

        Returns:
            处理后的文本
        """
        return text

    def run(self, text_blocks: "TextBlocks") -> "TextBlocks":
        """
        处理文本块列表

        Args:
            text_blocks: 输入的文本块列表

        Returns:
            处理后的文本块列表
        """
        if not text_blocks:
            return []

        for tb in text_blocks:
            if tb and "text" in tb and self.enabled:
                tb["text"] = self.process_text(tb["text"])

        return text_blocks
