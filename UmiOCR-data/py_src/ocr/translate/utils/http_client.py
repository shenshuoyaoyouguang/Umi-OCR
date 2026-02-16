# translate/utils/http_client.py: HTTP 客户端封装

"""
HTTP 客户端封装

基于 urllib.request 封装 HTTP 请求功能，提供：
- 超时设置
- 代理禁用（安全考虑）
- 统一错误处理
"""

from __future__ import annotations
import urllib.request
import urllib.error
import json
from typing import Dict, Any, Optional, Tuple, Union

from umi_log import logger

# 默认超时秒数（与 base.py 保持一致）
DEFAULT_TIMEOUT = 10


class HttpResponse:
    """
    HTTP 响应封装类
    
    提供更友好的响应访问接口。
    """
    
    def __init__(
        self, 
        status_code: int, 
        content: Union[str, bytes],
        headers: Optional[Dict[str, str]] = None
    ):
        self.status_code = status_code
        self._content = content
        self.headers = headers or {}
        self._json_cache: Optional[Any] = None
    
    @property
    def content(self) -> str:
        """获取文本内容"""
        if isinstance(self._content, bytes):
            return self._content.decode('utf-8', errors='replace')
        return self._content
    
    @property
    def raw_content(self) -> bytes:
        """获取原始字节内容"""
        if isinstance(self._content, str):
            return self._content.encode('utf-8')
        return self._content
    
    def json(self) -> Any:
        """解析 JSON 响应"""
        if self._json_cache is not None:
            return self._json_cache
        
        try:
            self._json_cache = json.loads(self.content)
            return self._json_cache
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
            return None
    
    def is_success(self) -> bool:
        """判断请求是否成功（状态码 2xx）"""
        return 200 <= self.status_code < 300
    
    def __repr__(self) -> str:
        return f"HttpResponse(status={self.status_code}, content_length={len(self._content)})"


class HttpClient:
    """
    HTTP 客户端封装
    
    基于 urllib.request 实现，提供安全的 HTTP 请求功能。
    
    特性：
    - 默认禁用代理，防止代理劫持
    - 支持请求超时设置
    - 统一的错误处理
    """
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        """
        初始化 HTTP 客户端
        
        Args:
            timeout: 请求超时秒数，默认 10 秒
        """
        self.timeout = timeout
        # 创建不使用代理的 opener
        self._opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({})  # 禁用代理
        )
    
    def request(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> HttpResponse:
        """
        发送 HTTP 请求
        
        Args:
            url: 请求 URL
            method: 请求方法（GET/POST）
            data: 请求体数据（字典，将被 JSON 序列化）
            headers: 请求头
            timeout: 超时秒数（覆盖默认值）
            
        Returns:
            HttpResponse 实例
        """
        request_timeout = timeout or self.timeout
        req_headers = headers or {}
        
        # 准备请求体
        req_data = None
        if data is not None:
            req_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            if 'Content-Type' not in req_headers:
                req_headers['Content-Type'] = 'application/json; charset=utf-8'
        
        # 创建请求对象
        req = urllib.request.Request(
            url,
            data=req_data,
            headers=req_headers,
            method=method
        )
        
        try:
            response = self._opener.open(req, timeout=request_timeout)
            content = response.read()
            
            # 提取响应头
            resp_headers = dict(response.headers)
            
            return HttpResponse(
                status_code=response.status,
                content=content,
                headers=resp_headers
            )
            
        except urllib.error.HTTPError as e:
            # HTTP 错误（4xx, 5xx）
            content = e.read() if e.fp else b""
            return HttpResponse(
                status_code=e.code,
                content=content,
                headers=dict(e.headers) if e.headers else {}
            )
            
        except urllib.error.URLError as e:
            # 网络错误
            logger.error(f"网络请求失败: {e.reason}")
            return HttpResponse(
                status_code=0,
                content=f"网络错误: {e.reason}"
            )
            
        except TimeoutError:
            logger.error(f"请求超时: {url}")
            return HttpResponse(
                status_code=0,
                content="请求超时"
            )
            
        except Exception as e:
            logger.error(f"请求异常: {e}", exc_info=True)
            return HttpResponse(
                status_code=0,
                content=f"请求异常: {str(e)}"
            )
    
    def get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> HttpResponse:
        """
        发送 GET 请求
        
        Args:
            url: 请求 URL
            headers: 请求头
            timeout: 超时秒数
            
        Returns:
            HttpResponse 实例
        """
        return self.request(url, method="GET", headers=headers, timeout=timeout)
    
    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> HttpResponse:
        """
        发送 POST 请求
        
        Args:
            url: 请求 URL
            data: 请求体数据
            headers: 请求头
            timeout: 超时秒数
            
        Returns:
            HttpResponse 实例
        """
        return self.request(url, method="POST", data=data, headers=headers, timeout=timeout)
    
    def post_raw(
        self,
        url: str,
        data: bytes,
        headers: Dict[str, str],
        timeout: Optional[int] = None
    ) -> HttpResponse:
        """
        发送原始字节 POST 请求
        
        用于需要精确控制请求体的场景（如签名请求）。
        
        Args:
            url: 请求 URL
            data: 原始请求体字节
            headers: 请求头
            timeout: 超时秒数
            
        Returns:
            HttpResponse 实例
        """
        request_timeout = timeout or self.timeout
        
        req = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method="POST"
        )
        
        try:
            response = self._opener.open(req, timeout=request_timeout)
            content = response.read()
            resp_headers = dict(response.headers)
            
            return HttpResponse(
                status_code=response.status,
                content=content,
                headers=resp_headers
            )
            
        except urllib.error.HTTPError as e:
            content = e.read() if e.fp else b""
            return HttpResponse(
                status_code=e.code,
                content=content,
                headers=dict(e.headers) if e.headers else {}
            )
            
        except urllib.error.URLError as e:
            logger.error(f"网络请求失败: {e.reason}")
            return HttpResponse(
                status_code=0,
                content=f"网络错误: {e.reason}"
            )
            
        except TimeoutError:
            logger.error(f"请求超时: {url}")
            return HttpResponse(
                status_code=0,
                content="请求超时"
            )
            
        except Exception as e:
            logger.error(f"请求异常: {e}", exc_info=True)
            return HttpResponse(
                status_code=0,
                content=f"请求异常: {str(e)}"
            )


# 全局默认客户端实例
default_client = HttpClient()
