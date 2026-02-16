# translate/utils/signature.py: 腾讯云 API 签名算法

"""
腾讯云 API 签名算法

实现 TC3-HMAC-SHA256 签名算法，用于腾讯云 API 请求认证。

参考文档：https://cloud.tencent.com/document/api/213/30654
"""

from __future__ import annotations
import hashlib
import hmac
import time
from datetime import datetime
from typing import Dict, Optional


class TencentSigner:
    """
    腾讯云 TC3-HMAC-SHA256 签名器
    
    用于生成腾讯云 API 请求的签名。
    """
    
    # 算法标识
    ALGORITHM = "TC3-HMAC-SHA256"
    
    @staticmethod
    def sign(
        secret_id: str,
        secret_key: str,
        service: str,
        host: str,
        action: str,
        payload: str,
        timestamp: Optional[int] = None,
        region: str = "",
        version: str = "2018-03-21"
    ) -> Dict[str, str]:
        """
        生成腾讯云 API 签名
        
        Args:
            secret_id: 腾讯云 SecretId
            secret_key: 腾讯云 SecretKey
            service: 服务名称（如 "tmt"）
            host: 请求主机（如 "tmt.tencentcloudapi.com"）
            action: API 动作名称（如 "TextTranslate"）
            payload: 请求体 JSON 字符串
            timestamp: 时间戳（可选，默认当前时间）
            region: 地域（可选）
            version: API 版本
            
        Returns:
            包含 Authorization 等请求头的字典
        """
        # 使用当前时间戳（如果未提供）
        if timestamp is None:
            timestamp = int(time.time())
        
        # 1. 拼接规范请求串
        http_request_method = "POST"
        canonical_uri = "/"
        canonical_querystring = ""
        content_type = "application/json; charset=utf-8"
        
        # 规范请求头
        canonical_headers = (
            f"content-type:{content_type}\n"
            f"host:{host}\n"
        )
        signed_headers = "content-type;host"
        
        # 请求体哈希
        hashed_request_payload = hashlib.sha256(
            payload.encode("utf-8")
        ).hexdigest()
        
        canonical_request = (
            f"{http_request_method}\n"
            f"{canonical_uri}\n"
            f"{canonical_querystring}\n"
            f"{canonical_headers}\n"
            f"{signed_headers}\n"
            f"{hashed_request_payload}"
        )
        
        # 2. 拼接待签名字符串
        date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")
        credential_scope = f"{date}/{service}/tc3_request"
        
        hashed_canonical_request = hashlib.sha256(
            canonical_request.encode("utf-8")
        ).hexdigest()
        
        string_to_sign = (
            f"{TencentSigner.ALGORITHM}\n"
            f"{timestamp}\n"
            f"{credential_scope}\n"
            f"{hashed_canonical_request}"
        )
        
        # 3. 计算签名
        # 派生密钥
        secret_date = TencentSigner._hmac_sha256(
            ("TC3" + secret_key).encode("utf-8"),
            date
        )
        secret_service = TencentSigner._hmac_sha256(secret_date, service)
        secret_signing = TencentSigner._hmac_sha256(secret_service, "tc3_request")
        
        # 计算签名
        signature = hmac.new(
            secret_signing,
            string_to_sign.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        # 4. 拼接 Authorization
        authorization = (
            f"{TencentSigner.ALGORITHM} "
            f"Credential={secret_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        
        # 5. 构造请求头
        headers = {
            "Authorization": authorization,
            "Content-Type": content_type,
            "Host": host,
            "X-TC-Action": action,
            "X-TC-Timestamp": str(timestamp),
            "X-TC-Version": version,
        }
        
        # 添加地域（如果指定）
        if region:
            headers["X-TC-Region"] = region
        
        return headers
    
    @staticmethod
    def _hmac_sha256(key: bytes, msg: str) -> bytes:
        """
        HMAC-SHA256 计算
        
        Args:
            key: 密钥字节
            msg: 消息字符串
            
        Returns:
            HMAC 结果字节
        """
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()
    
    @staticmethod
    def sha256_hex(data: str) -> str:
        """
        计算字符串的 SHA256 哈希值（十六进制）
        
        Args:
            data: 输入字符串
            
        Returns:
            十六进制哈希字符串
        """
        return hashlib.sha256(data.encode("utf-8")).hexdigest()


def generate_tencent_signature(
    secret_id: str,
    secret_key: str,
    service: str,
    host: str,
    action: str,
    payload: str,
    **kwargs
) -> Dict[str, str]:
    """
    生成腾讯云 API 签名（便捷函数）
    
    Args:
        secret_id: 腾讯云 SecretId
        secret_key: 腾讯云 SecretKey
        service: 服务名称
        host: 请求主机
        action: API 动作名称
        payload: 请求体 JSON 字符串
        **kwargs: 其他参数
        
    Returns:
        签名请求头字典
    """
    return TencentSigner.sign(
        secret_id=secret_id,
        secret_key=secret_key,
        service=service,
        host=host,
        action=action,
        payload=payload,
        **kwargs
    )
