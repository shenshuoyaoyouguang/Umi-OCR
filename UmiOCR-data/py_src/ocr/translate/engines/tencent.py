# translate/engines/tencent.py: 腾讯翻译引擎实现

"""
腾讯翻译引擎实现

调用腾讯翻译君 API 进行文本翻译。
API 文档：https://cloud.tencent.com/document/product/551/15619
"""

from __future__ import annotations
import json
from typing import Dict, Any, List

from umi_log import logger

from ..base import (
    TranslateEngine,
    TranslateResult,
    TRANSLATE_SUCCESS,
    TRANSLATE_ERROR_NETWORK,
    TRANSLATE_ERROR_API,
    TRANSLATE_ERROR_AUTH,
    TRANSLATE_ERROR_QUOTA,
    TRANSLATE_ERROR_INVALID_TEXT,
    TRANSLATE_ERROR_TIMEOUT,
    TRANSLATE_ERROR_PARSE,
    TRANSLATE_ERROR_UNKNOWN,
)
from ..utils.http_client import HttpClient, HttpResponse
from ..utils.signature import TencentSigner


# 腾讯翻译 API 配置
TENCENT_HOST = "tmt.tencentcloudapi.com"
TENCENT_URL = f"https://{TENCENT_HOST}"
TENCENT_SERVICE = "tmt"
TENCENT_ACTION = "TextTranslate"
TENCENT_VERSION = "2018-03-21"
TENCENT_REGION = "ap-beijing"

# 默认超时（秒）
DEFAULT_TIMEOUT = 10


