# translate/engines/custom.py: 自定义 API 翻译引擎实现

"""
自定义 API 翻译引擎实现

允许用户配置任意翻译 API，支持：
- 自定义请求 URL
- 自定义请求模板
- 自定义响应解析路径
"""

from __future__ import annotations
import json
import re
from typing import Dict, Any, List, Optional

from umi_log import logger

from ..base import (
    TranslateEngine,
    TranslateResult,
    TRANSLATE_SUCCESS,
    TRANSLATE_ERROR_NETWORK,
    TRANSLATE_ERROR_API,
    TRANSLATE_ERROR_INVALID_TEXT,
    TRANSLATE_ERROR_TIMEOUT,
    TRANSLATE_ERROR_PARSE,
    DEFAULT_TIMEOUT,
    MAX_RESPONSE_PATH_DEPTH,
)
from ..utils.http_client import HttpClient, HttpResponse


class CustomTranslateEngine(TranslateEngine):
    """
    自定义 API 翻译引擎
    
    支持用户配置任意的翻译 API。
    通过模板变量替换实现灵活的请求构造。
    """
    
    def __init__(self):
        """初始化自定义翻译引擎"""
        self._config: Dict[str, Any] = {}
        self._http_client: HttpClient = HttpClient(timeout=DEFAULT_TIMEOUT)
        self._initialized: bool = False
    
    @property
    def name(self) -> str:
        """引擎名称标识"""
        return "custom"
    
    @property
    def display_name(self) -> str:
        """引擎显示名称"""
        return "自定义API"
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        初始化引擎
        
        Args:
            config: 配置字典，包含：
                - url: API 地址（必需）
                - api_key: API 密钥（可选）
                - request_template: 请求体模板（可选）
                - response_path: 响应解析路径（可选）
                - headers: 请求头模板（可选）
                - method: 请求方法（可选，默认 POST）
                
        Returns:
            初始化是否成功
        """
        self._config = config.copy()
        
        # 验证必需配置
        if not self._config.get("url"):
            logger.warning("自定义翻译引擎初始化失败：缺少 API URL")
            self._initialized = False
            return False
        
        # 设置默认值
        self._config.setdefault("method", "POST")
        self._config.setdefault("request_template", {})
        self._config.setdefault("headers", {})
        self._config.setdefault("response_path", "")
        
        self._initialized = True
        logger.debug(f"自定义翻译引擎初始化成功：{self._config['url']}")
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
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            TranslateResult 实例
        """
        # 检查是否已初始化
        if not self._initialized:
            return TranslateResult(
                code=TRANSLATE_ERROR_API,
                original_text=text,
                translated_text="",
                source=self.name,
                error_message="引擎未初始化，请配置 API URL"
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
        
        # 构造请求
        request_data = self._build_request(text, source_lang, target_lang)
        headers = self._build_headers()
        
        # 发送请求
        method = self._config.get("method", "POST").upper()
        
        if method == "GET":
            # GET 请求，将参数拼接到 URL
            url = self._build_get_url(request_data)
            response = self._http_client.get(url, headers=headers)
        else:
            # POST 请求
            response = self._http_client.post(
                self._config["url"],
                request_data,
                headers
            )
        
        # 处理响应
        return self._handle_response(text, response)
    
    def _build_request(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str
    ) -> Dict[str, Any]:
        """
        构造请求体
        
        Args:
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            请求体字典
        """
        template = self._config.get("request_template", {})
        api_key = self._config.get("api_key", "")
        
        # 如果没有模板，使用默认格式
        if not template:
            return {
                "text": text,
                "source": source_lang,
                "target": target_lang,
            }
        
        # 替换模板变量
        result = {}
        for key, value in template.items():
            if isinstance(value, str):
                value = self._replace_variables(
                    value, 
                    text=text, 
                    source_lang=source_lang, 
                    target_lang=target_lang,
                    api_key=api_key
                )
            elif isinstance(value, dict):
                value = self._replace_dict_variables(
                    value,
                    text=text,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    api_key=api_key
                )
            result[key] = value
        
        return result
    
    def _build_headers(self) -> Dict[str, str]:
        """
        构造请求头
        
        Returns:
            请求头字典
        """
        template = self._config.get("headers", {})
        api_key = self._config.get("api_key", "")
        
        result = {}
        for key, value in template.items():
            if isinstance(value, str):
                value = self._replace_variables(value, api_key=api_key)
            result[key] = value
        
        return result
    
    def _build_get_url(self, params: Dict[str, Any]) -> str:
        """
        构造 GET 请求 URL
        
        Args:
            params: 查询参数
            
        Returns:
            完整 URL
        """
        base_url = self._config["url"]
        
        # 构造查询字符串
        query_parts = []
        for key, value in params.items():
            if isinstance(value, str):
                # URL 编码
                from urllib.parse import quote
                query_parts.append(f"{key}={quote(value)}")
            else:
                query_parts.append(f"{key}={value}")
        
        query_string = "&".join(query_parts)
        
        # 拼接 URL
        if "?" in base_url:
            return f"{base_url}&{query_string}"
        else:
            return f"{base_url}?{query_string}"
    
    def _replace_variables(
        self, 
        template: str, 
        text: str = "", 
        source_lang: str = "", 
        target_lang: str = "",
        api_key: str = ""
    ) -> str:
        """
        替换模板变量
        
        支持的变量：
        - {text}: 待翻译文本
        - {source_lang}: 源语言
        - {target_lang}: 目标语言
        - {api_key}: API 密钥
        
        Args:
            template: 模板字符串
            text: 待翻译文本
            source_lang: 源语言
            target_lang: 目标语言
            api_key: API 密钥
            
        Returns:
            替换后的字符串
        """
        result = template
        result = result.replace("{text}", text)
        result = result.replace("{source_lang}", source_lang)
        result = result.replace("{target_lang}", target_lang)
        result = result.replace("{api_key}", api_key)
        return result
    
    def _replace_dict_variables(
        self,
        template_dict: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        替换字典中的模板变量
        
        Args:
            template_dict: 模板字典
            **kwargs: 变量参数
            
        Returns:
            替换后的字典
        """
        result = {}
        for key, value in template_dict.items():
            if isinstance(value, str):
                value = self._replace_variables(value, **kwargs)
            elif isinstance(value, dict):
                value = self._replace_dict_variables(value, **kwargs)
            result[key] = value
        return result
    
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
        if not response.is_success():
            return TranslateResult(
                code=TRANSLATE_ERROR_NETWORK,
                original_text=original_text,
                translated_text="",
                source=self.name,
                error_message=f"HTTP 错误: {response.status_code}"
            )
        
        # 解析响应
        translated_text = self._extract_translation(response)
        
        if translated_text is None:
            # 尝试直接返回响应内容
            translated_text = response.content.strip()
            
            # 如果响应是 JSON，尝试提取
            try:
                data = json.loads(translated_text)
                if isinstance(data, dict):
                    # 尝试常见的翻译字段名
                    for field in ["translated_text", "translation", "result", "text", "data"]:
                        if field in data:
                            translated_text = str(data[field])
                            break
            except json.JSONDecodeError:
                pass
        
        if not translated_text:
            return TranslateResult(
                code=TRANSLATE_ERROR_PARSE,
                original_text=original_text,
                translated_text="",
                source=self.name,
                error_message="无法从响应中提取翻译结果"
            )
        
        return TranslateResult(
            code=TRANSLATE_SUCCESS,
            original_text=original_text,
            translated_text=translated_text,
            source=self.name
        )
    
    def _extract_translation(self, response: HttpResponse) -> Optional[str]:
        """
        从响应中提取翻译结果

        Args:
            response: HTTP 响应

        Returns:
            翻译结果，提取失败返回 None
        """
        path = self._config.get("response_path", "")

        # 如果没有指定路径，尝试自动解析
        if not path:
            return None

        # 安全验证：检查路径深度和非法字符
        keys = path.split(".")
        if len(keys) > MAX_RESPONSE_PATH_DEPTH:
            logger.warning(f"响应路径深度超过限制: {len(keys)} > {MAX_RESPONSE_PATH_DEPTH}")
            return None

        # 验证路径键的合法性（防止访问特殊属性）
        for key in keys:
            if not key or key.startswith("_") or key.startswith("__"):
                logger.warning(f"响应路径包含非法键: {key}")
                return None

        # 解析 JSON
        try:
            data = response.json()
            if data is None:
                return None
        except Exception:
            return None

        # 按路径提取
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
            elif isinstance(data, list) and key.isdigit():
                idx = int(key)
                data = data[idx] if idx < len(data) else None
            else:
                return None

            if data is None:
                return None

        # 转换为字符串
        if isinstance(data, str):
            return data
        elif isinstance(data, (list, dict)):
            return json.dumps(data, ensure_ascii=False)
        else:
            return str(data)
    
    def get_supported_languages(self) -> List[str]:
        """
        获取支持的语言列表
        
        自定义 API 的语言支持取决于具体 API。
        
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
        ]
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置是否有效
        
        Args:
            config: 配置字典
            
        Returns:
            配置是否有效
        """
        return bool(config.get("url"))
