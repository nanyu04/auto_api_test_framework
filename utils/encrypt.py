"""
【工具 — 加密类】
"""
import hashlib
import hmac
import base64


def md5(text: str) -> str:
    """MD5 哈希"""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def sha256(text: str) -> str:
    """SHA-256 哈希"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hmac_sha256(key: str, text: str) -> str:
    """HMAC-SHA256 签名"""
    return hmac.new(key.encode(), text.encode(), hashlib.sha256).hexdigest()


def base64_encode(text: str) -> str:
    """Base64 编码"""
    return base64.b64encode(text.encode("utf-8")).decode()


def base64_decode(text: str) -> str:
    """Base64 解码"""
    return base64.b64decode(text).decode("utf-8")


def sha256_with_salt(text: str, salt: str) -> str:
    """加盐 SHA-256"""
    return hashlib.sha256((text + salt).encode()).hexdigest()