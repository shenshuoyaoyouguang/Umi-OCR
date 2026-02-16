# translate/translate_plugin.py: TBPU 翻译插件主类

"""
TBPU 翻译插件主类

作为 TBPU（文本块处理单元）插件集成到 OCR 流程中，
在文本后处理阶段执行翻译操作。
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..tbpu.tbpu_types import TextBlocks

from umi_log import logger

# 导入 TBPU 基类（使用相对导入）
from ..tbpu.tbpu import Tbpu

# 导入翻译引擎
from .base import (
    TranslateEngine,
    TranslateResult,
    TRANSLATE_SUCCESS,
)
from .engines.tencent import TencentTranslateEngine
from .engines.custom import CustomTranslateEngine


# ===============================================
# 插件信息（供插件控制器读取）
# ===============================================

PluginInfo = {
    "id": "translate_online",
    "name": "在线翻译",
    "version": "1.0.0",
    "author": "Umi-OCR",
    "description": "将 OCR 识别文本翻译为指定语言，支持腾讯翻译和自定义 API",
    "group": "tbpu",
    "dependencies": [],
    
    # 全局配置选项
    "global_options": {
        "translate.enabled": {
            "title": "启用翻译",
            "toolTip": "是否启用 OCR 结果翻译功能",
            "default": False,
            "type": "boolean"
        },
        "translate.engine": {
            "title": "翻译引擎",
            "toolTip": "选择翻译服务提供商",
            "default": "tencent",
            "type": "enum",
            "optionsList": [
                ["tencent", "腾讯翻译君"],
                ["custom", "自定义API"],
            ]
        },
        "translate.target_lang": {
            "title": "目标语言",
            "toolTip": "翻译的目标语言",
            "default": "en",
            "type": "enum",
            "optionsList": [
                ["en", "英语"],
                ["zh", "中文"],
                ["ja", "日语"],
                ["ko", "韩语"],
                ["fr", "法语"],
                ["de", "德语"],
                ["es", "西班牙语"],
                ["ru", "俄语"],
                ["pt", "葡萄牙语"],
                ["vi", "越南语"],
                ["th", "泰语"],
            ]
        },
        "translate.source_lang": {
            "title": "源语言",
            "toolTip": "原文语言，auto 为自动检测",
            "default": "auto",
            "type": "enum",
            "optionsList": [
                ["auto", "自动检测"],
                ["zh", "中文"],
                ["en", "英语"],
                ["ja", "日语"],
                ["ko", "韩语"],
            ]
        },
        # 腾讯翻译配置
        "translate.tencent.secret_id": {
            "title": "腾讯云 SecretId",
            "toolTip": "在腾讯云控制台获取：https://console.cloud.tencent.com/cam/capi",
            "default": "",
            "type": "str"
        },
        "translate.tencent.secret_key": {
            "title": "腾讯云 SecretKey",
            "toolTip": "在腾讯云控制台获取：https://console.cloud.tencent.com/cam/capi",
            "default": "",
            "type": "str"
        },
        # 自定义 API 配置
        "translate.custom.url": {
            "title": "自定义 API 地址",
            "toolTip": "翻译 API 的 URL 地址",
            "default": "",
            "type": "str"
        },
        "translate.custom.api_key": {
            "title": "自定义 API 密钥",
            "toolTip": "API 密钥，会替换模板中的 {api_key}",
            "default": "",
            "type": "str"
        },
        "translate.custom.request_template": {
            "title": "请求模板",
            "toolTip": "请求体模板（JSON 格式），支持变量：{text}, {source_lang}, {target_lang}, {api_key}",
            "default": "{}",
            "type": "var"
        },
        "translate.custom.response_path": {
            "title": "响应路径",
            "toolTip": "翻译结果在响应 JSON 中的路径，如：data.translated_text",
            "default": "",
            "type": "str"
        },
    },
    
    "local_options": None,
    "api_class": None,  # 在文件末尾设置
}


# ===============================================
# 翻译 TBPU 插件类
# ===============================================

class TranslateTbpu(Tbpu):
    """
    在线翻译文本块处理器
    
    将 OCR 识别的文本翻译为指定语言。
    翻译结果以 `translation` 字段附加到文本块中，不影响原文。
    
    文本块扩展字段：
    - translation: 翻译结果
    - translation_source: 翻译引擎标识
    """
    
    def __init__(self):
        """初始化翻译处理器"""
        super().__init__()
        self.tbpu_name: str = "在线翻译"
        
        # 翻译引擎
        self._engine: Optional[TranslateEngine] = None
        
        # 语言配置
        self._target_lang: str = "en"
        self._source_lang: str = "auto"
        
        # 是否已配置
        self._configured: bool = False
    
    def configure(self, config: Dict[str, Any]) -> None:
        """
        配置翻译引擎
        
        Args:
            config: 配置字典，包含引擎选择和密钥信息
        """
        # 获取引擎类型
        engine_type = config.get("translate.engine", "tencent")
        
        # 获取语言配置
        self._target_lang = config.get("translate.target_lang", "en")
        self._source_lang = config.get("translate.source_lang", "auto")
        
        # 创建对应的引擎
        if engine_type == "tencent":
            self._engine = TencentTranslateEngine()
            engine_config = {
                "secret_id": config.get("translate.tencent.secret_id", ""),
                "secret_key": config.get("translate.tencent.secret_key", ""),
            }
            if not self._engine.initialize(engine_config):
                logger.warning("腾讯翻译引擎初始化失败，请检查 SecretId 和 SecretKey 配置")
                self._configured = False
                return
        
        elif engine_type == "custom":
            self._engine = CustomTranslateEngine()
            
            # 解析请求模板
            request_template = {}
            try:
                template_str = config.get("translate.custom.request_template", "{}")
                import json
                request_template = json.loads(template_str) if template_str.strip() else {}
            except json.JSONDecodeError as e:
                logger.warning(f"请求模板 JSON 解析失败: {e}")
            
            engine_config = {
                "url": config.get("translate.custom.url", ""),
                "api_key": config.get("translate.custom.api_key", ""),
                "request_template": request_template,
                "response_path": config.get("translate.custom.response_path", ""),
            }
            if not self._engine.initialize(engine_config):
                logger.warning("自定义 API 翻译引擎初始化失败，请检查 URL 配置")
                self._configured = False
                return
        
        else:
            logger.warning(f"未知的翻译引擎类型: {engine_type}")
            self._configured = False
            return
        
        self._configured = True
        logger.info(f"翻译引擎已配置: {engine_type}, 目标语言: {self._target_lang}")
    
    def run(self, text_blocks: TextBlocks) -> TextBlocks:
        """
        处理文本块列表 - 执行翻译
        
        Args:
            text_blocks: 输入的文本块列表
            
        Returns:
            处理后的文本块列表（包含翻译字段）
        """
        # 边界检查
        if not text_blocks:
            return []
        
        if not isinstance(text_blocks, list):
            logger.warning(f"TranslateTbpu: 输入类型错误: {type(text_blocks)}，期望 list")
            return []
        
        # 检查是否已配置
        if not self._configured or not self._engine:
            logger.debug("TranslateTbpu: 翻译引擎未配置，跳过翻译")
            return text_blocks
        
        try:
            # 收集需要翻译的文本
            texts_to_translate: List[tuple] = []
            for i, tb in enumerate(text_blocks):
                if isinstance(tb, dict) and "text" in tb:
                    text = tb["text"]
                    if text and text.strip():
                        texts_to_translate.append((i, text))
            
            if not texts_to_translate:
                logger.debug("TranslateTbpu: 没有需要翻译的文本")
                return text_blocks
            
            logger.debug(f"TranslateTbpu: 开始翻译 {len(texts_to_translate)} 个文本块")
            
            # 执行翻译（逐个处理）
            for idx, text in texts_to_translate:
                self._translate_block(text_blocks, idx, text)
            
            return text_blocks
            
        except Exception as e:
            logger.error(f"TranslateTbpu: 翻译处理失败: {e}", exc_info=True, stack_info=True)
            return text_blocks  # 失败时返回原始输入
    
    def _translate_block(
        self, 
        text_blocks: TextBlocks, 
        idx: int, 
        text: str
    ) -> None:
        """
        翻译单个文本块
        
        Args:
            text_blocks: 文本块列表
            idx: 文本块索引
            text: 待翻译文本
        """
        try:
            # 调用翻译引擎
            result = self._engine.translate(
                text,
                self._source_lang,
                self._target_lang
            )
            
            # 处理翻译结果
            if result.is_success():
                # 成功：添加翻译字段
                text_blocks[idx]["translation"] = result.translated_text
                text_blocks[idx]["translation_source"] = result.source
                logger.debug(f"TranslateTbpu: 文本块 {idx} 翻译成功")
            else:
                # 失败：记录错误，不添加翻译字段
                logger.debug(
                    f"TranslateTbpu: 文本块 {idx} 翻译失败 - "
                    f"[{result.code}] {result.error_message}"
                )
        
        except Exception as e:
            logger.error(f"TranslateTbpu: 翻译文本块 {idx} 时发生错误: {e}")
    
    def set_engine(self, engine: TranslateEngine) -> None:
        """
        设置翻译引擎（用于外部注入）
        
        Args:
            engine: 翻译引擎实例
        """
        self._engine = engine
        self._configured = True
    
    def set_languages(self, source: str, target: str) -> None:
        """
        设置源语言和目标语言
        
        Args:
            source: 源语言代码
            target: 目标语言代码
        """
        self._source_lang = source
        self._target_lang = target


# 设置 api_class
PluginInfo["api_class"] = TranslateTbpu


# ===============================================
# 导出
# ===============================================

__all__ = [
    "TranslateTbpu",
    "PluginInfo",
]