class TencentTranslateEngine(TranslateEngine):
    """
    腾讯翻译引擎
    
    使用腾讯翻译君 API 进行文本翻译。
    支持 100+ 种语言互译。
    """
    
    def __init__(self):
        """初始化腾讯翻译引擎"""
        self._secret_id: str = ""
        self._secret_key: str = ""
        self._http_client: HttpClient = HttpClient(timeout=DEFAULT_TIMEOUT)
        self._initialized: bool = False
    
    @property
    def name(self) -> str:
        """引擎名称标识"""
        return "tencent"
    
    @property
    def display_name(self) -> str:
        """引擎显示名称"""
        return "腾讯翻译君"
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化引擎
        
        Args:
            config: 配置字典，必须包含 secret_id 和 secret_key
            
        Returns:
            初始化是否成功
        """
        self._secret_id = config.get("secret_id", "")
        self._secret_key = config.get("secret_key", "")
        
        # 验证配置
        if not self._secret_id or not self._secret_key:
            logger.warning("腾讯翻译引擎初始化失败：缺少 SecretId 或 SecretKey")
            self._initialized = False
            return False
        
        self._initialized = True
        logger.debug("腾讯翻译引擎初始化成功")
        return True
    
    def translate(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str
    ) -> TranslateResult:
        """
        执行翻译
        
        Args:
            text: 待翻译文本
            source_lang: 源语言代码（如 "zh", "en", "auto"）
            target_lang: 目标语言代码
            
        Returns:
            TranslateResult 实例
        """
        # 检查是否已初始化
        if not self._initialized:
            return TranslateResult(
                code=TRANSLATE_ERROR_AUTH,
                original_text=text,
                translated_text="",
                source=self.name,
                error_message="引擎未初始化，请配置 SecretId 和 SecretKey"
            )
        
        # 检查文本有效性
        if not text or not text.strip():
            return TranslateResult(
                code=TRANSLATE_ERROR_INVALID_TEXT,
                original_text=text,
                translated_text="",
                source=self.name,
                error_message="待翻译文本为空"
            )
        
        # 构造请求体
        payload_dict = {
            "SourceText": text,
            "Source": source_lang,
            "Target": target_lang,
            "ProjectId": 0
        }
        payload = json.dumps(payload_dict, ensure_ascii=False)
        
        # 生成签名
        headers = TencentSigner.sign(
            secret_id=self._secret_id,
            secret_key=self._secret_key,
            service=TENCENT_SERVICE,
            host=TENCENT_HOST,
            action=TENCENT_ACTION,
            payload=payload,
            region=TENCENT_REGION,
            version=TENCENT_VERSION
        )
        
        # 发送请求
        response = self._http_client.post_raw(
            TENCENT_URL,
            payload.encode('utf-8'),
            headers
        )
        
        # 处理响应
        return self._handle_response(text, response)
    
    def _handle_response(
        self, 
        original_text: str, 
        response: HttpResponse
    ) -> TranslateResult:
        """
        处理 API 响应
        
        Args:
            original_text: 原文
            response: HTTP 响应
            
        Returns:
            TranslateResult 实例
        """
        # 检查网络错误
        if response.status_code == 0:
            error_msg = response.content
            if "超时" in error_msg:
                code = TRANSLATE_ERROR_TIMEOUT
            else:
                code = TRANSLATE_ERROR_NETWORK
            
            return TranslateResult(
                code=code,
                original_text=original_text,
                translated_text="",
                source=self.name,
                error_message=error_msg
            )
        
        # 检查 HTTP 状态码
        if response.status_code != 200:
            return TranslateResult(
                code=TRANSLATE_ERROR_NETWORK,
                original_text=original_text,
                translated_text="",
                source=self.name,
                error_message=f"HTTP 错误: {response.status_code}"
            )
        
        # 解析 JSON 响应
        try:
            result = response.json()
            if result is None:
                return TranslateResult(
                    code=TRANSLATE_ERROR_PARSE,
                    original_text=original_text,
                    translated_text="",
                    source=self.name,
                    error_message="JSON 解析失败"
                )
        except Exception as e:
            return TranslateResult(
                code=TRANSLATE_ERROR_PARSE,
                original_text=original_text,
                translated_text="",
                source=self.name,
                error_message=f"JSON 解析异常: {e}"
            )
        
        # 检查 API 响应结构
        if "Response" not in result:
            return TranslateResult(
                code=TRANSLATE_ERROR_API,
                original_text=original_text,
                translated_text="",
                source=self.name,
                error_message="响应格式错误：缺少 Response 字段"
            )
        
        resp = result["Response"]
        
        # 检查错误响应
        if "Error" in resp:
            error_info = resp["Error"]
            error_code = error_info.get("Code", "")
            error_message = error_info.get("Message", "未知错误")
            
            # 根据错误码映射
            if error_code in ["AuthFailure", "AuthFailure.SecretIdNotFound", 
                            "AuthFailure.SecretKeyNotFound", "AuthFailure.SignatureFailure"]:
                code = TRANSLATE_ERROR_AUTH
            elif error_code in ["RequestLimitExceeded", "ResourceInsufficient"]:
                code = TRANSLATE_ERROR_QUOTA
            else:
                code = TRANSLATE_ERROR_API
            
            return TranslateResult(
                code=code,
                original_text=original_text,
                translated_text="",
                source=self.name,
                error_message=f"[{error_code}] {error_message}"
            )
        
        # 提取翻译结果
        if "TargetText" not in resp:
            return TranslateResult(
                code=TRANSLATE_ERROR_API,
                original_text=original_text,
                translated_text="",
                source=self.name,
                error_message="响应格式错误：缺少 TargetText 字段"
            )
        
        translated_text = resp["TargetText"]
        
        return TranslateResult(
            code=TRANSLATE_SUCCESS,
            original_text=original_text,
            translated_text=translated_text,
            source=self.name
        )
    
    def get_supported_languages(self) -> List[str]:
        """
        获取支持的语言列表
        
        腾讯翻译支持的语言代码：
        zh: 中文
        en: 英语
        ja: 日语
        ko: 韩语
        fr: 法语
        de: 德语
        es: 西班牙语
        it: 意大利语
        ru: 俄语
        pt: 葡萄牙语
        vi: 越南语
        th: 泰语
        ms: 马来语
        ar: 阿拉伯语
        hi: 印地语
        auto: 自动检测
        
        Returns:
            语言代码列表
        """
        return [
            "auto",  # 自动检测
            "zh",    # 中文
            "en",    # 英语
            "ja",    # 日语
            "ko",    # 韩语
            "fr",    # 法语
            "de",    # 德语
            "es",    # 西班牙语
            "it",    # 意大利语
            "ru",    # 俄语
            "pt",    # 葡萄牙语
            "vi",    # 越南语
            "th",    # 泰语
            "ms",    # 马来语
            "ar",    # 阿拉伯语
            "hi",    # 印地语
        ]
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置是否有效
        
        Args:
            config: 配置字典
            
        Returns:
            配置是否有效
        """
        secret_id = config.get("secret_id", "")
        secret_key = config.get("secret_key", "")
        return bool(secret_id and secret_key)
