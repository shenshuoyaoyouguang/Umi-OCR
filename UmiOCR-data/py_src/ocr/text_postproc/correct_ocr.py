"""
文本后处理模块 - OCR文本纠错处理器
"""

from typing import Dict, Optional, TYPE_CHECKING

from .base import TextPostProcessor

if TYPE_CHECKING:
    from ..tbpu.tbpu_types import TextBlocks


class CorrectOcr(TextPostProcessor):
    """
    OCR文本纠错处理器

    基于规则和常见错误映射进行文本纠正。
    支持形近字纠正、常见拼写错误修正。
    """

    # 预定义的常见OCR错误映射（私有类变量，避免意外修改）
    _DEFAULT_CORRECTIONS: Dict[str, str] = {
        # 数字与字母混淆 (谨慎使用，可能需要上下文判断)
        # "0": "O",  # 数字0 -> 字母O（注释掉，因为可能误纠）
        # "1": "l",  # 数字1 -> 字母l
        # "5": "S",  # 数字5 -> 字母S
        # "8": "B",  # 数字8 -> 字母B
        # 中文形近字
        "己": "已",
        "巳": "已",
        "日": "曰",
        "未": "末",
        "土": "士",
        "甲": "由",
        "人": "入",
        "大": "太",
        "了": "子",
        "万": "方",
        # 常见OCR错误（字符粘连）
        "rn": "m",
        "vv": "w",
        "cl": "d",
        # 常见标点错误
        "，": ",",  # 全角逗号 -> 半角
        "。": ".",  # 全角句号 -> 半角
        "：": ":",
        "；": ";",
        "！": "!",
        "？": "?",
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
    }

    def __init__(
        self,
        corrections: Optional[Dict[str, str]] = None,
        enable_default: bool = True,
    ) -> None:
        """
        Args:
            corrections: 自定义纠正映射
            enable_default: 是否启用默认纠正规则
        """
        super().__init__()
        self.name = "OCR文本纠错"
        self.corrections: Dict[str, str] = {}

        if enable_default:
            self.corrections.update(self._DEFAULT_CORRECTIONS)

        if corrections:
            self.corrections.update(corrections)

    def process_text(self, text: str) -> str:
        """执行纠错"""
        if not text:
            return ""

        result = text
        # 按键长度降序排序，避免短字符串先替换影响长字符串
        sorted_items = sorted(self.corrections.items(), key=lambda x: len(x[0]), reverse=True)

        for wrong, correct in sorted_items:
            result = result.replace(wrong, correct)

        return result

    def add_correction(self, wrong: str, correct: str) -> None:
        """添加纠错规则"""
        self.corrections[wrong] = correct

    def remove_correction(self, wrong: str) -> None:
        """移除纠错规则"""
        if wrong in self.corrections:
            del self.corrections[wrong]


__all__ = ["CorrectOcr"]
