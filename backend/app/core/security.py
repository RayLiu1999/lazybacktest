"""
安全模組

提供速率限制、CSRF 防護、輸入消毒等安全功能。
"""
import secrets
import time
import re
from typing import Dict, Optional
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
import hashlib
import html

from fastapi import Request, HTTPException, status
from pydantic import BaseModel, Field, field_validator


# ========== 速率限制 (Rate Limiting) ==========

class RateLimiter:
    """
    記憶體式速率限制器
    
    使用滑動視窗演算法限制請求頻率。
    生產環境建議改用 Redis 後端。
    """
    
    def __init__(self):
        # {ip: [(timestamp, count), ...]}
        self._requests: Dict[str, list] = defaultdict(list)
        self._cleanup_interval = 60  # 每 60 秒清理過期記錄
        self._last_cleanup = time.time()
    
    def _cleanup(self):
        """清理過期的請求記錄"""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        cutoff = now - 3600  # 保留最近 1 小時的記錄
        for ip in list(self._requests.keys()):
            self._requests[ip] = [
                (ts, count) for ts, count in self._requests[ip]
                if ts > cutoff
            ]
            if not self._requests[ip]:
                del self._requests[ip]
        
        self._last_cleanup = now
    
    def is_allowed(self, ip: str, limit: int, window_seconds: int) -> tuple[bool, int]:
        """
        檢查請求是否在限制範圍內
        
        Args:
            ip: 客戶端 IP
            limit: 時間窗口內允許的最大請求數
            window_seconds: 時間窗口（秒）
            
        Returns:
            (是否允許, 剩餘請求數)
        """
        self._cleanup()
        
        now = time.time()
        cutoff = now - window_seconds
        
        # 計算時間窗口內的請求數
        recent_requests = [
            (ts, count) for ts, count in self._requests[ip]
            if ts > cutoff
        ]
        total_requests = sum(count for _, count in recent_requests)
        
        if total_requests >= limit:
            return False, 0
        
        # 記錄此次請求
        self._requests[ip].append((now, 1))
        
        remaining = limit - total_requests - 1
        return True, remaining


# 全域速率限制器實例
rate_limiter = RateLimiter()


def check_rate_limit(
    request: Request,
    limit: int = 5,
    window_seconds: int = 60
) -> None:
    """
    速率限制檢查
    
    Args:
        request: FastAPI Request 物件
        limit: 時間窗口內允許的最大請求數 (預設每分鐘 5 次)
        window_seconds: 時間窗口（秒）
        
    Raises:
        HTTPException: 超過速率限制時拋出 429 錯誤
    """
    # 取得客戶端 IP (考慮代理)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    allowed, remaining = rate_limiter.is_allowed(client_ip, limit, window_seconds)
    
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "message": "請求過於頻繁，請稍後再試",
                "retry_after": window_seconds
            },
            headers={
                "Retry-After": str(window_seconds),
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0"
            }
        )


# ========== CSRF 防護 ==========

class CSRFTokenStore:
    """
    CSRF Token 儲存與驗證
    
    使用記憶體儲存 Token，生產環境建議改用 Redis。
    """
    
    def __init__(self, token_lifetime_seconds: int = 3600):
        self._tokens: Dict[str, float] = {}  # {token: expiry_timestamp}
        self._lifetime = token_lifetime_seconds
        self._cleanup_interval = 300
        self._last_cleanup = time.time()
    
    def _cleanup(self):
        """清理過期 Token"""
        now = time.time()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        
        self._tokens = {
            token: expiry for token, expiry in self._tokens.items()
            if expiry > now
        }
        self._last_cleanup = now
    
    def generate_token(self) -> str:
        """
        產生新的 CSRF Token
        
        Returns:
            新產生的 Token 字串
        """
        self._cleanup()
        
        token = secrets.token_urlsafe(32)
        expiry = time.time() + self._lifetime
        self._tokens[token] = expiry
        
        return token
    
    def validate_token(self, token: str) -> bool:
        """
        驗證 CSRF Token
        
        Args:
            token: 待驗證的 Token
            
        Returns:
            Token 是否有效
        """
        if not token:
            return False
        
        self._cleanup()
        
        expiry = self._tokens.get(token)
        if not expiry:
            return False
        
        if time.time() > expiry:
            del self._tokens[token]
            return False
        
        # Token 使用後刪除 (一次性使用)
        del self._tokens[token]
        return True


# 全域 CSRF Token 儲存實例
csrf_store = CSRFTokenStore()


def verify_csrf_token(request: Request, token: Optional[str] = None) -> None:
    """
    驗證 CSRF Token
    
    Args:
        request: FastAPI Request 物件
        token: CSRF Token (若為 None，從 Header 取得)
        
    Raises:
        HTTPException: Token 無效時拋出 403 錯誤
    """
    if token is None:
        token = request.headers.get("X-CSRF-Token")
    
    if not csrf_store.validate_token(token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "csrf_validation_failed",
                "message": "CSRF Token 無效或已過期，請重新取得"
            }
        )


# ========== 輸入驗證與消毒 ==========

def sanitize_html(text: str) -> str:
    """
    HTML 消毒 - 移除潛在的 XSS 攻擊向量
    
    Args:
        text: 原始文字
        
    Returns:
        消毒後的文字
    """
    if not text:
        return text
    
    # 1. HTML 實體編碼
    sanitized = html.escape(text)
    
    # 2. 移除可能的 JavaScript 協議
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'data:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'vbscript:', '', sanitized, flags=re.IGNORECASE)
    
    # 3. 移除多餘的空白
    sanitized = ' '.join(sanitized.split())
    
    return sanitized


def validate_email(email: str) -> bool:
    """
    驗證 Email 格式
    
    Args:
        email: Email 地址
        
    Returns:
        是否為有效的 Email 格式
    """
    if not email:
        return True  # 選填欄位，空值為合法
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# ========== Pydantic 模型 ==========

class FeedbackRequest(BaseModel):
    """問題回報請求模型"""
    
    type: str = Field(
        ...,
        description="回報類型: bug, feature, question",
        min_length=1,
        max_length=20
    )
    title: str = Field(
        ...,
        description="標題",
        min_length=1,
        max_length=200
    )
    description: str = Field(
        ...,
        description="詳細說明",
        min_length=10,
        max_length=5000
    )
    email: Optional[str] = Field(
        None,
        description="聯絡信箱（選填）",
        max_length=255
    )
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        allowed_types = ['bug', 'feature', 'question']
        if v not in allowed_types:
            raise ValueError(f"類型必須是 {allowed_types} 其中之一")
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v):
        if v and not validate_email(v):
            raise ValueError("Email 格式不正確")
        return v
    
    def sanitized(self) -> "FeedbackRequest":
        """回傳消毒後的資料"""
        return FeedbackRequest(
            type=self.type,
            title=sanitize_html(self.title),
            description=sanitize_html(self.description),
            email=self.email
        )


class CSRFTokenResponse(BaseModel):
    """CSRF Token 回應模型"""
    csrf_token: str
    expires_in: int = 3600
