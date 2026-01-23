"""
問題回報 API 端點

提供安全的問題回報功能，包含速率限制、CSRF 防護與 LINE Bot 通知。
"""
from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel

from app.core.security import (
    check_rate_limit,
    verify_csrf_token,
    csrf_store,
    FeedbackRequest,
    CSRFTokenResponse
)
from app.services.line_notify import line_notify_service

router = APIRouter()


class FeedbackResponse(BaseModel):
    """問題回報回應模型"""
    success: bool
    message: str
    notification_sent: bool = False


@router.get("/csrf-token", response_model=CSRFTokenResponse)
async def get_csrf_token(request: Request):
    """
    取得 CSRF Token
    
    此端點不受速率限制，但 Token 有效期為 1 小時且僅能使用一次。
    """
    token = csrf_store.generate_token()
    return CSRFTokenResponse(csrf_token=token)


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(
    request: Request,
    feedback: FeedbackRequest
):
    """
    提交問題回報
    
    安全機制：
    - 速率限制: 每個 IP 每分鐘最多 5 次請求
    - CSRF 防護: 需提供有效的 CSRF Token
    - 輸入消毒: 自動過濾 XSS 攻擊向量
    """
    # 1. 速率限制檢查
    check_rate_limit(request, limit=5, window_seconds=60)
    
    # 2. CSRF Token 驗證
    verify_csrf_token(request)
    
    # 3. 輸入消毒
    sanitized_feedback = feedback.sanitized()
    
    # 4. 取得客戶端 IP
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    # 5. 發送 LINE 通知
    notification_sent = await line_notify_service.send_feedback_notification(
        feedback_type=sanitized_feedback.type,
        title=sanitized_feedback.title,
        description=sanitized_feedback.description,
        email=sanitized_feedback.email,
        client_ip=client_ip
    )
    
    return FeedbackResponse(
        success=True,
        message="感謝您的回饋！我們已收到您的問題回報。",
        notification_sent=notification_sent
    )
